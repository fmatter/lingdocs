from lingdocs.models import Language
from lingdocs.models import Text


def test_model_cldf():
    assert "url" in Language().cldf_metadata()


def test_model_vis():
    assert "[Unknown visualizer](a_lg_id)" == Language().query_string(
        url="a_lg_id", visualizer="haha"
    )
