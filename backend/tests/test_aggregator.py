import pytest

from app.models.research import Precedent
from app.services.legal_sources.aggregator import LegalSourceAggregator, court_authority_weight
from app.services.legal_sources.base import LegalSourceAdapter


def _precedent(title: str, court: str | None, adapter: str) -> Precedent:
    return Precedent(
        title=title,
        court=court,
        source_url=f"https://example.com/{title}",
        snippet="snippet",
        retrieved_at="2026-01-01T00:00:00Z",
        source_adapter=adapter,
    )


class _FakeAdapter(LegalSourceAdapter):
    name = "fake"

    def __init__(self, results: list[Precedent], enabled: bool = True):
        self._results = results
        self._enabled = enabled

    def is_enabled(self) -> bool:
        return self._enabled

    async def search(self, query, *, court_filter=None, limit=5):
        return self._results


def test_court_authority_weight_ranks_supreme_court_highest():
    assert court_authority_weight("Supreme Court of India") == 1.0
    assert court_authority_weight("Delhi High Court") == 0.75
    assert court_authority_weight(None) == 0.4
    assert court_authority_weight("District Court") == 0.4


@pytest.mark.asyncio
async def test_aggregator_dedupes_by_title_across_adapters():
    shared = _precedent("D.K. Basu v. State of West Bengal", "Supreme Court of India", "a")
    duplicate = _precedent("D.K. Basu v. State of West Bengal", "Supreme Court of India", "b")
    unique = _precedent("Pankaj Bansal v. Union of India", "Supreme Court of India", "b")

    agg = LegalSourceAggregator(adapters=[_FakeAdapter([shared]), _FakeAdapter([duplicate, unique])])
    results = await agg.search("query")

    assert len(results) == 2
    assert {r.title for r in results} == {
        "D.K. Basu v. State of West Bengal",
        "Pankaj Bansal v. Union of India",
    }


@pytest.mark.asyncio
async def test_aggregator_skips_disabled_adapters():
    enabled = _FakeAdapter([_precedent("Included", "Supreme Court of India", "a")], enabled=True)
    disabled = _FakeAdapter([_precedent("Excluded", "Supreme Court of India", "b")], enabled=False)

    agg = LegalSourceAggregator(adapters=[enabled, disabled])
    results = await agg.search("query")

    assert [r.title for r in results] == ["Included"]


@pytest.mark.asyncio
async def test_aggregator_sorts_by_court_authority():
    low = _precedent("District order", "District Court", "a")
    high = _precedent("SC judgment", "Supreme Court of India", "a")

    agg = LegalSourceAggregator(adapters=[_FakeAdapter([low, high])])
    results = await agg.search("query")

    assert [r.title for r in results] == ["SC judgment", "District order"]
