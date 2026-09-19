"""
Tithi / nakshatra end-time computation (src/engine.py) and formatting
(src/tweet_generator.format_end_time).

This is the detail that separates a real panjika from a pretty daily
graphic: not just *which* tithi/nakshatra is current, but *until when*.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from src.engine import (
    _date_to_jd,
    _get_sunrise_sunset_jd,
    _moon_longitude,
    _nakshatra_end_jd,
    _nakshatra_index,
    _sun_longitude,
    _tithi_end_jd,
    _tithi_index,
    PURI_LAT,
    PURI_LON,
    PURI_TZ,
    compute_panchang,
)
from src.tweet_generator import format_end_time


def _jd_for(d: date) -> float:
    jd_rise, _, _, _ = _get_sunrise_sunset_jd(d, PURI_LAT, PURI_LON, PURI_TZ)
    return jd_rise if jd_rise else _date_to_jd(d, 0.5)


@pytest.mark.parametrize(
    "d",
    [
        date(2026, 9, 19),
        date(2026, 7, 16),
        date(2026, 1, 1),
        date(2020, 1, 1),
        date(2030, 12, 31),
        date(2026, 5, 10),
    ],
)
def test_tithi_end_crosses_into_the_next_index(d: date):
    """The returned end time must be exactly where the tithi index itself
    flips to idx+1 (or wraps 0→29 at Amavasya) — the true definition of
    'this tithi ends here', checked against engine.py's own index logic
    rather than an external reference."""
    jd = _jd_for(d)
    sun_lon, moon_lon = _sun_longitude(jd), _moon_longitude(jd)
    tithi_idx = _tithi_index(moon_lon, sun_lon)

    end_jd = _tithi_end_jd(jd, tithi_idx)
    assert end_jd is not None
    assert end_jd > jd

    duration_hours = (end_jd - jd) * 24
    assert 0 < duration_hours < 30, f"implausible tithi duration: {duration_hours}h"

    new_idx = _tithi_index(_moon_longitude(end_jd), _sun_longitude(end_jd))
    assert new_idx == (tithi_idx + 1) % 30

    # Just before the boundary, the index must still be the old one.
    just_before = end_jd - (30 / 86400.0)  # 30 seconds earlier
    still_old = _tithi_index(_moon_longitude(just_before), _sun_longitude(just_before))
    assert still_old == tithi_idx


@pytest.mark.parametrize(
    "d",
    [
        date(2026, 9, 19),
        date(2026, 7, 16),
        date(2026, 1, 1),
        date(2020, 1, 1),
        date(2030, 12, 31),
        date(2026, 5, 10),
    ],
)
def test_nakshatra_end_crosses_into_the_next_index(d: date):
    jd = _jd_for(d)
    moon_lon = _moon_longitude(jd)
    nak_idx = _nakshatra_index(moon_lon)

    end_jd = _nakshatra_end_jd(jd, nak_idx)
    assert end_jd is not None
    assert end_jd > jd

    duration_hours = (end_jd - jd) * 24
    assert 0 < duration_hours < 30, f"implausible nakshatra duration: {duration_hours}h"

    new_idx = _nakshatra_index(_moon_longitude(end_jd))
    assert new_idx == (nak_idx + 1) % 27


def test_tithi_end_handles_amavasya_wraparound():
    """The one genuinely tricky case: tithi_idx=29 (Amavasya) wrapping to 0
    (Shukla Pratipada) — boundary_deg=360 modding back to ~0."""
    d = date(2026, 1, 1)
    end = d + timedelta(days=60)
    found = 0
    while d <= end and found < 2:
        jd = _jd_for(d)
        sun_lon, moon_lon = _sun_longitude(jd), _moon_longitude(jd)
        tithi_idx = _tithi_index(moon_lon, sun_lon)
        if tithi_idx == 29:
            found += 1
            end_jd = _tithi_end_jd(jd, tithi_idx)
            assert end_jd is not None
            new_idx = _tithi_index(_moon_longitude(end_jd), _sun_longitude(end_jd))
            assert new_idx == 0
        d += timedelta(days=1)
    assert found == 2, "expected to find at least 2 Amavasya days to test wraparound"


def test_compute_panchang_includes_end_times():
    p = compute_panchang(date(2026, 9, 19))
    assert p["tithi_end_ts"] is not None
    assert p["nakshatra_end_ts"] is not None
    # Full local ISO datetime with offset, not a bare HH:MM.
    assert p["tithi_end_ts"].startswith("2026-")
    assert "+05:30" in p["tithi_end_ts"]


class TestFormatEndTime:
    def test_same_day_end(self):
        assert format_end_time("2026-09-19T15:27:00+05:30", "2026-09-19") == "15:27 ପର୍ଯ୍ୟନ୍ତ"

    def test_next_day_end_is_flagged(self):
        result = format_end_time("2026-09-20T01:43:00+05:30", "2026-09-19")
        assert result == "କାଲି 01:43 ପର୍ଯ୍ୟନ୍ତ"

    def test_missing_end_ts_returns_empty(self):
        assert format_end_time(None, "2026-09-19") == ""
        assert format_end_time("", "2026-09-19") == ""

    def test_malformed_end_ts_returns_empty_not_raises(self):
        assert format_end_time("not-a-date", "2026-09-19") == ""


def test_caption_includes_end_times():
    from src.tweet_generator import generate_social_caption

    panchang = {
        "date": "2026-09-19",
        "vara": {"or": "ଶନିବାର"},
        "chandra_masa": {"or": "ଭାଦ୍ରବ"},
        "paksha": {"or": "ଶୁକ୍ଳ"},
        "tithi": {"or": "ଅଷ୍ଟମୀ", "end_ts": "2026-09-19T15:27:00+05:30"},
        "nakshatra": {"or": "ମୂଳ", "end_ts": "2026-09-20T01:43:00+05:30"},
        "yoga": {"or": "ଆୟୁଷ୍ମାନ"},
        "sunrise": "05:34",
        "sunset": "17:46",
        "festivals": [],
    }
    caption = generate_social_caption(panchang, None)
    assert "15:27 ପର୍ଯ୍ୟନ୍ତ" in caption
    assert "କାଲି 01:43 ପର୍ଯ୍ୟନ୍ତ" in caption
