from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.models.case import CaseFacts
from app.models.draft import ContentBlock, DraftOutput, DraftSection, FlaggedIssue
from app.models.enums import Severity, Tier
from app.models.research import Precedent, ResearchReport
from app.services import templates
from app.services.llm import generate_structured
from app.services.validation import check_required_fields

_SYSTEM_INSTRUCTION = """You are a senior litigation drafter preparing a court filing for an
Indian court. You must ground every factual statement strictly in the provided, validated case
facts and the provided list of real precedents — never invent names, dates, FIR numbers,
addresses, or case citations that are not given to you.

Formatting conventions you MUST follow, matching professional drafting practice:
- Do NOT repeat the section heading as a block of its own — the heading is rendered separately
  by the caller. The first block of each section must be substantive content, not a restatement
  of the section's title or number.
- Where a specific fact (name, date, address, FIR number, etc.) is required by the section but
  was not provided in the case facts, write a bracketed placeholder in this exact style:
  "[FIELD DESCRIPTION — GENUINELY ABSENT]". Do not guess or fabricate a value.
- Where something needs independent verification before filing (e.g. a citation's exact neutral
  number, a procedural rule, a document to be annexed), add "[DRAFTER'S NOTE: ...]" explaining
  what must be verified.
- Only cite a precedent (case name + citation) if it appears verbatim in the "Available
  precedents" list below — never invent a citation. If no precedent in the list supports a
  ground you'd normally cite, state the legal proposition without a citation and add a
  DRAFTER'S NOTE that supporting authority should be sourced.
- Tag EVERY block of text you produce with a tier:
  - "EXTRACTED" — a sentence that restates a fact directly from the provided case facts, with
    no added characterization.
  - "VERIFIED_COURT" — a sentence whose substance is a citation/quote from the provided
    precedent list.
  - "AI_ANALYSIS" — everything else: legal argument, characterization, structuring, synthesis.
- Produce sections in exactly the order and under exactly the headings given in
  "Required sections", one DraftSection per heading, using the key provided.
- Also produce a flagged_issues list covering: any missing_information you had to placeholder,
  any unsupported_claim risk, any conflicting_precedent you noticed among the provided
  precedents, and anything that needs lawyer_review before filing (e.g. verification items).
"""


class _BlockOut(BaseModel):
    text: str
    tier: str


class _SectionOut(BaseModel):
    key: str
    blocks: list[_BlockOut] = Field(default_factory=list)


class _IssueOut(BaseModel):
    category: str
    severity: str
    message: str
    section: str | None = None


class _DraftGenOutput(BaseModel):
    sections: list[_SectionOut] = Field(default_factory=list)
    flagged_issues: list[_IssueOut] = Field(default_factory=list)


_SEVERITY_MAP = {s.value: s for s in Severity}
_TIER_MAP = {t.value: t for t in Tier}


def _normalize(text: str) -> str:
    return "".join(ch for ch in text.lower() if ch.isalnum())


def _drop_heading_echo(heading: str, blocks: list[ContentBlock]) -> list[ContentBlock]:
    """Belt-and-suspenders: drop a leading block that just restates the heading,
    in case the model doesn't follow the system instruction against doing so."""
    if blocks and _normalize(blocks[0].text) == _normalize(heading):
        return blocks[1:]
    return blocks


def _precedents_blob(precedents: list[Precedent]) -> str:
    if not precedents:
        return "(none available — do not cite any case law in this draft)"
    return "\n\n".join(
        f"- {p.title} | citation: {p.citation or 'not given — do not state a citation'} | "
        f"court: {p.court} | date: {p.date}\n  snippet: {p.snippet}\n  "
        f"applicability: {p.applicability_note or 'n/a'}"
        for p in precedents
    )


async def generate_draft(
    facts: CaseFacts,
    research: ResearchReport | None,
    court_id: str,
    proceeding_type: str,
) -> DraftOutput:
    court_profile = templates.get_court_profile(court_id)
    proceeding = templates.get_proceeding_template(proceeding_type)

    required_field_issues = check_required_fields(facts)
    precedents = research.precedents if research else []

    section_spec = "\n".join(f"- key: {s['key']}, heading: {s['heading']}" for s in proceeding["sections"])

    prompt = f"""Court profile:
{court_profile}

Proceeding: {proceeding['name']}
Petition title: {proceeding['petition_title_template']}

Required sections (produce exactly these, in this order):
{section_spec}

Validated case facts:
{facts.model_dump_json(indent=2)}

Required-field validation (fields already confirmed missing — placeholder these, do not guess):
{[i.message for i in required_field_issues]}

Available precedents (only cite from this list, never invent a citation):
{_precedents_blob(precedents)}
"""

    result = generate_structured(prompt, _DraftGenOutput, system_instruction=_SYSTEM_INSTRUCTION)

    heading_by_key = {s["key"]: s["heading"] for s in proceeding["sections"]}
    sections: list[DraftSection] = []
    for section_out in result.sections:
        heading = heading_by_key.get(section_out.key, section_out.key)
        blocks = [
            ContentBlock(text=b.text, tier=_TIER_MAP.get(b.tier, Tier.AI_ANALYSIS))
            for b in section_out.blocks
        ]
        blocks = _drop_heading_echo(heading, blocks)
        sections.append(DraftSection(heading=heading, blocks=blocks))

    flagged_issues = [
        FlaggedIssue(
            category=i.category,
            severity=_SEVERITY_MAP.get(i.severity, Severity.NEEDS_REVIEW),
            message=i.message,
            section=i.section,
        )
        for i in result.flagged_issues
    ]
    # Always surface required-field gaps as flagged issues too, even if the LLM missed one.
    for issue in required_field_issues:
        flagged_issues.append(
            FlaggedIssue(
                category="missing_information",
                severity=issue.severity,
                message=issue.message,
                section=None,
            )
        )

    confidence_score = research.confidence_score if research else 0.0

    return DraftOutput(
        court_id=court_id,
        proceeding_type=proceeding_type,
        sections=sections,
        flagged_issues=flagged_issues,
        confidence_score=confidence_score,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
