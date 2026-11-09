from pydantic import BaseModel, Field

from app.models.case import CaseFacts, CategorySuggestion
from app.models.enums import CaseType, Tier
from app.services.llm import generate_structured

_SYSTEM_INSTRUCTION = """You are a senior Indian litigation drafter classifying a matter into
one of the five writ petition categories issuable by a High Court under Article 226 (or by the
Supreme Court under Article 32) of the Constitution of India, based ONLY on the structured case
facts given to you. Use these exact definitions:

- habeas_corpus: a person is allegedly detained illegally; the petition seeks to have the
  detained person produced before the court and obtain appropriate relief.
- mandamus: a government authority or public official has failed to perform a legal or public
  duty; the petition seeks a direction from the court to perform that duty.
- prohibition: a lower court or tribunal is proceeding, or about to proceed, with a case beyond
  its legal authority/jurisdiction; the petition seeks to stop it before it decides the matter.
- certiorari: a lower court, tribunal, or authority has already passed an unlawful order (e.g. an
  FIR, adjudication, or decision); the petition seeks to quash that order.
- quo_warranto: a person's legal authority/qualification to hold a public office is in question;
  the petition seeks to challenge their right to hold that office.
- other: the matter does not genuinely fit any of the above five writ categories.

Pick exactly one category — the single best fit. Give a confidence between 0 and 1 reflecting
how clearly the facts match that category's definition (low confidence if facts are sparse or
ambiguous between two categories). Give a one-to-three sentence reasoning grounded in the
specific facts provided (e.g. "An FIR has already been registered and the petitioner seeks to
quash it, which is the hallmark of certiorari." ) — never invent facts not given to you."""


class _ClassificationOut(BaseModel):
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


_CATEGORY_MAP = {c.value: c for c in CaseType}


def suggest_writ_category(facts: CaseFacts) -> CategorySuggestion:
    prompt = f"Case facts:\n{facts.model_dump_json(indent=2)}"
    result = generate_structured(prompt, _ClassificationOut, system_instruction=_SYSTEM_INSTRUCTION)
    category = _CATEGORY_MAP.get(result.category, CaseType.OTHER)
    return CategorySuggestion(
        category=category,
        confidence=result.confidence,
        reasoning=result.reasoning,
        tier=Tier.AI_ANALYSIS,
    )
