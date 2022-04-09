from pylingdocs.preprocessing import render_cldf


def test_mp(dataset):
    print(render_cldf("[mp](apa-neg)", dataset, output_format="github"))
