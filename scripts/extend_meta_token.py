#!/usr/bin/env python3
"""Turn a short-lived User token into a never-expiring Page token.

Reads from the environment (or .env):
  META_APP_ID
  META_APP_SECRET
  META_USER_ACCESS_TOKEN   # Graph Explorer User token, NOT the Page token
  META_PAGE_ID             # optional; if unset, prints Pages you admin

Writes META_PAGE_ACCESS_TOKEN into .env. Prints only expiry facts, never tokens.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
GRAPH = "https://graph.facebook.com/v22.0"


def _load_dotenv() -> None:
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _get(url: str, token: str | None = None) -> dict:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")[:500]
        try:
            err = json.loads(body).get("error") or {}
            print("graph_error", exc.code, err.get("type"), err.get("code"), err.get("message"))
        except Exception:
            print("graph_error", exc.code, body[:200])
        raise


def _upsert_env(key: str, value: str) -> None:
    lines = ENV_PATH.read_text(encoding="utf-8").splitlines() if ENV_PATH.exists() else []
    out, seen = [], False
    for line in lines:
        if line.startswith(f"{key}="):
            out.append(f"{key}={value}")
            seen = True
        else:
            out.append(line)
    if not seen:
        out.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    _load_dotenv()
    app_id = os.getenv("META_APP_ID") or ""
    app_secret = os.getenv("META_APP_SECRET") or ""
    user_token = os.getenv("META_USER_ACCESS_TOKEN") or ""
    page_id = os.getenv("META_PAGE_ID") or ""
    if not app_id or not app_secret or not user_token:
        print("Need META_APP_ID, META_APP_SECRET, and META_USER_ACCESS_TOKEN in .env")
        print("App id/secret: developers.facebook.com → your app → Settings → Basic")
        print("User token: Graph Explorer → Generate Access Token (User token, not Page)")
        return 1

    exchange = (
        f"{GRAPH}/oauth/access_token?"
        + urllib.parse.urlencode(
            {
                "grant_type": "fb_exchange_token",
                "client_id": app_id,
                "client_secret": app_secret,
                "fb_exchange_token": user_token,
            }
        )
    )
    try:
        long_user = _get(exchange)
    except Exception as exc:
        print("User-token exchange failed:", type(exc).__name__)
        return 1
    long_token = long_user.get("access_token") or ""
    print("long_lived_user expires_in_seconds=", long_user.get("expires_in"))
    _upsert_env("META_USER_ACCESS_TOKEN", long_token)
    print("saved long-lived User token to .env (not printed)")

    app_token = f"{app_id}|{app_secret}"
    probe = _get(
        f"{GRAPH}/debug_token?" + urllib.parse.urlencode({"input_token": long_token}),
        token=app_token,
    )
    probe_data = probe.get("data") or {}
    print("token_type=", probe_data.get("type"))
    if probe_data.get("type") == "PAGE":
        print("META_USER_ACCESS_TOKEN is a Page token, not a User token.")
        print("Graph Explorer top box after Generate Access Token is the User token.")
        print("Saving this Page token anyway.")
        if page_id:
            _upsert_env("META_PAGE_ID", page_id)
        _upsert_env("META_PAGE_ACCESS_TOKEN", long_token)
        exp = probe_data.get("expires_at")
        if not exp:
            print("page_token_expires_at= 0  (never — this is the goal)")
        else:
            from datetime import datetime, timezone

            when = datetime.fromtimestamp(int(exp), timezone.utc).isoformat()
            print("page_token_expires_at=", exp, "UTC", when)
            print("not never-expiring; need a User token from Graph Explorer top box")
        print("wrote META_PAGE_ACCESS_TOKEN to .env (not printed)")
        return 0

    me = _get(f"{GRAPH}/me?fields=id,name", token=long_token)
    print("user_ok id_len=", len(str(me.get("id") or "")))

    accounts = _get(
        f"{GRAPH}/me/accounts?fields=id,name,access_token,tasks",
        token=long_token,
    )
    rows = accounts.get("data") or []
    page_token = ""
    chosen_id = page_id
    for row in rows:
        if page_id and str(row.get("id")) == page_id:
            page_token = row.get("access_token") or ""
            chosen_id = str(row.get("id"))
            break
    if not page_token and len(rows) == 1:
        page_token = rows[0].get("access_token") or ""
        chosen_id = str(rows[0].get("id") or "")
        print("using only Page in /me/accounts id_len=", len(chosen_id))
    if not page_token:
        print("Set META_PAGE_ID to one of these Pages you admin:")
        for row in rows:
            print(" -", row.get("id"), row.get("name"))
        return 1

    debug = _get(
        f"{GRAPH}/debug_token?" + urllib.parse.urlencode({"input_token": page_token}),
        token=app_token,
    )
    info = debug.get("data") or {}
    print("page_token_type=", info.get("type"))
    print("page_token_expires_at=", info.get("expires_at"), "(0 means never)")
    print("page_token_is_valid=", info.get("is_valid"))

    _upsert_env("META_APP_ID", app_id)
    if chosen_id:
        _upsert_env("META_PAGE_ID", chosen_id)
    _upsert_env("META_PAGE_ACCESS_TOKEN", page_token)
    print("wrote META_PAGE_ACCESS_TOKEN to .env (not printed)")
    print("put the same values on the Render web service (not in GitHub)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
