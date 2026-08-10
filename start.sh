#!/bin/bash
# Startup script: seed DB if needed, refresh festivals, then start the API server.
set -e

echo "[start.sh] Odia Panjika API starting..."

# Seed DB if it doesn't exist or is empty
if [ ! -f "data/panchang.db" ] || [ ! -s "data/panchang.db" ]; then
    echo "[start.sh] Database not found — seeding 2024–2030..."
    mkdir -p data
    python3 seed.py --start 2024 --end 2030
    echo "[start.sh] Seeding complete."
else
    echo "[start.sh] Database found, skipping full seed."
fi

# Festival rows are rule/civil-override driven; cheap rewrite keeps deploy in sync
# after festivals.py / festival_civil.py changes (no ephemeris recompute).
if [ "${SKIP_FESTIVAL_REFRESH:-false}" != "true" ]; then
    echo "[start.sh] Refreshing festival rows from current rules…"
    python3 seed.py --refresh-festivals --start 2020 --end 2030
fi

mkdir -p logs

echo "[start.sh] Starting uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8001}"
