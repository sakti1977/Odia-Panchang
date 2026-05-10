"""
Layer 2 — Odia Cultural Enrichment Agent.
Uses Claude (Anthropic) to provide deep Odia cultural significance,
Jagannath/Biraja temple guidance, fasting rules, and bilingual notes.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rule-based cultural knowledge base (Odia tradition)
# ---------------------------------------------------------------------------

# Tithi presiding deities (index 0-29)
_TITHI_DEITIES = [
    {"deity": "Agni (Fire God)",          "deity_or": "ଅଗ୍ନି"},           # 1 Pratipada
    {"deity": "Brahma (Creator)",          "deity_or": "ବ୍ରହ୍ମା"},          # 2 Dwitiya
    {"deity": "Gauri (Parvati)",           "deity_or": "ଗୌରୀ"},             # 3 Tritiya
    {"deity": "Ganesha (Ganesh)",          "deity_or": "ଗଣେଶ"},             # 4 Chaturthi
    {"deity": "Naga (Serpent Gods)",       "deity_or": "ନାଗ"},              # 5 Panchami
    {"deity": "Karttikeya (Skanda)",       "deity_or": "କାର୍ତ୍ତିକେୟ"},      # 6 Shashti
    {"deity": "Surya (Sun God)",           "deity_or": "ସୂର୍ଯ୍ୟ"},           # 7 Saptami
    {"deity": "Shiva (Mahadeva)",          "deity_or": "ଶିବ"},              # 8 Ashtami
    {"deity": "Durga (Bhagavati)",         "deity_or": "ଦୁର୍ଗା"},            # 9 Navami
    {"deity": "Yama (Dharmaraj)",          "deity_or": "ଯମ"},               # 10 Dashami
    {"deity": "Vishnu (Jagannath)",        "deity_or": "ବିଷ୍ଣୁ/ଜଗନ୍ନାଥ"},    # 11 Ekadashi
    {"deity": "Vishnu (Hari)",             "deity_or": "ଶ୍ରୀ ହରି"},          # 12 Dwadashi
    {"deity": "Kama (Love God)",           "deity_or": "କାମଦେବ"},            # 13 Trayodashi
    {"deity": "Shiva (Pradosha)",          "deity_or": "ଶିବ (ପ୍ରଦୋଷ)"},      # 14 Chaturdashi
    {"deity": "Vishnu/Chandra (Full Moon)","deity_or": "ଜଗନ୍ନାଥ/ଚନ୍ଦ୍ର"},    # 15 Purnima
    # Krishna paksha repeats same deities
    {"deity": "Agni (Fire God)",          "deity_or": "ଅଗ୍ନି"},             # 16 K1
    {"deity": "Brahma (Creator)",          "deity_or": "ବ୍ରହ୍ମା"},            # 17 K2
    {"deity": "Gauri (Parvati)",           "deity_or": "ଗୌରୀ"},               # 18 K3
    {"deity": "Ganesha (Ganesh)",          "deity_or": "ଗଣେଶ"},               # 19 K4
    {"deity": "Naga (Serpent Gods)",       "deity_or": "ନାଗ"},                # 20 K5
    {"deity": "Karttikeya (Skanda)",       "deity_or": "କାର୍ତ୍ତିକେୟ"},        # 21 K6
    {"deity": "Surya (Sun God)",           "deity_or": "ସୂର୍ଯ୍ୟ"},             # 22 K7
    {"deity": "Shiva (Mahadeva)",          "deity_or": "ଶିବ"},                # 23 K8
    {"deity": "Durga (Bhagavati)",         "deity_or": "ଦୁର୍ଗା"},              # 24 K9
    {"deity": "Yama (Dharmaraj)",          "deity_or": "ଯମ"},                 # 25 K10
    {"deity": "Vishnu (Jagannath)",        "deity_or": "ବିଷ୍ଣୁ/ଜଗନ୍ନାଥ"},      # 26 K11
    {"deity": "Vishnu (Hari)",             "deity_or": "ଶ୍ରୀ ହରି"},            # 27 K12
    {"deity": "Kama (Love God)",           "deity_or": "କାମଦେବ"},              # 28 K13
    {"deity": "Shiva (Pradosha)",          "deity_or": "ଶିବ (ପ୍ରଦୋଷ)"},        # 29 K14
    {"deity": "Shiva/Ancestors (Amawas)", "deity_or": "ଶିବ/ପିତୃଗଣ"},           # 30 Amavasya
]

# Vara (weekday) significance
_VARA_SIGNIFICANCE = {
    "Sunday": {
        "deity": "Surya (Sun God)", "deity_or": "ଆଦିତ୍ୟ/ସୂର୍ଯ୍ୟ",
        "favorable": ["government matters", "authority", "medicine", "gold"],
        "avoid": ["oil massage", "cutting hair"],
        "jagannath_note": "Surya Puja at Jagannath temple. Chandalagi Besha (special dress) on Sundays.",
        "fasting": "Surya Vrat — dedicated to Lord Sun for health and vitality.",
    },
    "Monday": {
        "deity": "Shiva (Mahadeva)", "deity_or": "ଶିବ/ଚନ୍ଦ୍ର",
        "favorable": ["new ventures", "farming", "worship", "peace"],
        "avoid": ["harsh decisions", "conflicts"],
        "jagannath_note": "Shiva temples in Puri are especially active. Lingaraj is worshipped.",
        "fasting": "Somavar Vrat — fasting for Lord Shiva. Women fast for marital harmony.",
    },
    "Tuesday": {
        "deity": "Mangal (Mars) / Hanuman", "deity_or": "ମଙ୍ଗଳ/ହନୁମାନ",
        "favorable": ["courage", "property", "surgery", "disputes"],
        "avoid": ["travel (inauspicious for long journeys)", "new partnerships"],
        "jagannath_note": "Tuesdays are Hanuman worship days. Many Odia households observe Mangala Puja.",
        "fasting": "Mangalavar Vrat — for Hanuman and Devi Mangala. Odia tradition: Mangala Devi is especially revered in Cuttack.",
    },
    "Wednesday": {
        "deity": "Budha (Mercury) / Vishnu", "deity_or": "ବୁଧ/ବିଷ୍ଣୁ",
        "favorable": ["education", "commerce", "communication", "writing"],
        "avoid": ["hasty decisions", "excessive travel"],
        "jagannath_note": "Wednesdays in Puri: Jagannath temple has special Pahada rituals.",
        "fasting": "Budhavar Vrat — for Vishnu and Mercury. Good for students and businessmen.",
    },
    "Thursday": {
        "deity": "Brihaspati (Jupiter) / Vishnu", "deity_or": "ବୃହସ୍ପତି/ଶ୍ରୀ ହରି",
        "favorable": ["worship", "charity", "teaching", "spiritual practices"],
        "avoid": ["hair washing (traditional belief)", "new purchases on some occasions"],
        "jagannath_note": "Gurubar (Thursday) is especially sacred at Jagannath temple — Sahana Mela besha and prasad distribution.",
        "fasting": "Gurubar Vrat — for Vishnu and Jupiter. Yellow foods like banana and turmeric dal are offered.",
    },
    "Friday": {
        "deity": "Shukra (Venus) / Lakshmi / Mahalakshmi", "deity_or": "ଲକ୍ଷ୍ମୀ/ଶୁକ୍ର",
        "favorable": ["wealth", "beauty", "relationships", "art", "prosperity"],
        "avoid": ["debt", "quarrels"],
        "jagannath_note": "Lakshmi Puja at Jagannath temple. Kojagari Purnima (Lakshmi Puja) is biggest on Friday Purnima. Odia households do Laxmi Puja every Friday.",
        "fasting": "Shukravar Vrat — for Goddess Lakshmi. Odia women observe Manabasa Gurubar (Margashira Thursdays) for Lakshmi. On Fridays, Santoshi Mata Vrat is also observed.",
    },
    "Saturday": {
        "deity": "Shani (Saturn) / Shiva", "deity_or": "ଶନି/ଶିବ",
        "favorable": ["iron work", "servants", "labor", "oil-related"],
        "avoid": ["new ventures", "travel west", "purchases of new items"],
        "jagannath_note": "Shani Deva puja. Saturdays in Odisha: Hanuman Chalisa recitation for Shani protection.",
        "fasting": "Shanivar Vrat — for Shani Deva. Lighting sesame oil lamp at Shani temple removes obstacles.",
    },
}

# Nakshatra characteristics
_NAKSHATRA_QUALITY = {
    "Ashwini":          {"quality": "auspicious",   "nature": "swift", "suitable": ["travel", "medicine", "new beginnings"]},
    "Bharani":          {"quality": "mixed",         "nature": "fierce", "suitable": ["harsh actions", "courage tasks"]},
    "Krittika":         {"quality": "mixed",         "nature": "sharp", "suitable": ["fire rituals", "cooking", "surgery"]},
    "Rohini":           {"quality": "highly_auspicious", "nature": "fixed", "suitable": ["agriculture", "marriage", "planting"]},
    "Mrigashira":       {"quality": "auspicious",   "nature": "gentle", "suitable": ["learning", "travel", "new clothes"]},
    "Ardra":            {"quality": "inauspicious",  "nature": "fierce", "suitable": ["destruction of enemies only"]},
    "Punarvasu":        {"quality": "auspicious",   "nature": "movable","suitable": ["return journeys", "rebuilding", "healing"]},
    "Pushya":           {"quality": "highly_auspicious", "nature": "light", "suitable": ["all auspicious work", "worship", "medicine"]},
    "Ashlesha":         {"quality": "inauspicious",  "nature": "sharp", "suitable": ["matters requiring cunning"]},
    "Magha":            {"quality": "mixed",         "nature": "fierce", "suitable": ["ancestor rites", "coronation", "authority"]},
    "Purva Phalguni":   {"quality": "auspicious",   "nature": "fierce", "suitable": ["pleasure", "romance", "arts"]},
    "Uttara Phalguni":  {"quality": "auspicious",   "nature": "fixed",  "suitable": ["marriage", "long-term ventures", "charity"]},
    "Hasta":            {"quality": "highly_auspicious", "nature": "light", "suitable": ["crafts", "healing", "trade", "travel"]},
    "Chitra":           {"quality": "auspicious",   "nature": "soft",   "suitable": ["art", "architecture", "new clothes"]},
    "Swati":            {"quality": "auspicious",   "nature": "movable","suitable": ["trade", "travel", "learning"]},
    "Vishakha":         {"quality": "mixed",         "nature": "mixed",  "suitable": ["goal-setting", "fire rituals"]},
    "Anuradha":         {"quality": "auspicious",   "nature": "soft",   "suitable": ["friendship", "travel", "worship"]},
    "Jyeshtha":         {"quality": "mixed",         "nature": "sharp",  "suitable": ["leadership decisions", "harsh tasks"]},
    "Mula":             {"quality": "inauspicious",  "nature": "fierce", "suitable": ["research into foundations", "gardening"]},
    "Purva Ashadha":    {"quality": "mixed",         "nature": "fierce", "suitable": ["aggressive actions", "debates"]},
    "Uttara Ashadha":   {"quality": "auspicious",   "nature": "fixed",  "suitable": ["long-term projects", "stable ventures"]},
    "Shravana":         {"quality": "auspicious",   "nature": "movable","suitable": ["learning", "listening", "worship of Vishnu"]},
    "Dhanishtha":       {"quality": "auspicious",   "nature": "movable","suitable": ["music", "wealth ventures", "construction"]},
    "Shatabhisha":      {"quality": "mixed",         "nature": "movable","suitable": ["healing", "astrology", "meditation"]},
    "Purva Bhadrapada": {"quality": "mixed",         "nature": "fierce", "suitable": ["intense spiritual practice"]},
    "Uttara Bhadrapada":{"quality": "auspicious",   "nature": "fixed",  "suitable": ["stable work", "teaching", "charity"]},
    "Revati":           {"quality": "auspicious",   "nature": "soft",   "suitable": ["completion of journeys", "final rites", "gifts"]},
}

# Yoga quality (27 yogas)
_YOGA_QUALITY = {
    "Vishkumbha": "inauspicious", "Priti": "auspicious", "Ayushman": "auspicious",
    "Saubhagya": "auspicious", "Shobhana": "auspicious", "Atiganda": "inauspicious",
    "Sukarma": "auspicious", "Dhriti": "auspicious", "Shoola": "inauspicious",
    "Ganda": "inauspicious", "Vriddhi": "auspicious", "Dhruva": "auspicious",
    "Vyaghata": "inauspicious", "Harshana": "auspicious", "Vajra": "inauspicious",
    "Siddhi": "auspicious", "Vyatipata": "inauspicious", "Variyan": "auspicious",
    "Parigha": "inauspicious", "Shiva": "auspicious", "Siddha": "auspicious",
    "Sadhya": "auspicious", "Shubha": "auspicious", "Shukla": "auspicious",
    "Brahma": "auspicious", "Mahendra": "auspicious", "Vaidhriti": "inauspicious",
}


def get_rule_based_enrichment(panchang: dict) -> dict:
    """Build rule-based cultural context from panchang data."""
    tithi_idx_raw = panchang.get("tithi", {}).get("num", 1) - 1
    tithi_idx = min(max(tithi_idx_raw, 0), 29)
    # Adjust for krishna paksha (tithis 16-30 in 0-based are index 15-29)
    paksha = panchang.get("paksha", {}).get("en", "Shukla")
    if paksha == "Krishna":
        tithi_idx = 15 + (tithi_idx % 15)

    deity_info = _TITHI_DEITIES[tithi_idx] if tithi_idx < len(_TITHI_DEITIES) else {}

    vara_en = panchang.get("vara", {}).get("en", "")
    vara_info = _VARA_SIGNIFICANCE.get(vara_en, {})

    nakshatra_en = panchang.get("nakshatra", {}).get("en", "")
    nakshatra_info = _NAKSHATRA_QUALITY.get(nakshatra_en, {})

    yoga_en = panchang.get("yoga", {}).get("en", "")
    yoga_quality = _YOGA_QUALITY.get(yoga_en, "neutral")

    return {
        "tithi_deity": deity_info,
        "vara_info": vara_info,
        "nakshatra_character": nakshatra_info,
        "yoga_quality": yoga_quality,
    }


# ---------------------------------------------------------------------------
# Claude AI enrichment
# ---------------------------------------------------------------------------

def _get_claude_client():
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        return anthropic.Anthropic(api_key=api_key)
    except ImportError:
        logger.warning("anthropic package not installed. Run: pip install anthropic")
        return None


_ENRICHMENT_PROMPT = """You are a deeply knowledgeable Odia cultural scholar and Jagannath temple tradition expert.

CRITICAL INSTRUCTIONS:
- Provide ONLY authentic, verifiable information from standard Odia Panchangs (Kohinoor, Biraja, Drik Panchang)
- DO NOT fabricate or invent spiritual descriptions, rituals, or temple practices
- DO NOT make claims about special powers, cosmic energies, or divine attributes unless they are well-documented
- If you don't know specific temple practices for this day, provide general authentic guidance instead
- Keep all information simple, factual, and based on traditional Odia/Hindu practices

Provide cultural enrichment for this panchang day in Odisha:
- Date: {date} ({vara}, {paksha} {tithi_num} {tithi})
- Nakshatra: {nakshatra} | Yoga: {yoga} ({yoga_quality})
- Chandra Masa: {chandra_masa} | Soura Masa: {soura_masa}
- Special Day: {special_day_type} — {special_day_significance}
- Tithi deity: {tithi_deity} | Day deity: {vara_deity}
- Festivals today: {festivals}
- Special yogas: {special_yogas}

Respond ONLY with this JSON (keep all text concise, factual, under 50 words per field):
{{
  "jagannath_significance": {{"en": "...", "or": "ଓଡ଼ିଆ..."}},
  "biraja_significance": {{"en": "...", "or": "ଓଡ଼ିଆ..."}},
  "fasting_guidance": {{
    "recommended": true/false,
    "vrat_name": "...", "vrat_name_or": "ଓଡ଼ିଆ...",
    "description": "...", "description_or": "ଓଡ଼ିଆ..."
  }},
  "auspicious_activities": ["...", "...", "..."],
  "activities_to_avoid": ["...", "..."],
  "odia_proverb": {{"text": "...", "text_or": "ଓଡ଼ିଆ...", "meaning": "..."}},
  "seasonal_context": {{"en": "...", "or": "ଓଡ଼ିଆ..."}},
  "household_guidance": {{"en": "...", "or": "ଓଡ଼ିଆ..."}}
}}\
"""


def enrich_with_claude(panchang: dict, layer1_result: dict) -> dict:
    """
    Layer 2: Use Claude to provide deep Odia cultural enrichment.
    Falls back to rule-based enrichment if Claude is unavailable.
    """
    rule_based = get_rule_based_enrichment(panchang)

    # Build fallback from rule-based data
    vara_info = rule_based.get("vara_info", {})
    nakshatra_info = rule_based.get("nakshatra_character", {})
    tithi_deity = rule_based.get("tithi_deity", {})

    fallback = {
        "jagannath_significance": {
            "en": vara_info.get("jagannath_note", "Visit Jagannath temple for darshan and prasad."),
            "or": "",
        },
        "biraja_significance": {
            "en": "Offer prayers at Biraja Devi temple in Jajpur for blessings.",
            "or": "",
        },
        "fasting_guidance": {
            "recommended": layer1_result.get("special_day_type") in ("ekadashi", "amavasya", "purnima", "pradosha"),
            "vrat_name": vara_info.get("fasting", ""),
            "vrat_name_or": "",
            "description": layer1_result.get("special_day_significance", vara_info.get("fasting", "")),
            "description_or": "",
        },
        "auspicious_activities": nakshatra_info.get("suitable", []),
        "activities_to_avoid": vara_info.get("avoid", []),
        "odia_proverb": {"text": "", "text_or": "", "meaning": ""},
        "seasonal_context": {"en": "", "or": ""},
        "household_guidance": {
            "en": f"Today is presided over by {tithi_deity.get('deity', 'divine forces')}. Offer prayers with devotion.",
            "or": "",
        },
        "rule_based": rule_based,
    }

    client = _get_claude_client()
    if not client:
        return fallback

    try:
        prompt = _ENRICHMENT_PROMPT.format(
            date=panchang.get("date", ""),
            vara=panchang.get("vara", {}).get("en", ""),
            paksha=panchang.get("paksha", {}).get("en", ""),
            tithi_num=panchang.get("tithi", {}).get("num", ""),
            tithi=panchang.get("tithi", {}).get("en", ""),
            nakshatra=panchang.get("nakshatra", {}).get("en", ""),
            yoga=panchang.get("yoga", {}).get("en", ""),
            yoga_quality=rule_based.get("yoga_quality", "neutral"),
            chandra_masa=panchang.get("chandra_masa", {}).get("en", ""),
            soura_masa=panchang.get("soura_masa", {}).get("en", ""),
            special_day_type=layer1_result.get("special_day_type", "normal"),
            special_day_significance=layer1_result.get("special_day_significance", ""),
            tithi_deity=tithi_deity.get("deity", ""),
            vara_deity=vara_info.get("deity", ""),
            festivals=", ".join(f.get("name", {}).get("en", "") for f in panchang.get("festivals", [])) or "none",
            special_yogas=", ".join(y.get("name", "") for y in layer1_result.get("special_yogas", [])) or "none",
        )
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        # Extract JSON from response (handle markdown code blocks)
        if "```" in text:
            parts = text.split("```")
            text = parts[1] if len(parts) > 1 else parts[0]
            if text.startswith("json"):
                text = text[4:].strip()
        # Repair truncated JSON by finding last complete field
        try:
            ai_data = json.loads(text)
        except json.JSONDecodeError:
            # Try to salvage partial JSON by truncating at last complete key-value
            last_brace = text.rfind("},")
            if last_brace > 0:
                text = text[:last_brace + 1] + "}"
            ai_data = json.loads(text)
        ai_data["rule_based"] = rule_based  # always include rule-based context
        return ai_data
    except Exception as e:
        logger.warning(f"Claude enrichment failed: {e}")
        return fallback
