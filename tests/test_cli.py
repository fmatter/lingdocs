import logging
import shutil
from pathlib import Path
from click.testing import CliRunner
from pylingdocs.cli import author_config
from pylingdocs.cli import build
from pylingdocs.cli import check
from pylingdocs.cli import main
from pylingdocs.cli import new
from pylingdocs.cli import preview
from pylingdocs.cli import sublime
from pylingdocs.cli import update_structure


log = logging.getLogger(__name__)


def test_main():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Usage: " in result.output


def test_missing(caplog, tmp_path, md_path, data, monkeypatch):
    monkeypatch.chdir(tmp_path)
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
    caplog.clear()

    # add structure
    result = runner.invoke(build, args=["--cldf", md_path, "--source", data])
    assert result.exit_code == 0
    assert "Could not find metadata" in caplog.text


def test_cli_build(caplog, tmp_path, md_path, data, monkeypatch):
    runner = CliRunner()

    monkeypatch.chdir(tmp_path)

    # add tables
    shutil.copytree(data / "tables", tmp_path / "tables")
    runner.invoke(build, args=["--cldf", md_path, "--source", data, "--release"])

    assert "Rendering" in caplog.text

    output_formats = [x.name for x in (tmp_path / "output").iterdir()]

    assert "plain" in output_formats
    assert "latex" in output_formats
    assert "html" in output_formats
    assert "github" in output_formats

    for x in tmp_path.iterdir():
        if "README" in x.name or "CITATION" in x.name:
            assert "Florian" in open(x).read()


# same with metadata file
def test_cli_metadata(caplog, tmp_path, md_path, data, monkeypatch):
    runner = CliRunner()

    monkeypatch.chdir(tmp_path)

    # add tables
    shutil.copytree(data / "tables", tmp_path / "tables")
    shutil.copy(data / "metadata.yaml", tmp_path / "metadata.yaml")
    result = runner.invoke(
        build, args=["--cldf", md_path, "--source", data, "--release"]
    )
    assert "metadata.yaml not found" not in caplog.text

    assert result.exit_code == 0
    for x in tmp_path.iterdir():
        if "README" in x.name or "CITATION" in x.name:
            assert "Florian" in open(x).read()
            assert "Zwöite" in open(x).read()


def test_cli_preview(caplog, tmp_path, md_path, data, monkeypatch):
    runner = CliRunner()

    # add tables
    shutil.copytree(data / "tables", tmp_path / "tables")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        preview, args=["--cldf", md_path, "--source", data, "--refresh", False]
    )
    assert "Rendering preview" in caplog.text
    assert result.exit_code == 0


def test_cli_check(caplog, tmp_path, md_path, data, monkeypatch):
    runner = CliRunner()

    # add tables
    shutil.copytree(data / "tables", tmp_path / "tables")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(check, args=["--cldf", md_path, "--source", data])
    assert "No missing IDs found." in caplog.text
    assert result.exit_code == 0


def test_cli_sublime(caplog, tmp_path, md_path, data, monkeypatch):
    runner = CliRunner()

    runner.invoke(sublime, args=["--cldf", md_path, "--target", tmp_path])
    assert (tmp_path / ".pld_autocomplete.json").is_file()
    assert (tmp_path / ".pld_menudata.json").is_file()


def test_new(caplog, md_path, tmpdir, data, monkeypatch):
    monkeypatch.chdir(tmpdir)
    runner = CliRunner()
    result = runner.invoke(new)
    assert result.exit_code == 0
    assert "content" in [x.name for x in (Path(tmpdir) / "new-pld-document").iterdir()]


def test_update(caplog, md_path, tmpdir, data):
    runner = CliRunner()
    result = runner.invoke(update_structure)
    assert result.exit_code == 1
    assert "Updating document " in caplog.text  # making sure it tries


def test_author(tmp_path, monkeypatch, caplog):
    def mockreturn():
        return tmp_path

    monkeypatch.setattr("builtins.input", lambda _: "Mark")
    monkeypatch.setattr(Path, "home", mockreturn)
    runner = CliRunner()
    runner.invoke(author_config, catch_exceptions=False)
    assert "Saving to" in caplog.text
    assert (Path.home() / ".config/pld/author_config.yaml").is_file()
