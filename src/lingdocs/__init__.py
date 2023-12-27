"""Top-level package for lingdocs."""


import logging

import colorlog

from lingdocs.config import LOG_LEVEL

handler = colorlog.StreamHandler(None)
handler.setFormatter(
    colorlog.ColoredFormatter("%(log_color)s%(levelname)-7s%(reset)s %(message)s")
)
log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)
log.propagate = True
log.addHandler(handler)
