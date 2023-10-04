import logging
import re
from configparser import ConfigParser
from pathlib import Path

log = logging.getLogger(__name__)

try:
    from importlib.resources import files  # pragma: no cover
except ImportError:  # pragma: no cover
    from importlib_resources import files  # pragma: no cover

DATA_DIR = files("pylingdocs") / "data"
MD_LINK_PATTERN = re.compile(r"\[(?P<label>[^]]*)]\((?P<url>[^)]+)\)")
CONF_PATH = "pylingdocs.cfg"

log.debug("Loading configuration")

config = ConfigParser()
default_config = ConfigParser()
default_config.read(DATA_DIR / "config.cfg")

conf_path = Path(CONF_PATH)
if conf_path.is_file():
    config.read(conf_path)  # pragma: no cover
else:
    config.read(DATA_DIR / "config.cfg")


def get_config(section, label, as_path=False, as_boolean=False):
    if as_boolean:
        return config.getboolean(
            section, label, fallback=default_config.getboolean(section, label)
        )
    value = config.get(
        section, label, fallback=default_config.get(section, label, fallback=None)
    )
    if as_path:
        path = Path(value)
        return path
    return value


def get_path(label):
    return get_config("paths", label, as_path=True)


CONTENT_FOLDER = get_path("content")
OUTPUT_DIR = get_path("output")
CLDF_MD = get_path("cldf")
TABLE_DIR = get_path("tables")
FIGURE_DIR = get_path("figures")
MANEX_DIR = get_path("manual_examples")
TABLE_MD = get_path("table_metadata")
FIGURE_MD = get_path("figure_metadata")
OUTPUT_DIR = get_path("output")
STRUCTURE_FILE = get_path("structure_file")
BENCH = get_path("bench")
ADD_BIB = get_path("add_bib")

BUILDERS = get_config("output", "build").split(" ")
PREVIEW = get_config("output", "preview").split(" ")
CLLD_URI = get_config("clld", "db_uri")
ABBREV_FILE = get_config("input", "abbreviation_file")

CREATE_README = get_config("output", "readme", as_boolean=True)

METADATA_FILE = Path("./metadata.yaml")

OUTPUT_TEMPLATES = {}
for builder in (
    BUILDERS + PREVIEW + ["plain", "github", "html", "latex", "clld", "mkdocs"]
):
    OUTPUT_TEMPLATES[builder] = get_config(builder, "template")

LATEX_EX_TEMPL = get_config("latex", "interlinear_tool")
LATEX_TOPLEVEL = get_config("latex", "toplevel")
if not LATEX_TOPLEVEL:
    if OUTPUT_TEMPLATES["latex"] in ["book"]:
        LATEX_TOPLEVEL = "chapter"
    else:
        LATEX_TOPLEVEL = "section"

MKDOCS_RICH = get_config("mkdocs", "rich_data")

EX_SHOW_LG = get_config("examples", "show_language", as_boolean=True)
EX_SHOW_PRIMARY = get_config("examples", "show_primary", as_boolean=True)
EX_SRC_POS = get_config("examples", "source_position")

LFTS_SHOW_LG = get_config("lfts", "show_language", as_boolean=True)
LFTS_SHOW_FTR = get_config("lfts", "show_translation", as_boolean=True)
LFTS_SHOW_SOURCE = get_config("lfts", "show_source", as_boolean=True)

CONTENT_FILE_PREFIX = get_config("input", "content_file_prefix")


PLD_DIR = Path("./pld")
