from functools import lru_cache
from pathlib import Path

import yaml

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


@lru_cache
def _load_all(subdir: str) -> dict[str, dict]:
    registry: dict[str, dict] = {}
    for path in (_TEMPLATES_DIR / subdir).glob("*.yaml"):
        data = yaml.safe_load(path.read_text())
        registry[data["id"]] = data
    return registry


def get_court_profile(court_id: str) -> dict:
    courts = _load_all("courts")
    if court_id not in courts:
        raise KeyError(f"Unknown court_id: {court_id}")
    return courts[court_id]


def get_proceeding_template(proceeding_id: str) -> dict:
    proceedings = _load_all("proceedings")
    if proceeding_id not in proceedings:
        raise KeyError(f"Unknown proceeding_type: {proceeding_id}")
    return proceedings[proceeding_id]


def list_court_proceeding_combos() -> list[dict]:
    courts = _load_all("courts")
    proceedings = _load_all("proceedings")
    combos = []
    for proceeding in proceedings.values():
        for court_id in proceeding.get("applicable_courts", []):
            court = courts.get(court_id)
            if court:
                combos.append(
                    {
                        "court_id": court_id,
                        "court_name": court["name"],
                        "proceeding_type": proceeding["id"],
                        "proceeding_name": proceeding["name"],
                    }
                )
    return combos
