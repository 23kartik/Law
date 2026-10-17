from pydantic import BaseModel, Field

from app.models.enums import Severity, Tier


class ContentBlock(BaseModel):
    text: str
    tier: Tier


class DraftSection(BaseModel):
    heading: str
    paragraph_prefix: str | None = None  # e.g. "1." numbering root
    blocks: list[ContentBlock] = Field(default_factory=list)


class FlaggedIssue(BaseModel):
    category: str  # "missing_information" | "unsupported_claim" | "conflicting_precedent" | "lawyer_review"
    severity: Severity
    message: str
    section: str | None = None


class DraftRequest(BaseModel):
    court_id: str
    proceeding_type: str


class DraftOutput(BaseModel):
    court_id: str
    proceeding_type: str
    sections: list[DraftSection] = Field(default_factory=list)
    flagged_issues: list[FlaggedIssue] = Field(default_factory=list)
    confidence_score: float
    generated_at: str
