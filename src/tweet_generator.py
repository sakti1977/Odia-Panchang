"""
Tweet generator for Odia Panchang daily posts.
Formats panchang data into Twitter/X-ready content (≤280 chars main tweet + thread).
"""

from datetime import date
import logging

logger = logging.getLogger(__name__)

# Hashtags
_BASE_TAGS = "#OdiaPanchang #Jagannath #Odisha"
_FESTIVAL_TAG_MAP = {
    "Rath Yatra":       "#RathYatra",
    "Snana Yatra":      "#SnanaYatra",
    "Diwali":           "#Diwali",
    "Durga Puja":       "#DurgaPuja",
    "Hanuman Jayanti":  "#HanumanJayanti",
    "Pana Sankranti":   "#PanaSankranti",
    "Kumar Purnima":    "#KumarPurnima",
    "Kartik Purnima":   "#KartikPurnima",
    "Buddha Purnima":   "#BuddhaPurnima",
    "Shivaratri":       "#Shivaratri",
    "Dola Purnima":     "#DolaPurnima #Holi",
    "Nuakhai":          "#Nuakhai",
}

# Special day emojis
_SPECIAL_EMOJIS = {
    "ekadashi":  "🌙",
    "purnima":   "🌕",
    "amavasya":  "🌑",
    "pradosha":  "🕉️",
    "chaturthi": "🐘",
    "normal":    "🌸",
}


def _festival_hashtags(festivals: list) -> str:
    tags = []
    for f in festivals:
        name = f.get("name", {}).get("en", "")
        tag = _FESTIVAL_TAG_MAP.get(name)
        if tag:
            tags.append(tag)
    return " ".join(tags)


def generate_main_tweet(panchang: dict, enrichment: dict | None = None) -> str:
    """
    Generate the main tweet (≤280 characters).
    Format:
        {emoji} Odia Panchang | {date}
        📅 {chandra_masa} {paksha} {tithi} ({tithi_or})
        ⭐ {nakshatra}
        🎉 {festivals}   ← only if any
        ⏰ Rahu Kalam: {rahu_kalam}
        ✨ Abhijit: {abhijit}
        🙏 ଜୟ ଜଗନ୍ନାଥ
        #tags
    """
    d = date.fromisoformat(panchang["date"])
    date_str = d.strftime("%-d %b %Y")  # e.g. "1 May 2026"

    tithi_en = panchang["tithi"]["en"]
    tithi_or = panchang["tithi"]["or"]
    nakshatra = panchang["nakshatra"]["en"]
    chandra = panchang["chandra_masa"]["en"]
    paksha = panchang["paksha"]["en"]
    vara = panchang["vara"]["en"]

    astro = enrichment.get("astronomical", {}) if enrichment else {}
    special_day = astro.get("special_day_type", "normal")
    muhurtas = astro.get("muhurtas", {})
    rahu = muhurtas.get("rahu_kalam", "")
    abhijit = muhurtas.get("abhijit_muhurta", "")

    emoji = _SPECIAL_EMOJIS.get(special_day, "🌸")
    festivals = panchang.get("festivals", [])
    fest_names = [f["name"]["en"] for f in festivals]
    fest_str = " | ".join(fest_names) if fest_names else ""
    fest_tags = _festival_hashtags(festivals)

    lines = [
        f"{emoji} Odia Panchang | {date_str}",
        f"📅 {chandra} {paksha} {tithi_en} ({tithi_or})",
        f"⭐ {nakshatra} Nakshatra | {vara}",
    ]
    if fest_str:
        lines.append(f"🎉 {fest_str}")
    if rahu:
        lines.append(f"⏰ Rahu Kalam: {rahu}")
    if abhijit:
        lines.append(f"✨ Abhijit: {abhijit}")
    lines.append("🙏 ଜୟ ଜଗନ୍ନାଥ")

    # Build hashtags
    all_tags = _BASE_TAGS
    if fest_tags:
        all_tags += " " + fest_tags

    tweet = "\n".join(lines) + "\n" + all_tags

    # Trim to 280 chars if needed
    if len(tweet) > 280:
        # Drop Abhijit line first
        lines = [l for l in lines if "Abhijit" not in l]
        tweet = "\n".join(lines) + "\n" + all_tags
    if len(tweet) > 280:
        # Drop Rahu line
        lines = [l for l in lines if "Rahu" not in l]
        tweet = "\n".join(lines) + "\n" + all_tags
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."

    return tweet


def generate_thread_tweet(panchang: dict, enrichment: dict | None = None) -> str:
    """
    Generate thread reply (2nd tweet) with cultural enrichment.
    """
    if not enrichment:
        return ""

    cultural = enrichment.get("cultural", {})
    astro = enrichment.get("astronomical", {})

    parts = []

    # Jagannath significance
    jagannath = cultural.get("jagannath_significance", {}).get("en", "")
    if jagannath:
        parts.append(f"🛕 {jagannath}")

    # Fasting
    fasting = cultural.get("fasting_guidance", {})
    if fasting.get("recommended"):
        desc = fasting.get("description", "")
        if desc:
            parts.append(f"🍃 {desc}")

    # Day energy from Groq
    energy = astro.get("day_energy", "")
    if energy:
        parts.append(f"🌟 {energy}")

    # Special yogas
    yogas = astro.get("special_yogas", [])
    if yogas:
        yoga_names = " | ".join(y["name"] for y in yogas[:2])
        parts.append(f"✅ {yoga_names}")

    # Proverb
    proverb_or = cultural.get("odia_proverb", {}).get("text_or", "")
    if proverb_or:
        parts.append(f"📜 {proverb_or}")

    thread = "\n\n".join(parts)
    if len(thread) > 280:
        thread = thread[:277] + "..."
    return thread


def generate_tweet_bundle(panchang: dict, enrichment: dict | None = None) -> dict:
    """
    Returns both main tweet and thread reply, plus metadata.
    """
    main = generate_main_tweet(panchang, enrichment)
    thread = generate_thread_tweet(panchang, enrichment) if enrichment else ""

    return {
        "date": panchang["date"],
        "main_tweet": main,
        "main_tweet_length": len(main),
        "thread_reply": thread,
        "thread_reply_length": len(thread),
        "festivals": [f["name"]["en"] for f in panchang.get("festivals", [])],
    }
