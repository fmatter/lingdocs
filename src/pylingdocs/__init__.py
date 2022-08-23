"""Top-level package for pylingdocs."""
import logging
import colorlog


handler = colorlog.StreamHandler(None)
handler.setFormatter(
    colorlog.ColoredFormatter("%(log_color)s%(levelname)-7s%(reset)s %(message)s")
)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.propagate = True
log.addHandler(handler)


__author__ = "Florian Matter"
__email__ = "florianmatter@gmail.com"
__version__ = "0.0.8"
