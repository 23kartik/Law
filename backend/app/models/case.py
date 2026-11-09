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
    # FIR/case-crime number for Certiorari, or the number of the impugned order being
    # challenged — generic enough to cover either without a per-category field.
    case_reference_number: str | None = None
    # The public authority/official/tribunal/office at the centre of the writ: the
    # duty-bearer for Mandamus, the court/tribunal for Prohibition, the office-holder's
    # office for Quo Warranto.
    authority_name: str | None = None
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


class CategorySuggestion(BaseModel):
    """AI-suggested writ petition category — always reviewable/overridable by the user
    via the case's case_type field, which is what drafting actually uses."""

    category: CaseType
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    tier: Tier = Tier.AI_ANALYSIS


class CaseRecord(BaseModel):
    id: str
    raw_text: str
    case_facts: CaseFacts
    validation_issues: list[ValidationIssue] = Field(default_factory=list)
    category_suggestion: CategorySuggestion | None = None
    created_at: str
