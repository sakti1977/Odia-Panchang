"""
Festival-date audit: our festival calendar vs an independent reference.

The reference is `tests/fixtures/festival_reference/drik_bhubaneswar.json`
(Drik Panchang, Bhubaneswar, Tier B — fetched by
`scripts/fetch_festival_reference.py`, deterministic HTML parse, committed).
It is *never* generated from our engine (eval.md: do not re-derive expected
values from the engine under test).

REFERENCE_MAP says, for each of our festival names, which reference event(s)
mark the same observance:

  primary     — the reference date(s) we must match exactly
  alternates  — reference events whose date is also acceptable
                (Smarta vs ISKCON Janmashtami, Gauna/Vaishnava Ekadashi)

Festivals that are not in REFERENCE_MAP are reported as `unverified` — they
are not silently assumed correct. Puri-cycle festivals Drik does not list
(Snana/Bahuda/Hera…) are covered by Tier A goldens in tests/ and by
lunar-label checks, not here.

Used by: tests (CI blocking), scripts/audit_festivals.py (scheduled job),
scripts/post_daily.py (pre-publish guard).
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

REFERENCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "tests" / "fixtures" / "festival_reference" / "drik_bhubaneswar.json"
)


def _m(primary: list[str], alternates: list[str] | None = None, tolerance: int = 0) -> dict:
    """tolerance: days either side of a reference date that still count —
    only where Drik follows a documented different convention from Odisha;
    Tier A rows for the year (exact) take precedence."""
    return {"primary": primary, "alternates": alternates or [], "tolerance": tolerance}


# Purnimanta Ekadashi name (Drik Hindu page) → name on the Drik Odia page
_ODIA_EKADASHI = {'Kamada Ekadashi': 'Kamada Ekadashi', 'Papamochani Ekadashi': 'Papamochani Ekadashi', 'Mohini Ekadashi': 'Mohini Ekadashi', 'Varuthini Ekadashi': 'Baruthini Ekadashi', 'Nirjala Ekadashi': 'Nirjala Ekadashi', 'Apara Ekadashi': 'Jala Krida Ekadashi', 'Devshayani Ekadashi': 'Harishayan Ekadashi', 'Yogini Ekadashi': 'Khalilagi Ekadashi', 'Shravana Putrada Ekadashi': 'Shravana Putrada Ekadashi', 'Kamika Ekadashi': 'Kamika Ekadashi', 'Parsva Ekadashi': 'Parswa Paribartan Ekadashi', 'Aja Ekadashi': 'Kaliyadalan Ekadashi', 'Indira Ekadashi': 'Indira Ekadashi', 'Papankusha Ekadashi': 'Papankusha Ekadashi', 'Rama Ekadashi': 'Rama Ekadashi', 'Devutthana Ekadashi': 'Deva Utthapan Ekadashi', 'Utpanna Ekadashi': 'Utpanna Ekadashi', 'Mokshada Ekadashi': 'Gomati Ekadashi', 'Saphala Ekadashi': 'Saphala Ekadashi', 'Pausha Putrada Ekadashi': 'Pausha Putrada Ekadashi', 'Shattila Ekadashi': 'Sattila Ekadashi', 'Jaya Ekadashi': 'Bhouma Ekadashi', 'Vijaya Ekadashi': 'Pankoddhar Ekadashi', 'Amalaki Ekadashi': 'Papanasini Ekadashi'}


def _ekadashi(name: str) -> dict[str, list[str]]:
    """Smarta date is primary; Gauna (second-day) and Vaishnava dates are
    acceptable — the Jagannath temple keeps the Vaishnava Ekadashi."""
    names = [f"hindu:{name}", f"odia:{_ODIA_EKADASHI[name]}"]
    variants = [name, _ODIA_EKADASHI[name]]
    return _m(names, [f"{p} {n}" for p in ("Gauna", "Vaishnava") for n in variants])


# Our festival name_en → reference event names (Drik event names verbatim).
REFERENCE_MAP: dict[str, dict[str, list[str]]] = {
    # Puri / Jagannath
    "Rath Yatra": _m(["Rath Yatra", "Jagannath Rathyatra"]),
    "Snana Purnima": _m(["Jyeshtha Purnima"]),
    "Snana Yatra": _m(["Jyeshtha Purnima"]),
    "Chandan Yatra Begins": _m(["Akshaya Tritiya"]),
    "Utthana Ekadashi": _ekadashi("Devutthana Ekadashi"),
    # Lunar festivals
    "Odia New Year (Lunar)": _m(["Chaitra Navratri"], ["Ugadi", "Gudi Padwa"]),
    "Biraja New Year Puja": _m(["Chaitra Navratri"], ["Ugadi", "Gudi Padwa"]),
    "Rama Navami": _m(["Rama Navami", "Rama Navami Smarta"], ["Rama Navami ISKCON"]),
    "Akshaya Tritiya": _m(["Akshaya Tritiya"]),
    "Biraja Akshaya Tritiya": _m(["Akshaya Tritiya"]),
    "Buddha Purnima": _m(["Buddha Purnima"]),
    "Sital Shashthi": _m(["Jamai Shashti"]),
    "Gamha Purnima": _m(["Gamha Purnima"]),
    # Smarta Janmashtami also weighs Rohini nakshatra (Jayanti yoga), which
    # festival_calendar does not model; Odisha Government lists (Tier A)
    # decide exact years. Tolerance applies to the audit only — publishing
    # needs an exact match (is_verified).
    "Janmashtami": _m(["Krishna Janmashtami", "Janmashtami Smarta"], ["Janmashtami ISKCON"], tolerance=1),
    "Ganesh Chaturthi": _m(["Ganesh Chaturthi"]),
    "Nuakhai": _m(["Rishi Panchami"]),
    "Nuakhai Juhar": _m(["Rishi Panchami"]),
    "Mahalaya": _m(["Mahalaya Amabasya"]),
    # Drik's Mahastami is the udaya Ashtami; Odisha keeps the day-covering
    # Ashtami (Government lists). Same occasion, may differ by a day.
    "Durga Ashtami": _m(["Mahastami"], tolerance=1),
    "Maa Biraja Ashtami": _m(["Mahastami"], tolerance=1),
    "Mahanavami": _m(["Maha Navami"]),
    "Mahanavami at Biraja": _m(["Maha Navami"]),
    "Dussehra / Vijaya Dashami": _m(["Dasahara"]),
    "Vijaya Dashami at Biraja": _m(["Dasahara"]),
    # Odisha keeps the udaya Purnima (state holiday list); Drik's "Sharad
    # Purnima" is the north-Indian moonrise rule and may be a day earlier.
    "Kumar Purnima": _m(["Ashwina Purnima"], ["Sharad Purnima", "Kojagara Puja"]),
    "Naraka Chaturdashi": _m(["Narak Chaturdashi"], ["Kali Chaudas"]),
    "Diwali / Lakshmi Puja": _m(["Dipavali"]),
    "Bali Pratipada / Govardhan Puja": _m(["Govardhan Puja"]),
    "Kartik Purnima / Boita Bandana": _m(["Kartika Purnima"]),
    "Pausha Purnima": _m(["Pausha Purnima"]),
    "Vasanta Panchami / Saraswati Puja": _m(["Sri Panchami"], ["Vasant Panchami", "Saraswati Puja"]),
    "Magha Purnima": _m(["Magha Purnima"]),
    "Maha Shivaratri": _m(["Maha Shivaratri"]),
    "Lingaraj Maha Shivaratri": _m(["Maha Shivaratri"]),
    "Biraja Shivaratri": _m(["Maha Shivaratri"]),
    "Dola Purnima": _m(["Phalguna Purnima"], ["Holika Dahan"]),
    # Ekadashis (Purnimanta names as on the Drik Hindu page)
    "Kamada Ekadashi": _ekadashi("Kamada Ekadashi"),
    "Papamochani Ekadashi": _ekadashi("Papamochani Ekadashi"),
    "Mohini Ekadashi": _ekadashi("Mohini Ekadashi"),
    "Varuthini Ekadashi": _ekadashi("Varuthini Ekadashi"),
    "Nirjala Ekadashi": _ekadashi("Nirjala Ekadashi"),
    "Apara Ekadashi": _ekadashi("Apara Ekadashi"),
    "Devshayani / Padma Ekadashi": _ekadashi("Devshayani Ekadashi"),
    "Yogini Ekadashi": _ekadashi("Yogini Ekadashi"),
    "Putrada Ekadashi": _ekadashi("Shravana Putrada Ekadashi"),
    "Kamika Ekadashi": _ekadashi("Kamika Ekadashi"),
    "Parsva Ekadashi": _ekadashi("Parsva Ekadashi"),
    "Aja Ekadashi": _ekadashi("Aja Ekadashi"),
    "Indira Ekadashi": _ekadashi("Indira Ekadashi"),
    "Papankusha Ekadashi": _ekadashi("Papankusha Ekadashi"),
    "Rama Ekadashi": _ekadashi("Rama Ekadashi"),
    "Prabodhini / Devutthana Ekadashi": _ekadashi("Devutthana Ekadashi"),
    "Utpanna Ekadashi": _ekadashi("Utpanna Ekadashi"),
    "Mokshada Ekadashi": _ekadashi("Mokshada Ekadashi"),
    "Saphala Ekadashi": _ekadashi("Saphala Ekadashi"),
    "Pausha Putrada Ekadashi": _ekadashi("Pausha Putrada Ekadashi"),
    "Shattila Ekadashi": _ekadashi("Shattila Ekadashi"),
    "Jaya Ekadashi": _ekadashi("Jaya Ekadashi"),
    "Vijaya Ekadashi": _ekadashi("Vijaya Ekadashi"),
    "Amalaki Ekadashi": _ekadashi("Amalaki Ekadashi"),
    # Sankrantis (Odia page names)
    "Makar Sankranti": _m(["odia:Uttarayana Makar Sankranti"]),
    "Makar Sankranti Snanam at Biraja": _m(["odia:Uttarayana Makar Sankranti"]),
    "Kumbha Sankranti": _m(["odia:Kumbha Sankranti"]),
    "Meena Sankranti": _m(["odia:Meena Sankranti"]),
    "Pana Sankranti (Odia New Year)": _m(["odia:Mahabisuba Pana Sankranti"]),
    "Pana Sankranti at Jagannath": _m(["odia:Mahabisuba Pana Sankranti"]),
    "Pana Sankranti at Lingaraj": _m(["odia:Mahabisuba Pana Sankranti"]),
    "Pana Sankranti at Biraja": _m(["odia:Mahabisuba Pana Sankranti"]),
    "Vrishabha Sankranti": _m(["odia:Brusha Sankranti"]),
    "Mithuna Sankranti (Raja Parba)": _m(["odia:Raja Sankranti"]),
    "Karka Sankranti (Dakshinayana)": _m(["odia:Dakhinaya Karkata Sankranti"]),
    "Simha Sankranti": _m(["odia:Singha Sankranti"]),
    "Kanya Sankranti": _m(["odia:Kanya Sankranti"]),
    "Tula Sankranti": _m(["odia:Garbhana Sankranti"]),
    "Vrischika Sankranti": _m(["odia:Bichha Sankranti"]),
    "Dhanu Sankranti": _m(["odia:Dhanu Sankranti"]),
}

# Festivals that must never be posted unverified. The pre-publish guard and
# the yearly-coverage test enforce these for every seeded year.
MAJOR_FESTIVALS: frozenset[str] = frozenset(
    {
        "Rath Yatra", "Snana Purnima", "Maha Shivaratri", "Dola Purnima",
        "Rama Navami", "Akshaya Tritiya", "Janmashtami", "Ganesh Chaturthi",
        "Nuakhai", "Mahalaya", "Durga Ashtami", "Dussehra / Vijaya Dashami",
        "Kumar Purnima", "Diwali / Lakshmi Puja", "Kartik Purnima / Boita Bandana",
        "Vasanta Panchami / Saraswati Puja", "Makar Sankranti",
        "Pana Sankranti (Odia New Year)", "Mithuna Sankranti (Raja Parba)",
        "Prathamastami", "Savitri Amavasya", "Gamha Purnima",
    }
)


@lru_cache(maxsize=1)
def load_reference() -> dict:
    return json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))


def reference_years() -> range:
    y0, y1 = load_reference()["meta"]["years"]
    return range(y0, y1 + 1)


@lru_cache(maxsize=1)
def _reference_index() -> dict[str, set[str]]:
    """Reference event name → set of ISO dates. Names may be page-qualified
    ("odia:Dhanu Sankranti") where the two Drik pages use the same name
    under different conventions (the Hindu page's sankranti day differs)."""
    idx: dict[str, set[str]] = defaultdict(set)
    for e in load_reference()["events"]:
        idx[e["name"]].add(e["date"])
        idx[f"{e['page']}:{e['name']}"].add(e["date"])
    return idx


def expected_dates(festival: str, year: int) -> tuple[set[str], set[str]]:
    """(primary dates, all acceptable dates) for our festival in a year.

    Tier hierarchy (eval.md): if Tier A rows exist for this festival and
    year they are the answer, exactly; otherwise the Tier B reference with
    its alternates and documented tolerance."""
    from src.festival_civil import tier_a_rows

    prefix = f"{year}-"
    tier_a = {r["date"] for r in tier_a_rows() if r["name_en"] == festival and r["date"].startswith(prefix)}
    if tier_a:
        return tier_a, tier_a
    spec = REFERENCE_MAP.get(festival)
    if not spec:
        return set(), set()
    idx = _reference_index()
    primary = {d for n in spec["primary"] for d in idx.get(n, ()) if d.startswith(prefix)}
    alt = {d for n in spec["alternates"] for d in idx.get(n, ()) if d.startswith(prefix)}
    ok = primary | alt
    for d in list(ok):
        for k in range(1, spec.get("tolerance", 0) + 1):
            for sign in (-1, 1):
                ok.add((date.fromisoformat(d) + timedelta(days=sign * k)).isoformat())
    return primary, ok


@dataclass
class AuditResult:
    wrong: list[tuple[str, str, list[str]]] = field(default_factory=list)  # (festival, our date, expected)
    missing: list[tuple[str, str]] = field(default_factory=list)  # (festival, expected date)
    unverified: set[str] = field(default_factory=set)
    checked: int = 0

    @property
    def ok(self) -> bool:
        return not self.wrong and not self.missing

    def lines(self) -> list[str]:
        out = [f"WRONG    {f:40s} ours {d}  reference {', '.join(e) or '—'}" for f, d, e in self.wrong]
        out += [f"MISSING  {f:40s} reference {d}" for f, d in self.missing]
        return out


def audit(ours: dict[str, set[str]], years: range | list[int] | None = None) -> AuditResult:
    """
    ours: festival name_en → set of ISO dates we attach it to.
    Checks every mapped festival for every year in `years` (default: all
    reference years). A festival date is WRONG if it is not an acceptable
    reference date; a reference primary date is MISSING if we attach the
    festival to none of that occasion's acceptable dates.
    """
    from src.festival_civil import tier_a_rows

    years = list(years or reference_years())
    res = AuditResult()
    tier_a_names = {r["name_en"] for r in tier_a_rows()}
    res.unverified = {n for n in ours if n not in REFERENCE_MAP and n not in tier_a_names}
    for festival in sorted(set(REFERENCE_MAP) | tier_a_names):
        our_dates = ours.get(festival, set())
        for year in years:
            primary, ok = expected_dates(festival, year)
            if not ok:
                continue  # reference has no such event that year (e.g. Adhika-only)
            mine = {d for d in our_dates if d.startswith(f"{year}-")}
            for d in sorted(mine):
                res.checked += 1
                if d not in ok:
                    res.wrong.append((festival, d, sorted(primary)))
            for d in sorted(primary):
                # the same occasion may be matched on an alternate date (±1 day)
                window = {
                    (date.fromisoformat(d) + timedelta(days=k)).isoformat() for k in (-1, 0, 1)
                }
                if not (mine & ok & window):
                    res.missing.append((festival, d))
    return res


def festivals_from_db(db_path: str | Path = "data/panchang.db") -> dict[str, set[str]]:
    import sqlite3

    out: dict[str, set[str]] = defaultdict(set)
    with sqlite3.connect(str(db_path)) as conn:
        for d, name in conn.execute("select date, name_en from festivals"):
            out[name].add(d)
    return out


def check_day(day: str, festival_names: list[str]) -> list[str]:
    """Pre-publish guard for one day. Returns human-readable problems:
      - a festival we attach today that the reference or a Tier A row for
        this year places on another date;
      - a MAJOR festival that the reference or Tier A places today but we
        do not attach."""
    from src.festival_civil import tier_a_rows

    year = int(day[:4])
    if year not in reference_years():
        return [f"No festival reference for {year} — refresh the reference before posting"]
    problems = []
    tier_a_year = [r for r in tier_a_rows() if r["date"].startswith(f"{year}-")]
    for name in festival_names:
        primary, ok = expected_dates(name, year)
        if ok and day not in ok:
            problems.append(f"{name} attached on {day}; expected {', '.join(sorted(primary))}")
    d0 = date.fromisoformat(day)
    neighbours = {(d0 + timedelta(days=k)).isoformat() for k in (-1, 1)}
    for name in MAJOR_FESTIVALS:
        if name in festival_names:
            continue
        if name in REFERENCE_MAP:
            primary, ok = expected_dates(name, year)
            # an accepted alternate on an adjacent day is the same occasion
            if day in primary and not (ok & neighbours):
                problems.append(f"Reference has {name} on {day} but we do not")
        if any(r["date"] == day and r["name_en"] == name for r in tier_a_year):
            problems.append(f"Tier A has {name} on {day} but we do not")
    return problems


# ── Publication gate (social posts) ──────────────────────────────────────────

def is_verified(festival: str, day: str) -> bool:
    """True if an independent source confirms `festival` on `day`: the Tier B
    reference (for mapped festivals) or a Tier A row / reviewed correction."""
    from src.festival_civil import DATE_CORRECTIONS, tier_a_dates

    if day in tier_a_dates(festival):
        return True
    if any(c["date"] == day and festival in c["names"] for c in DATE_CORRECTIONS):
        return True
    year = int(day[:4])
    if festival in REFERENCE_MAP and year in reference_years():
        # exact reference dates only — the audit's convention tolerance
        # never counts as verification for an announcement
        spec = REFERENCE_MAP[festival]
        idx = _reference_index()
        names = spec["primary"] + spec["alternates"]
        return any(day in idx.get(n, ()) for n in names)
    return False  # (Tier A rows were checked above)


class PublishBlocked(RuntimeError):
    """Today's festival list contradicts the reference — do not post."""


def _festival_name(f: dict) -> str:
    return f.get("name_en") or (f.get("name") or {}).get("en") or ""


def prepare_for_publish(panchang: dict) -> tuple[dict, list[str]]:
    """
    Gate for public posts. Raises PublishBlocked if today's festivals
    contradict the reference (a wrong or missing major festival); otherwise
    returns (panchang with only verified festivals, names omitted as unverified).
    The API keeps every festival; only what we *announce* is restricted.
    """
    day = panchang["date"]
    names = [_festival_name(f) for f in panchang.get("festivals") or []]
    problems = check_day(day, names)
    if problems:
        raise PublishBlocked("; ".join(problems))
    kept, omitted = [], []
    for f in panchang.get("festivals") or []:
        (kept if is_verified(_festival_name(f), day) else omitted).append(f)
    return {**panchang, "festivals": kept}, [_festival_name(f) for f in omitted]
