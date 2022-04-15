import logging
from configparser import ConfigParser
from pathlib import Path


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
        path = Path(value)
        if not path.exists():
            log.warning(
                f"{value} does not exist. Please create it or change your configuration."
            )
        return path
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

BUILDERS = get_config("OUTPUT", "builders").split(" ")
PREVIEW = get_config("OUTPUT", "preview").split(" ")
CITATION_FILE = "./CITATION.cff"

METADATA_FILE = Path("./metadata.yaml")
if not METADATA_FILE.is_file():
    log.warning("Please create a metadata file (metadata.yaml)")
    METADATA_FILE = None
