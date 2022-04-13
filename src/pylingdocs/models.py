from pylingdocs.config import DATA_DIR


def load_template(name, style):
    with open(
        DATA_DIR / "model_templates" / name / f"{style}.md", "r", encoding="utf-8"
    ) as f:
        return f.read()


class Entity:
    """The base class for entities. Only this to create entirely new concepts,
    with not enough similarity to existing models.
    Refer to this class for documentation of the methods."""


    name = "ChangeMe"
    """The name of the model."""
    cldf_table = "ChangeMeTable"
    """The CLDF table corresponding to the model. Note that depending on how you set up your
    CLDF dataset, this can also be something like lexemes.csv"""
    shortcut = "chgme"
    """The shortcut which will be used in running text -- in this example,
    ``[chgme](id)``."""
    fallback = "plain"
    """The fallback for the builder, if there no builder-specific template is defined
    for the model."""
    formats = {"plain": "{{ ctx.name }}"}

    @classmethod
    def query_string(cls, url, visualizer="cldfviz"):
        """This method returns what commands in running text will be replaced with."""
        if visualizer == "cldfviz":
            return f"[{cls.name} {url}]({cls.cldf_table}#cldf:{url})"
        return f"[Unknown visualizer]({url}"

    @classmethod
    def representation(cls, output_format="plain"):
        """Gives the representation of this model for a given output format.

        Args:
            output_format: the chosen format
        Returns:
            str: a formatted string with a jinja placeholder for data"""
        return cls.formats.get(output_format, cls.formats.get(cls.fallback, None))


class Morpheme(Entity):

    name = "Morpheme"
    cldf_table = "MorphsetTable"
    shortcut = "mp"

    formats = {
        "plain": """{{ ctx["Form"] }}""",
        "github": """_{{ ctx["Form"] }}_""",
        "latex": load_template("morpheme", "latex"),
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
    fallback = None

    formats = {
        "plain": load_template("example", "plain"),
        "latex": load_template("example", "latex"),
        "html": load_template("example", "html"),
    }


models = [Morpheme, Morph, Example]
