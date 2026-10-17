import uuid
from datetime import datetime, timezone

from sqlmodel import select

from app.db import CaseDB, get_session
from app.models.case import CaseFacts, ValidationIssue
from app.models.draft import DraftOutput
from app.models.research import ResearchReport


def new_case_id() -> str:
    return uuid.uuid4().hex[:12]


def create_case(raw_text: str, facts: CaseFacts, issues: list[ValidationIssue]) -> str:
    case_id = new_case_id()
    row = CaseDB(
        id=case_id,
        raw_text=raw_text,
        case_facts_json=facts.model_dump_json(),
        validation_issues_json=f"[{','.join(i.model_dump_json() for i in issues)}]",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    with get_session() as session:
        session.add(row)
        session.commit()
    return case_id


def get_case(case_id: str) -> CaseDB | None:
    with get_session() as session:
        return session.exec(select(CaseDB).where(CaseDB.id == case_id)).first()


def update_case_facts(case_id: str, facts: CaseFacts, issues: list[ValidationIssue]) -> None:
    with get_session() as session:
        row = session.exec(select(CaseDB).where(CaseDB.id == case_id)).first()
        if row is None:
            raise KeyError(case_id)
        row.case_facts_json = facts.model_dump_json()
        row.validation_issues_json = f"[{','.join(i.model_dump_json() for i in issues)}]"
        session.add(row)
        session.commit()


def save_research_report(case_id: str, report: ResearchReport) -> None:
    with get_session() as session:
        row = session.exec(select(CaseDB).where(CaseDB.id == case_id)).first()
        if row is None:
            raise KeyError(case_id)
        row.research_report_json = report.model_dump_json()
        session.add(row)
        session.commit()


def save_draft_output(case_id: str, draft: DraftOutput) -> None:
    with get_session() as session:
        row = session.exec(select(CaseDB).where(CaseDB.id == case_id)).first()
        if row is None:
            raise KeyError(case_id)
        row.draft_output_json = draft.model_dump_json()
        session.add(row)
        session.commit()


def load_case_facts(row: CaseDB) -> CaseFacts:
    return CaseFacts.model_validate_json(row.case_facts_json)


def load_validation_issues(row: CaseDB) -> list[ValidationIssue]:
    import json

    return [ValidationIssue.model_validate(i) for i in json.loads(row.validation_issues_json)]


def load_research_report(row: CaseDB) -> ResearchReport | None:
    if not row.research_report_json:
        return None
    return ResearchReport.model_validate_json(row.research_report_json)


def load_draft_output(row: CaseDB) -> DraftOutput | None:
    if not row.draft_output_json:
        return None
    return DraftOutput.model_validate_json(row.draft_output_json)
