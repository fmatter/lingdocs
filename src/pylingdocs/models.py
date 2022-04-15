from pathlib import Path
import pycldf
from clldutils import jsonlib
from pylingdocs.config import DATA_DIR
from pylingdocs.helpers import comma_and_list


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
    def query_string(cls, url, *args, visualizer="cldfviz", **kwargs):
        """This method returns what commands in running text will be replaced with."""
        if visualizer == "cldfviz":
            arguments = "&".join(args)
            kwarguments = "&".join([f"{x}={y}" for x, y in kwargs.items()])
            arg_str = "&".join([arguments, kwarguments])
            if arg_str != "":
                arg_str = "?" + arg_str
            return f"[{cls.name} {url}]({cls.cldf_table}{arg_str}#cldf:{url})"
        return f"[Unknown visualizer]({url}"

    @classmethod
    def representations(cls, entities):
        return comma_and_list(entities)

    @classmethod
    def representation(cls, output_format="plain"):
        """Gives the representation of this model for a given output format.

        Args:
            output_format: the chosen format
        Returns:
            str: a formatted string with a jinja placeholder for data"""
        return cls.formats.get(output_format, cls.formats.get(cls.fallback, None))

    @classmethod
    def cldf_metadata(cls):
        """Loads the CLDF table specification for this model. If none is present
        in pylingdocs, it will search in pycldf"""
        path = DATA_DIR / "cldf" / f"{cls.cldf_table}-metadata.json"
        if not path.is_file():
            path = (
                Path(pycldf.__file__).resolve().parent
                / "components"
                / f"{cls.cldf_table}-metadata.json"
            )
        return jsonlib.load(path)


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


class Morph(Morpheme):

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


class Language(Entity):

    name = "Language"
    cldf_table = "LanguageTable"
    shortcut = "lg"
    fallback = None


models = [Morpheme, Morph, Example, Language]
