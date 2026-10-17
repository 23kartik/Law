from abc import ABC, abstractmethod

from app.models.research import Precedent


class LegalSourceAdapter(ABC):
    """Common interface every court-data source implements.

    Adapters are responsible only for fetching and normalizing real court
    documents into Precedent objects tagged VERIFIED_COURT with a resolvable
    source_url — they must never fabricate or embellish results.
    """

    name: str

    @abstractmethod
    def is_enabled(self) -> bool:
        ...

    @abstractmethod
    async def search(
        self,
        query: str,
        *,
        court_filter: list[str] | None = None,
        limit: int = 5,
    ) -> list[Precedent]:
        ...
