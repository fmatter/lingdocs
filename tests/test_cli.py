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


log = logging.getLogger(__name__)


def test_main():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Usage: " in result.output


def test_cli_build(caplog, tmp_path, md_path, data, monkeypatch):
    runner = CliRunner()

    monkeypatch.chdir(tmp_path)

    # add tables
    shutil.copytree(data / "tables", tmp_path / "tables")
    runner.invoke(build, args=["--cldf", md_path, "--source", data])
    assert "Building" in caplog.text

    output_formats = [x.name for x in (tmp_path / "output").iterdir()]

    assert "plain" in output_formats
    assert "latex" in output_formats
    assert "html" in output_formats
    assert "mkdocs" in output_formats

    for x in tmp_path.iterdir():
        if "CITATION" in x.name:
            assert "Florian" in open(x).read()


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
    shutil.copytree(md_path.parents[0], tmpdir / md_path.parents[0].name)
    monkeypatch.chdir(tmpdir)
    runner = CliRunner()
    result = runner.invoke(new)
    assert result.exit_code == 0
    assert "content" in [x.name for x in (Path(tmpdir) / "new-pld-document").iterdir()]


def test_author(tmp_path, monkeypatch, caplog):
    def mockreturn():
        return tmp_path

    monkeypatch.setattr("builtins.input", lambda _: "Mark")
    monkeypatch.setattr(Path, "home", mockreturn)
    runner = CliRunner()
    runner.invoke(author_config, catch_exceptions=False)
    assert "Saving to" in caplog.text
    assert (Path.home() / ".config/pld/author_config.yaml").is_file()
