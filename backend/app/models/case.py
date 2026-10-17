from pydantic import BaseModel, Field

from app.models.enums import CaseType, Severity, Tier


class Party(BaseModel):
    role: str  # e.g. "petitioner", "detenu", "respondent"
    name: str | None = None
    relationship: str | None = None
    details: str | None = None


class KeyDate(BaseModel):
    label: str
    date: str | None = None  # ISO date if known, else None (treated as missing)
    description: str | None = None


class CaseFacts(BaseModel):
    case_type: CaseType = CaseType.OTHER
    parties: list[Party] = Field(default_factory=list)
    key_dates: list[KeyDate] = Field(default_factory=list)
    location: str | None = None
    police_station: str | None = None
    facts_narrative: str = ""
    legal_issues: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    field: str
    severity: Severity
    message: str
    tier: Tier


class CaseInputRequest(BaseModel):
    text: str | None = None


class CaseRecord(BaseModel):
    id: str
    raw_text: str
    case_facts: CaseFacts
    validation_issues: list[ValidationIssue] = Field(default_factory=list)
    created_at: str
