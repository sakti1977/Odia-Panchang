"""Facebook / Instagram social posting unit tests (no real Meta API)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from src.meta_poster import (
    generate_facebook_message,
    generate_instagram_caption,
    meta_configured,
    post_facebook_page,
    post_instagram_feed,
    post_meta_bundle,
)
from src.social_card import generate_daily_card, public_card_url


client = TestClient(app)


def _panchang():
    return {
        "date": "2026-07-16",
        "vara": {"en": "Thursday", "or": "ଗୁରୁବାର"},
        "tithi": {"num": 2, "en": "Dwitiya", "or": "ଦ୍ୱିତୀୟା"},
        "chandra_masa": {"en": "Ashadha", "or": "ଆଷାଢ଼"},
        "paksha": {"en": "Shukla", "or": "ଶୁକ୍ଳ"},
        "nakshatra": {"en": "Ashlesha", "or": "ଆଶ୍ଲେଷା"},
        "yoga": {"en": "Siddhi", "or": "ସିଦ୍ଧି"},
        "soura_masa": {"en": "Mithuna", "or": "ମିଥୁନ"},
        "sunrise": "05:16",
        "sunset": "18:29",
        "festivals": [
            {
                "name": {"en": "Rath Yatra", "or": "ରଥ ଯାତ୍ରା"},
                "name_en": "Rath Yatra",
                "name_or": "ରଥ ଯାତ୍ରା",
                "tradition": "jagannath",
                "description": "x",
            }
        ],
        "meta": {"city": "puri"},
    }


def test_generate_card_png(tmp_path):
    path = generate_daily_card(_panchang(), None, out_dir=tmp_path)
    assert path.is_file()
    assert path.stat().st_size > 1000
    assert path.suffix == ".png"


def test_public_card_url():
    p = Path("static/social/cards/panjika_2026-07-16.png")
    url = public_card_url(p, public_base="https://example.com")
    assert url == "https://example.com/static/social/cards/panjika_2026-07-16.png"


def test_captions_include_odia():
    msg = generate_facebook_message(_panchang(), None)
    cap = generate_instagram_caption(_panchang(), None)
    assert "ଜୟ ଜଗନ୍ନାଥ" in msg
    assert "ଜୟ ଜଗନ୍ନାଥ" in cap
    assert len(cap) <= 2200


def test_facebook_logged_without_keys(monkeypatch):
    monkeypatch.delenv("META_PAGE_ID", raising=False)
    monkeypatch.delenv("META_PAGE_ACCESS_TOKEN", raising=False)
    res = post_facebook_page("hello test")
    assert res["status"] == "logged"
    assert res["platform"] == "facebook"


def test_instagram_requires_https(monkeypatch):
    monkeypatch.setenv("META_PAGE_ACCESS_TOKEN", "tok")
    monkeypatch.setenv("META_IG_USER_ID", "ig1")
    res = post_instagram_feed("cap", "http://insecure.example/x.png")
    assert res["status"] == "error"
    assert "HTTPS" in res["message"]


def test_facebook_posted_mock(monkeypatch):
    monkeypatch.setenv("META_PAGE_ID", "page1")
    monkeypatch.setenv("META_PAGE_ACCESS_TOKEN", "tok")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b'{"id":"123_456"}'
    mock_resp.json.return_value = {"id": "123_456"}

    with patch("src.meta_poster.httpx.Client") as cls:
        inst = cls.return_value.__enter__.return_value
        inst.post.return_value = mock_resp
        res = post_facebook_page("hello", image_url="https://x.test/a.png")
    assert res["status"] == "posted"
    assert res["post_id"] == "123_456"


def test_post_meta_bundle_logged(monkeypatch):
    monkeypatch.delenv("META_PAGE_ID", raising=False)
    monkeypatch.delenv("META_PAGE_ACCESS_TOKEN", raising=False)
    monkeypatch.setenv("PUBLIC_API_URL", "https://example.com")
    out = post_meta_bundle(_panchang(), None, platforms=["facebook"])
    assert out["status"] in ("logged", "partial", "error", "posted")
    assert "facebook" in out["platforms"]
    assert out["platforms"]["facebook"]["status"] == "logged"


def test_social_preview_endpoint():
    r = client.get("/social/preview")
    assert r.status_code == 200
    body = r.json()
    assert "facebook_message" in body
    assert "instagram_caption" in body
    assert body.get("date")


def test_social_post_requires_auth(monkeypatch):
    monkeypatch.delenv("TWEET_CRON_SECRET", raising=False)
    r = client.post("/social/post")
    assert r.status_code in (401, 503)


def test_social_post_with_auth_logged(monkeypatch):
    monkeypatch.setenv("TWEET_CRON_SECRET", "secret-test")
    monkeypatch.delenv("META_PAGE_ID", raising=False)
    monkeypatch.delenv("META_PAGE_ACCESS_TOKEN", raising=False)

    async def fake_social(platforms=None):
        return {
            "date": "2026-07-16",
            "social": {
                "status": "logged",
                "image_url": "https://example.com/static/x.png",
                "facebook_message": "m",
                "instagram_caption": "c",
                "platforms": {
                    "facebook": {"status": "logged", "message": "no keys"},
                    "instagram": {"status": "logged", "message": "no keys"},
                },
            },
        }

    monkeypatch.setattr("main.run_daily_social", fake_social)
    r = client.post(
        "/social/post",
        headers={"Authorization": "Bearer secret-test"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "logged"
    assert "facebook" in r.json()["platforms"]


def test_api_status_includes_meta():
    r = client.get("/api/status")
    assert r.status_code == 200
    body = r.json()
    assert "facebook" in body
    assert "instagram" in body
