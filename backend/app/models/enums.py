from enum import Enum


class Tier(str, Enum):
    """Provenance tag attached to every piece of output content.

    This is the backbone of the "clearly distinguish between verified court
    information, extracted information, and AI-generated analysis" requirement.
    """

    VERIFIED_COURT = "VERIFIED_COURT"
    EXTRACTED = "EXTRACTED"
    AI_ANALYSIS = "AI_ANALYSIS"


class Severity(str, Enum):
    MISSING = "missing"
    CONFLICTING = "conflicting"
    UNSUPPORTED = "unsupported"
    NEEDS_REVIEW = "needs_review"


class CaseType(str, Enum):
    HABEAS_CORPUS = "habeas_corpus"
    OTHER = "other"
