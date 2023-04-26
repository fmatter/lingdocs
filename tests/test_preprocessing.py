import logging
from pylingdocs.preprocessing import render_markdown


log = logging.getLogger(__name__)


def test_mp(dataset):
    assert (
        render_markdown("[mp](apa-neg)", dataset, output_format="plain") == "Apalaí pɨra ‘NEG’ ([Koehn and Koehn 1986](#source-koehn1986apalai): 77)"
    )
    assert (
        render_markdown("[mp](apa-neg)", dataset, output_format="github")
        == "Apalaí _pɨra_ ‘NEG’ ([Koehn and Koehn 1986](#source-koehn1986apalai): 77)"
    )
    assert (
        render_markdown("[mp](apa-neg)", dataset, output_format="latex")
        == "Apalaí \\obj{pɨra} ‘NEG’ \\parencites[77]{koehn1986apalai}"
    )
    assert (
        render_markdown("[mp](apa-neg)", dataset, output_format="html")
        == "Apalaí <i>pɨra</i> ‘NEG’ ([Koehn and Koehn 1986](#source-koehn1986apalai): 77)"
    )

    input_str = "[m](tri-se-1,tri-se-2,tri-se-3?with_language=False&with_source=False&nt)"
    formats = {
        "plain": "-se, -je, and -e",
        "github": "_-se_, _-je_, and _-e_",
        "latex": "\\obj{-se}, \\obj{-je}, and \\obj{-e}",
        # "html": "<i>-se</i>, <i>-je</i>, and <i>-e</i>",
    }
    for f, s in formats.items():
        assert render_markdown(input_str, dataset, output_format=f) == s
