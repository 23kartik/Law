from fastapi import APIRouter, HTTPException

from app import repository
from app.models.research import ResearchReport
from app.services.research import run_research

router = APIRouter(prefix="/api/cases", tags=["research"])


@router.post("/{case_id}/research", response_model=ResearchReport)
async def research_case(case_id: str) -> ResearchReport:
    row = repository.get_case(case_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")

    facts = repository.load_case_facts(row)
    issues = repository.load_validation_issues(row)
    report = await run_research(facts, issues, court_filter=["supremecourt", "highcourts"])
    repository.save_research_report(case_id, report)
    return report


@router.get("/{case_id}/research", response_model=ResearchReport)
async def get_research(case_id: str) -> ResearchReport:
    row = repository.get_case(case_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    report = repository.load_research_report(row)
    if report is None:
        raise HTTPException(status_code=404, detail="Research has not been run for this case yet.")
    return report
