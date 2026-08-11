"""
Astronomical Panchang calculation engine using Swiss Ephemeris (pyswisseph).
Default location: Bhubaneswar, Odisha (lat=20.2961, lon=85.8245, tz=+5.5)
Location is configurable via LOCATION_* env vars.
"""

from datetime import date, datetime, timezone, timedelta
import os
import swisseph as swe

from src.translations import (
    TITHIS, NAKSHATRAS, YOGAS, KARANAS, SOURA_MASA, CHANDRA_MASA, VARAS, PAKSHA,
)

# Bump when masa/tithi/anchor formula changes so seed/start can force reseed.
ENGINE_VERSION = "lahiri_purnimanta_v3_sunrise"

# Location — configurable via environment variables
# Default: Bhubaneswar, capital of Odisha
_LOCATION_NAME = os.getenv("LOCATION_NAME", "Bhubaneswar")
_LOC_LAT = float(os.getenv("LOCATION_LAT", "20.2961"))
_LOC_LON = float(os.getenv("LOCATION_LON", "85.8245"))
_LOC_TZ  = float(os.getenv("LOCATION_TZ",  "5.5"))

# Default env place is Bhubaneswar (not Puri). Historical aliases kept for
# backward-compat imports; prefer BHUBANESWAR_* or LOCATION_* env.
BHUBANESWAR_LAT = _LOC_LAT
BHUBANESWAR_LON = _LOC_LON
BHUBANESWAR_TZ = _LOC_TZ
PURI_LAT = _LOC_LAT  # misnamed legacy alias → module default lat
PURI_LON = _LOC_LON
PURI_TZ = _LOC_TZ

swe.set_ephe_path(None)  # use built-in ephemeris
swe.set_sid_mode(swe.SIDM_LAHIRI)  # Lahiri ayanamsa for Indian panchang
_SIDEREAL = swe.FLG_SWIEPH | swe.FLG_SIDEREAL


def _date_to_jd(d: date, hour: float = 0.0) -> float:
    """Convert a date + decimal hour (UT) to Julian Day Number."""
    return swe.julday(d.year, d.month, d.day, hour)


def _sun_longitude(jd: float) -> float:
    pos, _ = swe.calc_ut(jd, swe.SUN, _SIDEREAL)
    return pos[0]


def _moon_longitude(jd: float) -> float:
    pos, _ = swe.calc_ut(jd, swe.MOON, _SIDEREAL)
    return pos[0]


def _tithi_index(moon_lon: float, sun_lon: float) -> int:
    """Returns tithi index 0–29 (0 = Shukla Pratipada, 14 = Purnima, 29 = Amavasya)."""
    diff = (moon_lon - sun_lon) % 360
    return int(diff / 12)


def _nakshatra_index(moon_lon: float) -> int:
    """Returns nakshatra index 0–26."""
    return int((moon_lon % 360) / (360 / 27))


def _yoga_index(sun_lon: float, moon_lon: float) -> int:
    """Returns yoga index 0–26."""
    return int(((sun_lon + moon_lon) % 360) / (360 / 27))


def _karana_index(moon_lon: float, sun_lon: float) -> int:
    """
    Returns karana index.
    The 60 karanas cycle: first karana of Shukla Pratipada is Kimstughna (index 10),
    then 7 movable karanas repeat 8 times (indices 0–6), then 4 fixed ones at end.
    We map the half-tithi position to the standard 11-karana list.
    """
    diff = (moon_lon - sun_lon) % 360
    half_tithi = int(diff / 6)  # 0–59

    # First half-tithi: Kimstughna (fixed)
    if half_tithi == 0:
        return 10
    # Last 4 half-tithis (56–59): fixed karanas Shakuni, Chatushpada, Naga, Kimstughna
    if half_tithi >= 57:
        return [7, 8, 9, 10][half_tithi - 57]
    # Movable karanas cycle 0–6
    return (half_tithi - 1) % 7


def _soura_masa_index(sun_lon: float) -> int:
    """Returns solar month index 0–11 (0 = Mesha)."""
    return int(sun_lon / 30) % 12


def _chandra_masa_index(sun_lon: float, moon_lon: float) -> int:
    """
    Lunar month in the Purnimanta system (Odisha panji default).

    Purnimanta structure:
      - A lunar month ends on Purnima and is *named* for that closing Purnima.
      - Krishna paksha of a named month comes *before* its Shukla paksha
        (after the previous Purnima, through Amavasya, into Shukla, ending Purnima).

    Naming rule used here:
      Chandra masa index = solar rashi index of the Sun at the *closing* Purnima
      of the current lunar month.

      Closing Purnima ≈ now if tithi is Purnima; otherwise the upcoming Purnima.
      Sun longitude at that Purnima is estimated with ~1°/tithi motion
      (standard short-arc approximation used in many software panji engines).

      Mapping: SOURA_MASA index at that Purnima → same index in CHANDRA_MASA
      (Mesha-Purnima region → Chaitra, …, Mithuna-Purnima region → Jyeshtha, …).

    Why not (solar + 2) % 12:
      That offset matched one Drik sample (e.g. 2026-05-10) but shifted Snana /
      Rath month names off Odisha Tourism civil dates. Festival-aligned Purnimanta
      for Jagannath cycle is the product non-negotiable.

    Verified anchors (tithi rule → civil date under this formula, Lahiri, ~06:00 IST):
      - 2024-06-22 Snana (Jyeshtha Shukla 15)
      - 2024-07-07 Rath (Ashadha Shukla 2)
      - 2026-06-29 Snana (Jyeshtha Shukla 15)
      - 2026-07-16 Rath (Ashadha Shukla 2)
      - 2027-07-05 Rath (Ashadha Shukla 2)
    Note: 2025 Puri civil dates (Tourism) disagree with pure masa labels;
    festival attachment uses src/festival_civil.py overrides — see eval.md.
    """
    tithi_idx = _tithi_index(moon_lon, sun_lon)  # 0-29

    if tithi_idx <= 14:
        # Shukla (0–13) or Purnima (14): closing Purnima is upcoming / today
        # Tithis remaining until Purnima ≈ (14 - tithi_idx)
        sun_at_closing_purnima = (sun_lon + (14 - tithi_idx)) % 360
    else:
        # Krishna (15–29): month already past last Purnima; closing Purnima is next
        # Tithis to Amavasya ≈ (29 - tithi_idx), then +15 Shukla tithis to Purnima
        sun_at_closing_purnima = (sun_lon + (29 - tithi_idx) + 15) % 360

    return int(sun_at_closing_purnima / 30) % 12


def _jd_to_local_hhmm(jd: float, tz_hours: float) -> str:
    """Format a UT Julian Day as local HH:MM."""
    ist = timezone(timedelta(hours=tz_hours))
    yr, mo, dy, hr = swe.revjul(jd)
    hour = int(hr)
    minute = int((hr % 1) * 60)
    # Handle floating second rounding into next minute
    if minute >= 60:
        hour += 1
        minute -= 60
    dt = datetime(
        int(yr), int(mo), int(dy), hour % 24, minute, 0, tzinfo=timezone.utc
    ).astimezone(ist)
    return dt.strftime("%H:%M")


def _get_sunrise_sunset_jd(
    d: date,
    lat: float = PURI_LAT,
    lon: float = PURI_LON,
    tz_hours: float = PURI_TZ,
) -> tuple[float | None, float | None, str | None, str | None]:
    """
    Return (jd_sunrise, jd_sunset, sunrise_hhmm, sunset_hhmm) for lat/lon/tz.
    JD values are UT (Swiss Ephemeris convention).
    """
    # Search from ~previous evening UT so the next sunrise is civil date's morning
    jd_start = _date_to_jd(d, -6.0)
    geopos = (lon, lat, 0.0)
    try:
        res_rise = swe.rise_trans(jd_start, swe.SUN, swe.CALC_RISE, geopos)
        jd_rise = float(res_rise[1][0])
        res_set = swe.rise_trans(jd_start, swe.SUN, swe.CALC_SET, geopos)
        jd_set = float(res_set[1][0])
        # Prefer set after rise; if set came before rise, re-search set from rise
        if jd_set < jd_rise:
            res_set = swe.rise_trans(jd_rise, swe.SUN, swe.CALC_SET, geopos)
            jd_set = float(res_set[1][0])
        return (
            jd_rise,
            jd_set,
            _jd_to_local_hhmm(jd_rise, tz_hours),
            _jd_to_local_hhmm(jd_set, tz_hours),
        )
    except Exception:
        return None, None, None, None


def _get_sunrise_sunset(
    d: date,
    lat: float = PURI_LAT,
    lon: float = PURI_LON,
    tz_hours: float = PURI_TZ,
):
    """Return (sunrise_iso, sunset_iso) in local time for lat/lon/tz."""
    _, _, rise_iso, set_iso = _get_sunrise_sunset_jd(d, lat, lon, tz_hours)
    return rise_iso, set_iso


def compute_panchang(
    d: date,
    lat: float | None = None,
    lon: float | None = None,
    tz_hours: float | None = None,
) -> dict:
    """
    Compute full Panchang for a civil date at **local sunrise** (Path A).

    Day elements (tithi, masa, nakshatra, yoga, karana) use Lahiri longitudes
    at the place's sunrise JD. If sunrise cannot be computed, falls back to
    ~00:30 UT (≈ 06:00 IST).

    Optional lat/lon/tz_hours select the place (default LOCATION_* / Bhubaneswar).
    """
    lat = _LOC_LAT if lat is None else float(lat)
    lon = _LOC_LON if lon is None else float(lon)
    tz_hours = _LOC_TZ if tz_hours is None else float(tz_hours)

    jd_rise, jd_set, sunrise, sunset = _get_sunrise_sunset_jd(
        d, lat=lat, lon=lon, tz_hours=tz_hours
    )
    if jd_rise is not None:
        jd = jd_rise
        anchor = "local_sunrise"
    else:
        # Fallback: ~00:30 UT ≈ 06:00 IST
        jd = _date_to_jd(d, 0.5)
        anchor = "approx_06:00_IST_fallback"
        sunrise, sunset = _get_sunrise_sunset(d, lat=lat, lon=lon, tz_hours=tz_hours)

    sun_lon = _sun_longitude(jd)
    moon_lon = _moon_longitude(jd)

    tithi_idx = _tithi_index(moon_lon, sun_lon)
    nakshatra_idx = _nakshatra_index(moon_lon)
    yoga_idx = _yoga_index(sun_lon, moon_lon)
    karana_idx = _karana_index(moon_lon, sun_lon)
    soura_idx = _soura_masa_index(sun_lon)
    chandra_idx = _chandra_masa_index(sun_lon, moon_lon)

    # Paksha: tithi 0–14 = Shukla, 15–29 = Krishna
    paksha_key = "shukla" if tithi_idx < 15 else "krishna"
    # Tithi number within paksha (1–15)
    tithi_num_in_paksha = (tithi_idx % 15) + 1

    # Vara (day of week): Python weekday() 0=Mon, we need 0=Sun
    vara_idx = (d.weekday() + 1) % 7

    tithi_data = TITHIS[tithi_idx]
    nakshatra_data = NAKSHATRAS[nakshatra_idx]
    yoga_data = YOGAS[yoga_idx]
    karana_data = KARANAS[karana_idx]
    soura_data = SOURA_MASA[soura_idx]
    chandra_data = CHANDRA_MASA[chandra_idx]
    vara_data = VARAS[vara_idx]
    paksha_data = PAKSHA[paksha_key]

    return {
        "date": d.isoformat(),
        "vara_en": vara_data["en"],
        "vara_or": vara_data["or"],
        "soura_masa_en": soura_data["en"],
        "soura_masa_or": soura_data["or"],
        "chandra_masa_en": chandra_data["en"],
        "chandra_masa_or": chandra_data["or"],
        "paksha_en": paksha_data["en"],
        "paksha_or": paksha_data["or"],
        "tithi_num": tithi_num_in_paksha,
        "tithi_en": tithi_data["en"],
        "tithi_or": tithi_data["or"],
        "nakshatra_en": nakshatra_data["en"],
        "nakshatra_or": nakshatra_data["or"],
        "yoga_en": yoga_data["en"],
        "yoga_or": yoga_data["or"],
        "karana_en": karana_data["en"],
        "karana_or": karana_data["or"],
        "sunrise": sunrise,
        "sunset": sunset,
        "day_elements_anchor": anchor,
        "lat": lat,
        "lon": lon,
    }
