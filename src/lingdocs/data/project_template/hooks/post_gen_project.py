from pathlib import Path

import cookiecutter
from writio import dump, load

from lingdocs.cldf import generate_autocomplete
from lingdocs.config import CONTENT_FOLDER
from lingdocs.helpers import load_cldf_dataset

PROJECT_DIR = Path.cwd().resolve()


def remove_file(filename):
    (PROJECT_DIR / filename).unlink()


def create_file(file):
    filename = file + ".md"
    filepath = PROJECT_DIR / CONTENT_FOLDER / filename
    dump(
        f"# {file.capitalize()} [label]({file})\n\nInsert your content here (find this file at {filepath.resolve()})",
        filepath,
    )


if "No license" == "{{ cookiecutter.license }}":
    remove_file("LICENSE")

for i, file in enumerate({{cookiecutter.files.split(",")}}):
    create_file(file)

# add .. to path if relative to lingdocs project


def relativize(path):
    if not str(path).startswith("/"):
        return Path("..") / path
    return Path(path)


config = load(PROJECT_DIR / "config.yaml")
path = relativize("{{ cookiecutter.cldf }}")
config["paths"]["cldf"] = str(path)
dump(config, PROJECT_DIR / "config.yaml")

if "Yes" == "{{ cookiecutter.use_sublime_text }}":
    while not path.is_file():
        path = Path(input("Please enter a path to a metadata file: ").strip(" "))
    ds = load_cldf_dataset(path, source_dir=PROJECT_DIR)
    generate_autocomplete(ds, PROJECT_DIR)
