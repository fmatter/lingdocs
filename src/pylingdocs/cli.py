"""Console script for pylingdocs."""
import logging
import sys
from pathlib import Path
import click
import yaml
from pylingdocs.cldf import generate_autocomplete
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
from pylingdocs.helpers import load_content
from pylingdocs.helpers import new as create_new
from pylingdocs.helpers import write_readme
from pylingdocs.metadata import _load_metadata
from pylingdocs.output import check_ids
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
    contents = load_content(
        source_dir=source / CONTENT_FOLDER,
        structure_file=_get_relative_file(
            folder=source / CONTENT_FOLDER, file=STRUCTURE_FILE
        ),
    )
    metadata = _load_metadata(source / METADATA_FILE)
    create_output(
        contents,
        source,
        targets,
        ds,
        output_dir,
        metadata=metadata,
        latex=latex,
        release=release,
    )
    if CREATE_README:
        write_readme(source / METADATA_FILE, release=release)


@main.command(cls=BuildCommand)
@click.option(
    "--targets", multiple=True, default=PREVIEW, help="List of target output formats."
)
@click.option(
    "--html",
    is_flag=True,
    default=False,
    help="Serve an auto-refreshing HTML preview at localhost:8000",
)
@click.option(
    "--clld",
    is_flag=True,
    default=False,
    help="Auto-refresh the documents in your CLLD database",
)
@click.option("--refresh", default=True, help="Re-render preview on file change.")
def preview(  # pylint: disable=too-many-arguments
    source, targets, cldf, output_dir, refresh, latex, html, clld
):
    """Create a live preview using a lightweight, human-readable output format"""
    source = Path(source)
    output_dir = Path(output_dir)
    metadata = _load_metadata(source / METADATA_FILE)
    run_preview(
        cldf,
        source,
        output_dir,
        refresh=refresh,
        formats=targets,
        metadata=metadata,
        latex=latex,
        html=html,
        clld=clld,
    )


@main.command(cls=BuildCommand)
def check(source, cldf, output_dir, latex):
    del output_dir
    del latex
    ds = _load_cldf_dataset(cldf)
    structure = _load_structure(
        _get_relative_file(folder=source / CONTENT_FOLDER, file=STRUCTURE_FILE)
    )
    check_ids(source, ds, structure=structure)


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
def author_config():
    """Create a config file with default values for new pylingdocs projects"""
    val_dict = {
        "author_family_name": "Your family name",
        "author_given_name": "Your given name",
        "email": "Your e-mail address",
        "orcid": "Your ORCID",
        "affiliation": "Your institutional affiliation(s)",
    }
    for val, info in val_dict.items():
        val_dict[val] = input(f"{info}:\n")
    conf_path = Path.home() / ".config/pld"
    if not conf_path.is_dir():
        log.info(f"Creating folder {conf_path}")
    conf_path.mkdir(parents=True, exist_ok=True)
    yaml_path = conf_path / "author_config.yaml"
    log.info(f"Saving to {yaml_path}")
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(val_dict, f)


@main.command()
@click.option("--cldf", default=CLDF_MD, help="Path to metadata.json of CLDF dataset.")
@click.option("--target", default=CONTENT_FOLDER, help="Content folder.")
def sublime(cldf, target):
    ds = _load_cldf_dataset(cldf)
    generate_autocomplete(ds, target)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
