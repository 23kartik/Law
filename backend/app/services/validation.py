from pydantic import BaseModel, Field

from app.models.case import CaseFacts
from app.models.enums import CaseType, Severity, Tier
from app.models.case import ValidationIssue
from app.services.llm import generate_structured

# Deterministic, auditable required-field rules per case type — this is what
# actually drives "missing" findings, kept separate from LLM judgment so the
# platform's validation claims are reproducible and traceable.
_REQUIRED_FIELDS: dict[CaseType, list[tuple[str, str]]] = {
    CaseType.HABEAS_CORPUS: [
        ("parties.petitioner", "Petitioner's full name, parentage, age and address"),
        ("parties.detenu", "Detenu's full name, parentage, age and address"),
        ("petitioner_relationship", "Petitioner's relationship to the detenu"),
        ("location", "Place of detention (city/state)"),
        ("police_station", "Police station or detaining authority"),
        ("arrest_date", "Date and time of arrest/detention"),
        ("facts_narrative", "Narrative of facts"),
    ],
}


def _has_party(facts: CaseFacts, role: str) -> bool:
    return any(p.role.lower() == role and (p.name or p.details) for p in facts.parties)


def _has_date(facts: CaseFacts, label_contains: str) -> bool:
    label_contains = label_contains.lower()
    return any(label_contains in d.label.lower() and d.date for d in facts.key_dates)


def check_required_fields(facts: CaseFacts) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    required = _REQUIRED_FIELDS.get(facts.case_type, [])
    for field, label in required:
        present = True
        if field == "parties.petitioner":
            present = _has_party(facts, "petitioner")
        elif field == "parties.detenu":
            present = _has_party(facts, "detenu")
        elif field == "petitioner_relationship":
            present = any(p.role.lower() == "petitioner" and p.relationship for p in facts.parties)
        elif field == "location":
            present = bool(facts.location)
        elif field == "police_station":
            present = bool(facts.police_station)
        elif field == "arrest_date":
            present = _has_date(facts, "arrest")
        elif field == "facts_narrative":
            present = bool(facts.facts_narrative.strip())

        if not present:
            issues.append(
                ValidationIssue(
                    field=field,
                    severity=Severity.MISSING,
                    message=f"{label} — not provided, genuinely absent.",
                    tier=Tier.EXTRACTED,
                )
            )
    return issues


class _ConsistencyFinding(BaseModel):
    field: str
    severity: str  # "conflicting" | "unsupported"
    message: str


class _ConsistencyReport(BaseModel):
    findings: list[_ConsistencyFinding] = Field(default_factory=list)


_CONSISTENCY_SYSTEM_INSTRUCTION = """You are a legal case-intake reviewer. Given structured
case facts, identify ONLY genuine internal inconsistencies (e.g. contradictory dates, a
detenu described as both released and still detained) or assertions that are stated as fact
but not actually supported by the narrative provided. Do not flag merely incomplete
information — that is handled separately. If there are no issues, return an empty list."""


def check_consistency(facts: CaseFacts) -> list[ValidationIssue]:
    prompt = f"Case facts:\n{facts.model_dump_json(indent=2)}"
    report = generate_structured(prompt, _ConsistencyReport, system_instruction=_CONSISTENCY_SYSTEM_INSTRUCTION)
    severity_map = {"conflicting": Severity.CONFLICTING, "unsupported": Severity.UNSUPPORTED}
    return [
        ValidationIssue(
            field=f.field,
            severity=severity_map.get(f.severity, Severity.UNSUPPORTED),
            message=f.message,
            tier=Tier.AI_ANALYSIS,
        )
        for f in report.findings
    ]


def validate_case_facts(facts: CaseFacts) -> list[ValidationIssue]:
    return check_required_fields(facts) + check_consistency(facts)
