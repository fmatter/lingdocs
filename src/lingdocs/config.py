import logging
import re
from pathlib import Path

from importlib_resources import files  # pragma: no cover
from writio import load

log = logging.getLogger(__name__)

DATA_DIR = files("lingdocs") / "data"
MD_LINK_PATTERN = re.compile(r"\[(?P<label>[^]]*)]\((?P<url>[^)]+)\)")
LOG_LEVEL = logging.INFO
PLD_DIR = Path("pld")
EXTRA_DIR = "extra"
MANEX_DIR = "manual_examples"
BENCH = "bench"
CONTENT_FOLDER = "docs"
STRUCTURE_FILE = "structure.yaml"
FIGURE_DIR = "figures"
TABLE_DIR = "tables"
COLSTART = "<<<columns---"
COLEND = "---columns>>>"
COLDIV = "---col---"


def merge_dicts(a, b):
    for k1, v1 in b.items():
        if isinstance(v1, dict):
            for k2, v2 in v1.items():
                if isinstance(v2, dict):
                    log.warning(
                        "Your configuration file is too nested. Please check it."
                    )
                else:
                    a[k1][k2] = v2
        else:
            a[k1] = v1
    return a


class Config:
    def __init__(self):
        self.data = load(DATA_DIR / "config.yaml")
        self.fix_paths()
        self.dependents()

    def load_from_dir(self, path="."):
        locp = Path(path) / "config.yaml"
        self.data["source"] = Path(path)
        if locp.is_file():
            log.debug(f"Loading config file from {locp}")
            self.data = merge_dicts(self.data, load(locp))
        else:
            log.warning(f"No config file found at {locp}")
        self.fix_paths()
        self.dependents()

    def dependents(self):
        pass
        # if self.data["data"]["rich"]:
        #     self.data["data"]["data"] = True

    def fix_paths(self):
        for k, v in self.data["paths"].items():
            self.data["paths"][k] = Path(v)

    def __getitem__(self, k):
        return self.data[k]

    def __setitem__(self, k, v):
        self.data[k] = v


config = Config()
# import logging
# import re
# from configparser import ConfigParser
# from pathlib import Path

# log = logging.getLogger(__name__)

# try:
#     from importlib.resources import files  # pragma: no cover
# except ImportError:  # pragma: no cover
#     from importlib_resources import files  # pragma: no cover

# CONF_PATH = "lingdocs.cfg"
# LOG_LEVEL = logging.INFO

# config = ConfigParser()
# default_config = ConfigParser()
# default_config.read(DATA_DIR / "config.cfg")

# conf_path = Path(CONF_PATH)
# if conf_path.is_file():
#     config.read(conf_path)  # pragma: no cover
# else:
#     config.read(DATA_DIR / "config.cfg")


# def get_config(section, label, as_path=False, as_boolean=False):
#     if as_boolean:
#         return config.getboolean(
#             section, label, fallback=default_config.getboolean(section, label)
#         )
#     value = config.get(
#         section, label, fallback=default_config.get(section, label, fallback=None)
#     )
#     if as_path:
#         path = Path(value)
#         return path
#     return value


# def get_path(label):
#     return get_config("paths", label, as_path=True)


# CONTENT_FOLDER = get_path("content")
# OUTPUT_DIR = get_path("output")
# CLDF_MD = get_path("cldf")
# TABLE_DIR = get_path("tables")
# FIGURE_DIR = get_path("figures")
# MANEX_DIR = get_path("manual_examples")
# TABLE_MD = get_path("table_metadata")
# FIGURE_MD = get_path("figure_metadata")
# OUTPUT_DIR = get_path("output")
# STRUCTURE_FILE = get_path("structure_file")
# BENCH = get_path("bench")
# ADD_BIB = get_path("add_bib")

# BUILDERS = get_config("output", "build").split(" ")
# PREVIEW = get_config("output", "preview").split(" ")
# CLLD_URI = get_config("clld", "db_uri")
# ABBREV_FILE = get_config("input", "abbreviation_file")

# CREATE_README = get_config("output", "readme", as_boolean=True)

# METADATA_FILE = Path("./metadata.yaml")

# LAYOUT = get_config("output", "layout")

# LATEX_EX_TEMPL = get_config("latex", "interlinear_tool")
# LATEX_TOPLEVEL = get_config("latex", "toplevel")
# if not LATEX_TOPLEVEL:
#     if LAYOUT == "book":
#         LATEX_TOPLEVEL = "chapter"
#     else:
#         LATEX_TOPLEVEL = "section"

# WRITE_DATA = get_config("output", "data")
# if WRITE_DATA == "False":
#     WRITE_DATA = False
# elif "json" not in WRITE_DATA:
#     WRITE_DATA = True
# RICH = get_config("output", "rich", as_boolean=True)
# if RICH and not WRITE_DATA:
#     WRITE_DATA = True

# EX_SHOW_LG = get_config("examples", "show_language", as_boolean=True)
# EX_SHOW_PRIMARY = get_config("examples", "show_primary", as_boolean=True)
# EX_SRC_POS = get_config("examples", "source_position")

# LFTS_SHOW_LG = get_config("lfts", "show_language", as_boolean=True)
# LFTS_SHOW_FTR = get_config("lfts", "show_translation", as_boolean=True)
# LFTS_SHOW_SOURCE = get_config("lfts", "show_source", as_boolean=True)

# CONTENT_FILE_PREFIX = get_config("input", "content_file_prefix")
