from lingdocs.templates import find_template
from lingdocs.models import models
from lingdocs.formats import builders


def test_file_load():
    for fn, f in builders.items():
        for m in models:
            for view in ["inline", "list", "index", "detail"]:
                find_template(m, f(), view)
