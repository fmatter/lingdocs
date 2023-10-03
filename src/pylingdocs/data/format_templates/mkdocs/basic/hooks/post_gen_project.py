from pathlib import Path
from shutil import copy
from writio import dump
from writio import load
from pylingdocs.helpers import extract_chapters


try:
    from importlib.resources import files  # pragma: no cover
except ImportError:  # pragma: no cover
    from importlib_resources import files  # pragma: no cover

WEB_DIR = files("pylingdocs") / "data/web"


for filename in [
    "examples.css",
    "examples.js",
    "glossing.js",
    "styling.css",
    "crossref.js",
    "glossing.css",
    "alignment.css",
    "alignment.js",
    "tables.css",
]:
    source = Path(WEB_DIR / filename)
    target = Path("docs/assets/")
    copy(source, target)

chapters = extract_chapters(load("docs/index.md"), mode="pandoc")
for i, (k, v) in enumerate(chapters.items()):
    dump(v, f"docs/{k}.md")
index = """{{cookiecutter.get("landingpage", "")}}""" or "{{cookiecutter.abstract}}"
dump(index, "docs/index.md")
