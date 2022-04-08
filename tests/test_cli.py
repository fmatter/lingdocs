import logging
from pathlib import Path
from click.testing import CliRunner
from pylingdocs.cli import build
from pylingdocs.cli import main
from pylingdocs.cli import new
from pylingdocs.cli import preview


log = logging.getLogger(__name__)

try:
    from importlib.resources import files  # pragma: no cover
except ImportError:  # pragma: no cover
    from importlib_resources import files  # pragma: no cover

data = files("pylingdocs") / "tests/data"


def test_main():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Usage: " in result.output


def test_build(caplog, dataset, md_path, tmpdir, data):
    runner = CliRunner()

    # try running on empty
    result = runner.invoke(build)
    assert result.exit_code == 0
    assert "Please specify " in caplog.text

    # with a dataset
    result = runner.invoke(
        build,
        ["--cldf", md_path, "--output-dir", tmpdir, "--source", data / "contents"],
    )
    output_formats = list((x.name for x in Path(tmpdir).iterdir() if x.is_dir()))
    assert "plain" in output_formats
    assert "latex" in output_formats
    assert "html" in output_formats
    assert "github" in output_formats


def test_preview(caplog, dataset, md_path, tmpdir, data):
    runner = CliRunner()

    # try running on empty
    result = runner.invoke(preview)
    assert result.exit_code == 0
    assert "Please specify " in caplog.text


def test_new(caplog, md_path, tmpdir, data):
    runner = CliRunner()
    result = runner.invoke(new)
    assert result.exit_code == 0
