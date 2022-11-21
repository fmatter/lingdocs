import logging
import shutil
from pylingdocs.config import CONTENT_FOLDER
from pylingdocs.config import STRUCTURE_FILE

# import pytest
from pylingdocs.helpers import _get_relative_file
from pylingdocs.helpers import _load_structure
from pylingdocs.helpers import load_content
from pylingdocs.output import create_output, PlainText
from pylingdocs.preprocessing import postprocess
from pylingdocs.preprocessing import preprocess
from pylingdocs.preprocessing import render_markdown

log = logging.getLogger(__name__)


def test_structure(data, caplog):
    assert _load_structure(data / "content" / "structure.yaml") == {
        "test": {"abstract": "Some text.", "title": "A test section"},
        "verbs": {"title": "Verbs"},
        "nouns": {"title": "Nouns", "abstract": "Some text about nouns."},
        "possession": {"title": "Nominal possession", "abstract": "Another abstract"},
        "alien": {},
        "inalien": {"title": "Inalienable possession"},
    }


def test_citing(dataset):
    preprocessed = preprocess(
        "[src](abbott1976estrutura[2,3,5],abbott2015dictionary[89-91; 101])"
    )
    preprocessed = PlainText.preprocess_commands(preprocessed)
    preprocessed = render_markdown(preprocessed, dataset, output_format="html")
    assert (
        preprocessed
        == "[Abbott 1976](#source-abbott1976estrutura): 2,3,5, [Abbott et al. 2015](#source-abbott2015dictionary): 89-91; 101"
    )


def test_build(data, dataset, caplog, monkeypatch, tmp_path):

    shutil.copytree(data / "tables", tmp_path / "tables")
    shutil.copytree(data / "figures", tmp_path / "figures")

    monkeypatch.chdir(tmp_path)

    contents = load_content(
        source_dir=data / CONTENT_FOLDER,
        structure_file=_get_relative_file(
            folder=data / CONTENT_FOLDER, file=STRUCTURE_FILE
        ),
    )

    create_output(
        contents=contents,
        source_dir=data,
        output_dir="output",
        dataset=dataset,
        formats=["plain", "latex", "clld", "html"],
        structure=data / "content/structure.yaml",
        metadata={"project_title": "pylingdocs demo", "author": "Florian Matter"},
    )

    plain_output = open(tmp_path / "output/plain/document.txt").read()
    log.warning(plain_output)
    assert "tɨ-mami-n      ɨna" in plain_output
    assert "4.  numbered" in plain_output
    assert "texts: “Ekïrï”" in plain_output
    assert "(1) Ikpeng" in plain_output
    assert "(my_custom_id) Ikpeng" in plain_output
    assert "morphemes: -se" in plain_output

    latex_output = open(tmp_path / "output/latex/main.tex").read()
    assert "tɨ-mami-n ɨna" in latex_output
    assert (
        """\\item
  numbered"""
        in latex_output
    )
    assert "texts: ``Ekïrï''" in latex_output
    assert "ex Ikpeng" in latex_output
    assert "label{my_custom_id}" in latex_output
    assert "morphemes: \\obj{-se}" in latex_output

    latex_output = open(tmp_path / "output/html/index.html").read()
