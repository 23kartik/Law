from app.services import templates


def test_delhi_hc_habeas_corpus_combo_is_registered():
    combos = templates.list_court_proceeding_combos()
    assert any(
        c["court_id"] == "delhi_hc" and c["proceeding_type"] == "habeas_corpus" for c in combos
    )


def test_proceeding_sections_cover_sample_draft_structure():
    proceeding = templates.get_proceeding_template("habeas_corpus")
    keys = [s["key"] for s in proceeding["sections"]]
    assert keys == [
        "parties",
        "synopsis",
        "list_of_dates",
        "jurisdiction",
        "facts",
        "grounds",
        "reservation",
        "annexures",
        "prayer",
        "verification",
        "affidavit",
    ]


def test_unknown_court_raises():
    import pytest

    with pytest.raises(KeyError):
        templates.get_court_profile("bombay_hc")
