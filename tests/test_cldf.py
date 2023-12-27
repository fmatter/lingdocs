from lingdocs.helpers import table_metadata


def test_native():
    assert "url" in table_metadata("LanguageTable")
