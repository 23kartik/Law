import uuid
from datetime import datetime, timezone

from sqlmodel import select

from app.db import CaseAttachedPrecedentDB, CaseDB, CaseDocumentDB, get_session
from app.models.case import CaseFacts, CategorySuggestion, ValidationIssue
from app.models.documents import CaseDocument
from app.models.draft import DraftOutput
from app.models.research import AttachedPrecedent, Precedent, ResearchReport


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


def save_category_suggestion(case_id: str, suggestion: CategorySuggestion) -> None:
    with get_session() as session:
        row = session.exec(select(CaseDB).where(CaseDB.id == case_id)).first()
        if row is None:
            raise KeyError(case_id)
        row.category_suggestion_json = suggestion.model_dump_json()
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


def load_category_suggestion(row: CaseDB) -> CategorySuggestion | None:
    if not row.category_suggestion_json:
        return None
    return CategorySuggestion.model_validate_json(row.category_suggestion_json)


def _document_to_model(row: CaseDocumentDB) -> CaseDocument:
    return CaseDocument(
        id=row.id,
        filename=row.filename,
        content_type=row.content_type,
        size=row.size,
        annexure_label=row.annexure_label,
        uploaded_at=row.uploaded_at,
    )


def add_document(
    case_id: str,
    filename: str,
    content_type: str,
    content: bytes,
    annexure_label: str | None,
) -> CaseDocument:
    row = CaseDocumentDB(
        case_id=case_id,
        filename=filename,
        content_type=content_type,
        size=len(content),
        annexure_label=annexure_label,
        content=content,
        uploaded_at=datetime.now(timezone.utc).isoformat(),
    )
    with get_session() as session:
        session.add(row)
        session.commit()
        session.refresh(row)
        return _document_to_model(row)


def list_documents(case_id: str) -> list[CaseDocument]:
    with get_session() as session:
        rows = session.exec(
            select(CaseDocumentDB).where(CaseDocumentDB.case_id == case_id).order_by(CaseDocumentDB.uploaded_at)
        ).all()
        return [_document_to_model(r) for r in rows]


def get_document(case_id: str, document_id: str) -> CaseDocumentDB | None:
    with get_session() as session:
        return session.exec(
            select(CaseDocumentDB).where(
                CaseDocumentDB.case_id == case_id, CaseDocumentDB.id == document_id
            )
        ).first()


def delete_document(case_id: str, document_id: str) -> bool:
    with get_session() as session:
        row = session.exec(
            select(CaseDocumentDB).where(
                CaseDocumentDB.case_id == case_id, CaseDocumentDB.id == document_id
            )
        ).first()
        if row is None:
            return False
        session.delete(row)
        session.commit()
        return True


def _attached_precedent_to_model(row: CaseAttachedPrecedentDB) -> AttachedPrecedent:
    base = Precedent.model_validate_json(row.precedent_json)
    return AttachedPrecedent(
        **base.model_dump(),
        id=row.id,
        attach_source=row.attach_source,
        attached_at=row.attached_at,
    )


def add_attached_precedent(case_id: str, precedent: Precedent, attach_source: str) -> AttachedPrecedent:
    row = CaseAttachedPrecedentDB(
        case_id=case_id,
        precedent_json=precedent.model_dump_json(),
        attach_source=attach_source,
        attached_at=datetime.now(timezone.utc).isoformat(),
    )
    with get_session() as session:
        session.add(row)
        session.commit()
        session.refresh(row)
        return _attached_precedent_to_model(row)


def list_attached_precedents(case_id: str) -> list[AttachedPrecedent]:
    with get_session() as session:
        rows = session.exec(
            select(CaseAttachedPrecedentDB)
            .where(CaseAttachedPrecedentDB.case_id == case_id)
            .order_by(CaseAttachedPrecedentDB.attached_at)
        ).all()
        return [_attached_precedent_to_model(r) for r in rows]


def delete_attached_precedent(case_id: str, precedent_id: str) -> bool:
    with get_session() as session:
        row = session.exec(
            select(CaseAttachedPrecedentDB).where(
                CaseAttachedPrecedentDB.case_id == case_id, CaseAttachedPrecedentDB.id == precedent_id
            )
        ).first()
        if row is None:
            return False
        session.delete(row)
        session.commit()
        return True
