"""E-FEST-TRADITION-PARTITION and no Rath collapse."""

from src.festivals import TITHI_RULES


def test_simhadhwaja_is_biraja_not_jagannath_rath():
    biraja_names = {r[4] for r in TITHI_RULES if r[3] == "biraja"}
    jag_names = {r[4] for r in TITHI_RULES if r[3] == "jagannath"}
    assert any("Simhadhwaja" in n for n in biraja_names)
    assert not any(n == "Rath Yatra" for n in biraja_names)
    assert not any("Simhadhwaja" in n for n in jag_names)


def test_puri_chariot_cycle_is_jagannath_not_common():
    """#22 — Rath/Bahuda must not ride on common (Biraja mode isolation)."""
    by_name = {r[4]: r[3] for r in TITHI_RULES}
    assert by_name["Rath Yatra"] == "jagannath"
    assert by_name["Bahuda Yatra"] == "jagannath"


def test_every_rule_has_known_tradition():
    allowed = {"common", "jagannath", "biraja", "lingaraj"}
    for r in TITHI_RULES:
        assert r[3] in allowed, r
