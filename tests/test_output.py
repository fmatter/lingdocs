import logging
import shutil
from lingdocs.config import CONTENT_FOLDER
from lingdocs.config import STRUCTURE_FILE

# import pytest
from lingdocs.helpers import _get_relative_file
from lingdocs.formats import builders
from lingdocs.helpers import load_content
from writio import load
from lingdocs.output import create_output
from lingdocs.formats import PlainText
from lingdocs.postprocessing import postprocess
from lingdocs.preprocessing import preprocess
from lingdocs.preprocessing import render_markdown

log = logging.getLogger(__name__)


def test_citing(dataset):
    preprocessed = preprocess(
        "[src](abbott1976estrutura[2,3,5],abbott2015dictionary[89-91; 101])"
    )
    preprocessed = PlainText().preprocess_commands(preprocessed)
    preprocessed = render_markdown(preprocessed, dataset, builder=builders["html"])
    assert (
        preprocessed
        == "[Abbott 1976](#source-abbott1976estrutura): 2,3,5, [Abbott et al. 2015](#source-abbott2015dictionary): 89-91; 101"
    )


def _unidiff_output(expected, actual):
    """
    Helper function. Returns a string containing the unified diff of two multiline strings.
    """

    import difflib

    expected = expected.splitlines(1)
    actual = actual.splitlines(1)

    diff = difflib.unified_diff(expected, actual)

    return "".join(diff)


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
        "latex": "main.tex",
        "html": "index.html",
    }
    create_output(
        contents=contents,
        source_dir=data,
        output_dir="output",
        dataset=dataset,
        formats=formats.keys(),
        structure=data / "docs/structure.yaml",
        metadata=load(data / "metadata.yaml"),
    )
    for fmt, fname in formats.items():
        print(tmp_path / f"output/{fmt}/{fname}")
        output = load(tmp_path / f"output/{fmt}/{fname}")
        test_output = load(data / f"output/{fname}")
        assert output == test_output
