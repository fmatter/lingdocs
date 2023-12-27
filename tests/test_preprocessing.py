import logging
from lingdocs.preprocessing import render_markdown
from lingdocs.formats import builders

log = logging.getLogger(__name__)


def test_mp(dataset):
    assert (
        render_markdown("[mp](apa-neg)", dataset, builder=builders["plain"])
        == "Apalaí pɨra ‘NEG’ ([Koehn and Koehn 1986](#source-koehn1986apalai): 77)"
    )
    assert (
        render_markdown("[mp](apa-neg)", dataset, builder=builders["latex"])
        == "Apalaí \\obj{pɨra} ‘NEG’ \\parencites[77]{koehn1986apalai}"
    )
    assert (
        render_markdown("[mp](apa-neg)", dataset, builder=builders["html"])
        == "Apalaí <i>pɨra</i> ‘NEG’ ([Koehn and Koehn 1986](#source-koehn1986apalai): 77)"
    )

    input_str = (
        "[m](tri-se-1,tri-se-2,tri-se-3?with_language=False&with_source=False&nt)"
    )
    formats = {
        "plain": "-se, -je, and -e",
        "latex": "\\obj{-se}, \\obj{-je}, and \\obj{-e}",
        "html": "<i>-se</i>, <i>-je</i>, and <i>-e</i>",
    }
    for f, s in formats.items():
        assert render_markdown(input_str, dataset, builder=builders[f]) == s
