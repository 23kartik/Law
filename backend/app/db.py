from sqlmodel import Field, Session, SQLModel, create_engine

from app.config import get_settings


class CaseDB(SQLModel, table=True):
    __tablename__ = "cases"

    id: str = Field(primary_key=True)
    raw_text: str
    case_facts_json: str
    validation_issues_json: str = "[]"
    research_report_json: str | None = None
    draft_output_json: str | None = None
    created_at: str


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
        SQLModel.metadata.create_all(_engine)
    return _engine


def get_session() -> Session:
    return Session(get_engine())
