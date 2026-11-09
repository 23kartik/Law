from pydantic import BaseModel


class CaseDocument(BaseModel):
    """Metadata for a supporting document (annexure) attached to a case.

    Content bytes are never included here — they're served separately via the
    download endpoint so listing documents stays cheap.
    """

    id: str
    filename: str
    content_type: str
    size: int
    annexure_label: str | None = None
    uploaded_at: str
