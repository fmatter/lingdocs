from pylingdocs.cldf import metadata


def test_native():
    assert "url" in metadata("LanguageTable")
