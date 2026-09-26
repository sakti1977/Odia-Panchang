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
ENGINE_VERSION = "lahiri_purnimanta_v5_sunrise_sankranti_adhika"

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
swe.set_sid_mode(swe.SIDM_LAHIRI)  # Lahiri ayanamsa for Indian panchang — see
# _set_lahiri_mode() below for why this alone is not enough.
_SIDEREAL = swe.FLG_SWIEPH | swe.FLG_SIDEREAL


def _set_lahiri_mode() -> None:
    """
    pyswisseph's sidereal mode is thread-local in the underlying C library,
    not process-global. The module-level swe.set_sid_mode() call above only
    affects the thread that imports this module. FastAPI/Starlette runs
    every sync `def` route handler in a worker thread pool, so any live
    (non-DB) panchang computed inside a request handler was silently
    running under Swiss Ephemeris's *default* sidereal mode (Fagan-Bradley,
    ~0.88° off Lahiri for the current era) instead of Lahiri — confirmed via
    a ThreadPoolExecutor reproduction.

    Absolute-longitude fields (nakshatra, soura_masa, chandra_masa, yoga —
    yoga uses sun+moon) were affected; a constant ayanamsa offset cancels
    out of moon-sun *differences*, so tithi and karana were unaffected.
    The error is small enough (~0.88° of a ~13.3° nakshatra span) that it
    rarely flips the reported name, which is why this went unnoticed — but
    it does distort computed end-times, and would occasionally flip a name
    right at a boundary day.

    Cheap enough to call on every longitude fetch rather than relying on
    which thread happened to import this module.
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)


def _date_to_jd(d: date, hour: float = 0.0) -> float:
    """Convert a date + decimal hour (UT) to Julian Day Number."""
    return swe.julday(d.year, d.month, d.day, hour)


def _sun_longitude(jd: float) -> float:
    _set_lahiri_mode()
    pos, _ = swe.calc_ut(jd, swe.SUN, _SIDEREAL)
    return pos[0]


def _moon_longitude(jd: float) -> float:
    _set_lahiri_mode()
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


def _chandra_masa_at(jd: float) -> tuple[int, bool]:
    """
    Purnimanta lunar month (index, is_adhika) at a moment.

    Standard panji rule (src/lunar_calendar.py): an Amanta month is named by
    the sankranti inside it — Sun's sign at the opening new moon r gives month
    (r + 1) % 12, Chaitra = 0; no sankranti inside → Adhika. The Krishna
    paksha takes the next month's name (Purnimanta, the Odia convention).

    Replaces the "Sun's sign at the closing Purnima" heuristic, which was a
    month off whenever the Sun sat near a sign boundary at full moon (≈ half
    of all months) — see eval.md E-FEST-REFERENCE. Verified against Drik's
    Purnimanta labels on 1,255 of 1,264 reference days 2020–2030; the rest
    are days whose tithi changes just after sunrise (observance-day labels).
    """
    from src.lunar_calendar import masa_at

    return masa_at(jd)


def _crossing_jd(
    jd_start: float,
    angle_fn,
    target_deg: float,
    *,
    max_hours: float = 48.0,
    tol_seconds: float = 20.0,
) -> float | None:
    """
    Find the first JD after jd_start where a monotonically-increasing
    (mod 360) angle quantity reaches target_deg. Used to find exactly when
    the current tithi/nakshatra ends — e.g. angle_fn = moon-sun separation,
    target_deg = the next 12° tithi boundary.

    target_deg may be up to 360 (the *next* cycle's 0°, e.g. Amavasya →
    Shukla Pratipada, or Revati → Ashwini) — handled by unwrapping angle_fn
    relative to its starting value rather than bisecting the raw %360
    result, which would otherwise reset to ~0 right at the crossing and
    break monotonicity.

    Returns None if no crossing is found within max_hours (should not
    happen for real tithi/nakshatra durations, which run ~19-27h; this is
    a safety cap, not an expected outcome).
    """
    start_val = angle_fn(jd_start)

    def unwrapped(jd: float) -> float:
        raw = angle_fn(jd)
        if raw < start_val - 180.0:
            raw += 360.0
        return raw

    step_hours = 2.0
    jd_hi = jd_start
    val_hi = start_val
    hours_elapsed = 0.0
    while val_hi < target_deg and hours_elapsed < max_hours:
        jd_hi += step_hours / 24.0
        hours_elapsed += step_hours
        val_hi = unwrapped(jd_hi)
    if val_hi < target_deg:
        return None

    jd_lo = jd_hi - step_hours / 24.0
    while (jd_hi - jd_lo) * 86400.0 > tol_seconds:
        jd_mid = (jd_lo + jd_hi) / 2.0
        if unwrapped(jd_mid) < target_deg:
            jd_lo = jd_mid
        else:
            jd_hi = jd_mid
    return jd_hi


def _tithi_end_jd(jd_ref: float, tithi_idx: int) -> float | None:
    target = (tithi_idx + 1) * 12.0

    def angle_fn(jd: float) -> float:
        return (_moon_longitude(jd) - _sun_longitude(jd)) % 360

    return _crossing_jd(jd_ref, angle_fn, target)


def _nakshatra_end_jd(jd_ref: float, nakshatra_idx: int) -> float | None:
    target = (nakshatra_idx + 1) * (360.0 / 27.0)

    def angle_fn(jd: float) -> float:
        return _moon_longitude(jd) % 360

    return _crossing_jd(jd_ref, angle_fn, target)


def _jd_to_local_iso(jd: float, tz_hours: float) -> str:
    """Format a UT Julian Day as a full local ISO datetime (date + time +
    offset) — unlike _jd_to_local_hhmm, this keeps the date so a caller can
    tell a same-day end time from one that falls on the next civil day."""
    ist = timezone(timedelta(hours=tz_hours))
    yr, mo, dy, hr = swe.revjul(jd)
    dt_utc = datetime(int(yr), int(mo), int(dy), tzinfo=timezone.utc) + timedelta(
        hours=hr
    )
    return dt_utc.astimezone(ist).replace(microsecond=0).isoformat()


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

    tithi_end_jd = _tithi_end_jd(jd, tithi_idx)
    tithi_end_ts = _jd_to_local_iso(tithi_end_jd, tz_hours) if tithi_end_jd else None
    nakshatra_end_jd = _nakshatra_end_jd(jd, nakshatra_idx)
    nakshatra_end_ts = (
        _jd_to_local_iso(nakshatra_end_jd, tz_hours) if nakshatra_end_jd else None
    )

    yoga_idx = _yoga_index(sun_lon, moon_lon)
    karana_idx = _karana_index(moon_lon, sun_lon)
    soura_idx = _soura_masa_index(sun_lon)
    chandra_idx, adhika = _chandra_masa_at(jd)

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
    if adhika:
        chandra_data = {"en": f"Adhika {chandra_data['en']}", "or": f"ଅଧିକ {chandra_data['or']}"}
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
        "adhika_masa": adhika,
        "paksha_en": paksha_data["en"],
        "paksha_or": paksha_data["or"],
        "tithi_num": tithi_num_in_paksha,
        "tithi_en": tithi_data["en"],
        "tithi_or": tithi_data["or"],
        "tithi_end_ts": tithi_end_ts,
        "nakshatra_en": nakshatra_data["en"],
        "nakshatra_or": nakshatra_data["or"],
        "nakshatra_end_ts": nakshatra_end_ts,
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
