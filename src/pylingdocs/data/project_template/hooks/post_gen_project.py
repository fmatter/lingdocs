from configparser import ConfigParser
from pathlib import Path
import cookiecutter
from pylingdocs.cldf import generate_autocomplete
from pylingdocs.helpers import _load_cldf_dataset


PROJECT_DIR = Path.cwd().resolve()


def remove_file(filename):
    (PROJECT_DIR / filename).unlink()


def create_file(file):
    filename = file + ".md"
    filepath = PROJECT_DIR / "content" / filename
    with open(filepath, "w") as f:
        f.write(
            f"# {file.capitalize()} [label]({file})\n\nInsert your content here (find this file at {filepath.resolve()})"
        )


if "No license" == "{{ cookiecutter.license }}":
    remove_file("LICENSE")

for i, file in enumerate({{cookiecutter.files.split(",")}}):
    create_file(file)

# add .. to path if relative to pylingdocs project
config = ConfigParser()
config.read(PROJECT_DIR / "pylingdocs.cfg")
path = "{{ cookiecutter.cldf }}"
if not path.startswith("/"):
    path = Path("..") / path
config.set("paths", "cldf", str(path))
with open(PROJECT_DIR / "pylingdocs.cfg", "w", encoding="utf-8") as configfile:
    config.write(configfile)

if "Yes" == "{{ cookiecutter.use_sublime_text }}":
    ds = _load_cldf_dataset(path)
    generate_autocomplete(ds, PROJECT_DIR)
