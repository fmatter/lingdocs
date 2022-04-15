import logging
import pytest
from pylingdocs.output import _load_structure, _load_content

log = logging.getLogger(__name__)


def test_structure(data, caplog):
    assert _load_structure(data / "content" / "structure.yaml") == {
        "document": {
            "title": "Test data",
            "parts": {
                "test": {"abstract": "Some text.", "title": "A test section"},
                "verbs": {"title": "Verbs"},
                "nouns": {
                    "title": "Nouns",
                    "abstract": "Some text about nouns.",
                    "parts": {
                        "possession": {
                            "title": "Nominal possession",
                            "abstract": "Another abstract",
                            "parts": {
                                "alien": {"title": "Alienable possession"},
                                "inalien": {"title": "Inalienable possession"},
                            },
                        }
                    },
                },
            },
        }
    }


def test_load_content1(data, caplog):
    with pytest.raises(SystemExit):
        _load_content()
    assert "not found" in caplog.text


def test_load_content2(data, caplog):
    with pytest.raises(SystemExit):
        _load_content(structure_file=data / "content" / "structure.yaml")
    assert "does not exist" in caplog.text


# def test_load_content3(data, caplog):
#     res, parts = _load_content(
#         structure_file=data / "content" / "structure.yaml", source_dir=data / "content"
#     )
#     assert res == {
#         "test": "## Test\n\nA little *test*.\n\n\n[src](alvarez1998split[133-134])\n[psrc](alvarez1998split[133-134])",
#         "verbs": "## Verbs\n\nSomething about verbs.",
#         "nouns": "## Nouns\n\nSomething about nouns.\nAn example?",
#         "possession": "## Nominal possession\n\nSomething about nominal possession.",
#         "alien": "### Alienable possession\nText",
#         "inalien": "### Inalienable possession\nText",
#     }
