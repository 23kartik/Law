from fastapi import APIRouter, Form, HTTPException, UploadFile

from app import repository
from app.models.case import CaseFacts, CaseRecord
from app.services import extraction, validation

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.post("", response_model=CaseRecord)
async def create_case(text: str | None = Form(None), file: UploadFile | None = None) -> CaseRecord:
    if file is not None:
        pdf_bytes = await file.read()
        raw_text = extraction.extract_text_from_pdf(pdf_bytes)
    elif text:
        raw_text = text
    else:
        raise HTTPException(status_code=400, detail="Provide either 'text' or a 'file' upload.")

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="No extractable text found in the input.")

    facts = extraction.extract_case_facts(raw_text)
    issues = validation.validate_case_facts(facts)
    case_id = repository.create_case(raw_text, facts, issues)
    row = repository.get_case(case_id)
    assert row is not None
    return CaseRecord(
        id=row.id,
        raw_text=row.raw_text,
        case_facts=facts,
        validation_issues=issues,
        created_at=row.created_at,
    )


@router.get("/{case_id}", response_model=CaseRecord)
async def get_case(case_id: str) -> CaseRecord:
    row = repository.get_case(case_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    return CaseRecord(
        id=row.id,
        raw_text=row.raw_text,
        case_facts=repository.load_case_facts(row),
        validation_issues=repository.load_validation_issues(row),
        created_at=row.created_at,
    )


@router.patch("/{case_id}", response_model=CaseRecord)
async def update_case(case_id: str, facts: CaseFacts) -> CaseRecord:
    row = repository.get_case(case_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    issues = validation.validate_case_facts(facts)
    repository.update_case_facts(case_id, facts, issues)
    return CaseRecord(
        id=case_id,
        raw_text=row.raw_text,
        case_facts=facts,
        validation_issues=issues,
        created_at=row.created_at,
    )
