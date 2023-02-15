from ..data_processing.parse_manifest import parse

def test_parse_manifest():
    parse("../../original_web_interface/ApplicationManifest.json")
    assert True