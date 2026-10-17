from datetime import datetime, timezone

import httpx

from app.config import get_settings
from app.models.research import Precedent
from app.services.legal_sources.base import LegalSourceAdapter


class KanoonDevAdapter(LegalSourceAdapter):
    """Zero-setup free pilot API at kanoon.dev — no key required.

    Coverage is a small historical sample (pilot stage), not a comprehensive
    case-law database, so this adapter deliberately does not hard-filter by
    court: doing so against such sparse coverage would mostly return nothing.
    It searches unfiltered and lets the caller weigh results by court authority.
    """

    name = "kanoon_dev"

    def __init__(self) -> None:
        self._settings = get_settings()
        self._base_url = self._settings.kanoon_dev_base_url

    def is_enabled(self) -> bool:
        return True

    async def search(
        self,
        query: str,
        *,
        court_filter: list[str] | None = None,
        limit: int = 5,
    ) -> list[Precedent]:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=15) as client:
            try:
                resp = await client.get("/v1/search", params={"q": query[:2000], "limit": min(limit, 50)})
                resp.raise_for_status()
            except httpx.HTTPError:
                return []
            data = resp.json()

            precedents: list[Precedent] = []
            for doc in data.get("results", []):
                precedents.append(
                    Precedent(
                        title=doc.get("title", "Untitled document"),
                        citation=None,
                        court=doc.get("court_id"),
                        date=doc.get("document_date"),
                        source_url=doc.get("source_url", doc.get("document_url", "")),
                        snippet=doc.get("snippet", ""),
                        retrieved_at=datetime.now(timezone.utc).isoformat(),
                        source_adapter=self.name,
                    )
                )
            return precedents
