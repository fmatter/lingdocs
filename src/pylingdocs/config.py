from configparser import ConfigParser
from pathlib import Path
import logging

log = logging.getLogger(__name__)


try:
    from importlib.resources import files  # pragma: no cover
except ImportError:  # pragma: no cover
    from importlib_resources import files  # pragma: no cover

DATA_DIR = files("pylingdocs") / "data"

log.info("Loading configuration")

config = ConfigParser()
default_config = ConfigParser()
CONF_PATH = "pylingdocs.cfg"

default_config.read(DATA_DIR / "config.cfg")

conf_path = Path(CONF_PATH)
if conf_path.is_file():
    config.read(conf_path)
else:
    config.read(DATA_DIR / "config.cfg")


def get_config(section, label, as_path=False):
    value = config.get(section, label, fallback=default_config.get(section, label))
    if as_path:
        return Path(value)
    return value


def get_path(label):
    return get_config("PATHS", label, as_path=True)


CONTENT_FOLDER = get_path("content")
OUTPUT_DIR = get_path("output")
CLDF_MD = get_path("cldf")
TABLE_DIR = get_path("tables")
TABLE_MD = get_path("table_metadata")
OUTPUT_DIR = get_path("output")
STRUCTURE_FILE = get_path("structure_file")
BENCH = get_path("bench")

BUILDERS = ["plain", "github", "html", "latex"]
PREVIEW = ["plain"]
CITATION_FILE = "./CITATION.cff"