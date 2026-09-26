"""'ଜାଣନ୍ତୁ ଓଡ଼ିଶା' daily heritage series in the Facebook/Instagram posts."""

from datetime import date, timedelta
from itertools import groupby

import pytest

from src.odisha_heritage import (
    CATEGORIES,
    HERITAGE,
    SERIES_OR,
    _ROTATION,
    heritage_caption_block,
    heritage_for_date,
    validate_all_heritage,
)
from src.tweet_generator import CAPTION_MAX_LEN, generate_social_caption


def _panchang(day: str, festivals=None):
    return {
        "date": day,
        "vara": {"en": "Monday", "or": "ସୋମବାର"},
        "tithi": {"num": 2, "en": "Dwitiya", "or": "ଦ୍ୱିତୀୟା"},
        "chandra_masa": {"en": "Ashwina", "or": "ଆଶ୍ୱିନ"},
        "paksha": {"en": "Krishna", "or": "କୃଷ୍ଣ"},
        "nakshatra": {"en": "Revati", "or": "ରେବତୀ"},
        "yoga": {"en": "Dhruva", "or": "ଧ୍ରୁବ"},
        "sunrise": "05:36",
        "sunset": "17:37",
        "festivals": festivals or [],
        "meta": {"city": "puri"},
    }


def test_all_heritage_odia_valid_and_sourced():
    assert validate_all_heritage() == []
    assert len(HERITAGE) >= 40
    assert {e["category"] for e in HERITAGE} == set(CATEGORIES)


def test_anniversary_wins_on_its_day():
    e = heritage_for_date("2026-09-28")
    assert e["key"] == "radhanath_ray" and e["is_anniversary"]
    assert "ଆଜି ଜୟନ୍ତୀ" in heritage_caption_block("2026-09-28")
    assert "ଆଜି ଉତ୍କଳ ଦିବସ" in heritage_caption_block("2027-04-01")


def test_rotation_covers_everything_and_varies_category():
    assert {e["key"] for e in _ROTATION} == {e["key"] for e in HERITAGE}
    cats = [e["category"] for e in _ROTATION]
    runs = [len(list(g)) for _, g in groupby(cats + cats)]  # include wrap-around
    assert max(runs) <= 2


def test_deterministic_and_teases_tomorrow():
    day = date(2026, 10, 2)
    block = heritage_caption_block(day)
    assert block == heritage_caption_block(day.isoformat())
    assert block.startswith(f"✨ {SERIES_OR}")
    tomorrow = heritage_for_date(day + timedelta(days=1))
    assert f"ଆସନ୍ତାକାଲି: {tomorrow['title']['or']}" in block


def test_caption_carries_heritage_and_fits_every_day_of_year():
    long_fest = {
        "name": {"en": "Rath Yatra", "or": "ରଥ ଯାତ୍ରା"},
        "name_en": "Rath Yatra",
        "name_or": "ରଥ ଯାତ୍ରା",
        "description": "x",
    }
    start = date(2026, 1, 1)
    for i in range(366):
        day = (start + timedelta(days=i)).isoformat()
        cap = generate_social_caption(_panchang(day, [long_fest, long_fest]), None)
        assert len(cap) <= CAPTION_MAX_LEN, day
        assert "ରଥ ଯାତ୍ରା" in cap, day
    cap = generate_social_caption(_panchang("2026-09-28"), None)
    assert "କବିବର ରାଧାନାଥ ରାୟ" in cap
    assert "#KnowOdisha" in cap


def test_card_fields_have_glyphs_in_vendored_font():
    """title_or/short_or are painted on the card; any missing glyph is a tofu box."""
    ttlib = pytest.importorskip("fontTools.ttLib")
    from src.social_card import _ASSET_FONTS

    cmap = ttlib.TTFont(_ASSET_FONTS / "NotoSansOriya-Regular.ttf").getBestCmap()
    for e in HERITAGE:
        for text in (e["title"]["or"], e["short_or"], SERIES_OR, e["anniversary_or"]):
            missing = {c for c in text if ord(c) not in cmap and c not in "‌‍"}
            assert not missing, f"{e['key']}: {missing}"


def test_cards_render_with_heritage(tmp_path):
    from src.social_card import generate_daily_card, generate_story_card

    for day in ("2026-09-28", "2026-10-02"):
        feed = generate_daily_card(_panchang(day), None, out_dir=tmp_path)
        story = generate_story_card(_panchang(day), None, feed_path=feed, out_dir=tmp_path)
        assert feed.stat().st_size > 1000 and story.stat().st_size > 1000


# ── Festival-matched entries ─────────────────────────────────────────────

def test_festival_map_uses_real_festival_names():
    from src.festival_stories import FESTIVAL_STORIES
    from src.odisha_heritage import FESTIVAL_HERITAGE

    assert set(FESTIVAL_HERITAGE) <= set(FESTIVAL_STORIES)


def test_festival_picks_complementary_entry():
    e = heritage_for_date("2026-07-16", ["Rath Yatra"])
    assert e["key"] == "salabega" and not e["is_anniversary"]
    # Unmapped festival → plain rotation
    assert heritage_for_date("2026-07-16", ["Pradosha Vrat"]) == heritage_for_date("2026-07-16", [])
    # Anniversary beats festival
    assert heritage_for_date("2026-09-28", ["Rath Yatra"])["key"] == "radhanath_ray"


def test_caption_and_card_follow_the_days_festival():
    fest = {"name": {"en": "Rath Yatra", "or": "ରଥ ଯାତ୍ରା"}, "name_en": "Rath Yatra",
            "name_or": "ରଥ ଯାତ୍ରା", "description": "x"}
    cap = generate_social_caption(_panchang("2026-07-16", [fest]), None)
    assert "ଭକ୍ତକବି ସାଲବେଗ" in cap
    from src.social_card import _heritage_entry

    assert _heritage_entry(_panchang("2026-07-16", [fest]))["key"] == "salabega"


def test_tomorrow_teaser_reads_tomorrows_festivals_from_db():
    import sqlite3

    row = sqlite3.connect("data/panchang.db").execute(
        "select date from festivals where name_en = 'Rath Yatra' order by date desc limit 1"
    ).fetchone()
    if not row:
        pytest.skip("no Rath Yatra row in local DB")
    rath = date.fromisoformat(row[0])
    if rath.strftime("%m-%d") in {e["anniversary"] for e in HERITAGE}:
        pytest.skip("Rath Yatra falls on an anniversary this year")
    block = heritage_caption_block(rath - timedelta(days=1), [])
    assert "ଆସନ୍ତାକାଲି: ଭକ୍ତକବି ସାଲବେଗ" in block


def test_missing_db_falls_back_to_rotation(monkeypatch):
    from src.odisha_heritage import _festival_names_on

    monkeypatch.setenv("DATABASE_URL", "sqlite:////nonexistent/dir/panchang.db")
    assert _festival_names_on(date(2026, 7, 16)) == []


# ── Heritage card ────────────────────────────────────────────────────────

def test_heritage_card_body_glyphs_in_vendored_font():
    ttlib = pytest.importorskip("fontTools.ttLib")
    from src.social_card import _ASSET_FONTS

    cmap = ttlib.TTFont(_ASSET_FONTS / "NotoSansOriya-Regular.ttf").getBestCmap()
    for e in HERITAGE:
        missing = {c for c in e["body"]["or"] if ord(c) not in cmap}
        assert not missing, f"{e['key']}: {missing}"


def test_every_heritage_body_fits_the_card_untruncated():
    from PIL import Image, ImageDraw

    from src.social_card import (
        HERITAGE_BODY_TOP,
        IMAGE_HEIGHT,
        IMAGE_WIDTH,
        _heritage_body_layout,
    )

    draw = ImageDraw.Draw(Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT)))
    max_w = IMAGE_WIDTH - 2 * (48 + 70)
    height = IMAGE_HEIGHT - 48 - 150 - HERITAGE_BODY_TOP
    for e in HERITAGE:
        body = e["body"]["or"]
        _, lines, _ = _heritage_body_layout(draw, body, max_w, height)
        assert " ".join(lines) == " ".join(body.split()), f"{e['key']} truncated"


def test_heritage_cards_render(tmp_path):
    from PIL import Image

    from src.social_card import generate_heritage_card, generate_heritage_story_card

    card = generate_heritage_card(_panchang("2026-09-28"), out_dir=tmp_path)
    story = generate_heritage_story_card(_panchang("2026-09-28"), heritage_path=card, out_dir=tmp_path)
    assert card.name == "panjika_2026-09-28_heritage.jpg"
    assert Image.open(card).size == (1080, 1350)
    assert Image.open(story).size == (1080, 1920)
