import logging
from click.testing import CliRunner
from pylingdocs.cli import build
from pylingdocs.cli import main
from pylingdocs.cli import new
from pylingdocs.cli import preview, update_structure
import shutil

log = logging.getLogger(__name__)


def test_main():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Usage: " in result.output


def test_missing(caplog, tmp_path, md_path, data, monkeypatch):
    runner = CliRunner()
    # try running on empty, no CLDF metadata
    result = runner.invoke(build)
    assert result.exit_code == 1
    assert "No such" in caplog.text
    caplog.clear()

    # add CLDF, missing structure file
    result = runner.invoke(build, args=["--cldf", md_path])
    assert result.exit_code == 1
    assert "Structure file" in caplog.text
    assert "Metadata file" in caplog.text
    caplog.clear()

    # add structure
    result = runner.invoke(
        build, args=["--cldf", md_path, "--source", data / "content"]
    )
    assert result.exit_code == 1
    assert "Table file" in caplog.text


def test_build(caplog, tmp_path, md_path, data, monkeypatch):
    runner = CliRunner()

    # add tables
    shutil.copytree(data / "tables", tmp_path / "tables")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        build, args=["--cldf", md_path, "--source", data / "content"]
    )
    assert result.exit_code == 0
    assert "Rendering" in caplog.text

    output_formats = [x.name for x in (tmp_path / "output").iterdir()]

    assert "plain" in output_formats
    assert "latex" in output_formats
    assert "html" in output_formats
    assert "github" in output_formats

    for x in tmp_path.iterdir():
        if "README" in x.name or "CITATION" in x.name:
            assert "Anonymous" in open(x).read()


def test_cli_preview(caplog, tmp_path, md_path, data, monkeypatch):
    runner = CliRunner()

    # add tables
    shutil.copytree(data / "tables", tmp_path / "tables")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        preview, args=["--cldf", md_path, "--source", data / "content", "--refresh", False]
    )
    assert "Rendering preview" in caplog.text
    assert result.exit_code == 0

def test_new(caplog, md_path, tmpdir, data):
    runner = CliRunner()
    result = runner.invoke(new)
    assert result.exit_code == 0

def test_update(caplog, md_path, tmpdir, data):
    runner = CliRunner()
    result = runner.invoke(update_structure)
    assert result.exit_code == 1
    assert "Updating document " in caplog.text # making sure it tries

