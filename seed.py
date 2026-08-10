"""
Seed script: pre-compute Panchang for a range of years and store in SQLite.
Run once (or when you want to refresh the data):
    python seed.py
    python seed.py --start 2020 --end 2030
    python seed.py --force --start 2020 --end 2030
    python seed.py --refresh-festivals
    python seed.py --ensure-engine
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/panchang.db")

from src.engine import ENGINE_VERSION, compute_panchang
from src.festivals import match_festivals, get_sankranti_festivals
from src.models import PanchangDay, Festival, get_engine, get_session_factory, init_db


def _db_path_from_url(url: str) -> Path | None:
    if url.startswith("sqlite:///"):
        return Path(url.replace("sqlite:///", "", 1))
    return None


def engine_version_path() -> Path:
    dbp = _db_path_from_url(DATABASE_URL)
    if dbp is not None:
        return dbp.parent / ".engine_version"
    return Path("data") / ".engine_version"


def read_stored_engine_version() -> str | None:
    p = engine_version_path()
    if not p.is_file():
        return None
    return p.read_text(encoding="utf-8").strip() or None


def write_stored_engine_version(version: str = ENGINE_VERSION) -> None:
    p = engine_version_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(version + "\n", encoding="utf-8")


def wipe_range(session, start: date, end: date) -> None:
    """Delete panji + festival rows for [start, end]."""
    session.query(Festival).filter(
        Festival.date >= start.isoformat(),
        Festival.date <= end.isoformat(),
    ).delete(synchronize_session=False)
    session.query(PanchangDay).filter(
        PanchangDay.date >= start.isoformat(),
        PanchangDay.date <= end.isoformat(),
    ).delete(synchronize_session=False)
    session.commit()


def seed(start_year: int = 2020, end_year: int = 2030, *, force: bool = False):
    engine = get_engine(DATABASE_URL)
    init_db(engine)
    Session = get_session_factory(engine)

    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    total = (end - start).days + 1

    print(f"Seeding {total} days ({start_year}–{end_year}) force={force} …")
    print(f"  ENGINE_VERSION={ENGINE_VERSION}")

    session = Session()
    if force:
        print("  wiping existing rows in range…")
        wipe_range(session, start, end)

    batch = []
    prev_soura = None
    current = start
    count = 0
    written = 0

    while current <= end:
        existing = session.get(PanchangDay, current.isoformat())
        if existing and not force:
            current += timedelta(days=1)
            count += 1
            continue

        try:
            p = compute_panchang(current)
        except Exception as e:
            print(f"  ⚠️  {current}: {e}", file=sys.stderr)
            current += timedelta(days=1)
            count += 1
            continue

        day_obj = PanchangDay(
            date=p["date"],
            vara_en=p["vara_en"],
            vara_or=p["vara_or"],
            soura_masa_en=p["soura_masa_en"],
            soura_masa_or=p["soura_masa_or"],
            chandra_masa_en=p["chandra_masa_en"],
            chandra_masa_or=p["chandra_masa_or"],
            paksha_en=p["paksha_en"],
            paksha_or=p["paksha_or"],
            tithi_num=p["tithi_num"],
            tithi_en=p["tithi_en"],
            tithi_or=p["tithi_or"],
            nakshatra_en=p["nakshatra_en"],
            nakshatra_or=p["nakshatra_or"],
            yoga_en=p["yoga_en"],
            yoga_or=p["yoga_or"],
            karana_en=p["karana_en"],
            karana_or=p["karana_or"],
            sunrise=p["sunrise"],
            sunset=p["sunset"],
        )

        for f in match_festivals(p):
            day_obj.festivals.append(
                Festival(
                    date=p["date"],
                    name_en=f["name_en"],
                    name_or=f["name_or"],
                    tradition=f["tradition"],
                    description=f["description"],
                )
            )

        if prev_soura is not None and p["soura_masa_en"] != prev_soura:
            for f in get_sankranti_festivals(p["soura_masa_en"]):
                day_obj.festivals.append(
                    Festival(
                        date=p["date"],
                        name_en=f["name_en"],
                        name_or=f["name_or"],
                        tradition=f["tradition"],
                        description=f["description"],
                    )
                )

        prev_soura = p["soura_masa_en"]
        batch.append(day_obj)
        count += 1
        written += 1

        if len(batch) >= 500:
            session.add_all(batch)
            session.commit()
            print(f"  ✅ {count}/{total} days ({written} written) …")
            batch = []

        current += timedelta(days=1)

    if batch:
        session.add_all(batch)
        session.commit()

    session.close()
    write_stored_engine_version()
    print(f"✅ Done! {written} days written into {DATABASE_URL}")
    print(f"  stamped engine version → {ENGINE_VERSION}")


def refresh_festivals(start_year: int = 2020, end_year: int = 2030):
    """
    Recompute Festival rows for existing PanchangDay records.
    Use after changing TITHI_RULES / festival_civil overrides without wiping panji rows.
    """
    engine = get_engine(DATABASE_URL)
    init_db(engine)
    Session = get_session_factory(engine)
    session = Session()

    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    print(f"Refreshing festivals {start_year}–{end_year} …")

    deleted = (
        session.query(Festival)
        .filter(Festival.date >= start.isoformat())
        .filter(Festival.date <= end.isoformat())
        .delete(synchronize_session=False)
    )
    session.commit()
    print(f"  removed {deleted} old festival rows")

    current = start
    prev_soura = None
    if start > date(1900, 1, 1):
        prev_row = session.get(PanchangDay, (start - timedelta(days=1)).isoformat())
        if prev_row:
            prev_soura = prev_row.soura_masa_en

    added = 0
    batch: list = []
    while current <= end:
        row = session.get(PanchangDay, current.isoformat())
        if not row:
            current += timedelta(days=1)
            continue

        day_dict = {
            "date": row.date,
            "paksha_en": row.paksha_en,
            "tithi_num": row.tithi_num,
            "chandra_masa_en": row.chandra_masa_en,
            "soura_masa_en": row.soura_masa_en,
        }
        for f in match_festivals(day_dict):
            batch.append(
                Festival(
                    date=row.date,
                    name_en=f["name_en"],
                    name_or=f["name_or"],
                    tradition=f["tradition"],
                    description=f["description"],
                )
            )
            added += 1

        if prev_soura is not None and row.soura_masa_en != prev_soura:
            for f in get_sankranti_festivals(row.soura_masa_en):
                batch.append(
                    Festival(
                        date=row.date,
                        name_en=f["name_en"],
                        name_or=f["name_or"],
                        tradition=f["tradition"],
                        description=f["description"],
                    )
                )
                added += 1

        prev_soura = row.soura_masa_en
        if len(batch) >= 500:
            session.add_all(batch)
            session.commit()
            batch = []
            print(f"  … through {current.isoformat()} ({added} festivals)")
        current += timedelta(days=1)

    if batch:
        session.add_all(batch)
        session.commit()
    session.close()
    print(f"✅ Festival refresh done — {added} rows written")


def ensure_engine(start_year: int = 2020, end_year: int = 2030) -> int:
    """
    If stored engine version != ENGINE_VERSION, force-reseed year range.
    Returns 0 if OK, 1 if reseeded (still success for start.sh).
    """
    stored = read_stored_engine_version()
    print(f"[ensure-engine] stored={stored!r} current={ENGINE_VERSION!r}")
    if stored == ENGINE_VERSION:
        print("[ensure-engine] versions match — no full reseed")
        # Still refresh festivals so civil overrides stay current
        refresh_festivals(start_year, end_year)
        return 0
    print("[ensure-engine] mismatch — force reseeding astronomy + festivals")
    seed(start_year, end_year, force=True)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Odia Panchang database")
    parser.add_argument("--start", type=int, default=2020, help="Start year")
    parser.add_argument("--end", type=int, default=2030, help="End year (inclusive)")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete and recompute panji rows in range (after engine formula changes)",
    )
    parser.add_argument(
        "--refresh-festivals",
        action="store_true",
        help="Rewrite Festival rows for existing days (after rule/civil-override changes)",
    )
    parser.add_argument(
        "--ensure-engine",
        action="store_true",
        help="Force reseed if data/.engine_version != ENGINE_VERSION; else festival refresh",
    )
    args = parser.parse_args()
    if args.ensure_engine:
        raise SystemExit(ensure_engine(args.start, args.end))
    if args.refresh_festivals:
        refresh_festivals(args.start, args.end)
    else:
        seed(args.start, args.end, force=args.force)
