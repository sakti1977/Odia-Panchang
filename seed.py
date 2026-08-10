"""
Seed script: pre-compute Panchang for a range of years and store in SQLite.
Run once (or when you want to refresh the data):
    python seed.py
    python seed.py --start 2020 --end 2030
"""

import argparse
import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/panchang.db")

from src.engine import compute_panchang
from src.festivals import match_festivals, get_sankranti_festivals
from src.models import PanchangDay, Festival, get_engine, get_session_factory, init_db


def seed(start_year: int = 2020, end_year: int = 2030):
    engine = get_engine(DATABASE_URL)
    init_db(engine)
    Session = get_session_factory(engine)

    start = date(start_year, 1, 1)
    end   = date(end_year, 12, 31)
    total = (end - start).days + 1

    print(f"Seeding {total} days ({start_year}–{end_year}) …")

    session = Session()
    batch = []
    prev_soura = None

    current = start
    count = 0

    while current <= end:
        # Skip if already seeded
        existing = session.get(PanchangDay, current.isoformat())
        if existing:
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
            date            = p["date"],
            vara_en         = p["vara_en"],
            vara_or         = p["vara_or"],
            soura_masa_en   = p["soura_masa_en"],
            soura_masa_or   = p["soura_masa_or"],
            chandra_masa_en = p["chandra_masa_en"],
            chandra_masa_or = p["chandra_masa_or"],
            paksha_en       = p["paksha_en"],
            paksha_or       = p["paksha_or"],
            tithi_num       = p["tithi_num"],
            tithi_en        = p["tithi_en"],
            tithi_or        = p["tithi_or"],
            nakshatra_en    = p["nakshatra_en"],
            nakshatra_or    = p["nakshatra_or"],
            yoga_en         = p["yoga_en"],
            yoga_or         = p["yoga_or"],
            karana_en       = p["karana_en"],
            karana_or       = p["karana_or"],
            sunrise         = p["sunrise"],
            sunset          = p["sunset"],
        )

        # Tithi-based festivals
        for f in match_festivals(p):
            day_obj.festivals.append(Festival(
                date        = p["date"],
                name_en     = f["name_en"],
                name_or     = f["name_or"],
                tradition   = f["tradition"],
                description = f["description"],
            ))

        # Sankranti: detect solar month change
        if prev_soura is not None and p["soura_masa_en"] != prev_soura:
            for f in get_sankranti_festivals(p["soura_masa_en"]):
                day_obj.festivals.append(Festival(
                    date        = p["date"],
                    name_en     = f["name_en"],
                    name_or     = f["name_or"],
                    tradition   = f["tradition"],
                    description = f["description"],
                ))

        prev_soura = p["soura_masa_en"]
        batch.append(day_obj)
        count += 1

        # Commit in batches of 500 for performance
        if len(batch) >= 500:
            session.add_all(batch)
            session.commit()
            print(f"  ✅ {count}/{total} days committed …")
            batch = []

        current += timedelta(days=1)

    if batch:
        session.add_all(batch)
        session.commit()

    session.close()
    print(f"✅ Done! {count} days seeded into {DATABASE_URL}")


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

    # Drop festivals in range
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
    # Need prev day's solar month for sankranti detection
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Odia Panchang database")
    parser.add_argument("--start", type=int, default=2020, help="Start year")
    parser.add_argument("--end",   type=int, default=2030, help="End year (inclusive)")
    parser.add_argument(
        "--refresh-festivals",
        action="store_true",
        help="Rewrite Festival rows for existing days (after rule/civil-override changes)",
    )
    args = parser.parse_args()
    if args.refresh_festivals:
        refresh_festivals(args.start, args.end)
    else:
        seed(args.start, args.end)
