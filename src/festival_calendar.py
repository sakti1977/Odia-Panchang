"""
Festival calendar: which civil day each festival falls on, for a year and place.

Replaces per-day sunrise matching (one sample per day), which put a festival
on the wrong day whenever its tithi was skipped (kshaya — no sunrise inside
it, e.g. Diwali vanished in 2021/2022/2024), repeated (vriddhi — two days),
or is classically observed at another time of day.

For each rule (Purnimanta month, paksha, tithi) we take the tithi's actual
interval in the matching non-Adhika lunation (src/lunar_calendar.py) and pick
the civil day by the festival's kala (observance time):

  sunrise    — tithi prevailing at sunrise (udaya tithi): the default
  purvahna   — first half of daytime           (Akshaya Tritiya, Saraswati Puja)
  madhyahna  — 3rd fifth of daytime            (Rama Navami, Ganesh Chaturthi)
  aparahna   — 4th fifth of daytime            (Vijaya Dashami)
  pradosha   — first fifth of the night        (Diwali Lakshmi Puja)
  nishita    — midnight muhurta (1/15 of night) (Maha Shivaratri, Janmashtami)

Day kalas need the tithi to cover most of the window (vyapini); night kalas
need it to reach the window. If the tithi prevails at the kala on two days, `tie` picks the first (default) or
second; if on none, the day in which the tithi mostly falls. A civil "day"
runs sunrise → next sunrise at the place.

Sankrantis fall on the civil date of the solar transit, moving to the next
day for transits late in the evening (see SANKRANTI_CUTOFF_HOURS).
Ekadashis follow the Vaishnava arunodaya-viddha rule (see ekadashi_day).

Every date produced here is audited against an independent reference in
tests (src/festival_audit.py). Never tune a kala to make one year pass:
kalas below follow the classical rule for the observance.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from functools import lru_cache

import swisseph as swe

from src.lunar_calendar import lunations_for_year, sankrantis_for_year
from src.translations import CHANDRA_MASA, SOURA_MASA

_MASA_INDEX = {m["en"]: i for i, m in enumerate(CHANDRA_MASA)}
_SOURA_INDEX = {m["en"]: i for i, m in enumerate(SOURA_MASA)}

# festival name_en → (kala, tie, criterion). Unlisted: sunrise (udaya tithi),
# the Odia panji default. Each entry is the classical observance rule for that
# festival (Dharmasindhu / Nirnayasindhu tradition as used by Odia panjis);
# the reference audit confirms them, it did not pick them.
#   criterion "vyapini": the tithi must cover most of the kala window
#             "sparsha": the tithi need only be present during it
#             "trimuhurta": Yugadi rule — the second day if the tithi lasts
#                           ≥ 3 muhurtas after that day's sunrise, else the first
KALA: dict[str, tuple[str, str, str]] = {
    # Krishna's midnight birth: Smarta nishita Ashtami (Odisha Government
    # holiday list: Janmashtami 15 Aug 2025, not the udaya 16 Aug)
    "Janmashtami": ("nishita", "first", "sparsha"),
    # Shiva's night: Chaturdashi at midnight
    "Maha Shivaratri": ("nishita", "first", "sparsha"),
    "Lingaraj Maha Shivaratri": ("nishita", "first", "sparsha"),
    "Biraja Shivaratri": ("nishita", "first", "sparsha"),
    # Lakshmi Puja in pradosha; if Amavasya reaches pradosha on both days, the second
    "Diwali / Lakshmi Puja": ("pradosha", "second", "sparsha"),
    # Vijaya Dashami: aparahna-vyapini Dashami
    "Dussehra / Vijaya Dashami": ("aparahna", "first", "vyapini"),
    "Vijaya Dashami at Biraja": ("aparahna", "first", "vyapini"),
    # Mahalaya shraddha at aparahna
    "Mahalaya": ("aparahna", "first", "vyapini"),
    # Madhyahna-vyapini: Ganesha's birth at midday
    "Ganesh Chaturthi": ("madhyahna", "first", "vyapini"),
    # Durga Puja days: the tithi present at midday (Odisha Government
    # holiday lists 2025 and 2026 — e.g. Saptami 17 Oct 2026 although
    # Shashthi held at that sunrise). Drik's udaya Mahastami differs.
    "Durga Saptami": ("madhyahna", "first", "sparsha"),
    "Durga Ashtami": ("madhyahna", "first", "sparsha"),
    "Maa Biraja Ashtami": ("madhyahna", "first", "sparsha"),
    "Mahanavami": ("madhyahna", "first", "sparsha"),
    "Mahanavami at Biraja": ("madhyahna", "first", "sparsha"),
    # Present at midday, earlier day preferred
    "Nuakhai": ("madhyahna", "first", "sparsha"),
    "Nuakhai Juhar": ("madhyahna", "first", "sparsha"),
    # Rama Navami and Savitri Amavasya follow the udaya tithi in Odisha
    # (Government holiday lists: Ram Navami 27 Mar 2026, Savitri 27 May 2025).
    # Present in the forenoon, earlier day preferred
    "Vasanta Panchami / Saraswati Puja": ("purvahna", "first", "sparsha"),
    "Bali Pratipada / Govardhan Puja": ("purvahna", "first", "sparsha"),
    # Akshaya Tritiya is a Yugadi tithi
    "Akshaya Tritiya": ("purvahna", "first", "trimuhurta"),
    "Chandan Yatra Begins": ("purvahna", "first", "trimuhurta"),
    "Biraja Akshaya Tritiya": ("purvahna", "first", "trimuhurta"),
    # Gamha Purnima: forenoon-vyapini Purnima (cattle worship, Balabhadra puja)
    "Gamha Purnima": ("purvahna", "first", "vyapini"),
}


def _civil_date(jd: float, tz_hours: float) -> date:
    y, m, d, _ = swe.revjul(jd + tz_hours / 24.0)
    return date(y, m, d)


@lru_cache(maxsize=4096)
def _sun_times(d: date, lat: float, lon: float, tz_hours: float) -> tuple[float, float]:
    from src.engine import _get_sunrise_sunset_jd

    rise, sset, _, _ = _get_sunrise_sunset_jd(d, lat=lat, lon=lon, tz_hours=tz_hours)
    if rise is None or sset is None:  # never at Odisha latitudes; fail loud elsewhere
        raise RuntimeError(f"no sunrise/sunset for {d} at {lat},{lon}")
    return rise, sset


def _window(d: date, kala: str, place: tuple[float, float, float]) -> tuple[float, float]:
    rise, sset = _sun_times(d, *place)
    if kala == "sunrise":
        return rise, rise
    day = sset - rise
    if kala == "purvahna":
        return rise, rise + day / 2
    if kala == "madhyahna":
        return rise + 2 * day / 5, rise + 3 * day / 5
    if kala == "aparahna":
        return rise + 3 * day / 5, rise + 4 * day / 5
    rise_next, _ = _sun_times(d + timedelta(days=1), *place)
    night = rise_next - sset
    if kala == "pradosha":
        return sset, sset + night / 5
    if kala == "nishita":
        mid = sset + night / 2
        return mid - night / 30, mid + night / 30
    raise ValueError(f"unknown kala {kala!r}")


MUHURTA_DAYS = 48 / 1440


def observance_day(
    start: float,
    end: float,
    kala: str,
    tie: str,
    place: tuple[float, float, float],
    criterion: str = "vyapini",
) -> date:
    """Civil day on which a tithi [start, end) is observed."""
    tz = place[2]
    if criterion == "trimuhurta":
        d2 = _civil_date(end, tz)
        rise2, _ = _sun_times(d2, *place)
        if start <= rise2 and end - rise2 >= 3 * MUHURTA_DAYS:
            return d2
        criterion = "sparsha"
    majority = criterion == "vyapini"
    first = _civil_date(start, tz) - timedelta(days=1)
    last = _civil_date(end, tz) + timedelta(days=1)
    days = [first + timedelta(days=k) for k in range((last - first).days + 1)]
    hits = []
    for d in days:
        w0, w1 = _window(d, kala, place)
        if w0 == w1:
            prevails = start <= w0 < end
        elif kala in ("pradosha", "nishita") or not majority:  # the tithi must reach it
            prevails = start < w1 and end > w0
        else:  # the tithi must cover most of the window (vyapini)
            prevails = min(end, w1) - max(start, w0) >= (w1 - w0) / 2
        if prevails:
            hits.append(d)
    if hits:
        return hits[-1] if (tie == "second" and len(hits) > 1) else hits[0]
    # The tithi prevails at the kala on neither day: fall back to the udaya
    # day (tithi at sunrise), as the panji does.
    if kala != "sunrise":
        for d in days:
            rise, _ = _sun_times(d, *place)
            if start <= rise < end:
                return d
    # True kshaya (no sunrise inside the tithi): the day holding most of it
    best, best_overlap = days[0], -1.0
    for d in days:
        r0, _ = _sun_times(d, *place)
        r1, _ = _sun_times(d + timedelta(days=1), *place)
        overlap = min(end, r1) - max(start, r0)
        if overlap > best_overlap:
            best, best_overlap = d, overlap
    return best


ARUNODAYA_DAYS = 96 / 1440  # 4 ghatikas before sunrise


def ekadashi_day(start: float, end: float, place: tuple[float, float, float]) -> date:
    """Ekadashi fast day: the udaya day, moved to the next day when
      - Dashami still prevails at that day's arunodaya (96 min before
        sunrise) — a Dashami-viddha Ekadashi is rejected; or
      - Ekadashi prevails at the next sunrise too (vriddhi) — the
        Dwadashi-joined second day is kept."""
    d = observance_day(start, end, "sunrise", "first", place)
    rise, _ = _sun_times(d, *place)
    rise_next, _ = _sun_times(d + timedelta(days=1), *place)
    if start > rise - ARUNODAYA_DAYS or end > rise_next:
        return d + timedelta(days=1)
    return d


def _is_ekadashi(name_en: str) -> bool:
    return "Ekadashi" in name_en


# Odia sankranti day: a solar transit up to about 21:13 IST falls on that
# civil date; from about 21:32 IST it moves to the next day. Measured on all
# 132 transits in the 2020–2030 reference with no overlap; the classical
# cutoff inside that 19-minute band is not established, so transits inside
# it are listed by sankranti_edge_cases() for human confirmation.
SANKRANTI_CUTOFF_HOURS = 21.375  # 21:22:30 IST, midpoint of the measured band
SANKRANTI_EDGE_BAND = (21.2, 21.55)


def sankranti_day(jd: float, tz_hours: float) -> date:
    y, m, d, h = swe.revjul(jd + tz_hours / 24.0)
    day = date(y, m, d)
    return day + timedelta(days=1) if h >= SANKRANTI_CUTOFF_HOURS else day


def sankranti_edge_cases(years: range, tz_hours: float = 5.5) -> list[tuple[int, str]]:
    """(sign, local ISO timestamp) of transits inside the unconfirmed band."""
    out = []
    for year in years:
        for sign, jd in sankrantis_for_year(year):
            y, m, d, h = swe.revjul(jd + tz_hours / 24.0)
            if y == year and SANKRANTI_EDGE_BAND[0] <= h <= SANKRANTI_EDGE_BAND[1]:
                out.append((sign, f"{y}-{m:02d}-{d:02d} {int(h):02d}:{int(h % 1 * 60):02d}"))
    return out


def _tithi_number(paksha: str, num: int) -> int:
    return num if paksha.lower() == "shukla" else 15 + num


@lru_cache(maxsize=32)
def festival_calendar(
    year: int, lat: float, lon: float, tz_hours: float
) -> dict[str, tuple[dict, ...]]:
    """ISO date → festival payloads (name_en, name_or, tradition, description)."""
    from src.festivals import SANKRANTI_RULES, TITHI_RULES

    place = (lat, lon, tz_hours)
    out: dict[str, list[dict]] = defaultdict(list)
    lunations = [lu for y in (year - 1, year, year + 1) for lu in lunations_for_year(y)]
    seen_lu = set()
    uniq = []
    for lu in lunations:
        if lu.start not in seen_lu:
            seen_lu.add(lu.start)
            uniq.append(lu)

    for masa, paksha, num, tradition, name_en, name_or, desc in TITHI_RULES:
        t = _tithi_number(paksha, num)
        m = _MASA_INDEX[masa]
        kala, tie, criterion = KALA.get(name_en, ("sunrise", "first", "vyapini"))
        for lu in uniq:
            if lu.adhika or lu.purnimanta(t) != m:
                continue
            s, e = lu.tithi_interval(t)
            if _is_ekadashi(name_en) and name_en not in KALA:
                d = ekadashi_day(s, e, place)
            else:
                d = observance_day(s, e, kala, tie, place, criterion)
            if d.year != year:
                continue
            row = {"name_en": name_en, "name_or": name_or, "tradition": tradition, "description": desc}
            if row not in out[d.isoformat()]:
                out[d.isoformat()].append(row)

    from src.festivals import RELATIVE_RULES

    for anchor, offset, tradition, name_en, name_or, desc in RELATIVE_RULES:
        for iso, rows in list(out.items()):
            if any(r["name_en"] == anchor for r in rows):
                d = (date.fromisoformat(iso) + timedelta(days=offset)).isoformat()
                out[d].append(
                    {"name_en": name_en, "name_or": name_or, "tradition": tradition, "description": desc}
                )

    by_sign: dict[int, list[tuple]] = defaultdict(list)
    for soura, tradition, name_en, name_or, desc in SANKRANTI_RULES:
        by_sign[_SOURA_INDEX[soura]].append((name_en, name_or, tradition, desc))
    for sign, jd in [*sankrantis_for_year(year - 1), *sankrantis_for_year(year)]:
        d = sankranti_day(jd, tz_hours)
        if d.year != year:
            continue
        for name_en, name_or, tradition, desc in by_sign.get(sign, []):
            out[d.isoformat()].append(
                {"name_en": name_en, "name_or": name_or, "tradition": tradition, "description": desc}
            )
    _apply_corrections(out, year)
    return {k: tuple(v) for k, v in out.items() if v}


class StaleCorrection(RuntimeError):
    """A DATE_CORRECTIONS entry no longer matches where the engine puts the
    festival — the engine changed; the correction must be re-reviewed."""


TIER_A_MAX_SHIFT_DAYS = 2


def _apply_tier_a(out: dict[str, list[dict]], year: int) -> None:
    """Tier A civil dates (Odisha Government list, temple schedule) are the
    authority: move the festival onto the cited date. The engine must already
    be within TIER_A_MAX_SHIFT_DAYS — a larger gap is an engine bug, not a
    convention difference, and fails loudly."""
    from src.festival_civil import tier_a_rows

    for row in tier_a_rows():
        if not row["date"].startswith(f"{year}-"):
            continue
        name, target = row["name_en"], date.fromisoformat(row["date"])
        if any(r["name_en"] == name for r in out.get(row["date"], [])):
            continue
        near = [
            (target + timedelta(days=k)).isoformat()
            for k in range(-TIER_A_MAX_SHIFT_DAYS, TIER_A_MAX_SHIFT_DAYS + 1)
            if any(r["name_en"] == name for r in out.get((target + timedelta(days=k)).isoformat(), []))
        ]
        if not near:
            raise StaleCorrection(
                f"{name}: Tier A says {row['date']} ({row['id']}) but the engine is more than "
                f"{TIER_A_MAX_SHIFT_DAYS} days away — investigate the rule, do not widen the window"
            )
        src = near[0]
        moved = [r for r in out[src] if r["name_en"] == name]
        out[src] = [r for r in out[src] if r["name_en"] != name]
        out[row["date"]].extend(moved)


def _apply_corrections(out: dict[str, list[dict]], year: int) -> None:
    _apply_tier_a(out, year)
    from src.festival_civil import corrections_for_year

    for c in corrections_for_year(year):
        for name in c["names"]:
            moved = [r for r in out.get(c["engine_date"], []) if r["name_en"] == name]
            if not moved:
                raise StaleCorrection(
                    f"{name}: correction expects the engine on {c['engine_date']}; re-review it"
                )
            out[c["engine_date"]] = [r for r in out[c["engine_date"]] if r["name_en"] != name]
            out[c["date"]].extend(moved)


def festivals_on(d: date | str, lat: float, lon: float, tz_hours: float) -> list[dict]:
    if isinstance(d, str):
        d = date.fromisoformat(d)
    return [dict(f) for f in festival_calendar(d.year, lat, lon, tz_hours).get(d.isoformat(), ())]
