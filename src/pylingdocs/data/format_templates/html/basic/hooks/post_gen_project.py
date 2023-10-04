from pathlib import Path
from shutil import copy

try:
    from importlib.resources import files  # pragma: no cover
except ImportError:  # pragma: no cover
    from importlib_resources import files  # pragma: no cover

WEB_DIR = files("pylingdocs") / "data/web"


for filename in [
    "examples.css",
    "examples.js",
    "glossing.js",
    "glossing.css",
    "crossref.js",
    "alignment.css",
    "alignment.js",
    "tables.css",
    "styling.css",
]:
    source = Path(WEB_DIR / filename)
    target = Path(".")
    copy(source, target)
