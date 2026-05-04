"""
Render Cron Job trigger — calls POST /tweet/post on the web service.
Retries up to 5 times with backoff to handle free-tier cold-start (~30s spin-up).
"""

import httpx
import time
import sys
import os

API_URL = os.getenv("PUBLIC_API_URL", "https://odia-panchang.onrender.com").rstrip("/")
ENDPOINT = f"{API_URL}/tweet/post"
MAX_RETRIES = 5
INITIAL_WAIT = 30  # seconds — allow time for free-tier spin-up


def trigger():
    print(f"[cron] Triggering daily tweet: {ENDPOINT}")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = httpx.post(ENDPOINT, timeout=60)
            resp.raise_for_status()
            print(f"[cron] ✅ Success (attempt {attempt}): {resp.json()}")
            sys.exit(0)
        except Exception as e:
            print(f"[cron] ⚠️  Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                wait = INITIAL_WAIT * attempt
                print(f"[cron] Retrying in {wait}s...")
                time.sleep(wait)

    print("[cron] ❌ All attempts failed.")
    sys.exit(1)


if __name__ == "__main__":
    trigger()
