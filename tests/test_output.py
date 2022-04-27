import logging

# import pytest
from pylingdocs.helpers import _load_structure
from pylingdocs.output import create_output
import shutil


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


def test_build(data, dataset, caplog, monkeypatch, tmp_path):

    shutil.copytree(data / "tables", tmp_path / "tables")
    monkeypatch.chdir(tmp_path)

    create_output(
        source_dir=data / "content/",
        output_dir="output",
        dataset=dataset,
        formats=["plain", "latex"],
        structure=data / "content/structure.yaml",
        metadata={"project_title": "pylingdocs demo", "author": "Florian Matter"},
    )

    plain_output = open(tmp_path / "output/plain/document.txt").read()
    assert "tɨ-mami-n ɨna" in plain_output
    assert "4.  numbered" in plain_output
    assert "texts: “Ekïrï”" in plain_output
    assert "(ekiri-1) Ikpeng" in plain_output
    assert "morphemes: -se" in plain_output

    latex_output = open(tmp_path / "output/latex/main.tex").read()
    assert "tɨ-mami-n ɨna" in latex_output
    assert (
        """\\item
  numbered"""
        in latex_output
    )
    assert "texts: ``Ekïrï''" in latex_output
    assert "<ekiri-1> Ikpeng" in latex_output
    assert "morphemes: \\obj{-se}" in latex_output
