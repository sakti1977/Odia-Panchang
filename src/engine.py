"""
Astronomical Panchang calculation engine using Swiss Ephemeris (pyswisseph).
Default location: Bangalore, Karnataka (lat=12.9716, lon=77.5946, tz=+5.5)
Location is configurable via LOCATION_* env vars.
"""

from datetime import date, datetime, timezone, timedelta
import os
import swisseph as swe

from src.translations import (
    TITHIS, NAKSHATRAS, YOGAS, KARANAS, SOURA_MASA, CHANDRA_MASA, VARAS, PAKSHA,
)

# Location — configurable via environment variables
_LOCATION_NAME = os.getenv("LOCATION_NAME", "Bangalore")
_LOC_LAT = float(os.getenv("LOCATION_LAT", "12.9716"))
_LOC_LON = float(os.getenv("LOCATION_LON", "77.5946"))
_LOC_TZ  = float(os.getenv("LOCATION_TZ",  "5.5"))

# Keep old names as aliases for backward compatibility
PURI_LAT = _LOC_LAT
PURI_LON = _LOC_LON
PURI_TZ  = _LOC_TZ

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
    Lunar month in Purnimanta system (used in Odisha):
    - Month is named by the Purnima that closes it.
    - Shukla paksha: upcoming Purnima's solar month determines the name.
    - Krishna paksha: last Purnima's solar month determines the name.
    Sun moves ~1°/day ≈ 1° per tithi.
    """
    tithi_idx = _tithi_index(moon_lon, sun_lon)  # 0-29
    if tithi_idx < 15:
        # Shukla paksha: tithis remaining until Purnima = 14 - tithi_idx
        sun_at_purnima = (sun_lon + (14 - tithi_idx)) % 360
    else:
        # Krishna paksha: tithis since last Purnima = tithi_idx - 14
        sun_at_purnima = (sun_lon - (tithi_idx - 14)) % 360
    return int(sun_at_purnima / 30) % 12


def _get_sunrise_sunset(d: date, lat: float = PURI_LAT, lon: float = PURI_LON):
    """Return (sunrise_iso, sunset_iso) in local IST time."""
    # Start search from previous noon UT
    jd_start = _date_to_jd(d, -6.0)  # ~midnight UT (5:30 AM IST previous day)
    geopos = (lon, lat, 0.0)
    ist = timezone(timedelta(hours=PURI_TZ))

    try:
        res_rise = swe.rise_trans(
            jd_start, swe.SUN, swe.CALC_RISE, geopos
        )
        jd_rise = res_rise[1][0]
        yr, mo, dy, hr = swe.revjul(jd_rise)
        frac, mins = divmod(int((hr % 1) * 60), 1)
        rise_dt = datetime(
            int(yr), int(mo), int(dy),
            int(hr), int((hr % 1) * 60), 0,
            tzinfo=timezone.utc
        ).astimezone(ist)
        rise_iso = rise_dt.strftime("%H:%M")

        res_set = swe.rise_trans(
            jd_start, swe.SUN, swe.CALC_SET, geopos
        )
        jd_set = res_set[1][0]
        yr, mo, dy, hr = swe.revjul(jd_set)
        set_dt = datetime(
            int(yr), int(mo), int(dy),
            int(hr), int((hr % 1) * 60), 0,
            tzinfo=timezone.utc
        ).astimezone(ist)
        set_iso = set_dt.strftime("%H:%M")

        return rise_iso, set_iso

    except Exception:
        return None, None


def compute_panchang(d: date) -> dict:
    """
    Compute full Panchang for a given date (at sunrise time ~6 AM UT).
    Returns a dict with all fields bilingual (en + or).
    """
    # Use 0:30 UT ≈ 6:00 AM IST for sunrise-based panchang
    jd = _date_to_jd(d, 0.5)

    sun_lon  = _sun_longitude(jd)
    moon_lon = _moon_longitude(jd)

    tithi_idx     = _tithi_index(moon_lon, sun_lon)
    nakshatra_idx = _nakshatra_index(moon_lon)
    yoga_idx      = _yoga_index(sun_lon, moon_lon)
    karana_idx    = _karana_index(moon_lon, sun_lon)
    soura_idx     = _soura_masa_index(sun_lon)
    chandra_idx   = _chandra_masa_index(sun_lon, moon_lon)

    # Paksha: tithi 0–14 = Shukla, 15–29 = Krishna
    paksha_key = "shukla" if tithi_idx < 15 else "krishna"
    # Tithi number within paksha (1–15)
    tithi_num_in_paksha = (tithi_idx % 15) + 1

    # Vara (day of week): Python weekday() 0=Mon, we need 0=Sun
    vara_idx = (d.weekday() + 1) % 7

    sunrise, sunset = _get_sunrise_sunset(d)

    tithi_data     = TITHIS[tithi_idx]
    nakshatra_data = NAKSHATRAS[nakshatra_idx]
    yoga_data      = YOGAS[yoga_idx]
    karana_data    = KARANAS[karana_idx]
    soura_data     = SOURA_MASA[soura_idx]
    chandra_data   = CHANDRA_MASA[chandra_idx]
    vara_data      = VARAS[vara_idx]
    paksha_data    = PAKSHA[paksha_key]

    return {
        "date":             d.isoformat(),
        "vara_en":          vara_data["en"],
        "vara_or":          vara_data["or"],
        "soura_masa_en":    soura_data["en"],
        "soura_masa_or":    soura_data["or"],
        "chandra_masa_en":  chandra_data["en"],
        "chandra_masa_or":  chandra_data["or"],
        "paksha_en":        paksha_data["en"],
        "paksha_or":        paksha_data["or"],
        "tithi_num":        tithi_num_in_paksha,
        "tithi_en":         tithi_data["en"],
        "tithi_or":         tithi_data["or"],
        "nakshatra_en":     nakshatra_data["en"],
        "nakshatra_or":     nakshatra_data["or"],
        "yoga_en":          yoga_data["en"],
        "yoga_or":          yoga_data["or"],
        "karana_en":        karana_data["en"],
        "karana_or":        karana_data["or"],
        "sunrise":          sunrise,
        "sunset":           sunset,
    }
