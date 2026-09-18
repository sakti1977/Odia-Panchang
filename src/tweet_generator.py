"""
Tweet / social caption generator for Odia Panjika daily posts.

Twitter/X: ≤280 chars main tweet + thread.
Facebook + Instagram: one caption capped at Instagram's 2200 characters.
"""

from datetime import date
import logging

logger = logging.getLogger(__name__)

# Instagram caption hard limit. Facebook allows more; we cap at Instagram
# so the same caption can go to both platforms.
CAPTION_MAX_LEN = 2200

# Hashtags — using Panjika (ପଞ୍ଜିକା), not Panchang
_BASE_TAGS = "#OdiaPanjika #Jagannath #Odisha"
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
    Generate the main tweet (≤280 characters) — in Odia script, starting with Jai Jagannath.
    Format:
        🙏 ଜୟ ଜଗନ୍ନାଥ 🙏
        {emoji} ଓଡ଼ିଆ ପଞ୍ଜିକା | {date_or}
        📅 {chandra_or} {paksha_or} {tithi_or}
        ⭐ {nakshatra_or} ନକ୍ଷତ୍ର | {vara_or}
        🎉 {festivals_or}   ← only if any
        ⏰ ରାହୁ କାଳ: {rahu_kalam}
        #tags
    """
    d = date.fromisoformat(panchang["date"])
    # Odia date format
    _OR_MONTHS = ["ଜାନୁଆରୀ","ଫେବ୍ରୁଆରୀ","ମାର୍ଚ୍ଚ","ଏପ୍ରିଲ","ମଇ","ଜୁନ","ଜୁଲାଇ","ଅଗଷ୍ଟ","ସେପ୍ଟେମ୍ବର","ଅକ୍ଟୋବର","ନଭେମ୍ବର","ଡିସେମ୍ବର"]
    date_or = f"{d.day} {_OR_MONTHS[d.month-1]} {d.year}"

    tithi_or    = panchang["tithi"]["or"]
    nakshatra_or= panchang["nakshatra"]["or"]
    chandra_or  = panchang["chandra_masa"]["or"]
    paksha_or   = panchang["paksha"]["or"]
    vara_or     = panchang["vara"]["or"]
    yoga_or     = panchang["yoga"]["or"]

    astro = enrichment.get("astronomical", {}) if enrichment else {}
    special_day = astro.get("special_day_type", "normal")
    muhurtas = astro.get("muhurtas", {})
    rahu = muhurtas.get("rahu_kalam", "")
    abhijit = muhurtas.get("abhijit_muhurta", "")

    emoji = _SPECIAL_EMOJIS.get(special_day, "🌸")
    festivals = panchang.get("festivals", [])
    fest_or = " | ".join(f["name"]["or"] for f in festivals) if festivals else ""
    fest_tags = _festival_hashtags(festivals)

    # Optional place line (meta.city or city key)
    place = ""
    meta = panchang.get("meta") or {}
    city_key = meta.get("city") or panchang.get("city") or ""
    if isinstance(city_key, str) and city_key.strip():
        place = city_key.strip().replace("_", " ").title()

    lines = [
        "🙏 ଜୟ ଜଗନ୍ନାଥ 🙏",
        f"{emoji} ଓଡ଼ିଆ ପଞ୍ଜିକା | {date_or}",
        f"📅 {chandra_or} {paksha_or} {tithi_or}",
        f"⭐ {nakshatra_or} | {vara_or} | {yoga_or} ଯୋଗ",
    ]
    if place:
        lines.append(f"📍 {place}")
    if fest_or:
        lines.append(f"🎉 {fest_or}")
    # Sunrise / Sunset
    sunrise = panchang.get("sunrise", "")
    sunset  = panchang.get("sunset", "")
    if sunrise and sunset:
        lines.append(f"🌅 ସୂର୍ଯ୍ୟୋଦୟ {sunrise} | 🌇 ଅସ୍ତ {sunset}")
    if rahu:
        lines.append(f"⏰ ରାହୁ କାଳ: {rahu}")
    if abhijit:
        lines.append(f"✨ ଅଭିଜିତ: {abhijit}")

    # Build hashtags
    all_tags = _BASE_TAGS
    if fest_tags:
        all_tags += " " + fest_tags

    tweet = "\n".join(lines) + "\n" + all_tags

    # Trim to 280 chars if needed (drop least important lines first)
    if len(tweet) > 280:
        lines = [l for l in lines if "ଅଭିଜିତ" not in l]
        tweet = "\n".join(lines) + "\n" + all_tags
    if len(tweet) > 280:
        lines = [l for l in lines if "ରାହୁ" not in l]
        tweet = "\n".join(lines) + "\n" + all_tags
    if len(tweet) > 280:
        lines = [l for l in lines if "ସୂର୍ଯ୍ୟୋଦୟ" not in l]
        tweet = "\n".join(lines) + "\n" + all_tags
    if len(tweet) > 280:
        lines = [l for l in lines if "ଯୋଗ" not in l]
        tweet = "\n".join(lines) + "\n" + all_tags
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."

    return tweet


def _one_line_story(festival: dict, prefer_or: bool = True, max_len: int = 160) -> str:
    """
    One-line story blurb for tweets from curated festival story fields.
    Prefer Odia; fall back to English. Truncate cleanly.
    """
    story = festival.get("story") or {}
    why = festival.get("why_today") or {}
    text = ""
    if prefer_or:
        text = (story.get("or") or why.get("or") or story.get("en") or why.get("en") or "").strip()
    else:
        text = (story.get("en") or why.get("en") or story.get("or") or why.get("or") or "").strip()
    if not text:
        # Fallback: short description
        text = (festival.get("description") or "").strip()
    if not text:
        return ""
    # Collapse whitespace / newlines for tweet line
    text = " ".join(text.split())
    if len(text) > max_len:
        cut = text[: max_len - 1]
        # avoid mid-word when possible
        if " " in cut:
            cut = cut.rsplit(" ", 1)[0]
        text = cut + "…"
    return text


def generate_thread_tweet(panchang: dict, enrichment: dict | None = None) -> str:
    """
    Generate thread reply (2nd tweet): festival story first, then optional AI cultural notes.
    Festival stories work even when enrichment is empty.
    """
    enrichment = enrichment or {}
    cultural = enrichment.get("cultural", {}) or {}

    parts = []

    # Curated festival stories (priority — accuracy over AI)
    festivals = panchang.get("festivals") or []
    for f in festivals[:2]:  # at most two festivals to keep under 280
        name_or = (f.get("name") or {}).get("or") or (f.get("name") or {}).get("en") or ""
        blurb = _one_line_story(f, prefer_or=True, max_len=140)
        if blurb:
            if name_or:
                parts.append(f"🎉 {name_or}\n{blurb}")
            else:
                parts.append(f"🎉 {blurb}")

    # Jagannath significance in Odia
    jagannath_or = cultural.get("jagannath_significance", {}).get("or", "")
    jagannath_en = cultural.get("jagannath_significance", {}).get("en", "")
    if jagannath_or:
        parts.append(f"🛕 {jagannath_or}")
    elif jagannath_en:
        parts.append(f"🛕 {jagannath_en}")

    # Fasting in Odia
    fasting = cultural.get("fasting_guidance", {})
    if fasting.get("recommended"):
        desc_or = fasting.get("description_or", "")
        desc_en = fasting.get("description", "")
        desc = desc_or or desc_en
        if desc:
            parts.append(f"🍃 {desc}")

    # Odia proverb
    proverb_or = cultural.get("odia_proverb", {}).get("text_or", "")
    if proverb_or:
        parts.append(f"📜 {proverb_or}")

    # Household guidance in Odia
    guidance_or = cultural.get("household_guidance", {}).get("or", "")
    if guidance_or and not proverb_or:
        parts.append(f"🙏 {guidance_or}")

    # Build thread by adding parts one-by-one; stop before exceeding 280 chars
    # so the tweet never ends mid-sentence.
    thread = ""
    for part in parts:
        candidate = (thread + "\n\n" + part).lstrip("\n") if thread else part
        if len(candidate) <= 280:
            thread = candidate
        else:
            break
    return thread


def _truncate_at_word_boundary(text: str, max_len: int, min_keep: int = 20) -> str:
    """Hard cap at max_len, breaking at the last space. Ellipsis counts in budget."""
    if len(text) <= max_len:
        return text
    ellipsis = "…"
    if max_len <= len(ellipsis):
        return text[:max_len]
    truncated = text[: max_len - len(ellipsis)]
    last_space = truncated.rfind(" ")
    if last_space > min_keep:
        truncated = truncated[:last_space]
    return truncated + ellipsis


def _fit_hashtags(hashtags: str, budget: int) -> str:
    if not hashtags or budget <= 0:
        return ""
    if len(hashtags) <= budget:
        return hashtags
    fitted: list[str] = []
    used = 0
    for tag in hashtags.split():
        extra = len(tag) + (1 if fitted else 0)
        if used + extra > budget:
            break
        fitted.append(tag)
        used += extra
    return " ".join(fitted)


def _odia_civil_date(panchang: dict) -> str:
    d = date.fromisoformat(panchang["date"])
    months = [
        "ଜାନୁଆରୀ", "ଫେବ୍ରୁଆରୀ", "ମାର୍ଚ୍ଚ", "ଏପ୍ରିଲ", "ମଇ", "ଜୁନ",
        "ଜୁଲାଇ", "ଅଗଷ୍ଟ", "ସେପ୍ଟେମ୍ବର", "ଅକ୍ଟୋବର", "ନଭେମ୍ବର", "ଡିସେମ୍ବର",
    ]
    return f"{d.day} {months[d.month - 1]} {d.year}"


def _with_festival_stories(panchang: dict) -> dict:
    festivals = panchang.get("festivals") or []
    if not festivals:
        return panchang
    from src.festival_stories import attach_story

    enriched_fests = []
    for f in festivals:
        row = dict(f)
        if "name_en" not in row and isinstance(row.get("name"), dict):
            row["name_en"] = row["name"].get("en", "")
            row["name_or"] = row["name"].get("or", "")
        if not row.get("story"):
            row = attach_story(row)
            if "name" not in row or not isinstance(row.get("name"), dict):
                row["name"] = {
                    "en": row.get("name_en", ""),
                    "or": row.get("name_or", ""),
                }
        enriched_fests.append(row)
    return {**panchang, "festivals": enriched_fests}


def caption_fingerprint(text: str) -> str:
    """Date-bearing header used to detect a duplicate day's post."""
    for line in (text or "").split("\n"):
        if "ଓଡ଼ିଆ ପଞ୍ଜିକା" in line:
            return line.strip()
    return (text or "").split("\n", 1)[0].strip()


def generate_social_caption(
    panchang: dict,
    enrichment: dict | None = None,
    *,
    max_len: int = CAPTION_MAX_LEN,
) -> str:
    """
    Facebook Page + Instagram caption (≤ max_len, Instagram's 2200).

    Core panji lines always come from the panchang dict, never from Layer 2.
    Festival stories are curated (`festival_stories.py`). Hashtags lose first
    if the budget is tight.
    """
    panchang = _with_festival_stories(panchang)
    enrichment = enrichment or {}
    date_or = _odia_civil_date(panchang)
    astro = enrichment.get("astronomical") or {}
    special_day = astro.get("special_day_type", "normal")
    emoji = _SPECIAL_EMOJIS.get(special_day, "🌸")
    muhurtas = astro.get("muhurtas") or {}
    cultural = enrichment.get("cultural") or {}

    tithi_or = panchang["tithi"]["or"]
    nakshatra_or = panchang["nakshatra"]["or"]
    chandra_or = panchang["chandra_masa"]["or"]
    paksha_or = panchang["paksha"]["or"]
    vara_or = panchang["vara"]["or"]
    yoga_or = panchang["yoga"]["or"]

    place = ""
    meta = panchang.get("meta") or {}
    city_key = meta.get("city") or panchang.get("city") or ""
    if isinstance(city_key, str) and city_key.strip():
        place = city_key.strip().replace("_", " ").title()

    header_lines = [
        "🙏 ଜୟ ଜଗନ୍ନାଥ 🙏",
        f"{emoji} ଓଡ଼ିଆ ପଞ୍ଜିକା | {date_or}",
        f"{vara_or} | {chandra_or} {paksha_or} {tithi_or}",
        f"ନକ୍ଷତ୍ର {nakshatra_or}",
        f"ଯୋଗ {yoga_or}",
    ]
    if place:
        header_lines.append(f"📍 {place}")
    sunrise = panchang.get("sunrise") or ""
    sunset = panchang.get("sunset") or ""
    if sunrise and sunset:
        header_lines.append(f"🌅 ସୂର୍ଯ୍ୟୋଦୟ {sunrise} / ଅସ୍ତ {sunset}")

    blocks: list[str] = ["\n".join(header_lines)]

    muhurta_lines = []
    rahu = muhurtas.get("rahu_kalam") or ""
    abhijit = muhurtas.get("abhijit_muhurta") or ""
    if rahu:
        muhurta_lines.append(f"ରାହୁ କାଳ: {rahu}")
    if abhijit:
        muhurta_lines.append(f"ଅଭିଜିତ (ଶୁଭ): {abhijit}")
    if muhurta_lines:
        blocks.append("\n".join(muhurta_lines))

    for f in panchang.get("festivals") or []:
        name_or = (f.get("name") or {}).get("or") or f.get("name_or") or ""
        story = f.get("story") or {}
        why = f.get("why_today") or {}
        body = (story.get("or") or why.get("or") or story.get("en") or why.get("en") or "").strip()
        body = " ".join(body.split())
        if body:
            body = _truncate_at_word_boundary(body, 500)
        if name_or and body:
            blocks.append(f"🎉 {name_or}\n{body}")
        elif name_or:
            blocks.append(f"🎉 {name_or}")

    jagannath_or = (cultural.get("jagannath_significance") or {}).get("or", "")
    if jagannath_or:
        blocks.append(f"🛕 {jagannath_or.strip()}")
    fasting = cultural.get("fasting_guidance") or {}
    if fasting.get("recommended"):
        desc = (fasting.get("description_or") or fasting.get("description") or "").strip()
        if desc:
            blocks.append(f"🍃 {desc}")
    proverb_or = (cultural.get("odia_proverb") or {}).get("text_or", "")
    if proverb_or:
        blocks.append(f"📜 {proverb_or.strip()}")

    tags = _BASE_TAGS
    fest_tags = _festival_hashtags(panchang.get("festivals") or [])
    if fest_tags:
        tags = f"{tags} {fest_tags}"

    # Assemble: keep core panji; drop hashtags first, then cultural extras.
    def join(parts: list[str], hashtags: str) -> str:
        body = "\n\n".join(p for p in parts if p)
        if hashtags:
            return f"{body}\n\n{hashtags}"
        return body

    caption = join(blocks, tags)
    if len(caption) <= max_len:
        return caption

    leftover = max_len - len(join(blocks, "")) - 2
    fitted = _fit_hashtags(tags, leftover)
    caption = join(blocks, fitted)
    if len(caption) <= max_len:
        return caption

    # Drop optional cultural blocks from the end (keep header + muhurta + festivals)
    while len(caption) > max_len and len(blocks) > 2:
        blocks.pop()
        caption = join(blocks, "")
    if len(caption) > max_len:
        caption = _truncate_at_word_boundary(caption, max_len)
    return caption


def generate_tweet_bundle(panchang: dict, enrichment: dict | None = None) -> dict:
    """
    Returns both main tweet and thread reply, plus metadata.
    Thread includes festival stories when present (no enrichment required).
    """
    # Ensure festivals carry stories if only names/descriptions were loaded from DB
    festivals = panchang.get("festivals") or []
    if festivals:
        from src.festival_stories import attach_story

        enriched_fests = []
        for f in festivals:
            # Normalize ORM-style vs API-style
            if "name_en" not in f and isinstance(f.get("name"), dict):
                f = {
                    **f,
                    "name_en": f["name"].get("en", ""),
                    "name_or": f["name"].get("or", ""),
                }
            if not f.get("story"):
                f = attach_story(dict(f))
                # restore nested name for tweet formatting
                if "name" not in f or not isinstance(f.get("name"), dict):
                    f["name"] = {
                        "en": f.get("name_en", ""),
                        "or": f.get("name_or", ""),
                    }
            enriched_fests.append(f)
        panchang = {**panchang, "festivals": enriched_fests}

    main = generate_main_tweet(panchang, enrichment)
    thread = generate_thread_tweet(panchang, enrichment)

    return {
        "date": panchang["date"],
        "main_tweet": main,
        "main_tweet_length": len(main),
        "thread_reply": thread,
        "thread_reply_length": len(thread),
        "festivals": [
            (f.get("name") or {}).get("en") or f.get("name_en", "")
            for f in panchang.get("festivals", [])
        ],
    }
