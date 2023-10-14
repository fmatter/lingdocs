from writio import load, dump
from pylingdocs.config import config
import logging
import sys

log = logging.getLogger(__name__)


def release(source):
    config.load_from_dir(source)
    odir = config["paths"]["output"]
    for fmt, name in config["releasing"]["zip"].items():
        target = odir / fmt
        if not target.is_dir():
            log.warning(
                f"No directory {target.resolve()}.\nRemove {fmt} from the releasing>zip entry or build the format."
            )
            sys.exit()
        for f in target.iterdir():
            if f.is_file():
                print("file", f)
            else:
                print("folder", f)
    md = load(source / "metadata.yaml")
