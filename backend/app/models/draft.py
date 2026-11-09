from pydantic import BaseModel, Field

from app.models.enums import DraftStatus, Severity, Tier


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
    status: DraftStatus = DraftStatus.DRAFT
    generated_at: str


class DraftEditRequest(BaseModel):
    """Payload for saving user edits to a generated draft before final approval."""

    sections: list[DraftSection]
