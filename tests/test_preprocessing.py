from pylingdocs.preprocessing import render_markdown
import logging

log = logging.getLogger(__name__)


def test_mp(dataset):
    assert render_markdown("[mp](apa-neg)", dataset, output_format="github") == "_pɨra_"
    assert (
        render_markdown("[mp](apa-neg)", dataset, output_format="latex")
        == "\\obj{pɨra}"
    )
    assert (
        render_markdown("[mp](apa-neg)", dataset, output_format="html") == "<i>pɨra</i>"
    )
