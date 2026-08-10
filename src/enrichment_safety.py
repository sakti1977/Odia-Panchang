"""
Safety helpers for AI enrichment layers (issue #25).

- Denylist scan against curated phrases (and enrichment text)
- Strip empty Odia fields rather than ship blank `or`
- Mark enrichment as non-authoritative
- Never allow LLM output to rewrite base panji fields (caller enforces)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_DENYLIST_PATH = _ROOT / "tests" / "fixtures" / "denylist_phrases.txt"

# Minimal Odia placeholders when rule-based EN exists but OR was empty
_OR_GENERIC = "ପାରମ୍ପରିକ ଓଡ଼ିଆ ପାଞ୍ଜି ଅନୁସାରେ ଆଜି ଭକ୍ତି ଓ ସାବଧାନତାର ସହିତ ଦିନ ପାଳନ କରନ୍ତୁ।"
_OR_JAGANNATH = "ଶ୍ରୀଜଗନ୍ନାଥ ମନ୍ଦିରରେ ଦର୍ଶନ ଓ ପ୍ରସାଦ ଗ୍ରହଣ କରିବା ଶୁଭ।"
_OR_BIRAJA = "ଯାଜପୁର ବିରଜା ଦେବୀ ପୀଠରେ ପ୍ରାର୍ଥନା କରିବା ଶୁଭ (ନିୟମ-ମାତ୍ର ସୂଚନା)।"


def load_denylist() -> list[str]:
    if not _DENYLIST_PATH.is_file():
        return [
            "mahakashiya shakti",
            "guaranteed cosmic energy",
            "devadasis perform abhishek",
            "official biraja ephemeris",
            "official khadiratna reprint",
        ]
    return [
        ln.strip()
        for ln in _DENYLIST_PATH.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]


def text_hits_denylist(text: str, phrases: list[str] | None = None) -> list[str]:
    if not text:
        return []
    blob = text.lower()
    phrases = phrases if phrases is not None else load_denylist()
    return [p for p in phrases if p.lower() in blob]


def _scrub_string(s: str, phrases: list[str]) -> tuple[str, bool]:
    """Return (text, redacted?) — blank if denylist hit."""
    hits = text_hits_denylist(s, phrases)
    if hits:
        return "", True
    return s, False


def _walk_scrub(obj: Any, phrases: list[str], hits: list[str]) -> Any:
    if isinstance(obj, dict):
        return {k: _walk_scrub(v, phrases, hits) for k, v in obj.items()}
    if isinstance(obj, list):
        out = []
        for item in obj:
            scrubbed = _walk_scrub(item, phrases, hits)
            if scrubbed == "" and isinstance(item, str):
                continue
            out.append(scrubbed)
        return out
    if isinstance(obj, str):
        cleaned, redacted = _scrub_string(obj, phrases)
        if redacted:
            hits.append(obj[:80])
        return cleaned
    return obj


def omit_empty_or_fields(obj: Any) -> Any:
    """Drop bilingual pairs where `or` is empty; drop empty strings in general."""
    if isinstance(obj, dict):
        # Bilingual en/or pair
        if "en" in obj and "or" in obj and isinstance(obj.get("or"), str):
            new = {k: omit_empty_or_fields(v) for k, v in obj.items() if k != "or" or (obj.get("or") or "").strip()}
            if "or" in obj and not (obj.get("or") or "").strip():
                new.pop("or", None)
            return new
        return {k: omit_empty_or_fields(v) for k, v in obj.items() if v not in ("", None, [], {})}
    if isinstance(obj, list):
        return [omit_empty_or_fields(x) for x in obj if x not in ("", None, [], {})]
    return obj


def fill_rule_based_odia(cultural: dict) -> dict:
    """Ensure common bilingual keys have non-empty Odia when English is present."""
    c = dict(cultural)

    def ensure_pair(key: str, or_default: str) -> None:
        val = c.get(key)
        if not isinstance(val, dict):
            return
        en = (val.get("en") or "").strip()
        or_t = (val.get("or") or "").strip()
        if en and not or_t:
            val = {**val, "or": or_default}
            c[key] = val

    ensure_pair("jagannath_significance", _OR_JAGANNATH)
    ensure_pair("biraja_significance", _OR_BIRAJA)
    ensure_pair("household_guidance", _OR_GENERIC)
    ensure_pair("seasonal_context", _OR_GENERIC)

    fg = c.get("fasting_guidance")
    if isinstance(fg, dict):
        if (fg.get("description") or "").strip() and not (fg.get("description_or") or "").strip():
            fg = {**fg, "description_or": _OR_GENERIC}
            c["fasting_guidance"] = fg

    return c


def sanitize_enrichment(enrichment: dict) -> dict:
    """
    Apply denylist + Odia fill + empty-or omit + non-authoritative flag.
    """
    phrases = load_denylist()
    hits: list[str] = []
    scrubbed = _walk_scrub(enrichment, phrases, hits)
    if not isinstance(scrubbed, dict):
        scrubbed = {}

    cultural = scrubbed.get("cultural")
    if isinstance(cultural, dict):
        scrubbed["cultural"] = omit_empty_or_fields(fill_rule_based_odia(cultural))

    astronomical = scrubbed.get("astronomical")
    if isinstance(astronomical, dict):
        scrubbed["astronomical"] = omit_empty_or_fields(astronomical)

    scrubbed["non_authoritative"] = True
    scrubbed["note"] = (
        "Enrichment is advisory cultural context only. "
        "It must not change base tithi/masa/nakshatra. "
        "Not a temple authority or commercial panjika reprint."
    )
    if hits:
        scrubbed["denylist_redactions"] = len(hits)
    return scrubbed
