#!/usr/bin/env python3
"""
Free-tier ops helpers for Odia-Panchang on Render Free + GitHub Actions.

Usage:
  python scripts/free_tier_ops.py wake    [--url URL]
  python scripts/free_tier_ops.py tweet   [--url URL]
  python scripts/free_tier_ops.py social  [--url URL] [--platforms facebook,instagram]
  python scripts/free_tier_ops.py all     [--url URL]
  python scripts/free_tier_ops.py health  [--url URL]

Environment:
  PUBLIC_API_URL      Base API URL (default https://odia-panchang.onrender.com)
  TWEET_CRON_SECRET   Required for tweet/social/all (Bearer token)
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
    headers: dict[str, str] | None = None,
) -> tuple[int, Any]:
    """Minimal HTTP JSON client (stdlib only — no httpx required in CI)."""
    req = Request(url, method=method.upper())
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "odia-panchang-free-tier-ops/1.0")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
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
    secret = (os.getenv("TWEET_CRON_SECRET") or "").strip()
    if not secret:
        print(
            "[tweet] TWEET_CRON_SECRET is not set. "
            "Add it as a GitHub Actions secret and on the Render web service."
        )
        return 1

    if wake_first and not wake_service(api):
        print("[tweet] continuing despite wake failure")

    endpoint = f"{api}/tweet/post"
    auth_headers = {"Authorization": f"Bearer {secret}"}
    print(f"[tweet] POST {endpoint} (with cron secret)")
    last_status = "unknown"
    for attempt in range(1, max_attempts + 1):
        code, data = http_json(
            "POST", endpoint, timeout=request_timeout, headers=auth_headers
        )
        print(f"[tweet] attempt {attempt}/{max_attempts}: HTTP {code}")
        if isinstance(data, dict):
            print(json.dumps(data, indent=2, ensure_ascii=False)[:2500])
        if code == 401:
            print("[tweet] unauthorized — check TWEET_CRON_SECRET matches Render")
            return 1
        if code == 503:
            print("[tweet] server missing TWEET_CRON_SECRET configuration")
            return 1
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


def _auth_headers() -> dict[str, str] | None:
    secret = (os.getenv("TWEET_CRON_SECRET") or "").strip()
    if not secret:
        print(
            "[auth] TWEET_CRON_SECRET is not set. "
            "Add it as a GitHub Actions secret and on the Render web service."
        )
        return None
    return {"Authorization": f"Bearer {secret}"}


def post_social(
    url: str | None = None,
    *,
    platforms: str = "facebook,instagram",
    max_attempts: int = 5,
    initial_wait: float = 25.0,
    request_timeout: float = 180.0,
    wake_first: bool = True,
) -> int:
    """POST /social/post — Facebook and/or Instagram."""
    api = base_url(url)
    headers = _auth_headers()
    if not headers:
        return 1
    if wake_first and not wake_service(api):
        print("[social] continuing despite wake failure")

    endpoint = f"{api}/social/post?platforms={platforms}"
    print(f"[social] POST {endpoint}")
    for attempt in range(1, max_attempts + 1):
        code, data = http_json(
            "POST", endpoint, timeout=request_timeout, headers=headers
        )
        print(f"[social] attempt {attempt}/{max_attempts}: HTTP {code}")
        if isinstance(data, dict):
            print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
        if code == 401:
            print("[social] unauthorized — check TWEET_CRON_SECRET")
            return 1
        if code == 200 and isinstance(data, dict):
            st = data.get("status")
            if st in ("posted", "partial", "logged"):
                print(f"[social] done status={st}")
                return 0 if st != "error" else 1
            if st == "error":
                return 1
        if attempt < max_attempts:
            wait = initial_wait * attempt
            print(f"[social] retry in {wait:.0f}s…")
            time.sleep(wait)
    return 1


def post_all_channels(
    url: str | None = None,
    *,
    wake_first: bool = True,
    request_timeout: float = 240.0,
) -> int:
    """POST /social/post/all — X + Facebook + Instagram."""
    api = base_url(url)
    headers = _auth_headers()
    if not headers:
        return 1
    if wake_first and not wake_service(api):
        print("[all] continuing despite wake failure")
    endpoint = f"{api}/social/post/all"
    print(f"[all] POST {endpoint}")
    code, data = http_json("POST", endpoint, timeout=request_timeout, headers=headers)
    print(f"[all] HTTP {code}")
    if isinstance(data, dict):
        print(json.dumps(data, indent=2, ensure_ascii=False)[:3500])
    if code == 401:
        return 1
    if code != 200:
        return 1
    # Success if any channel posted or logged
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Free-tier wake / tweet / social ops")
    p.add_argument(
        "command",
        choices=["wake", "tweet", "social", "all", "health"],
    )
    p.add_argument("--url", default=None, help="API base URL")
    p.add_argument("--no-wake", action="store_true", help="Skip wake before post")
    p.add_argument(
        "--platforms",
        default="facebook,instagram",
        help="For social command: facebook,instagram",
    )
    args = p.parse_args(argv)

    if args.command == "wake":
        return 0 if wake_service(args.url) else 1
    if args.command == "health":
        return health_check(args.url)
    if args.command == "tweet":
        return post_tweet(args.url, wake_first=not args.no_wake)
    if args.command == "social":
        return post_social(
            args.url,
            platforms=args.platforms,
            wake_first=not args.no_wake,
        )
    if args.command == "all":
        return post_all_channels(args.url, wake_first=not args.no_wake)
    return 2


if __name__ == "__main__":
    sys.exit(main())
