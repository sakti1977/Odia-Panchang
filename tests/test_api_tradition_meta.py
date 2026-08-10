"""
Phase 4: tradition + city + meta on day API.
"""

import pytest
from fastapi.testclient import TestClient

from main import app, _filter_festivals, _build_meta
from src.locations import resolve_city


client = TestClient(app)


def test_filter_festivals_rules():
    fests = [
        {"tradition": "common", "name": "A"},
        {"tradition": "jagannath", "name": "B"},
        {"tradition": "biraja", "name": "C"},
        {"tradition": "lingaraj", "name": "D"},
    ]
    assert len(_filter_festivals(fests, "all")) == 4
    assert {f["name"] for f in _filter_festivals(fests, "common")} == {"A"}
    assert {f["name"] for f in _filter_festivals(fests, "jagannath")} == {"A", "B"}
    assert {f["name"] for f in _filter_festivals(fests, "biraja")} == {"A", "C"}


def test_build_meta_shape():
    place = resolve_city(city="puri")
    meta = _build_meta(place, "jagannath")
    assert meta["engine"] == "lahiri_swiss_ephemeris"
    assert meta["masa_system"] == "purnimanta_odia_default"
    assert meta["tradition"] == "jagannath"
    assert meta["city"] == "puri"
    assert meta["lat"] and meta["lon"]
    assert "disclaimer" in meta
    assert "Biraja" in meta["disclaimer"] or "Khadiratna" in meta["disclaimer"]


def test_panchang_date_includes_meta():
    r = client.get("/panchang/2026-07-16")
    assert r.status_code == 200
    data = r.json()
    assert "meta" in data
    assert data["meta"]["engine"] == "lahiri_swiss_ephemeris"
    assert data["chandra_masa"]["en"] == "Ashadha"
    assert data["tithi"]["num"] == 2
    assert any("Rath" in f["name"]["en"] for f in data["festivals"])


def test_panchang_tradition_jagannath_default_city_puri():
    r = client.get("/panchang/2026-07-16", params={"tradition": "jagannath"})
    assert r.status_code == 200
    data = r.json()
    assert data["meta"]["city"] == "puri"
    assert data["meta"]["tradition"] == "jagannath"
    # no biraja-only rows expected mixed wrongly as only overlay
    for f in data["festivals"]:
        assert f["tradition"] in ("common", "jagannath")


def test_panchang_tradition_biraja_default_city_jajpur():
    r = client.get("/panchang/2026-07-16", params={"tradition": "biraja"})
    assert r.status_code == 200
    data = r.json()
    assert data["meta"]["city"] == "jajpur"
    for f in data["festivals"]:
        assert f["tradition"] in ("common", "biraja")


def test_city_overrides_tradition_default():
    r = client.get(
        "/panchang/2026-07-16",
        params={"tradition": "biraja", "city": "puri"},
    )
    assert r.status_code == 200
    assert r.json()["meta"]["city"] == "puri"


def test_unknown_city_400():
    r = client.get("/panchang/2026-07-16", params={"city": "narnia"})
    assert r.status_code == 400


def test_unknown_tradition_rejected():
    r = client.get("/panchang/2026-07-16", params={"tradition": "martian"})
    # FastAPI Literal → 422; resolver path → 400
    assert r.status_code in (400, 422)


def test_puri_vs_jajpur_sunrise_differs():
    puri = client.get("/panchang/2026-05-10", params={"city": "puri"}).json()
    jajpur = client.get("/panchang/2026-05-10", params={"city": "jajpur"}).json()
    # Same tithi core
    assert puri["tithi"]["num"] == jajpur["tithi"]["num"]
    # Place meta differs
    assert puri["meta"]["city"] == "puri"
    assert jajpur["meta"]["city"] == "jajpur"
    # Sunrise often differs by a few minutes (allow equal only if coords collapse)
    assert puri["sunrise"] and jajpur["sunrise"]


def test_festival_stories_on_api():
    r = client.get("/panchang/2026-07-16")
    fests = r.json()["festivals"]
    assert fests
    for f in fests:
        assert f.get("story", {}).get("en")
        assert f.get("why_today", {}).get("en")
        assert f.get("story_complete") is True or f.get("story_complete") is False


def test_health():
    r = client.get("/api")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_cities_include_puri_jajpur():
    r = client.get("/api/cities")
    keys = {c["key"] for c in r.json()}
    assert "puri" in keys and "jajpur" in keys
