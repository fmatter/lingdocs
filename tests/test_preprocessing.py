from pylingdocs.preprocessing import render_cldf


def test_mp(dataset):
    print(render_cldf("[mp](tojpe)", dataset, output_format="github"))
