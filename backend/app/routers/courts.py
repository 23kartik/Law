from fastapi import APIRouter

from app.services import templates

router = APIRouter(prefix="/api/courts", tags=["courts"])


@router.get("")
async def list_courts() -> list[dict]:
    return templates.list_court_proceeding_combos()
