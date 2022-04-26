import logging
from click.testing import CliRunner
from pylingdocs.cli import build
from pylingdocs.cli import main
from pylingdocs.cli import new
from pylingdocs.cli import preview

log = logging.getLogger(__name__)


def test_main():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Usage: " in result.output


def test_empty_build(caplog):
    runner = CliRunner()

    # try running on empty
    result = runner.invoke(build)
    assert result.exit_code == 1
    log.debug(caplog.text)
    assert "No such" in caplog.text


# # not working right now because the build command relies on a structure.yaml
# # file and I don't know how to do that.
# def test_build(caplog, dataset, md_path, data, working_dir):
#     runner = CliRunner()

#     result = runner.invoke(
#         build,
#         ["--cldf", md_path, "--source", data / "contents"],
#     )
#     assert result.exit_code == 0
#     output_formats = list(
# (x.name for x in (working_dir / "output").iterdir() if x.is_dir())
# )
#     assert "plain" in output_formats
#     assert "latex" in output_formats
#     assert "html" in output_formats
#     assert "github" in output_formats


def test_preview(caplog, dataset, md_path, tmpdir, data):
    runner = CliRunner()

    # try running on empty
    result = runner.invoke(preview)
    assert result.exit_code == 1
    assert "No such " in caplog.text


def test_new(caplog, md_path, tmpdir, data):
    runner = CliRunner()
    result = runner.invoke(new)
    assert result.exit_code == 0
