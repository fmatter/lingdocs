from configparser import ConfigParser
from pathlib import Path
import cookiecutter


PROJECT_DIR = Path.cwd().resolve()


def remove_file(filename):
    (PROJECT_DIR / filename).unlink()


def create_file(file):
    filename = file + ".md"
    with open((PROJECT_DIR / "content" / filename), "w") as f:
        f.write(f"# {file.capitalize()} [label](sec:{file})\n\nInsert content")


if "No license" == "{{ cookiecutter.license }}":
    remove_file("LICENSE")

for i, file in enumerate({{cookiecutter.files.split(",")}}):
    create_file(file)

config = ConfigParser()
config.read(PROJECT_DIR / "pylingdocs.cfg")

path = config.get("paths", "cldf")
if not path.startswith("/"):
    path = Path("..") / path
config.set("paths", "cldf", str(path))
with open(PROJECT_DIR / "pylingdocs.cfg", "w", encoding="utf-8") as configfile:
    config.write(configfile)
