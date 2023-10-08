import logging
import shutil
from pylingdocs.config import CONTENT_FOLDER
from pylingdocs.config import STRUCTURE_FILE

# import pytest
from pylingdocs.helpers import _get_relative_file
from pylingdocs.helpers import _load_structure
from pylingdocs.helpers import load_content
from writio import load
from pylingdocs.output import create_output
from pylingdocs.formats import PlainText
from pylingdocs.postprocessing import postprocess
from pylingdocs.metadata import _load_metadata
from pylingdocs.preprocessing import preprocess
from pylingdocs.preprocessing import render_markdown

log = logging.getLogger(__name__)


def test_structure(data, caplog):
    assert _load_structure(data / "content" / "structure.yaml") == {
        "intro": {},
        "markdown": {},
        "data": {},
        "examples": {},
        "sources": {},
    }


def test_citing(dataset):
    preprocessed = preprocess(
        "[src](abbott1976estrutura[2,3,5],abbott2015dictionary[89-91; 101])"
    )
    preprocessed = PlainText().preprocess_commands(preprocessed)
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
    formats = {
        "plain": "document.txt",
        "mkdocs": "mkdocs.yml",
        "latex": "main.tex",
        "html": "index.html",
    }
    create_output(
        contents=contents,
        source_dir=data,
        output_dir="output",
        dataset=dataset,
        formats=formats.keys(),
        structure=data / "content/structure.yaml",
        metadata=_load_metadata(data / "metadata.yaml"),
    )

    for fmt, fname in formats.items():
        output = load(tmp_path / f"output/{fmt}/{fname}")
        test_output = load(data / f"output/{fname}")
        assert output == test_output
