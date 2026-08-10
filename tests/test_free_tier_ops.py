"""Unit tests for free-tier ops helpers (no network)."""

import json
from unittest.mock import patch, MagicMock
from io import BytesIO

import pytest

from scripts import free_tier_ops as ops


def test_base_url_strips_slash(monkeypatch):
    monkeypatch.delenv("PUBLIC_API_URL", raising=False)
    assert ops.base_url("https://x.example.com/") == "https://x.example.com"
    monkeypatch.setenv("PUBLIC_API_URL", "https://env.example.com/")
    assert ops.base_url() == "https://env.example.com"


def test_wake_service_success_first_try():
    with patch.object(ops, "http_json", return_value=(200, {"status": "ok"})):
        assert ops.wake_service("https://example.com", max_attempts=2, initial_wait=0) is True


def test_wake_service_retries_then_ok():
    calls = {"n": 0}

    def flaky(method, url, timeout=60.0):
        calls["n"] += 1
        if calls["n"] < 3:
            return 0, {"error": "down"}
        return 200, {"status": "ok"}

    with patch.object(ops, "http_json", side_effect=flaky):
        with patch.object(ops.time, "sleep"):
            assert ops.wake_service("https://example.com", max_attempts=5, initial_wait=0.01) is True
    assert calls["n"] == 3


def test_post_tweet_posted():
    with patch.object(ops, "wake_service", return_value=True):
        with patch.object(
            ops,
            "http_json",
            return_value=(200, {"result": {"status": "posted"}, "date": "2026-08-10"}),
        ):
            assert ops.post_tweet("https://example.com", wake_first=True) == 0


def test_post_tweet_logged_is_success():
    with patch.object(ops, "wake_service", return_value=True):
        with patch.object(
            ops,
            "http_json",
            return_value=(200, {"result": {"status": "logged"}}),
        ):
            assert ops.post_tweet("https://example.com") == 0


def test_post_tweet_error_status_fails():
    with patch.object(ops, "wake_service", return_value=True):
        with patch.object(
            ops,
            "http_json",
            return_value=(200, {"result": {"status": "error", "message": "x"}}),
        ):
            assert ops.post_tweet("https://example.com", max_attempts=1) == 1


def test_cli_health(monkeypatch):
    with patch.object(ops, "health_check", return_value=0) as h:
        assert ops.main(["health", "--url", "https://x"]) == 0
        h.assert_called()


def test_scheduler_default_off_in_main():
    """Free-tier default: in-process scheduler disabled."""
    import importlib
    import os

    # Read flag helper behaviour
    from main import _env_flag

    assert _env_flag("UNSET_XYZ_FLAG_FOR_TEST", default=False) is False
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("ENABLE_INPROCESS_SCHEDULER", "false")
    assert _env_flag("ENABLE_INPROCESS_SCHEDULER", default=True) is False
    monkeypatch.setenv("ENABLE_INPROCESS_SCHEDULER", "true")
    assert _env_flag("ENABLE_INPROCESS_SCHEDULER", default=False) is True
    monkeypatch.undo()
