"""Console script for lingdocs."""
import logging
import sys
from pathlib import Path

import click
from writio import dump, load

from lingdocs.cldf import create_cldf, generate_autocomplete
from lingdocs.config import CONTENT_FOLDER, STRUCTURE_FILE, config
from lingdocs.helpers import _get_relative_file, load_cldf_dataset, load_content
from lingdocs.helpers import new as create_new
from lingdocs.helpers import write_readme
from lingdocs.output import check_abbrevs, check_ids, clean_output
from lingdocs.output import compile_latex as cmplatex
from lingdocs.output import create_output
from lingdocs.output import preview as run_preview
from lingdocs.output import update_structure as do_update_structure
from lingdocs.preprocessing import preprocess_cldfviz

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
                    default=config["paths"]["output"],
                    show_default=True,
                    help="Folder where output is generated.",
                    type=click.Path(path_type=Path),
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
                    default=".",
                    show_default=True,
                    help="Source folder to process.",
                    type=click.Path(exists=True, path_type=Path),
                ),
                click.core.Option(
                    ("--cldf",),
                    help="Path to metadata.json of CLDF dataset.",
                ),
            ]
        )


@main.command(cls=BuildCommand)
@click.option(
    "--targets",
    multiple=True,
    default=None,
    help="List of target output formats.",
)
@click.option(
    "--release",
    is_flag=True,
    default=False,
    help="Prepare for a citeable release",
    show_default=True,
)
def build(source, targets, cldf, output_dir, release):
    """Create formatted output of lingdocs project."""
    source = Path(source)
    config.load_from_dir(source)
    if not cldf:
        cldf = config["source"] / config["paths"]["cldf"]
    contents = load_content(
        source_dir=source / CONTENT_FOLDER,
        structure_file=source / CONTENT_FOLDER / STRUCTURE_FILE,
    )
    ds = load_cldf_dataset(cldf, source_dir=source)
    metadata = load(source / "metadata.yaml")
    targets = targets or config["output"]["build"]
    if not isinstance(targets, list) and not isinstance(targets, tuple):
        targets = [targets]
    create_output(
        contents,
        source,
        targets,
        ds,
        output_dir,
        metadata=metadata,
        release=release,
    )
    if config["output"]["readme"]:
        write_readme(source / "metadata.yaml", release=release)
    if config["input"]["sublime"]:
        generate_autocomplete(ds, source / "docs")


@main.command(cls=BuildCommand)
@click.option(
    "--target",
    default=None,
    help="Output format for the preview.",
)
@click.option(
    "--refresh",
    default=True,
    help="Re-render preview on file change.",
    show_default=True,
)
def preview(source, target, cldf, output_dir, refresh):
    """Create a live preview using a lightweight, human-readable output format"""
    source = Path(source)
    config.load_from_dir(source)
    config["paths"]["output"] = output_dir
    target = target or config["output"]["preview"]
    if cldf is None:
        cldf = config["paths"]["cldf"]
    contents = load_content(
        source_dir=source / CONTENT_FOLDER,
        structure_file=source / CONTENT_FOLDER / STRUCTURE_FILE,
    )
    ds = load_cldf_dataset(cldf, source_dir=source)
    metadata = load(source / "metadata.yaml") or {}
    from lingdocs.formats import builders

    run_preview(
        dataset=ds,
        source_dir=source,
        output_dir=output_dir,
        refresh=refresh,
        builder=builders[target](),
        metadata=metadata,
    )


@main.command(cls=BuildCommand)
def check(source, cldf, output_dir):
    config.load_from_dir(source)
    del output_dir
    if cldf is None:
        cldf = config["paths"]["cldf"]
    ds = load_cldf_dataset(cldf)
    contents = load_content(
        source_dir=source / CONTENT_FOLDER,
        structure_file=_get_relative_file(
            folder=source / CONTENT_FOLDER, file=STRUCTURE_FILE
        ),
    )
    check_ids(contents, ds, source)
    check_abbrevs(ds, source, "\n".join([x["content"] for x in contents.values()]))


@main.command(cls=BuildCommand)
@click.option(
    "--add",
    default=None,
    multiple=True,
    help="Additional documents",
    type=click.Path(exists=True, path_type=Path),
)
def cldf(source, cldf, output_dir, add):
    config.load_from_dir(source)
    cldf = cldf or config["source"] / config["paths"]["cldf"]
    ds = load_cldf_dataset(cldf)
    contents = load_content(
        source_dir=source / CONTENT_FOLDER,
        structure_file=_get_relative_file(
            folder=source / CONTENT_FOLDER, file=STRUCTURE_FILE
        ),
    )
    add_docs = []
    for add_doc in add:
        with open(add_doc, "r", encoding="utf-8") as f:
            content = f.read()
            add_docs.append(
                {
                    "ID": add_doc.stem,
                    "Name": add_doc.stem.capitalize(),
                    "Description": "".join(preprocess_cldfviz(content)),
                }
            )
    create_cldf(
        contents,
        ds,
        source,
        output_dir,
        metadata_file=config["source"] / "metadata.yaml",
        add_documents=add_docs,
    )


@main.command()
def update_structure():
    do_update_structure()


@main.command(cls=OutputCommand)
def compile_latex(output_dir):  # pragma: no cover
    """Compile the generated LaTeX output"""
    cmplatex(output_dir=output_dir)


@main.command(cls=OutputCommand)
def clean(output_dir):  # pragma: no cover
    """Compile the generated LaTeX output"""
    clean_output(output_dir=output_dir)


@main.command()
def new():
    """Create a new lingdocs project."""
    create_new()


@main.command()
def author_config():
    """Create a config file with default values for new lingdocs projects"""
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
    dump(val_dict, yaml_path)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
