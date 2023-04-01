import logging
from pylingdocs.preprocessing import render_markdown


log = logging.getLogger(__name__)


def test_mp(dataset):
    assert (
        render_markdown("[mp](apa-neg)", dataset, output_format="plain") == "pɨra ‘NEG’"
    )
    assert (
        render_markdown("[mp](apa-neg)", dataset, output_format="github")
        == "_pɨra_ ‘NEG’"
    )
    assert (
        render_markdown("[mp](apa-neg)", dataset, output_format="latex")
        == "\\obj{pɨra} ‘NEG’"
    )
    assert (
        render_markdown("[mp](apa-neg)", dataset, output_format="html")
        == "<i>pɨra</i> ‘NEG’"
    )

    input_str = "[m](tri-se-1,tri-se-2,tri-se-3?nt)"
    formats = {
        "plain": "-se, -je, and -e",
        "github": "_-se_, _-je_, and _-e_",
        "latex": "\\obj{-se}, \\obj{-je}, and \\obj{-e}",
        "html": "<i>-se</i>, <i>-je</i>, and <i>-e</i>",
    }
    for f, s in formats.items():
        assert render_markdown(input_str, dataset, output_format=f) == s
