"""Phase 3: Odisha peetha cities + tradition default resolver."""

import pytest

from src.locations import (
    ODISHA_CITIES,
    TRADITION_DEFAULT_CITY,
    get_city_info,
    list_all_cities,
    resolve_city,
)


REQUIRED_ODISHA = {
    "bhubaneswar",
    "puri",
    "jajpur",
    "cuttack",
    "berhampur",
    "sambalpur",
    "rourkela",
    "balasore",
    "konark",
}


def test_required_odisha_cities_present():
    for key in REQUIRED_ODISHA:
        assert key in ODISHA_CITIES, f"missing {key}"
        info = ODISHA_CITIES[key]
        assert "name_or" in info and info["name_or"]
        assert 17.5 < info["lat"] < 23.0
        assert 81.5 < info["lon"] < 88.0
        assert info["tz"] == 5.5


def test_puri_and_jajpur_coords_distinct():
    puri = get_city_info("puri")
    jajpur = get_city_info("jajpur")
    bbsr = get_city_info("bhubaneswar")
    assert puri and jajpur and bbsr
    assert puri["lat"] != jajpur["lat"] or puri["lon"] != jajpur["lon"]
    assert abs(puri["lat"] - 19.8135) < 0.01
    assert abs(jajpur["lat"] - 20.85) < 0.05


def test_tradition_default_city_map():
    assert TRADITION_DEFAULT_CITY["jagannath"] == "puri"
    assert TRADITION_DEFAULT_CITY["biraja"] == "jajpur"
    assert TRADITION_DEFAULT_CITY["common"] == "bhubaneswar"


def test_resolve_city_explicit_wins():
    info = resolve_city(city="cuttack", tradition="biraja")
    assert info["key"] == "cuttack"
    assert info["name"] == "Cuttack"


def test_resolve_city_tradition_defaults():
    assert resolve_city(tradition="jagannath")["key"] == "puri"
    assert resolve_city(tradition="biraja")["key"] == "jajpur"
    assert resolve_city(tradition="common")["key"] == "bhubaneswar"
    assert resolve_city()["key"] == "bhubaneswar"


def test_resolve_city_unknown_raises():
    with pytest.raises(ValueError, match="Unknown city"):
        resolve_city(city="narnia")
    with pytest.raises(ValueError, match="Unknown tradition"):
        resolve_city(tradition="martian")


def test_list_all_cities_includes_keys():
    keys = {c["key"] for c in list_all_cities()}
    assert REQUIRED_ODISHA <= keys
