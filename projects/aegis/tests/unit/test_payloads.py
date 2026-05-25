import pytest
from app.countermeasure.payloads.library import PayloadLibrary

@pytest.fixture
def library():
    return PayloadLibrary()

def test_load_payload_templates(library):
    templates = library.get_templates("pi_injection")
    assert len(templates) > 0

def test_select_payload_by_target(library):
    payload = library.select_payload("pi_injection", "html")
    assert payload is not None
    assert "{INJECTION_POINT}" in payload.template

def test_select_payload_exacts_match(library):
    """When target_type matches, return template with that type, not first template"""
    # pi-001 has target_types=["html", "javascript"]
    # pi-002 has target_types=["json", "api"]
    payload = library.select_payload("pi_injection", "json")
    assert payload is not None
    assert "json" in payload.target_types  # Should match json, not fallback to html
    assert payload.id == "pi-002"
