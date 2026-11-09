from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app import repository
from app.models.documents import CaseDocument

router = APIRouter(prefix="/api/cases", tags=["documents"])


@router.post("/{case_id}/documents", response_model=CaseDocument)
async def attach_document(
    case_id: str, file: UploadFile, annexure_label: str | None = Form(None)
) -> CaseDocument:
    """Admin action: attach a supporting document (e.g. an annexure) to the case."""
    row = repository.get_case(case_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    return repository.add_document(
        case_id=case_id,
        filename=file.filename or "document",
        content_type=file.content_type or "application/octet-stream",
        content=content,
        annexure_label=annexure_label,
    )


@router.get("/{case_id}/documents", response_model=list[CaseDocument])
async def list_documents(case_id: str) -> list[CaseDocument]:
    row = repository.get_case(case_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    return repository.list_documents(case_id)


@router.get("/{case_id}/documents/{document_id}")
async def download_document(case_id: str, document_id: str) -> Response:
    doc_row = repository.get_document(case_id, document_id)
    if doc_row is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return Response(
        content=doc_row.content,
        media_type=doc_row.content_type,
        headers={"Content-Disposition": f'inline; filename="{doc_row.filename}"'},
    )


@router.delete("/{case_id}/documents/{document_id}", status_code=204)
async def detach_document(case_id: str, document_id: str) -> Response:
    """Admin action: detach (remove) a previously attached supporting document."""
    deleted = repository.delete_document(case_id, document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found.")
    return Response(status_code=204)
