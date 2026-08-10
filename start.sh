#!/bin/bash
# Startup script: ensure DB matches ENGINE_VERSION, refresh festivals, start API.
set -e

echo "[start.sh] Odia Panjika API starting..."

mkdir -p data logs

# Full seed if DB missing/empty
if [ ! -f "data/panchang.db" ] || [ ! -s "data/panchang.db" ]; then
    echo "[start.sh] Database not found — seeding 2020–2030..."
    python3 seed.py --start 2020 --end 2030 --force
    echo "[start.sh] Seeding complete."
else
    echo "[start.sh] Database found."
fi

# If engine formula version changed → force reseed; else refresh festivals only
# SKIP_ENGINE_ENSURE=true skips both (emergency)
if [ "${SKIP_ENGINE_ENSURE:-false}" != "true" ]; then
    echo "[start.sh] Ensuring engine version + festivals…"
    python3 seed.py --ensure-engine --start 2020 --end 2030
fi

echo "[start.sh] Starting uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8001}"
