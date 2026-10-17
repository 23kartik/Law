from io import BytesIO

from pypdf import PdfReader

from app.models.case import CaseFacts
from app.services.llm import generate_structured

_SYSTEM_INSTRUCTION = """You are a legal intake assistant for an Indian litigation platform.
Extract ONLY facts explicitly stated or directly implied by the input. Never invent names,
dates, addresses, or other details that are not present in the source text. If a detail is
not given, simply omit it (leave the field null or the list empty) rather than guessing —
downstream validation will flag what's missing. Dates must be in YYYY-MM-DD format if a full
date is given; if only a relative/partial time reference is given (e.g. "last 24 hours"),
leave the date field null and put the raw reference in the description instead.
Classify case_type as "habeas_corpus" if the matter concerns someone detained/arrested whose
production or release is sought; otherwise "other"."""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def extract_case_facts(raw_text: str) -> CaseFacts:
    prompt = f"Extract structured case facts from the following input:\n\n{raw_text}"
    facts = generate_structured(prompt, CaseFacts, system_instruction=_SYSTEM_INSTRUCTION)
    facts.missing_fields = []  # computed deterministically by validation.py, not the LLM
    return facts
