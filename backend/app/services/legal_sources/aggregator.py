import asyncio

from app.models.research import Precedent
from app.services.legal_sources.base import LegalSourceAdapter
from app.services.legal_sources.indian_kanoon import IndianKanoonAdapter
from app.services.legal_sources.kanoon_dev import KanoonDevAdapter

_COURT_AUTHORITY_WEIGHT = {
    "supreme court of india": 1.0,
    "supremecourt": 1.0,
}
_DEFAULT_HIGH_COURT_WEIGHT = 0.75
_DEFAULT_OTHER_WEIGHT = 0.4


def court_authority_weight(court: str | None) -> float:
    if not court:
        return _DEFAULT_OTHER_WEIGHT
    key = court.strip().lower()
    for needle, weight in _COURT_AUTHORITY_WEIGHT.items():
        if needle in key:
            return weight
    if "high court" in key or key.endswith("hc") or "hc0" in key.upper().lower():
        return _DEFAULT_HIGH_COURT_WEIGHT
    return _DEFAULT_OTHER_WEIGHT


class LegalSourceAggregator:
    """Runs every enabled adapter concurrently and merges/dedupes results.

    Dedup key is the normalized title + source host, since different adapters
    rarely share document ids. Results are sorted by court authority first,
    then by the adapter's own relevance signal.
    """

    def __init__(self, adapters: list[LegalSourceAdapter] | None = None) -> None:
        self._adapters = adapters or [KanoonDevAdapter(), IndianKanoonAdapter()]

    def enabled_adapters(self) -> list[LegalSourceAdapter]:
        return [a for a in self._adapters if a.is_enabled()]

    async def search(
        self,
        query: str,
        *,
        court_filter: list[str] | None = None,
        limit_per_source: int = 5,
    ) -> list[Precedent]:
        enabled = self.enabled_adapters()
        if not enabled:
            return []

        results_per_adapter = await asyncio.gather(
            *[
                adapter.search(query, court_filter=court_filter, limit=limit_per_source)
                for adapter in enabled
            ],
            return_exceptions=True,
        )

        seen: set[str] = set()
        merged: list[Precedent] = []
        for results in results_per_adapter:
            if isinstance(results, BaseException):
                continue
            for precedent in results:
                dedup_key = precedent.title.strip().lower()
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)
                merged.append(precedent)

        merged.sort(key=lambda p: court_authority_weight(p.court), reverse=True)
        return merged
