from pylingdocs.config import DATA_DIR


def load_template(name, style):
    with open(
        DATA_DIR / "model_templates" / name / f"{style}.md", "r", encoding="utf-8"
    ) as f:
        return f.read()


class Entity:
    """The base class for entities"""

    name = "ChangeMe"
    cldf_table = "ChangeMeTable"
    shortcut = "chgme"

    fallback = "plain"
    formats = {"plain": "{{ ctx.name }}"}

    @classmethod
    def query_string(cls, url, visualizer="cldfviz"):
        if visualizer == "cldfviz":
            return f"[{cls.name} {url}]({cls.cldf_table}#cldf:{url})"

    @classmethod
    def representation(cls, output_format="plain"):
        return cls.formats.get(output_format, cls.formats.get(cls.fallback, None))


class Morpheme(Entity):

    name = "Morpheme"
    cldf_table = "MorphsetTable"
    shortcut = "mp"

    formats = {
        "plain": """{{ ctx["Form"] }}""",
        "github": """_{{ ctx["Form"] }}_""",
        "latex": r"""\obj{% raw %}{{% endraw %}{{ ctx["Form"] }}{% raw %}}{% endraw %}""",
        "html": """<i>{{ctx["Form"]}}</i>""",
    }


class Morph(Entity):

    name = "Morph"
    cldf_table = "MorphTable"
    shortcut = "m"


class Example(Entity):

    name = "Example"
    cldf_table = "ExampleTable"
    shortcut = "ex"

    formats = {
        "plain": load_template("example", "plain"),
        "latex": load_template("example", "latex"),
        "html": load_template("example", "html"),
    }


models = [Morpheme, Morph, Example]
