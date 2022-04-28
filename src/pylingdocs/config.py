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
    config.read(conf_path)  # pragma: no cover
else:
    config.read(DATA_DIR / "config.cfg")


def get_config(section, label, as_path=False, as_boolean=False):
    if as_boolean:
        return config.getboolean(section, label, fallback=default_config.getboolean(section, label))
    value = config.get(section, label, fallback=default_config.get(section, label))
    if as_path:
        path = Path(value)
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

CREATE_CFF = get_config("OUTPUT", "citation_cff", as_boolean=True)
CREATE_README = get_config("OUTPUT", "readme", as_boolean=True)

METADATA_FILE = Path("./metadata.yaml")

OUTPUT_TEMPLATES = {}
for builder in BUILDERS:
    OUTPUT_TEMPLATES[builder] = get_config(builder, "template")
