from functools import lru_cache
from typing import TypeVar

from google import genai
from google.genai import errors, types
from pydantic import BaseModel
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings

T = TypeVar("T", bound=BaseModel)

# The free tier of Gemini's newer models intermittently returns 503 "high demand"
# errors even though the SDK's own internal retry already ran out of attempts —
# retrying once more at the application level makes the demo reliable.
_retry_on_overload = retry(
    retry=retry_if_exception_type(errors.ServerError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=20),
    reraise=True,
)


@lru_cache
def _client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Get a free key at https://aistudio.google.com/apikey "
            "and add it to backend/.env"
        )
    return genai.Client(api_key=settings.gemini_api_key)


@_retry_on_overload
def generate_structured(prompt: str, response_schema: type[T], *, system_instruction: str | None = None) -> T:
    """Calls Gemini and parses the response into the given Pydantic model.

    Every call site in this codebase that uses this function is producing
    AI_ANALYSIS-tier content — callers must tag their output accordingly.
    """
    settings = get_settings()
    response = _client().models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.1,
        ),
    )
    return response_schema.model_validate_json(response.text)


@_retry_on_overload
def generate_text(prompt: str, *, system_instruction: str | None = None, temperature: float = 0.2) -> str:
    settings = get_settings()
    response = _client().models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
        ),
    )
    return response.text or ""
