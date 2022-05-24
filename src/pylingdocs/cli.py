"""Console script for pylingdocs."""
import logging
import sys
from pathlib import Path
import click
from pylingdocs.cldf import generate_autocomplete as autogen
from pylingdocs.config import BUILDERS
from pylingdocs.config import CLDF_MD
from pylingdocs.config import CONTENT_FOLDER
from pylingdocs.config import CREATE_README
from pylingdocs.config import METADATA_FILE
from pylingdocs.config import OUTPUT_DIR
from pylingdocs.config import PREVIEW
from pylingdocs.config import STRUCTURE_FILE
from pylingdocs.helpers import _get_relative_file
from pylingdocs.helpers import _load_cldf_dataset
from pylingdocs.helpers import _load_structure
from pylingdocs.helpers import new as create_new
from pylingdocs.helpers import write_readme
from pylingdocs.metadata import _read_metadata_file
from pylingdocs.output import clean_output
from pylingdocs.output import compile_latex as cmplatex
from pylingdocs.output import create_output
from pylingdocs.output import run_preview
from pylingdocs.output import update_structure as do_update_structure


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
                    ("--source",), default=".", help="Source folder to process."
                ),
                click.core.Option(
                    ("--cldf",),
                    default=CLDF_MD,
                    help="Path to metadata.json of CLDF dataset.",
                ),
                click.core.Option(
                    ("--latex",),
                    is_flag=True,
                    default=False,
                    help="Automatically compile the generated LaTeX",
                ),
            ]
        )


@main.command(cls=BuildCommand)
@click.option(
    "--targets", multiple=True, default=BUILDERS, help="List of target output formats."
)
@click.option(
    "--release", is_flag=True, default=False, help="Prepare for a citeable release"
)
def build(
    source, targets, cldf, output_dir, latex, release
):  # pylint: disable=too-many-arguments
    """Create formatted output of pylingdocs project."""
    source = Path(source)
    output_dir = Path(output_dir)
    ds = _load_cldf_dataset(cldf)
    metadata = _read_metadata_file(source / METADATA_FILE)
    structure = _load_structure(
        _get_relative_file(folder=source / CONTENT_FOLDER, file=STRUCTURE_FILE)
    )
    create_output(
        source,
        targets,
        ds,
        output_dir,
        structure=structure,
        metadata=metadata,
        latex=latex,
    )
    if CREATE_README:
        write_readme(source / METADATA_FILE, release=release)


@main.command(cls=BuildCommand)
@click.option(
    "--targets", multiple=True, default=PREVIEW, help="List of target output formats."
)
@click.option("--refresh", default=True, help="Re-render preview on file change.")
def preview(  # pylint: disable=too-many-arguments
    source, targets, cldf, output_dir, refresh, latex
):
    """Create a live preview using a lightweight, human-readable output format"""
    source = Path(source)
    output_dir = Path(output_dir)
    ds = _load_cldf_dataset(cldf)
    metadata = _read_metadata_file(METADATA_FILE)
    structure = _load_structure(_get_relative_file(folder=source, file=STRUCTURE_FILE))
    run_preview(
        refresh=refresh,
        source_dir=source,
        formats=targets,
        dataset=ds,
        output_dir=output_dir,
        structure=structure,
        metadata=metadata,
        latex=latex,
    )


@main.command()
def update_structure():
    do_update_structure()


@main.command(cls=OutputCommand)
def compile_latex(output_dir):  # pragma: no cover
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


@main.command()
@click.option("--cldf", default=CLDF_MD, help="Path to metadata.json of CLDF dataset.")
@click.option("--target", default=CONTENT_FOLDER, help="Content folder.")
def sublime(cldf, target):
    ds = _load_cldf_dataset(cldf)
    autogen(ds, target)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
