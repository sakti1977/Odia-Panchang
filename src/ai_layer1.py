"""
Layer 1 — Astronomical Validation & Muhurta Agent.
Uses Groq (free tier) with Llama-3.1-70b to validate panchang accuracy
and compute muhurta timings, special yogas, and astronomical context.
"""

import os
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Muhurta calculations (rule-based, verified against Jyotish standard tables)
# ---------------------------------------------------------------------------

# Day divided into 8 equal parts from sunrise to sunset.
# Rahu Kalam slot number (1-based): Mon=2,Sat=3,Fri=4,Wed=5,Thu=6,Tue=7,Sun=8
_RAHU_SLOTS   = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}  # weekday (Mon=0)
# Gulika Kalam slot: Sun=7,Mon=6,Tue=5,Wed=4,Thu=3,Fri=2,Sat=1
_GULIKA_SLOTS = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 7}
# Yamagandam slot: Sun=5,Mon=2,Tue=7,Wed=6,Thu=4,Fri=3,Sat=1
_YAMA_SLOTS   = {0: 2, 1: 7, 2: 6, 3: 4, 4: 3, 5: 1, 6: 5}


def _parse_time(t: str, base_date: str) -> datetime | None:
    """Parse HH:MM string into a datetime on base_date."""
    if not t:
        return None
    try:
        dt = datetime.strptime(f"{base_date} {t}", "%Y-%m-%d %H:%M")
        return dt
    except ValueError:
        return None


def _fmt(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def compute_muhurtas(date_str: str, sunrise: str, sunset: str, weekday: int) -> dict:
    """
    Compute Rahu Kalam, Gulika Kalam, Yamagandam, Abhijit Muhurta, Brahma Muhurta.
    weekday: Python weekday() — Mon=0, Sun=6.
    Returns dict with timing strings (IST).
    """
    sr = _parse_time(sunrise, date_str)
    ss = _parse_time(sunset, date_str)
    if not sr or not ss:
        return {}

    day_mins = (ss - sr).total_seconds() / 60
    slot_mins = day_mins / 8  # each of the 8 equal daytime slots

    def slot_range(slot_num: int) -> tuple[str, str]:
        start = sr + timedelta(minutes=(slot_num - 1) * slot_mins)
        end   = sr + timedelta(minutes=slot_num * slot_mins)
        return _fmt(start), _fmt(end)

    rahu_s,   rahu_e   = slot_range(_RAHU_SLOTS[weekday])
    gulika_s, gulika_e = slot_range(_GULIKA_SLOTS[weekday])
    yama_s,   yama_e   = slot_range(_YAMA_SLOTS[weekday])

    # Abhijit Muhurta: 15 equal muhurtas in daytime; 8th is centered on noon
    # Duration = day_duration / 15 each muhurta
    muhurta_mins = day_mins / 15
    noon = sr + timedelta(minutes=day_mins / 2)
    abhi_s = noon - timedelta(minutes=muhurta_mins / 2)
    abhi_e = noon + timedelta(minutes=muhurta_mins / 2)

    # Brahma Muhurta: 2 muhurtas (96 min) before sunrise, last 48 min most sacred
    brahma_s = sr - timedelta(minutes=96)
    brahma_e = sr - timedelta(minutes=48)

    return {
        "rahu_kalam":      f"{rahu_s}–{rahu_e}",
        "gulika_kalam":    f"{gulika_s}–{gulika_e}",
        "yamagandam":      f"{yama_s}–{yama_e}",
        "abhijit_muhurta": f"{_fmt(abhi_s)}–{_fmt(abhi_e)}",
        "brahma_muhurta":  f"{_fmt(brahma_s)}–{_fmt(brahma_e)}",
    }


# ---------------------------------------------------------------------------
# Special compound yogas (Vara + Nakshatra pairs)
# ---------------------------------------------------------------------------

# Amrit Siddhi Yoga: most auspicious, ensures success in new beginnings
_AMRIT_SIDDHI = {
    6: "Hasta", 0: "Mrigashira", 1: "Ashwini", 2: "Anuradha",
    3: "Pushya", 4: "Revati", 5: "Rohini",  # Sun,Mon,Tue,Wed,Thu,Fri,Sat
}

# Sarvartha Siddhi Yoga: all purposes are fulfilled
_SARVARTHA_SIDDHI = {
    6: ["Hasta", "Pushya", "Uttara Phalguni", "Uttara Ashadha", "Uttara Bhadrapada"],
    0: ["Rohini", "Mrigashira", "Punarvasu", "Pushya", "Shravana"],
    1: ["Ashwini", "Krittika", "Mrigashira", "Chitra", "Dhanishtha"],
    2: ["Rohini", "Anuradha", "Jyeshtha", "Uttara Phalguni", "Revati"],
    3: ["Pushya", "Anuradha", "Punarvasu", "Uttara Bhadrapada", "Revati"],
    4: ["Anuradha", "Ashwini", "Uttara Phalguni", "Shatabhisha", "Revati"],
    5: ["Rohini", "Swati", "Vishakha", "Shravana", "Dhanishtha"],
}

# Siddha Yoga: auspicious for starting ventures
_SIDDHA_YOGA = {
    6: ["Uttara Phalguni", "Pushya"],
    0: ["Anuradha", "Rohini"],
    1: ["Mrigashira", "Krittika"],
    2: ["Hasta", "Punarvasu"],
    3: ["Anuradha", "Ashwini"],
    4: ["Rohini", "Revati"],
    5: ["Krittika", "Hasta"],
}


def detect_special_yogas(weekday: int, nakshatra_en: str, yoga_en: str) -> list[dict]:
    """Detect compound astronomical yogas for the day."""
    found = []
    wd = weekday  # Mon=0, Sun=6

    if _AMRIT_SIDDHI.get(wd) == nakshatra_en:
        found.append({
            "name": "Amrit Siddhi Yoga",
            "name_or": "ଅମୃତ ସିଦ୍ଧି ଯୋଗ",
            "quality": "highly_auspicious",
            "meaning": "Most auspicious yoga. Excellent for new beginnings, major decisions, and important ceremonies.",
        })

    if nakshatra_en in _SARVARTHA_SIDDHI.get(wd, []):
        found.append({
            "name": "Sarvartha Siddhi Yoga",
            "name_or": "ସର୍ବାର୍ଥ ସିଦ୍ଧି ଯୋଗ",
            "quality": "auspicious",
            "meaning": "All purposes are fulfilled. Good for business, travel, and worship.",
        })

    if nakshatra_en in _SIDDHA_YOGA.get(wd, []):
        found.append({
            "name": "Siddha Yoga",
            "name_or": "ସିଦ୍ଧ ଯୋଗ",
            "quality": "auspicious",
            "meaning": "Auspicious for starting new ventures and important tasks.",
        })

    # Inauspicious base yogas (from the 27 yoga cycle)
    _ASHUBHA_YOGAS = {
        "Vishkumbha", "Atiganda", "Shoola", "Ganda", "Vyaghata",
        "Vajra", "Vyatipata", "Parigha", "Vaidhriti",
    }
    if yoga_en in _ASHUBHA_YOGAS:
        found.append({
            "name": f"{yoga_en} (Ashubha)",
            "name_or": f"ଅଶୁଭ ଯୋଗ",
            "quality": "inauspicious",
            "meaning": f"{yoga_en} is an inauspicious yoga. Avoid major decisions, travel, and new ventures.",
        })

    return found


# ---------------------------------------------------------------------------
# Groq AI validation
# ---------------------------------------------------------------------------

def _get_groq_client():
    """Lazy-import Groq client."""
    try:
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return None
        return Groq(api_key=api_key)
    except ImportError:
        logger.warning("groq package not installed. Run: pip install groq")
        return None


_VALIDATION_PROMPT = """You are an expert Vedic astrologer and Odia Panchang scholar.
Validate and enrich the following panchang data for {date}.

PANCHANG DATA:
{panchang_json}

COMPUTED MUHURTAS:
{muhurta_json}

SPECIAL YOGAS DETECTED:
{yogas_json}

Your task:
1. Validate the astronomical data (tithi, nakshatra, yoga, karana) — check if the values are consistent with each other and the time of year.
2. Note any astronomical significance (e.g., if the Moon is in a special position, if this is near an eclipse window, if Sun is in a significant degree).
3. Identify any additional special day types: Ekadashi, Pradosha, Amavasya, Purnima, Chaturthi, Shashti, Ashtami, Navami significance.
4. Provide a brief astrological summary of the day's energy.

Respond with ONLY a valid JSON object in this exact schema:
{{
  "validation_status": "valid" | "anomaly_detected",
  "anomalies": ["..."],
  "astronomical_notes": ["..."],
  "special_day_type": "normal" | "ekadashi" | "pradosha" | "amavasya" | "purnima" | "chaturthi" | "shashti" | "ashtami" | "navami" | "other",
  "special_day_significance": "brief description if special",
  "day_energy": "brief 1-2 sentence summary of the day's astrological energy",
  "day_energy_or": "same in Odia script if possible, else empty string"
}}"""


def validate_with_ai(panchang: dict, muhurtas: dict, yogas: list) -> dict:
    """
    Layer 1: Use Groq/Llama-3.1 to validate panchang and add astronomical context.
    Falls back to rule-based result if Groq is unavailable.
    """
    # Always compute rule-based muhurtas (they are reliable)
    result = {
        "muhurtas": muhurtas,
        "special_yogas": yogas,
        "validation_status": "rule_based",
        "astronomical_notes": [],
        "special_day_type": _detect_special_day_type(panchang),
        "special_day_significance": "",
        "day_energy": "",
        "day_energy_or": "",
    }
    result["special_day_significance"] = _get_special_day_significance(result["special_day_type"])

    client = _get_groq_client()
    if not client:
        return result

    try:
        prompt = _VALIDATION_PROMPT.format(
            date=panchang.get("date", ""),
            panchang_json=json.dumps(panchang, ensure_ascii=False, indent=2),
            muhurta_json=json.dumps(muhurtas, ensure_ascii=False, indent=2),
            yogas_json=json.dumps(yogas, ensure_ascii=False, indent=2),
        )
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=600,
            response_format={"type": "json_object"},
        )
        ai_data = json.loads(response.choices[0].message.content)
        result.update({
            "validation_status": ai_data.get("validation_status", "valid"),
            "anomalies":         ai_data.get("anomalies", []),
            "astronomical_notes": ai_data.get("astronomical_notes", []),
            "special_day_type":  ai_data.get("special_day_type", result["special_day_type"]),
            "special_day_significance": ai_data.get("special_day_significance", result["special_day_significance"]),
            "day_energy":        ai_data.get("day_energy", ""),
            "day_energy_or":     ai_data.get("day_energy_or", ""),
        })
    except Exception as e:
        logger.warning(f"Groq validation failed: {e}")

    return result


# ---------------------------------------------------------------------------
# Rule-based special day detection (fallback)
# ---------------------------------------------------------------------------

def _detect_special_day_type(panchang: dict) -> str:
    tithi = panchang.get("tithi", {})
    tithi_num = panchang.get("tithi", {})
    tithi_en = tithi.get("en", "") if isinstance(tithi, dict) else ""
    t = tithi_en.lower()
    if "ekadashi" in t:  return "ekadashi"
    if "amavasya" in t:  return "amavasya"
    if "purnima" in t:   return "purnima"
    if "chaturthi" in t: return "chaturthi"
    if "shashti" in t:   return "shashti"
    if "ashtami" in t:   return "ashtami"
    if "navami" in t:    return "navami"
    # Pradosha: Trayodashi (13th tithi)
    if "trayodashi" in t: return "pradosha"
    return "normal"


def _get_special_day_significance(day_type: str) -> str:
    return {
        "ekadashi":  "Ekadashi is the most sacred fasting day dedicated to Lord Vishnu/Jagannath. Observing Ekadashi Vrat grants moksha and removes sins.",
        "pradosha":  "Pradosha (Trayodashi) is sacred to Lord Shiva. Evening worship during twilight is especially meritorious.",
        "amavasya":  "Amavasya (New Moon) is for ancestor veneration (Pitru Tarpana), Shiva worship, and Tarpanam rituals.",
        "purnima":   "Purnima (Full Moon) is for Satyanarayan Puja, Lakshmi worship, and sacred river bathing.",
        "chaturthi": "Chaturthi is dedicated to Lord Ganesha. Ganesh Chaturthi (Bhadra Shukla 4) is a major festival.",
        "shashti":   "Shashti is dedicated to Kartikeya (Murugan/Skanda) and Goddess Shashthi, protector of children.",
        "ashtami":   "Ashtami is sacred to Goddess Durga/Bhagavati. Durgashtami fasting is observed.",
        "navami":    "Navami is dedicated to Goddess Durga (Navratri's climax) and Lord Rama (Ram Navami).",
        "normal":    "",
    }.get(day_type, "")
