from app.models.case import CaseFacts, KeyDate, Party
from app.models.enums import CaseType, Severity
from app.services.validation import check_required_fields


def test_flags_all_missing_fields_for_bare_narrative():
    facts = CaseFacts(case_type=CaseType.HABEAS_CORPUS, facts_narrative="My brother was detained.")
    issues = check_required_fields(facts)
    fields = {i.field for i in issues}
    assert "parties.petitioner" in fields
    assert "parties.detenu" in fields
    assert "arrest_date" in fields
    assert all(i.severity == Severity.MISSING for i in issues)


def test_no_missing_issues_when_fully_populated():
    facts = CaseFacts(
        case_type=CaseType.HABEAS_CORPUS,
        parties=[
            Party(role="petitioner", name="Jane Doe", relationship="sister"),
            Party(role="detenu", name="Amit Doe"),
        ],
        key_dates=[KeyDate(label="date of arrest", date="2026-10-14")],
        location="New Delhi",
        police_station="Karol Bagh",
        facts_narrative="Amit was detained on 2026-10-14.",
    )
    issues = check_required_fields(facts)
    assert issues == []


def test_other_case_type_has_no_required_fields():
    facts = CaseFacts(case_type=CaseType.OTHER, facts_narrative="Some other matter.")
    assert check_required_fields(facts) == []
