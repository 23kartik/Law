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


def test_all_five_writ_categories_are_registered_proceedings():
    proceedings = {
        templates.get_proceeding_template(pid)["case_type"]
        for pid in ["habeas_corpus", "mandamus", "prohibition", "certiorari", "quo_warranto"]
    }
    assert proceedings == {
        "habeas_corpus",
        "mandamus",
        "prohibition",
        "certiorari",
        "quo_warranto",
    }


def test_certiorari_is_registered_for_allahabad_hc():
    combos = templates.list_court_proceeding_combos()
    assert any(
        c["court_id"] == "allahabad_hc" and c["proceeding_type"] == "certiorari" for c in combos
    )
