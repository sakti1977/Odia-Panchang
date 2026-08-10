#!/usr/bin/env python3
"""
Free-tier ops helpers for Odia-Panchang on Render Free + GitHub Actions.

Usage:
  python scripts/free_tier_ops.py wake   [--url URL]
  python scripts/free_tier_ops.py tweet  [--url URL]
  python scripts/free_tier_ops.py health [--url URL]

Environment:
  PUBLIC_API_URL  Base API URL (default https://odia-panchang.onrender.com)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_URL = "https://odia-panchang.onrender.com"


def base_url(url: str | None = None) -> str:
    return (url or os.getenv("PUBLIC_API_URL") or DEFAULT_URL).rstrip("/")


def http_json(
    method: str,
    url: str,
    *,
    timeout: float = 60.0,
) -> tuple[int, Any]:
    """Minimal HTTP JSON client (stdlib only — no httpx required in CI)."""
    req = Request(url, method=method.upper())
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "odia-panchang-free-tier-ops/1.0")
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            code = getattr(resp, "status", 200) or 200
            try:
                return code, json.loads(body) if body else {}
            except json.JSONDecodeError:
                return code, {"raw": body[:500]}
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        try:
            data = json.loads(body) if body else {"error": str(e)}
        except json.JSONDecodeError:
            data = {"error": str(e), "raw": body[:500]}
        return e.code, data
    except URLError as e:
        return 0, {"error": str(e.reason if hasattr(e, "reason") else e)}


def wake_service(
    url: str | None = None,
    *,
    max_attempts: int = 8,
    initial_wait: float = 20.0,
    request_timeout: float = 45.0,
) -> bool:
    """
    Hit GET /api until healthy. Designed for Render free-tier cold start (~30–60s).
    Returns True if healthy.
    """
    api = base_url(url)
    health = f"{api}/api"
    print(f"[wake] Warming {health}")
    for attempt in range(1, max_attempts + 1):
        code, data = http_json("GET", health, timeout=request_timeout)
        ok = code == 200 and (
            (isinstance(data, dict) and data.get("status") == "ok") or code == 200
        )
        print(f"[wake] attempt {attempt}/{max_attempts}: HTTP {code} {data!r}"[:200])
        if ok:
            print("[wake] service is up")
            return True
        if attempt < max_attempts:
            wait = initial_wait * min(attempt, 3)
            print(f"[wake] sleeping {wait:.0f}s for free-tier spin-up…")
            time.sleep(wait)
    print("[wake] failed to wake service")
    return False


def post_tweet(
    url: str | None = None,
    *,
    max_attempts: int = 5,
    initial_wait: float = 25.0,
    request_timeout: float = 120.0,
    wake_first: bool = True,
) -> int:
    """
    Wake (optional) then POST /tweet/post with retries.
    Exit codes: 0 success (posted or logged), 1 hard failure.
    """
    api = base_url(url)
    if wake_first and not wake_service(api):
        # still try tweet — wake might have partially worked
        print("[tweet] continuing despite wake failure")

    endpoint = f"{api}/tweet/post"
    print(f"[tweet] POST {endpoint}")
    last_status = "unknown"
    for attempt in range(1, max_attempts + 1):
        code, data = http_json("POST", endpoint, timeout=request_timeout)
        print(f"[tweet] attempt {attempt}/{max_attempts}: HTTP {code}")
        if isinstance(data, dict):
            print(json.dumps(data, indent=2, ensure_ascii=False)[:2500])
        result = (data or {}).get("result") if isinstance(data, dict) else {}
        last_status = (result or {}).get("status", "unknown")

        if code == 200 and last_status in ("posted", "logged"):
            if last_status == "posted":
                print("[tweet] posted to Twitter/X")
            else:
                print(
                    "[tweet] logged only — set TWITTER_* on the Render web service "
                    "to actually post"
                )
            return 0
        if code == 200 and last_status == "error":
            # App handled the job but Twitter failed — do not infinite-retry forever
            print("[tweet] application returned error status (check Render logs / Twitter keys)")
            return 1

        if attempt < max_attempts:
            wait = initial_wait * attempt
            print(f"[tweet] retry in {wait:.0f}s…")
            time.sleep(wait)

    print(f"[tweet] all attempts failed (last status={last_status})")
    return 1


def health_check(url: str | None = None) -> int:
    api = base_url(url)
    code, data = http_json("GET", f"{api}/api", timeout=30)
    print(f"HTTP {code} {data}")
    return 0 if code == 200 else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Free-tier wake / tweet ops")
    p.add_argument("command", choices=["wake", "tweet", "health"])
    p.add_argument("--url", default=None, help="API base URL")
    p.add_argument("--no-wake", action="store_true", help="Skip wake before tweet")
    args = p.parse_args(argv)

    if args.command == "wake":
        return 0 if wake_service(args.url) else 1
    if args.command == "health":
        return health_check(args.url)
    if args.command == "tweet":
        return post_tweet(args.url, wake_first=not args.no_wake)
    return 2


if __name__ == "__main__":
    sys.exit(main())
