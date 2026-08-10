"""
E-SAFE tweet regressions: length, story inclusion, enrichment isolation.
"""

from __future__ import annotations

from src.festival_stories import attach_story
from src.tweet_generator import generate_main_tweet, generate_tweet_bundle, _one_line_story


def _sample_panchang(with_rath: bool = False) -> dict:
    fests = []
    if with_rath:
        fests.append(
            attach_story(
                {
                    "name": {"en": "Rath Yatra", "or": "ରଥ ଯାତ୍ରା"},
                    "name_en": "Rath Yatra",
                    "name_or": "ରଥ ଯାତ୍ରା",
                    "tradition": "common",
                    "description": "Chariot festival",
                }
            )
        )
        # nested name for tweet formatter
        fests[0]["name"] = {"en": "Rath Yatra", "or": "ରଥ ଯାତ୍ରା"}

    return {
        "date": "2026-07-16" if with_rath else "2026-08-10",
        "tithi": {"en": "Dwitiya", "or": "ଦ୍ୱିତୀୟା", "num": 2},
        "nakshatra": {"en": "Ashlesha", "or": "ଆଶ୍ଲେଷା"},
        "chandra_masa": {"en": "Ashadha", "or": "ଆଷାଢ଼"},
        "paksha": {"en": "Shukla", "or": "ଶୁକ୍ଳ"},
        "vara": {"en": "Thursday", "or": "ଗୁରୁବାର"},
        "yoga": {"en": "Siddhi", "or": "ସିଦ୍ଧି"},
        "sunrise": "05:16",
        "sunset": "18:29",
        "festivals": fests,
    }


def test_e_safe_003_main_tweet_max_280():
    for with_rath in (False, True):
        p = _sample_panchang(with_rath=with_rath)
        enrichment = {
            "astronomical": {
                "special_day_type": "normal",
                "muhurtas": {
                    "rahu_kalam": "07:00–08:37",
                    "abhijit_muhurta": "11:25–12:17",
                },
            }
        }
        tweet = generate_main_tweet(p, enrichment)
        assert len(tweet) <= 280, len(tweet)
        assert "ଜୟ ଜଗନ୍ନାଥ" in tweet
        assert "ଆଷାଢ଼" in tweet or "ଦ୍ୱିତୀୟା" in tweet


def test_e_safe_001_enrichment_cannot_change_base_tithi_text():
    p = _sample_panchang(with_rath=False)
    base = generate_main_tweet(p, None)
    poisoned = generate_main_tweet(
        p,
        {
            "astronomical": {
                "special_day_type": "purnima",
                "muhurtas": {"rahu_kalam": "00:00–01:00"},
            },
            "cultural": {
                "jagannath_significance": {
                    "or": "FAKE TITHI SHOULD NOT REPLACE",
                    "en": "fake",
                }
            },
        },
    )
    # Core masa/tithi lines must still come from panchang dict
    assert "ଦ୍ୱିତୀୟା" in poisoned
    assert "ଆଷାଢ଼" in poisoned
    # Main tweet must not inject cultural fake as tithi replacement
    assert "FAKE TITHI" not in poisoned
    assert "ଦ୍ୱିତୀୟା" in base


def test_rath_day_bundle_includes_story_line():
    p = _sample_panchang(with_rath=True)
    bundle = generate_tweet_bundle(p, None)
    assert bundle["main_tweet_length"] <= 280
    assert "Rath Yatra" in bundle["festivals"] or "ରଥ" in bundle["main_tweet"]
    # Thread should carry story blurb (Gundicha / chariot lore)
    thread = bundle["thread_reply"]
    assert thread
    assert "Gundicha" in thread or "ଗୁଣ୍ଡିଚା" in thread or "ରଥ" in thread


def test_one_line_story_prefers_odia():
    f = attach_story({"name_en": "Rath Yatra", "name_or": "ରଥ ଯାତ୍ରା", "tradition": "common", "description": "x"})
    line = _one_line_story(f, prefer_or=True, max_len=80)
    assert line
    # Odia characters present
    assert any("\u0b00" <= c <= "\u0b7f" for c in line)
