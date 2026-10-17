from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app import repository
from app.models.draft import DraftOutput, DraftRequest
from app.services import templates
from app.services.drafting import generate_draft
from app.services.export import draft_to_docx
from app.services.research import run_research

router = APIRouter(prefix="/api/cases", tags=["draft"])


@router.post("/{case_id}/draft", response_model=DraftOutput)
async def create_draft(case_id: str, body: DraftRequest) -> DraftOutput:
    row = repository.get_case(case_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")

    try:
        templates.get_court_profile(body.court_id)
        proceeding = templates.get_proceeding_template(body.proceeding_type)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if body.court_id not in proceeding.get("applicable_courts", []):
        raise HTTPException(
            status_code=400,
            detail=f"Proceeding '{body.proceeding_type}' is not configured for court '{body.court_id}'.",
        )

    facts = repository.load_case_facts(row)
    issues = repository.load_validation_issues(row)
    research = repository.load_research_report(row)
    if research is None:
        research = await run_research(facts, issues, court_filter=["supremecourt", "highcourts"])
        repository.save_research_report(case_id, research)

    draft = await generate_draft(facts, research, body.court_id, body.proceeding_type)
    repository.save_draft_output(case_id, draft)
    return draft


@router.get("/{case_id}/draft", response_model=DraftOutput)
async def get_draft(case_id: str) -> DraftOutput:
    row = repository.get_case(case_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    draft = repository.load_draft_output(row)
    if draft is None:
        raise HTTPException(status_code=404, detail="No draft generated for this case yet.")
    return draft


@router.get("/{case_id}/draft/export")
async def export_draft(case_id: str) -> Response:
    row = repository.get_case(case_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    draft = repository.load_draft_output(row)
    if draft is None:
        raise HTTPException(status_code=404, detail="No draft generated for this case yet.")

    court = templates.get_court_profile(draft.court_id)
    proceeding = templates.get_proceeding_template(draft.proceeding_type)
    docx_bytes = draft_to_docx(draft, court["name"], proceeding["name"])
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="draft-{case_id}.docx"'},
    )
