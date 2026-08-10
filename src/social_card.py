"""
Generate a daily Odia Panjika share card (PNG) for Instagram / Facebook.
Uses system Noto Sans Oriya when available.
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

_CARD_DIR = Path("static/social/cards")
_FONT_CANDIDATES = [
    Path("/usr/share/fonts/truetype/noto/NotoSansOriya-Regular.ttf"),
    Path("/usr/share/fonts/truetype/noto/NotoSansOriya-Bold.ttf"),
    Path("assets/fonts/NotoSansOriya-Regular.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]


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
    d = date.fromisoformat(panchang["date"])
    months = [
        "ଜାନୁଆରୀ", "ଫେବ୍ରୁଆରୀ", "ମାର୍ଚ୍ଚ", "ଏପ୍ରିଲ", "ମଇ", "ଜୁନ",
        "ଜୁଲାଇ", "ଅଗଷ୍ଟ", "ସେପ୍ଟେମ୍ବର", "ଅକ୍ଟୋବର", "ନଭେମ୍ବର", "ଡିସେମ୍ବର",
    ]
    date_or = f"{d.day} {months[d.month - 1]} {d.year}"
    lines = [
        "ଜୟ ଜଗନ୍ନାଥ",
        "ଓଡ଼ିଆ ପଞ୍ଜିକା",
        date_or,
        f"{panchang['chandra_masa']['or']} {panchang['paksha']['or']} {panchang['tithi']['or']}",
        f"{panchang['nakshatra']['or']} · {panchang['vara']['or']}",
        f"ଯୋଗ: {panchang['yoga']['or']}",
    ]
    fests = panchang.get("festivals") or []
    if fests:
        names = " · ".join(
            (f.get("name") or {}).get("or") or f.get("name_or") or ""
            for f in fests[:2]
        )
        if names.strip(" ·"):
            lines.append(names)
    sr, ss = panchang.get("sunrise") or "", panchang.get("sunset") or ""
    if sr and ss:
        lines.append(f"ସୂର୍ଯ୍ୟୋଦୟ {sr} · ଅସ୍ତ {ss}")
    rahu = ""
    if enrichment:
        rahu = (enrichment.get("astronomical") or {}).get("muhurtas", {}).get(
            "rahu_kalam", ""
        )
    if rahu:
        lines.append(f"ରାହୁ କାଳ {rahu}")
    lines.append("odiapanjika · free panji")
    return lines


def generate_daily_card(
    panchang: dict,
    enrichment: dict | None = None,
    *,
    out_dir: Path | None = None,
) -> Path:
    """
    Render a 1080×1350 portrait card (IG-friendly 4:5).
    Returns local filesystem path under static/social/cards/.
    """
    from PIL import Image, ImageDraw

    out_dir = out_dir or _CARD_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    day = panchang.get("date") or date.today().isoformat()
    out_path = out_dir / f"panjika_{day}.png"

    W, H = 1080, 1350
    # Deep temple-inspired gradient base
    img = Image.new("RGB", (W, H), (18, 32, 56))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(18 + (120 - 18) * t * 0.35)
        g = int(32 + (40 - 32) * t)
        b = int(56 + (20 - 56) * t * 0.2)
        # saffron wash toward bottom
        r2 = int(r + (180 - r) * (t**2) * 0.45)
        g2 = int(g + (90 - g) * (t**2) * 0.35)
        draw.line([(0, y), (W, y)], fill=(r2, g2, b))

    # Gold frame
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

    title_font = _find_font(64)
    body_font = _find_font(42)
    small_font = _find_font(32)

    lines = _line(panchang, enrichment)
    y = 160
    for i, text in enumerate(lines):
        font = title_font if i < 2 else (small_font if i == len(lines) - 1 else body_font)
        # center text
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        color = (255, 220, 140) if i < 2 else (250, 245, 235)
        if i == len(lines) - 1:
            color = (200, 180, 120)
        draw.text((x, y), text, font=font, fill=color)
        y += (bbox[3] - bbox[1]) + (36 if i < 2 else 28)

    img.save(out_path, format="PNG", optimize=True)
    logger.info("[SocialCard] wrote %s", out_path)
    return out_path


def public_card_url(local_path: Path, public_base: str | None = None) -> str:
    """Map static path to public URL for Instagram Graph API."""
    import os

    base = (public_base or os.getenv("PUBLIC_API_URL") or "").rstrip("/")
    # Prefer path relative to static/
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
