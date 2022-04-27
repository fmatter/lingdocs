from pylingdocs.cldf import metadata


def test_table():
    assert "url" in metadata("TextTable")


def test_native():
    assert "url" in metadata("LanguageTable")
