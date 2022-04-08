"""Console script for pylingdocs."""
import logging
import sys
from pathlib import Path
import click
from pycldf import Dataset
from pylingdocs.config import BUILDERS
from pylingdocs.config import CLDF_MD
from pylingdocs.config import CONTENT_FOLDER
from pylingdocs.config import OUTPUT_DIR
from pylingdocs.helpers import new as create_new
from pylingdocs.output import clean_output
from pylingdocs.output import compose_latex as cmplatex
from pylingdocs.output import create_output
from pylingdocs.output import run_preview


log = logging.getLogger(__name__)


@click.group()
def main():
    pass  # pragma: no cover


class OutputCommand(click.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params.extend(
            [
                click.core.Option(
                    ("--output-dir",),
                    default=OUTPUT_DIR,
                    help="Folder where output is generated.",
                )
            ]
        )


class BuildCommand(OutputCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params.extend(
            [
                click.core.Option(
                    ("--source",),
                    default=CONTENT_FOLDER,
                    help="Source folder to process.",
                ),
                click.core.Option(
                    ("--targets",),
                    multiple=True,
                    default=BUILDERS,
                    help="List of target output formats.",
                ),
                click.core.Option(
                    ("--cldf",),
                    default=CLDF_MD,
                    help="Path to metadata.json of CLDF dataset.",
                ),
            ]
        )


@main.command(cls=BuildCommand)
def build(source, targets, cldf, output_dir):
    """Create formatted output of pylingdocs project."""
    source = Path(source)
    output_dir = Path(output_dir)
    try:
        ds = Dataset.from_metadata(cldf)
    except FileNotFoundError as e:
        log.error(e)
        log.error("Please specify a path to a valid CLDF metadata file.")
        sys.exit()
    create_output(source, targets, ds, output_dir)


@main.command()
@click.option("--refresh", default=True, help="Re-render preview on file change.")
def preview(refresh):
    """Create a live preview using a lightweight, human-readable output format"""
    run_preview(refresh=refresh)


@main.command(cls=OutputCommand)
def compose_latex(output_dir):  # pragma: no cover
    """Compile the generated LaTeX output"""
    output_dir = Path(output_dir)
    cmplatex(output_dir=output_dir)


@main.command(cls=OutputCommand)
def clean(output_dir):  # pragma: no cover
    """Compile the generated LaTeX output"""
    output_dir = Path(output_dir)
    clean_output(output_dir=output_dir)


@main.command()
def new():
    """Create a new pylingdocs project."""
    create_new()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
