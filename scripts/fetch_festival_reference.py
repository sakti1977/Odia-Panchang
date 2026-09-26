#!/usr/bin/env python3
"""Fetch the independent festival-date reference (Drik Panchang, Bhubaneswar).

Writes tests/fixtures/festival_reference/drik_bhubaneswar.json — the Tier B
reference that `src/festival_audit.py` checks our DB against. The fixture is
committed so CI never depends on the network; this script only refreshes it
(yearly, or when the scheduled audit reports that the live page changed).

    python scripts/fetch_festival_reference.py --start 2020 --end 2030
    python scripts/fetch_festival_reference.py --check      # diff only, exit 1 on change

Two Drik pages per year, both computed for Bhubaneswar (geoname 1275817):
  - Odia calendar (Odia festival names; Amanta month labels)
  - Hindu calendar (all Purnima/Amavasya/Ekadashi; Purnimanta month labels)

Parsing is deterministic HTML scraping — never an LLM summary — so a
reference date is exactly what the page shows. Review the fixture diff like
code: a changed reference date is a claim that needs a human look.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "festival_reference" / "drik_bhubaneswar.json"
GEONAME_BHUBANESWAR = 1275817
PAGES = {
    "odia": "https://www.drikpanchang.com/oriya/oriya-calendar.html?year={year}&geoname-id={geo}",
    "hindu": "https://www.drikpanchang.com/calendars/hindu/hinducalendar.html?year={year}&geoname-id={geo}",
}
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120 Safari/537.36 odia-panchang-audit"
)
_EVENT = re.compile(
    r'<div class="dpEventName[^"]*">(.*?)</div>'
    r'<div class="dpEventGregDate">(.*?)</div>(.*?)</div>',
    re.S,
)
_LOCATION = re.compile(r"Bhubaneshwar, Odisha, India")


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(html.unescape(text).replace("*", " ").split())


def parse_events(page_html: str, *, page: str, year: int) -> list[dict]:
    if not _LOCATION.search(page_html):
        raise ValueError(f"{page} {year}: page is not computed for Bhubaneswar")
    out = []
    for name, greg, lunar in _EVENT.findall(page_html):
        d = datetime.strptime(_clean(greg), "%B %d, %Y, %A").date()
        if d.year != year:
            continue
        out.append({"date": d.isoformat(), "name": _clean(name), "lunar": _clean(lunar), "page": page})
    if len(out) < 40:
        raise ValueError(f"{page} {year}: only {len(out)} events parsed — page layout changed?")
    return out


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_years(start: int, end: int) -> list[dict]:
    events: list[dict] = []
    for year in range(start, end + 1):
        for page, template in PAGES.items():
            url = template.format(year=year, geo=GEONAME_BHUBANESWAR)
            events.extend(parse_events(fetch(url), page=page, year=year))
            time.sleep(2)  # be polite: two small pages per year
    uniq = {(e["date"], e["name"], e["page"]): e for e in events}
    return sorted(uniq.values(), key=lambda e: (e["date"], e["page"], e["name"]))


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--start", type=int)
    ap.add_argument("--end", type=int)
    ap.add_argument(
        "--check",
        action="store_true",
        help="fetch and diff against the committed fixture; exit 1 if the live reference changed",
    )
    args = ap.parse_args(argv)

    existing = load_fixture() if FIXTURE.exists() else None
    start = args.start or (existing["meta"]["years"][0] if existing else date.today().year)
    end = args.end or (existing["meta"]["years"][1] if existing else date.today().year + 1)
    events = fetch_years(start, end)

    if args.check:
        if not existing:
            print("No committed fixture to check against", file=sys.stderr)
            return 1
        old = {
            (e["date"], e["name"], e["page"])
            for e in existing["events"]
            if start <= int(e["date"][:4]) <= end
        }
        new = {(e["date"], e["name"], e["page"]) for e in events}
        added, removed = sorted(new - old), sorted(old - new)
        for row in removed:
            print(f"- {row[0]}  {row[1]}  ({row[2]})")
        for row in added:
            print(f"+ {row[0]}  {row[1]}  ({row[2]})")
        if added or removed:
            print(f"Live reference differs from fixture ({len(removed)} removed, {len(added)} added)")
            return 1
        print(f"Live reference matches fixture for {start}-{end} ({len(new)} events)")
        return 0

    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "meta": {
            "source": "Drik Panchang (Tier B) — Odia calendar + Hindu calendar pages",
            "location": "Bhubaneswar, Odisha (geoname 1275817)",
            "urls": list(PAGES.values()),
            "years": [start, end],
            "retrieved": date.today().isoformat(),
            "note": "Deterministic HTML parse by scripts/fetch_festival_reference.py. "
            "Odia page month labels are Amanta; Hindu page labels are Purnimanta.",
        },
        "events": events,
    }
    FIXTURE.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {len(events)} events for {start}-{end} to {FIXTURE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
