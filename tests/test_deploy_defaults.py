"""
E-INV-005: Deploy defaults must be Odisha, never silent Bangalore.
"""

from pathlib import Path

import yaml

import src.engine as engine


ROOT = Path(__file__).resolve().parents[1]


def test_engine_default_location_is_odisha():
    # Defaults are read at import from env; module constants reflect file defaults
    # when LOCATION_* unset. Check source defaults via reading module docstring/attrs.
    src = (ROOT / "src" / "engine.py").read_text(encoding="utf-8")
    assert 'LOCATION_LAT", "20.2961"' in src or 'LOCATION_LAT", "20.2961' in src
    assert "20.2961" in src
    assert "85.8245" in src
    # Must not hardcode Bangalore as default in engine
    assert 'LOCATION_LAT", "12.9716"' not in src


def test_render_yaml_location_is_bhubaneswar_not_bangalore():
    data = yaml.safe_load((ROOT / "render.yaml").read_text(encoding="utf-8"))
    web = next(s for s in data["services"] if s.get("name") == "odia-panjika-api")
    env = {e["key"]: e.get("value") for e in web.get("envVars", []) if "value" in e}
    assert env.get("LOCATION_NAME") == "Bhubaneswar"
    assert env.get("LOCATION_LAT") == "20.2961"
    assert env.get("LOCATION_LON") == "85.8245"
    assert float(env["LOCATION_LAT"]) > 17.5  # Odisha box
    assert float(env["LOCATION_LON"]) > 81.5
    assert "Bangalore" not in (env.get("LOCATION_NAME") or "")
    assert env.get("LOCATION_LAT") != "12.9716"
