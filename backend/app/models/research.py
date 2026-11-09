from pydantic import BaseModel, Field

from app.models.enums import Tier


class Precedent(BaseModel):
    title: str
    citation: str | None = None
    court: str | None = None
    date: str | None = None
    source_url: str
    snippet: str
    relevance_score: float = 0.0  # 0-1, AI-assessed applicability to the current case
    applicability_note: str | None = None  # AI_ANALYSIS: why this precedent matters here
    retrieved_at: str
    source_adapter: str
    tier: Tier = Tier.VERIFIED_COURT


class ResearchFinding(BaseModel):
    summary: str
    tier: Tier = Tier.AI_ANALYSIS
    supporting_precedent_titles: list[str] = Field(default_factory=list)


class ConfidenceBreakdown(BaseModel):
    data_completeness: float
    source_count_score: float
    court_authority_weight: float
    llm_relevance_avg: float


class ResearchReport(BaseModel):
    findings: list[ResearchFinding] = Field(default_factory=list)
    precedents: list[Precedent] = Field(default_factory=list)
    confidence_score: float
    confidence_breakdown: ConfidenceBreakdown
    generated_at: str


class AttachedPrecedent(Precedent):
    """A precedent the user has curated onto the case — either picked from the research
    results or typed in manually. When any precedents are attached, drafting cites only
    these instead of the full (unfiltered) research results."""

    id: str
    attach_source: str  # "research" | "manual"
    attached_at: str


class ManualPrecedentInput(BaseModel):
    """A precedent the user knows about but that wasn't surfaced by research — entered by
    hand, so it's tagged EXTRACTED (user-supplied, not independently verified by the
    platform against a court source), never VERIFIED_COURT."""

    title: str
    citation: str | None = None
    court: str | None = None
    date: str | None = None
    source_url: str | None = None
    note: str | None = None
