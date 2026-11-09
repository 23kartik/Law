from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app import repository
from app.models.enums import Tier
from app.models.research import AttachedPrecedent, ManualPrecedentInput, Precedent

router = APIRouter(prefix="/api/cases", tags=["precedents"])


@router.post("/{case_id}/precedents", response_model=AttachedPrecedent)
async def attach_precedent(case_id: str, body: Precedent) -> AttachedPrecedent:
    """Attach a precedent the user picked from the research results onto the case, so it
    (and only the other attached precedents, if any) is what drafting cites — rather than
    every precedent research happened to turn up."""
    row = repository.get_case(case_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    return repository.add_attached_precedent(case_id, body, attach_source="research")


@router.post("/{case_id}/precedents/manual", response_model=AttachedPrecedent)
async def attach_manual_precedent(case_id: str, body: ManualPrecedentInput) -> AttachedPrecedent:
    """Attach a precedent the user knows about but that research didn't surface. Always
    tagged EXTRACTED — it's user-supplied and hasn't been independently verified by the
    platform against a real court source, unlike precedents that come from research."""
    row = repository.get_case(case_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")

    precedent = Precedent(
        title=body.title,
        citation=body.citation,
        court=body.court,
        date=body.date,
        source_url=body.source_url or "",
        snippet=body.note or "",
        relevance_score=0.0,
        applicability_note=body.note,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        source_adapter="manual_entry",
        tier=Tier.EXTRACTED,
    )
    return repository.add_attached_precedent(case_id, precedent, attach_source="manual")


@router.get("/{case_id}/precedents", response_model=list[AttachedPrecedent])
async def list_attached_precedents(case_id: str) -> list[AttachedPrecedent]:
    row = repository.get_case(case_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    return repository.list_attached_precedents(case_id)


@router.delete("/{case_id}/precedents/{precedent_id}", status_code=204)
async def detach_precedent(case_id: str, precedent_id: str) -> None:
    deleted = repository.delete_attached_precedent(case_id, precedent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Attached precedent not found.")
