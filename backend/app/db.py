import uuid

from sqlmodel import Field, Session, SQLModel, create_engine

from app.config import get_settings


class CaseDB(SQLModel, table=True):
    __tablename__ = "cases"

    id: str = Field(primary_key=True)
    raw_text: str
    case_facts_json: str
    validation_issues_json: str = "[]"
    category_suggestion_json: str | None = None
    research_report_json: str | None = None
    draft_output_json: str | None = None
    created_at: str


class CaseDocumentDB(SQLModel, table=True):
    __tablename__ = "case_documents"

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12], primary_key=True)
    case_id: str = Field(index=True)
    filename: str
    content_type: str
    size: int
    annexure_label: str | None = None
    content: bytes
    uploaded_at: str


class CaseAttachedPrecedentDB(SQLModel, table=True):
    __tablename__ = "case_attached_precedents"

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12], primary_key=True)
    case_id: str = Field(index=True)
    precedent_json: str
    attach_source: str
    attached_at: str


_engine = None


def _migrate_existing_tables(engine) -> None:
    """SQLModel.metadata.create_all only creates missing tables — it never alters an
    existing one, so a pre-existing cases table from before this column was added needs
    a manual ALTER TABLE. Safe to run every startup: it's a no-op once the column exists."""
    with engine.connect() as conn:
        existing_cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(cases)")}
        if existing_cols and "category_suggestion_json" not in existing_cols:
            conn.exec_driver_sql("ALTER TABLE cases ADD COLUMN category_suggestion_json VARCHAR")
            conn.commit()


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
        SQLModel.metadata.create_all(_engine)
        _migrate_existing_tables(_engine)
    return _engine


def get_session() -> Session:
    return Session(get_engine())
