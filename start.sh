#!/bin/bash
# Startup script: seed DB if needed, then start the API server.
set -e

echo "[start.sh] Odia Panjika API starting..."

# Seed DB if it doesn't exist or is empty
if [ ! -f "data/panchang.db" ] || [ ! -s "data/panchang.db" ]; then
    echo "[start.sh] Database not found — seeding 2024–2030..."
    mkdir -p data
    python3 seed.py --start 2024 --end 2030
    echo "[start.sh] Seeding complete."
else
    echo "[start.sh] Database found, skipping seed."
fi

mkdir -p logs

echo "[start.sh] Starting uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8001}"
