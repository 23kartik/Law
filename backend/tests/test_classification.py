from app.models.case import CaseFacts, Party
from app.models.enums import CaseType
from app.services.validation import check_required_fields


def test_certiorari_required_fields_flagged_when_missing():
    facts = CaseFacts(case_type=CaseType.CERTIORARI, facts_narrative="An FIR was lodged against me.")
    issues = check_required_fields(facts)
    fields = {i.field for i in issues}
    assert "case_reference_number" in fields
    assert "parties.petitioner" in fields


def test_certiorari_satisfied_when_fully_populated():
    facts = CaseFacts(
        case_type=CaseType.CERTIORARI,
        parties=[Party(role="petitioner", name="Amit Kumar Mishra")],
        case_reference_number="0341 of 2026",
        police_station="Kotwali",
        location="Unnao",
        facts_narrative="FIR was lodged against the petitioner without basis.",
    )
    assert check_required_fields(facts) == []


def test_mandamus_requires_authority_and_duty():
    facts = CaseFacts(case_type=CaseType.MANDAMUS, facts_narrative="The authority has not acted.")
    issues = check_required_fields(facts)
    fields = {i.field for i in issues}
    assert "authority_name" in fields
    assert "legal_issues" in fields


def test_quo_warranto_requires_authority_name():
    facts = CaseFacts(
        case_type=CaseType.QUO_WARRANTO,
        parties=[Party(role="petitioner", name="A Citizen")],
        facts_narrative="Respondent holds office without qualification.",
    )
    issues = check_required_fields(facts)
    fields = {i.field for i in issues}
    assert "authority_name" in fields
