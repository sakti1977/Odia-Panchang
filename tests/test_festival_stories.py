"""
Evals: festival story coverage, Odia script purity, API-shaped payload.
"""

import pytest

from src.festival_stories import (
    FESTIVAL_STORIES,
    attach_story,
    coverage_report,
    get_festival_story,
    validate_all_stories,
    validate_odia_text,
)
from src.festivals import match_festivals, TITHI_RULES, SANKRANTI_RULES
from src.tweet_generator import _one_line_story, generate_tweet_bundle


def test_e_inv_009_full_story_coverage():
    report = coverage_report()
    assert report["missing"] == [], f"Missing stories for: {report['missing']}"
    assert report["curated"] == report["total_rules"]
    assert report["total_rules"] >= 70


def test_odia_script_non_negotiable_all_stories():
    """No Latin / Devanagari letters in Odia fields; all curated stories valid."""
    errors = validate_all_stories()
    assert errors == [], "Odia validation failed:\n" + "\n".join(errors)


def test_odia_rejects_english_and_devanagari_letters():
    with pytest.raises(ValueError):
        validate_odia_text("Hello world")
    with pytest.raises(ValueError):
        validate_odia_text("राम नवमी")  # Devanagari
    # Valid Odia
    validate_odia_text("ରଥଯାତ୍ରା ପୁରୀରେ ପାଳିତ ହୁଏ।")


def test_festival_name_or_is_odia():
    """Festival labels in rules must be real Odia, not Latin."""
    for rule in TITHI_RULES:
        name_or = rule[5]
        validate_odia_text(name_or, field=rule[4])
    for rule in SANKRANTI_RULES:
        name_or = rule[3]
        validate_odia_text(name_or, field=rule[2])


def test_get_festival_story_always_has_bilingual():
    for name in list(FESTIVAL_STORIES)[:5] + ["__no_such_festival__"]:
        s = get_festival_story(name)
        assert s["story"]["en"].strip()
        assert s["why_today"]["en"].strip()
        validate_odia_text(s["story"]["or"])
        validate_odia_text(s["why_today"]["or"])
        assert s["kind"] in {
            "puranic_tradition",
            "historical_cultural",
            "ritual_observance",
        }


def test_rath_yatra_story_mentions_gundicha_or_chariot():
    s = get_festival_story("Rath Yatra")
    blob = (s["story"]["en"] + " " + s["why_today"]["en"]).lower()
    assert s["complete"] is True
    assert "gundicha" in blob or "chariot" in blob


def test_match_festivals_attaches_story():
    day = {
        "paksha_en": "Shukla",
        "tithi_num": 2,
        "chandra_masa_en": "Ashadha",
        "soura_masa_en": "Mithuna",
    }
    fests = match_festivals(day)
    assert fests
    rath = next(f for f in fests if "Rath" in f["name_en"])
    assert rath["story"]["en"]
    assert rath["why_today"]["en"]
    assert rath["story_complete"] is True
    assert rath["story_sources"]


def test_attach_story_on_api_shaped_festival():
    f = attach_story(
        {
            "name": {"en": "Boita Bandana", "or": "ବୋଇତ"},
            "name_en": "Kartik Purnima / Boita Bandana",
            "tradition": "common",
            "description": "test",
        }
    )
    # lookup uses name_en
    assert f["story_complete"] is True
    assert "kalinga" in f["story"]["en"].lower() or "sadhab" in f["story"]["en"].lower()


def test_tweet_thread_includes_festival_story_without_enrichment():
    panchang = {
        "date": "2026-07-16",
        "vara": {"en": "Thursday", "or": "ଗୁରୁବାର"},
        "tithi": {"en": "Dwitiya", "or": "ଦ୍ୱିତୀୟା", "num": 2},
        "nakshatra": {"en": "X", "or": "ଯ"},
        "chandra_masa": {"en": "Ashadha", "or": "ଆଷାଢ଼"},
        "paksha": {"en": "Shukla", "or": "ଶୁକ୍ଳ"},
        "yoga": {"en": "Y", "or": "ଯୋ"},
        "sunrise": "05:15",
        "sunset": "18:30",
        "festivals": [
            {
                "name": {"en": "Rath Yatra", "or": "ରଥ ଯାତ୍ରା"},
                "tradition": "common",
                "description": "Chariot festival",
            }
        ],
    }
    bundle = generate_tweet_bundle(panchang, enrichment=None)
    assert bundle["main_tweet"]
    assert len(bundle["main_tweet"]) <= 280
    # Thread should carry story even without AI enrichment
    assert bundle["thread_reply"]
    assert len(bundle["thread_reply"]) <= 280
    low = bundle["thread_reply"].lower()
    assert "ରଥ" in bundle["thread_reply"] or "rath" in low or "gundicha" in low


def test_one_line_story_truncates():
    long_f = {
        "story": {"en": "word " * 80, "or": ""},
        "why_today": {"en": "", "or": ""},
    }
    line = _one_line_story(long_f, prefer_or=False, max_len=50)
    assert len(line) <= 50
    assert line.endswith("…")
