#!/usr/bin/env python3
"""Audit festival dates in the SQLite store against the committed reference.

    python scripts/audit_festivals.py                 # all reference years
    python scripts/audit_festivals.py --years 2026 2027
    python scripts/audit_festivals.py --upcoming 60   # only the next 60 days

Exit 1 on any WRONG or MISSING festival. See src/festival_audit.py.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.festival_audit import audit, festivals_from_db, reference_years  # noqa: E402


CONFIRM_WITHIN_DAYS = 45


def print_schedule(db: str, days: int) -> int:
    """Markdown table of upcoming festivals: announced (verified) or held back.

    Exit 1 if any day's festivals contradict the reference (a post would be
    blocked); exit 2 if a MAJOR festival within CONFIRM_WITHIN_DAYS is held
    back for lack of confirmation (add a Tier A row to announce it)."""
    import sqlite3

    from src.festival_audit import MAJOR_FESTIVALS, check_day, is_verified

    today = date.today()
    end = today + timedelta(days=days)
    by_day: dict[str, list[str]] = {}
    with sqlite3.connect(db) as conn:
        for d, name in conn.execute(
            "select date, name_en from festivals where date between ? and ? order by date",
            (today.isoformat(), end.isoformat()),
        ):
            by_day.setdefault(d, []).append(name)
    print("| Date | Announced (verified) | Held back (unverified) | Problems |")
    print("|---|---|---|---|")
    blocked = 0
    needs_confirmation = []
    confirm_by = (today + timedelta(days=CONFIRM_WITHIN_DAYS)).isoformat()
    for d in sorted(by_day):
        names = by_day[d]
        ok = [n for n in names if is_verified(n, d)]
        held = [n for n in names if n not in ok]
        problems = check_day(d, names)
        blocked += bool(problems)
        needs_confirmation += [f"{d} {n}" for n in held if n in MAJOR_FESTIVALS and d <= confirm_by]
        print(f"| {d} | {', '.join(ok) or '—'} | {', '.join(held) or '—'} | {'; '.join(problems) or ''} |")
    if needs_confirmation:
        print(
            "\n**Major festivals held back — confirm from an Odia panjika / Government list and add "
            "a Tier A row to tests/fixtures/golden_festivals.json:** " + "; ".join(needs_confirmation)
        )
    if blocked:
        return 1
    return 2 if needs_confirmation else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--db", default=str(ROOT / "data" / "panchang.db"))
    ap.add_argument("--years", type=int, nargs="*")
    ap.add_argument("--upcoming", type=int, help="only report problems in the next N days")
    ap.add_argument("--verbose", action="store_true", help="list unverified festival names")
    ap.add_argument(
        "--schedule",
        type=int,
        metavar="DAYS",
        help="print the next DAYS days of festivals with what will be announced (markdown)",
    )
    args = ap.parse_args(argv)

    if args.schedule:
        return print_schedule(args.db, args.schedule)

    ours = festivals_from_db(args.db)
    years = args.years or list(reference_years())
    res = audit(ours, years)
    lines = res.lines()
    if args.upcoming:
        today = date.today()
        horizon = {(today + timedelta(days=k)).isoformat() for k in range(args.upcoming + 1)}
        lines = [ln for ln in lines if any(d in ln for d in horizon)]

    for ln in lines:
        print(ln)
    print(
        f"\nChecked {res.checked} festival dates across {years[0]}–{years[-1]}: "
        f"{len(res.wrong)} wrong, {len(res.missing)} missing"
        + (f" (showing next {args.upcoming} days: {len(lines)})" if args.upcoming else "")
    )
    if args.verbose:
        print("Unverified (no independent reference):", ", ".join(sorted(res.unverified)))
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
