"""Facebook / Instagram social posting unit tests (no real Meta API)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from main import app
from src.meta_poster import (
    GraphAPIError,
    generate_facebook_message,
    generate_instagram_caption,
    post_facebook_page,
    post_instagram_feed,
    post_meta_bundle,
    post_to_meta,
)
from src.social_card import generate_daily_card, generate_story_card, public_card_url
from src.tweet_generator import CAPTION_MAX_LEN, caption_fingerprint, generate_social_caption


client = TestClient(app)

PAGE_ENV = {
    "META_PAGE_ID": "page1",
    "META_PAGE_ACCESS_TOKEN": "token1",
    "META_IG_USER_ID": "",
}


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


def test_generate_card_jpeg(tmp_path):
    path = generate_daily_card(_panchang(), None, out_dir=tmp_path)
    assert path.is_file()
    assert path.stat().st_size > 1000
    assert path.suffix == ".jpg"
    story = generate_story_card(_panchang(), None, feed_path=path, out_dir=tmp_path)
    assert story.is_file()
    assert story.stat().st_size > 1000
    assert "_story.jpg" in story.name


def test_card_lines_avoid_glyphs_missing_from_noto_sans_oriya():
    """Regression guard: Noto Sans Oriya (the card's rendering font) has no
    Latin letters and no U+00B7 middot. Either one renders as a tofu box
    (□) on the published card instead of the intended character — this bit
    the daily card before (see social_card._line docstring). Use the Odia
    danda (।) for separators and keep every card line in Odia script."""
    from src.social_card import _line

    lines = _line(_panchang(), None)
    for text in lines:
        assert "·" not in text, f"middot has no glyph in Noto Sans Oriya: {text!r}"
        assert not any(c.isascii() and c.isalpha() for c in text), (
            f"Latin letters have no glyph in Noto Sans Oriya: {text!r}"
        )


def test_public_card_url():
    p = Path("static/social/cards/panjika_2026-07-16.jpg")
    url = public_card_url(p, public_base="https://example.com")
    assert url == "https://example.com/static/social/cards/panjika_2026-07-16.jpg"


def test_captions_include_odia_and_fit_instagram():
    msg = generate_facebook_message(_panchang(), None)
    cap = generate_instagram_caption(_panchang(), None)
    assert "ଜୟ ଜଗନ୍ନାଥ" in msg
    assert "ଓଡ଼ିଆ ପଞ୍ଜିକା" in msg
    assert "16 ଜୁଲାଇ 2026" in msg
    assert "ରଥ ଯାତ୍ରା" in cap
    assert len(cap) <= CAPTION_MAX_LEN
    assert caption_fingerprint(msg) == caption_fingerprint(cap)
    assert "16 ଜୁଲାଇ 2026" in caption_fingerprint(msg)


def test_social_caption_not_twitter_truncated():
    """Facebook/Instagram caption is allowed to exceed Twitter's 280 chars."""
    p = _panchang()
    enrichment = {
        "astronomical": {
            "special_day_type": "normal",
            "muhurtas": {
                "rahu_kalam": "07:00–08:37",
                "abhijit_muhurta": "11:25–12:17",
            },
        },
        "cultural": {
            "jagannath_significance": {"or": "ଆଜି ଶ୍ରୀମନ୍ଦିରରେ ରଥ ଯାତ୍ରା ନୀତି।", "en": "x"},
            "fasting_guidance": {
                "recommended": True,
                "description_or": "ଉପବାସ କଲେ ଫଳ ମିଳେ।",
            },
            "odia_proverb": {"text_or": "ଧର୍ମର ଜୟ ହୁଏ।"},
        },
    }
    cap = generate_social_caption(p, enrichment)
    assert "ରାହୁ କାଳ" in cap
    assert "ଅଭିଜିତ" in cap
    assert "ଆଜି ଶ୍ରୀମନ୍ଦିରରେ" in cap
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


def test_post_meta_bundle_logged(monkeypatch):
    monkeypatch.delenv("META_PAGE_ID", raising=False)
    monkeypatch.delenv("META_PAGE_ACCESS_TOKEN", raising=False)
    monkeypatch.setenv("PUBLIC_API_URL", "https://example.com")
    out = post_meta_bundle(_panchang(), None, platforms=["facebook"])
    assert out["status"] == "logged"
    assert "facebook" in out["platforms"]
    assert out["platforms"]["facebook"]["status"] == "logged"
    assert out["card_path"].endswith(".jpg")


def test_social_preview_endpoint():
    r = client.get("/social/preview")
    assert r.status_code == 200
    body = r.json()
    assert "facebook_message" in body
    assert "instagram_caption" in body
    assert body.get("date")
    assert "ଜୟ ଜଗନ୍ନାଥ" in body["facebook_message"]


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
                "image_url": "https://example.com/static/x.jpg",
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


def test_post_to_meta_raises_when_credentials_missing(monkeypatch):
    monkeypatch.delenv("META_PAGE_ID", raising=False)
    monkeypatch.delenv("META_PAGE_ACCESS_TOKEN", raising=False)
    with pytest.raises(RuntimeError) as ctx:
        post_to_meta("some caption")
    assert "META_PAGE_ID" in str(ctx.value)
    assert "META_PAGE_ACCESS_TOKEN" in str(ctx.value)


class TestPostToMeta:
    def setup_method(self):
        self.env = mock.patch.dict(os.environ, PAGE_ENV, clear=False)
        self.env.start()
        self.ig_linked = False
        self.fb_recent: list[str] = []
        self.ig_recent: list[str] = []
        self.container_status = "FINISHED"
        self.get = mock.patch("src.meta_poster._graph_get", side_effect=self._get).start()
        mock.patch("src.meta_poster._graph_get_retry", side_effect=self._get).start()
        self.post = mock.patch("src.meta_poster._graph_post", side_effect=self._post).start()
        self.multipart = mock.patch(
            "src.meta_poster._graph_post_multipart",
            return_value={"id": "photo1", "post_id": "fbpost1"},
        ).start()
        self.host = mock.patch(
            "src.meta_poster._host_image_temporarily",
            return_value="https://litterbox.catbox.moe/img.jpg",
        ).start()

    def teardown_method(self):
        mock.patch.stopall()
        self.env.stop()

    def _get(self, path, token, params=None):
        params = params or {}
        fields = params.get("fields", "")
        if "instagram_business_account" in fields:
            if self.ig_linked:
                return {"name": "ଓଡ଼ିଆ ପଞ୍ଜିକା", "instagram_business_account": {"id": "ig1"}}
            return {"name": "ଓଡ଼ିଆ ପଞ୍ଜିକା"}
        if path.endswith("/posts"):
            return {"data": [{"message": m} for m in self.fb_recent]}
        if path.endswith("/media") and "caption" in fields:
            return {"data": [{"caption": c} for c in self.ig_recent]}
        if "images" in fields:
            return {
                "images": [
                    {
                        "source": "https://scontent.xx.fbcdn.net/panchang.jpg",
                        "width": 1080,
                        "height": 1350,
                    }
                ]
            }
        if "status_code" in fields:
            return {"status_code": self.container_status}
        return {}

    def _post(self, path, token, params=None):
        if path.endswith("/feed"):
            return {"id": "fbpost1"}
        if path.endswith("/media_publish"):
            return {"id": "igmedia1"}
        if path.endswith("/media"):
            return {"id": "container1"}
        return {"id": "unknown"}

    def test_posts_text_only_facebook_when_no_image(self):
        self.ig_linked = True
        result = post_to_meta("some caption")
        self.post.assert_any_call("/page1/feed", "token1", {"message": "some caption"})
        self.multipart.assert_not_called()
        assert result["facebook"]["id"] == "fbpost1"
        assert result["instagram"]["reason"] == "no_image"

    def test_posts_facebook_photo_when_image_provided(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as handle:
            handle.write(b"jpeg-bytes-not-empty")
            handle.flush()
            result = post_to_meta("some caption", image_path=handle.name)
        self.multipart.assert_called_once()
        args, kwargs = self.multipart.call_args
        assert args[0] == "/page1/photos"
        assert kwargs["fields"]["message"] == "some caption"
        assert result["facebook"]["id"] == "photo1"

    def test_instagram_publishes_as_story(self):
        self.ig_linked = True
        with tempfile.NamedTemporaryFile(suffix=".jpg") as handle:
            handle.write(b"jpeg-bytes-not-empty")
            handle.flush()
            result = post_to_meta("some caption", image_path=handle.name, story_path=handle.name)
        media_calls = [call for call in self.post.call_args_list if call.args[0] == "/ig1/media"]
        assert len(media_calls) == 1
        assert media_calls[0].args[2]["media_type"] == "STORIES"
        assert media_calls[0].args[2]["image_url"] == "https://scontent.xx.fbcdn.net/panchang.jpg"
        assert "caption" not in media_calls[0].args[2]
        self.post.assert_any_call("/ig1/media_publish", "token1", {"creation_id": "container1"})
        assert self.multipart.call_args.kwargs["fields"].get("published") == "false"
        self.host.assert_not_called()
        assert result["instagram"]["id"] == "igmedia1"

    def test_instagram_falls_back_to_temp_host_when_cdn_missing(self):
        self.ig_linked = True

        def get_without_cdn(path, token, params=None):
            params = params or {}
            if "images" in params.get("fields", ""):
                return {"images": []}
            return self._get(path, token, params)

        mock.patch("src.meta_poster._graph_get_retry", side_effect=get_without_cdn).start()
        with tempfile.NamedTemporaryFile(suffix=".jpg") as handle:
            handle.write(b"jpeg-bytes-not-empty")
            handle.flush()
            post_to_meta("some caption", image_path=handle.name)
        self.host.assert_called_once()
        media_calls = [call for call in self.post.call_args_list if call.args[0] == "/ig1/media"]
        assert media_calls[0].args[2]["image_url"] == "https://litterbox.catbox.moe/img.jpg"

    def test_skips_facebook_when_already_posted_today(self):
        self.fb_recent = [
            "🌸 ଓଡ଼ିଆ ପଞ୍ଜିକା | 16 ଜୁଲାଇ 2026\nrest of yesterday's post would not match"
        ]
        caption = "🙏 ଜୟ ଜଗନ୍ନାଥ 🙏\n🌸 ଓଡ଼ିଆ ପଞ୍ଜିକା | 16 ଜୁଲାଇ 2026\nଗୁରୁବାର"
        result = post_to_meta(caption)
        self.post.assert_not_called()
        self.multipart.assert_not_called()
        assert result["facebook"]["reason"] == "already_posted"

    def test_facebook_success_instagram_failure_still_raises(self):
        self.ig_linked = True

        def post_ig_fails(path, token, params=None):
            if path.endswith("/media"):
                raise GraphAPIError("bad image_url")
            return self._post(path, token, params)

        self.post.side_effect = post_ig_fails
        with tempfile.NamedTemporaryFile(suffix=".jpg") as handle:
            handle.write(b"jpeg-bytes-not-empty")
            handle.flush()
            with pytest.raises(RuntimeError) as ctx:
                post_to_meta("some caption", image_path=handle.name)
        assert "Instagram" in str(ctx.value)
        assert self.multipart.call_count >= 1

    def test_wraps_graph_errors_in_runtime_error(self):
        self.post.side_effect = GraphAPIError("boom", code=190)
        with pytest.raises(RuntimeError) as ctx:
            post_to_meta("some caption")
        assert "Facebook: boom" in str(ctx.value)

    def test_uses_explicit_ig_user_id_env(self):
        self.ig_linked = True
        with mock.patch.dict(os.environ, {**PAGE_ENV, "META_IG_USER_ID": "ig-from-env"}):
            with tempfile.NamedTemporaryFile(suffix=".jpg") as handle:
                handle.write(b"jpeg-bytes-not-empty")
                handle.flush()
                post_to_meta("some caption", image_path=handle.name)
        paths = [call.args[0] for call in self.post.call_args_list]
        assert "/ig-from-env/media" in paths
        assert "/ig-from-env/media_publish" in paths
