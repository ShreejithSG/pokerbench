"""Persona specs and tilt behavior."""

from pokerbench.personas import PERSONA_SPECS, get_persona_names, get_persona_spec


def test_all_personas_have_spec():
    for name in get_persona_names():
        assert get_persona_spec(name) is not None


def test_tilt_spec_exists():
    assert "tilt" in PERSONA_SPECS
    assert PERSONA_SPECS["tilt"].context_adjuster == "tilt"
