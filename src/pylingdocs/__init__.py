"""Top-level package for pylingdocs."""


import logging

import colorlog

from pylingdocs.config import LOG_LEVEL

handler = colorlog.StreamHandler(None)
handler.setFormatter(
    colorlog.ColoredFormatter("%(log_color)s%(levelname)-7s%(reset)s %(message)s")
)
log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)
log.propagate = True
log.addHandler(handler)

__author__ = "Florian Matter"
__email__ = "flmt@mailbox.org"
__version__ = "0.0.13.dev"
