from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.models.case import CaseFacts, ValidationIssue
from app.models.enums import Tier
from app.models.research import ConfidenceBreakdown, Precedent, ResearchFinding, ResearchReport
from app.services.legal_sources.aggregator import LegalSourceAggregator, court_authority_weight
from app.services.llm import generate_structured

_DEFAULT_QUERIES_BY_CASE_TYPE = {
    "habeas_corpus": "habeas corpus illegal detention arrest grounds production before magistrate",
}


def _build_queries(facts: CaseFacts) -> list[str]:
    queries: list[str] = []
    if facts.legal_issues:
        queries.append(" ".join(facts.legal_issues)[:1500])
    default = _DEFAULT_QUERIES_BY_CASE_TYPE.get(facts.case_type.value)
    if default:
        queries.append(default)
    if facts.facts_narrative:
        queries.append(facts.facts_narrative[:1500])
    return queries or ["legal precedent"]


class _PrecedentAssessment(BaseModel):
    index: int  # 1-based position in the "Candidate precedents" list below — never the title,
    # since an LLM-reproduced title can drift (whitespace/punctuation/truncation) from the
    # original and silently fail to match, leaving relevance_score stuck at its 0.0 default.
    relevance_score: float = Field(ge=0, le=1)
    applicability_note: str


class _ResearchAnalysis(BaseModel):
    precedent_assessments: list[_PrecedentAssessment] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)


_ANALYSIS_SYSTEM_INSTRUCTION = """You are a legal research analyst comparing a current case
against candidate precedents retrieved from real court sources. For each precedent, score how
applicable it is to the current case's facts and legal issues (0 = irrelevant, 1 = directly
on point) and write one sentence on why — identify each precedent by its index number (1-based
position in the "Candidate precedents" list), not its title. Then write up to 5 overall
findings synthesizing what the available precedents suggest for this case. Ground every
statement strictly in the provided case facts and precedent snippets — do not assume facts not
given, and do not cite any case not present in the provided precedent list. Score and return
every precedent in the list — do not skip any."""


async def _assess_precedents(facts: CaseFacts, precedents: list[Precedent]) -> _ResearchAnalysis:
    if not precedents:
        return _ResearchAnalysis(
            findings=[
                "No precedents were returned by the connected legal-data sources for this "
                "case's search terms. This may reflect the limited coverage of the free-tier "
                "sources currently connected, not an absence of relevant law — verify manually "
                "before relying on this absence."
            ]
        )
    precedent_blob = "\n\n".join(
        f"{idx}. {p.title} | court: {p.court} | date: {p.date}\n  snippet: {p.snippet}"
        for idx, p in enumerate(precedents, start=1)
    )
    prompt = (
        f"Case facts:\n{facts.model_dump_json(indent=2)}\n\n"
        f"Candidate precedents:\n{precedent_blob}"
    )
    return generate_structured(prompt, _ResearchAnalysis, system_instruction=_ANALYSIS_SYSTEM_INSTRUCTION)


def _compute_confidence(
    facts: CaseFacts,
    validation_issues: list[ValidationIssue],
    precedents: list[Precedent],
) -> tuple[float, ConfidenceBreakdown]:
    missing_count = sum(1 for i in validation_issues if i.severity.value == "missing")
    total_required = max(missing_count + 1, 5)  # avoid div-by-zero; rough normalization
    data_completeness = max(0.0, 1 - (missing_count / total_required))

    source_count_score = min(1.0, len(precedents) / 5)

    if precedents:
        court_authority = sum(court_authority_weight(p.court) for p in precedents) / len(precedents)
        llm_relevance_avg = sum(p.relevance_score for p in precedents) / len(precedents)
    else:
        court_authority = 0.0
        llm_relevance_avg = 0.0

    breakdown = ConfidenceBreakdown(
        data_completeness=round(data_completeness, 3),
        source_count_score=round(source_count_score, 3),
        court_authority_weight=round(court_authority, 3),
        llm_relevance_avg=round(llm_relevance_avg, 3),
    )
    score = (
        0.30 * data_completeness
        + 0.20 * source_count_score
        + 0.20 * court_authority
        + 0.30 * llm_relevance_avg
    ) * 100
    return round(score, 1), breakdown


async def run_research(
    facts: CaseFacts,
    validation_issues: list[ValidationIssue],
    *,
    court_filter: list[str] | None = None,
) -> ResearchReport:
    aggregator = LegalSourceAggregator()
    queries = _build_queries(facts)

    merged: dict[str, Precedent] = {}
    for query in queries:
        results = await aggregator.search(query, court_filter=court_filter, limit_per_source=5)
        for p in results:
            merged.setdefault(p.title.strip().lower(), p)
    precedents = list(merged.values())

    analysis = await _assess_precedents(facts, precedents)
    assessment_by_index = {a.index: a for a in analysis.precedent_assessments}
    for idx, p in enumerate(precedents, start=1):
        match = assessment_by_index.get(idx)
        if match:
            p.relevance_score = match.relevance_score
            p.applicability_note = match.applicability_note

    precedents.sort(key=lambda p: (court_authority_weight(p.court), p.relevance_score), reverse=True)

    confidence_score, breakdown = _compute_confidence(facts, validation_issues, precedents)

    findings = [ResearchFinding(summary=f, tier=Tier.AI_ANALYSIS) for f in analysis.findings]

    return ResearchReport(
        findings=findings,
        precedents=precedents,
        confidence_score=confidence_score,
        confidence_breakdown=breakdown,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
