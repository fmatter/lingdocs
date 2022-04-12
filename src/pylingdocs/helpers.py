"""Various helpers"""
import logging
from pylingdocs.config import CITATION_FILE
import yaml

log = logging.getLogger(__name__)


def new():
    """Create a new pylingdocs project"""
    # TODO implement
    log.info("Hello world!")


def load_metadata(citation_file=CITATION_FILE):
    metadata = yaml.load(open(citation_file, encoding="utf-8"), Loader=yaml.SafeLoader)
    log.debug(metadata)