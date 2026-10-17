import html
import re
from datetime import datetime, timezone

import httpx

from app.config import get_settings
from app.models.research import Precedent
from app.services.legal_sources.base import LegalSourceAdapter

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_tags(text: str) -> str:
    return html.unescape(_TAG_RE.sub(" ", text)).strip()


class IndianKanoonAdapter(LegalSourceAdapter):
    """Official Indian Kanoon API — 30M+ judgments, Supreme Court + 24 High Courts.

    Only active when INDIAN_KANOON_API_KEY is set (free tier: 200 credits/mo).
    Matches the official IKAPI client: POST requests, Authorization: Token header.
    """

    name = "indian_kanoon"
    _base_url = "https://api.indiankanoon.org"

    def __init__(self) -> None:
        self._settings = get_settings()

    def is_enabled(self) -> bool:
        return bool(self._settings.indian_kanoon_api_key)

    async def search(
        self,
        query: str,
        *,
        court_filter: list[str] | None = None,
        limit: int = 5,
    ) -> list[Precedent]:
        if not self.is_enabled():
            return []

        form_input = query
        if court_filter:
            doctypes = ",".join(court_filter)
            form_input = f"{query} doctypes: {doctypes}"

        headers = {"Authorization": f"Token {self._settings.indian_kanoon_api_key}"}
        async with httpx.AsyncClient(base_url=self._base_url, timeout=20) as client:
            try:
                resp = await client.post(
                    "/search/",
                    params={"formInput": form_input, "pagenum": 0},
                    headers=headers,
                )
                resp.raise_for_status()
            except httpx.HTTPError:
                return []
            data = resp.json()

            precedents: list[Precedent] = []
            for doc in data.get("docs", [])[:limit]:
                tid = doc.get("tid")
                if tid is None:
                    continue
                precedents.append(
                    Precedent(
                        title=_strip_tags(doc.get("title", "Untitled document")),
                        citation=None,
                        court=doc.get("docsource"),
                        date=doc.get("publishdate"),
                        source_url=f"https://indiankanoon.org/doc/{tid}/",
                        snippet=_strip_tags(doc.get("headline", ""))[:600],
                        retrieved_at=datetime.now(timezone.utc).isoformat(),
                        source_adapter=self.name,
                    )
                )
            return precedents
