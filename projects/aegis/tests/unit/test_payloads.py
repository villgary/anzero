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
