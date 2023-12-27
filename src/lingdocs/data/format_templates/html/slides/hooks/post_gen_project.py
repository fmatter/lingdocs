from pathlib import Path
from shutil import copy

try:
    from importlib.resources import files  # pragma: no cover
except ImportError:  # pragma: no cover
    from importlib_resources import files  # pragma: no cover

WEB_DIR = files("lingdocs") / "data/web"


for filename in [
    "examples.css",
    "examples.js",
    "glossing.js",
    "crossref.js",
    "alignment.css",
    "alignment.js",
    "slides.css",
]:
    source = Path(WEB_DIR / filename)
    target = Path(".")
    copy(source, target)
