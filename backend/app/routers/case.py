from fastapi import APIRouter, Form, HTTPException, UploadFile

from app import repository
from app.models.case import CaseFacts, CaseRecord, CategorySuggestion
from app.services import classification, extraction, validation

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

    # Suggest the writ petition category from the facts just extracted. The suggestion
    # is advisory — it also pre-fills case_type so drafting has a sensible default, but
    # the user reviews/changes it via the normal PATCH endpoint below before drafting.
    suggestion = classification.suggest_writ_category(facts)
    facts.case_type = suggestion.category

    issues = validation.validate_case_facts(facts)
    case_id = repository.create_case(raw_text, facts, issues)
    repository.save_category_suggestion(case_id, suggestion)
    row = repository.get_case(case_id)
    assert row is not None
    return CaseRecord(
        id=row.id,
        raw_text=row.raw_text,
        case_facts=facts,
        validation_issues=issues,
        category_suggestion=suggestion,
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
        category_suggestion=repository.load_category_suggestion(row),
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
        category_suggestion=repository.load_category_suggestion(row),
        created_at=row.created_at,
    )


@router.post("/{case_id}/suggest-category", response_model=CategorySuggestion)
async def resuggest_category(case_id: str) -> CategorySuggestion:
    """Re-runs category suggestion against the case's current (possibly edited) facts —
    used when the user has updated facts and wants a fresh AI suggestion before deciding
    whether to accept it or pick a different category themselves."""
    row = repository.get_case(case_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    facts = repository.load_case_facts(row)
    suggestion = classification.suggest_writ_category(facts)
    repository.save_category_suggestion(case_id, suggestion)
    return suggestion
