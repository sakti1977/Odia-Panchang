"""
Daily Odia Panjika share cards for Facebook / Instagram.

Instagram feed accepts JPEG at 4:5 (1080×1350). Instagram Stories require
9:16 (1080×1920). Facebook Page photos accept the same 4:5 JPEG.
Uses system Noto Sans Oriya when available.
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

_CARD_DIR = Path("static/social/cards")
# Vendored Noto Sans Oriya (notofonts release, OFL) comes first: the older
# build shipped by Debian/Ubuntu fonts-noto-core mis-positions marks in
# clusters such as ନ୍ତୁ and reph over ତ୍ତ/ଣ୍ଣ (କାର୍ତ୍ତିକ, ପୂର୍ଣ୍ଣିମା).
_ASSET_FONTS = Path(__file__).resolve().parents[1] / "assets" / "fonts"
_FONT_CANDIDATES = [
    _ASSET_FONTS / "NotoSansOriya-Regular.ttf",
    Path("/usr/share/fonts/truetype/noto/NotoSansOriya-Regular.ttf"),
    Path("/usr/share/fonts/truetype/noto/NotoSansOriya-Bold.ttf"),
    Path("/usr/share/fonts/truetype/lohit-orya/Lohit-Odia.ttf"),
    Path("/usr/share/fonts/truetype/lohit-oriya/Lohit-Oriya.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]

IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1350
STORY_WIDTH = 1080
STORY_HEIGHT = 1920


def _find_font(size: int):
    from PIL import ImageFont

    for path in _FONT_CANDIDATES:
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def _line(panchang: dict, enrichment: dict | None = None) -> list[str]:
    """Card text lines. Odia script only — Noto Sans Oriya has no Latin
    glyphs and no U+00B7 (middot), so both must be avoided here or the
    rendered card shows a tofu box (□) instead of the character. Use the
    Odia danda (।, U+0964) as a separator; it is present in the font."""
    d = date.fromisoformat(panchang["date"])
    months = [
        "ଜାନୁଆରୀ", "ଫେବ୍ରୁଆରୀ", "ମାର୍ଚ୍ଚ", "ଏପ୍ରିଲ", "ମଇ", "ଜୁନ",
        "ଜୁଲାଇ", "ଅଗଷ୍ଟ", "ସେପ୍ଟେମ୍ବର", "ଅକ୍ଟୋବର", "ନଭେମ୍ବର", "ଡିସେମ୍ବର",
    ]
    date_or = f"{d.day} {months[d.month - 1]} {d.year}"

    from src.tweet_generator import format_end_time

    tithi_line = f"{panchang['chandra_masa']['or']} {panchang['paksha']['or']} {panchang['tithi']['or']}"
    tithi_end = format_end_time(panchang["tithi"].get("end_ts"), panchang["date"])
    if tithi_end:
        tithi_line += f" । {tithi_end}"

    nakshatra_line = f"{panchang['nakshatra']['or']} । {panchang['vara']['or']}"
    nakshatra_end = format_end_time(
        panchang["nakshatra"].get("end_ts"), panchang["date"]
    )
    if nakshatra_end:
        nakshatra_line += f" । {nakshatra_end}"

    lines = [
        "ଜୟ ଜଗନ୍ନାଥ",
        "ଓଡ଼ିଆ ପଞ୍ଜିକା",
        date_or,
        tithi_line,
        nakshatra_line,
        f"ଯୋଗ: {panchang['yoga']['or']}",
    ]
    fests = panchang.get("festivals") or []
    if fests:
        names = " । ".join(
            (f.get("name") or {}).get("or") or f.get("name_or") or ""
            for f in fests[:2]
        )
        if names.strip(" ।"):
            lines.append(names)
    sr, ss = panchang.get("sunrise") or "", panchang.get("sunset") or ""
    if sr and ss:
        lines.append(f"ସୂର୍ଯ୍ୟୋଦୟ {sr} । ଅସ୍ତ {ss}")
    rahu = ""
    if enrichment:
        rahu = (enrichment.get("astronomical") or {}).get("muhurtas", {}).get(
            "rahu_kalam", ""
        )
    if rahu:
        lines.append(f"ରାହୁ କାଳ {rahu}")
    lines.append("ମାଗଣା ଦୈନିକ ପଞ୍ଜିକା")
    return lines


def _paint_background(W: int, H: int):
    """Navy→maroon gradient with the double gold border shared by all cards."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (W, H), (18, 32, 56))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(18 + (120 - 18) * t * 0.35)
        g = int(32 + (40 - 32) * t)
        b = int(56 + (20 - 56) * t * 0.2)
        r2 = int(r + (180 - r) * (t**2) * 0.45)
        g2 = int(g + (90 - g) * (t**2) * 0.35)
        draw.line([(0, y), (W, y)], fill=(r2, g2, b))

    margin = 48
    draw.rounded_rectangle(
        [margin, margin, W - margin, H - margin],
        radius=36,
        outline=(212, 168, 75),
        width=4,
    )
    draw.rounded_rectangle(
        [margin + 14, margin + 14, W - margin - 14, H - margin - 14],
        radius=28,
        outline=(212, 168, 75),
        width=1,
    )
    return img, draw, margin


def _heritage_entry(panchang: dict) -> dict:
    from src.odisha_heritage import festival_names, heritage_for_date

    return heritage_for_date(panchang["date"], festival_names(panchang.get("festivals")))


def _paint_feed_card(panchang: dict, enrichment: dict | None = None):
    W, H = IMAGE_WIDTH, IMAGE_HEIGHT
    img, draw, margin = _paint_background(W, H)

    title_font = _find_font(64)
    body_font = _find_font(42)
    small_font = _find_font(32)

    lines = _line(panchang, enrichment)
    y = 160
    for i, text in enumerate(lines):
        font = title_font if i < 2 else (small_font if i == len(lines) - 1 else body_font)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        color = (255, 220, 140) if i < 2 else (250, 245, 235)
        if i == len(lines) - 1:
            color = (200, 180, 120)
        draw.text((x, y), text, font=font, fill=color)
        y += (bbox[3] - bbox[1]) + (36 if i < 2 else 28)

    _paint_heritage_panel(
        draw,
        _heritage_entry(panchang),
        top=max(y + 24, 900),
        bottom=H - margin - 36,
        left=margin + 40,
        right=W - margin - 40,
    )
    return img


def _wrap(draw, text: str, font, max_w: int, max_lines: int) -> list[str]:
    """Greedy word wrap by rendered width (Odia words are space separated)."""
    lines: list[str] = []
    cur = ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and draw.textlength(trial, font=font) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines[:max_lines]


def _fit_font(draw, text: str, size: int, max_w: int, min_size: int):
    font = _find_font(size)
    while size > min_size and draw.textlength(text, font=font) > max_w:
        size -= 2
        font = _find_font(size)
    return font


def _centered(draw, text: str, font, cx: int, y: int, color) -> int:
    """Draw text centred on cx; return the y just below it."""
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (bbox[2] - bbox[0]) // 2, y), text, font=font, fill=color)
    return y + (bbox[3] - bbox[1])


def _paint_heritage_panel(draw, entry: dict, *, top: int, bottom: int, left: int, right: int) -> None:
    """'ଜାଣନ୍ତୁ ଓଡ଼ିଶା' panel: series label, title, one-line hook.
    Odia script only — see _line docstring about glyphs missing from the font;
    odisha_heritage validates title_or/short_or against that at import."""
    from src.odisha_heritage import SERIES_OR, heritage_label_or

    draw.rounded_rectangle(
        [left, top, right, bottom],
        radius=24,
        fill=(34, 40, 62),
        outline=(212, 168, 75),
        width=2,
    )
    cx = (left + right) // 2
    max_w = right - left - 60

    y = top + 26
    label = f"{SERIES_OR} । {heritage_label_or(entry)}"
    y = _centered(draw, label, _fit_font(draw, label, 34, max_w, 24), cx, y, (255, 200, 110)) + 30
    title = entry["title"]["or"]
    y = _centered(draw, title, _fit_font(draw, title, 50, max_w, 30), cx, y, (255, 235, 190)) + 30
    body_font = _find_font(36)
    for text in _wrap(draw, entry["short_or"], body_font, max_w, 2):
        if y + 40 > bottom - 16:
            break
        y = _centered(draw, text, body_font, cx, y, (250, 245, 235)) + 20


HERITAGE_BODY_TOP = 520  # conservative: below series name, label, 2-line title
_BODY_SIZES = (40, 37, 34, 31)


def _heritage_body_layout(draw, body: str, max_w: int, height: int):
    """Largest font size at which the whole story fits; at the smallest size
    the tail is cut (tests assert no curated entry ever gets there)."""
    for size in _BODY_SIZES:
        font = _find_font(size)
        step = int(size * 1.6)
        lines = _wrap(draw, body, font, max_w, 99)
        if len(lines) * step <= height:
            return font, lines, step
    logger.warning("[SocialCard] heritage body truncated to fit the card")
    return font, lines[: max(1, height // step)], step


def _paint_heritage_card(panchang: dict):
    """Dedicated 4:5 'ଜାଣନ୍ତୁ ଓଡ଼ିଶା' card: the full Odia story, second image
    of the day's post. Odia script only (the body may carry quotes, commas,
    em dashes and digits — all present in the vendored font)."""
    from src.odisha_heritage import SERIES_OR, heritage_label_or, tomorrow_heritage

    entry = _heritage_entry(panchang)
    W, H = IMAGE_WIDTH, IMAGE_HEIGHT
    img, draw, margin = _paint_background(W, H)
    cx = W // 2
    max_w = W - 2 * (margin + 70)

    y = 140
    y = _centered(draw, SERIES_OR, _find_font(64), cx, y, (255, 220, 140)) + 30
    label = heritage_label_or(entry)
    y = _centered(draw, label, _find_font(36), cx, y, (255, 200, 110)) + 44
    title = entry["title"]["or"]
    y = _centered(draw, title, _fit_font(draw, title, 60, max_w, 36), cx, y, (255, 235, 190)) + 40
    draw.line([(cx - 140, y), (cx + 140, y)], fill=(212, 168, 75), width=2)
    y += 44

    footer_top = H - margin - 150
    font, lines, step = _heritage_body_layout(draw, entry["body"]["or"], max_w, footer_top - y)
    for text in lines:
        _centered(draw, text, font, cx, y, (250, 245, 235))
        y += step

    teaser = f"ଆସନ୍ତାକାଲି: {tomorrow_heritage(panchang['date'])['title']['or']}"
    _centered(draw, teaser, _fit_font(draw, teaser, 34, max_w, 24), cx, footer_top + 40, (255, 200, 110))
    _centered(draw, "ଓଡ଼ିଆ ପଞ୍ଜିକା", _find_font(30), cx, footer_top + 96, (200, 180, 120))
    return img


def generate_daily_card(
    panchang: dict,
    enrichment: dict | None = None,
    *,
    out_dir: Path | None = None,
) -> Path:
    """
    Render a 1080×1350 portrait JPEG (IG-friendly 4:5).
    Returns local filesystem path under static/social/cards/.
    """
    out_dir = out_dir or _CARD_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    day = panchang.get("date") or date.today().isoformat()
    out_path = out_dir / f"panjika_{day}.jpg"

    img = _paint_feed_card(panchang, enrichment)
    img.save(out_path, format="JPEG", quality=90, optimize=True)
    logger.info("[SocialCard] wrote %s", out_path)
    return out_path


_STORY_PROMPT = "ପ୍ରତିଦିନ ପଞ୍ଜିକା ଓ ଓଡ଼ିଶାର ନୂଆ କାହାଣୀ ପାଇଁ ଫଲୋ କରନ୍ତୁ"


def _pad_to_story(src: Path, out_path: Path) -> Path:
    """Pad a 4:5 card onto a 9:16 canvas for Instagram Stories, with a
    follow prompt in the bottom band (a story has no caption)."""
    from PIL import Image, ImageDraw

    canvas = Image.new("RGB", (STORY_WIDTH, STORY_HEIGHT), (18, 32, 56))
    with Image.open(src) as raw:
        card = raw.convert("RGB")
        card = card.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)
    top = (STORY_HEIGHT - IMAGE_HEIGHT) // 2
    canvas.paste(card, (0, top))

    draw = ImageDraw.Draw(canvas)
    font = _fit_font(draw, _STORY_PROMPT, 36, STORY_WIDTH - 120, 24)
    _centered(draw, _STORY_PROMPT, font, STORY_WIDTH // 2, top + IMAGE_HEIGHT + 40, (255, 200, 110))
    canvas.save(out_path, format="JPEG", quality=90, optimize=True)
    logger.info("[SocialCard] wrote story %s", out_path)
    return out_path


def generate_story_card(
    panchang: dict,
    enrichment: dict | None = None,
    *,
    feed_path: Path | None = None,
    out_dir: Path | None = None,
) -> Path:
    """9:16 Instagram Story version of the daily panji card."""
    out_dir = out_dir or _CARD_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    day = panchang.get("date") or date.today().isoformat()

    if feed_path is None or not Path(feed_path).is_file():
        feed_path = generate_daily_card(panchang, enrichment, out_dir=out_dir)
    return _pad_to_story(Path(feed_path), out_dir / f"panjika_{day}_story.jpg")


def generate_heritage_card(panchang: dict, *, out_dir: Path | None = None) -> Path:
    """4:5 'ଜାଣନ୍ତୁ ଓଡ଼ିଶା' card — second image of the Facebook post /
    Instagram carousel."""
    out_dir = out_dir or _CARD_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"panjika_{panchang['date']}_heritage.jpg"
    _paint_heritage_card(panchang).save(out_path, format="JPEG", quality=90, optimize=True)
    logger.info("[SocialCard] wrote %s", out_path)
    return out_path


def generate_heritage_story_card(
    panchang: dict,
    *,
    heritage_path: Path | None = None,
    out_dir: Path | None = None,
) -> Path:
    """9:16 Instagram Story version of the heritage card."""
    out_dir = out_dir or _CARD_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    if heritage_path is None or not Path(heritage_path).is_file():
        heritage_path = generate_heritage_card(panchang, out_dir=out_dir)
    return _pad_to_story(
        Path(heritage_path), out_dir / f"panjika_{panchang['date']}_heritage_story.jpg"
    )


def public_card_url(local_path: Path, public_base: str | None = None) -> str:
    """Map static path to public URL (preview only — Instagram ingest uses FB CDN)."""
    import os

    base = (public_base or os.getenv("PUBLIC_API_URL") or "").rstrip("/")
    s = str(local_path).replace("\\", "/")
    if "/static/" in s:
        rel = "static/" + s.split("/static/", 1)[1]
    elif s.startswith("static/"):
        rel = s
    else:
        rel = f"static/social/cards/{local_path.name}"
    if base:
        return f"{base}/{rel}"
    return f"/{rel}"
