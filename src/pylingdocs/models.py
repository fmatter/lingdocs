from pathlib import Path
import pycldf
from clldutils import jsonlib
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
    templates = {"plain": "{{ ctx.name }}"}
    list_templates = {"plain": "{% for x in ctx %} {{ x['Form'] }}{% endfor %}"}

    @classmethod
    def _compile_cldfviz_args(cls, args, kwargs):
        arguments = "&".join(args)
        kwarguments = "&".join([f"{x}={y}" for x, y in kwargs.items()])
        arg_str = "&".join([arguments, kwarguments])
        if arg_str != "":
            arg_str = "?" + arg_str.strip("&")
        return arg_str

    @classmethod
    def query_string(cls, url, *args, multiple=False, visualizer="cldfviz", **kwargs):
        """This method returns what commands in running text will be replaced with."""
        if visualizer == "cldfviz":
            if not multiple:
                arg_str = cls._compile_cldfviz_args(args, kwargs)
                return f"[{cls.name} {url}]({cls.cldf_table}{arg_str}#cldf:{url})"
            arg_str = cls._compile_cldfviz_args(args, kwargs)
            return f"[{cls.name} {url}]({cls.cldf_table}{arg_str}#cldf:__all__)"
        return f"[Unknown visualizer]({url}"

    @classmethod
    def representation(cls, output_format="plain", multiple=False):
        """Gives the representation of this model for a given output format.

        Args:
            output_format: the chosen format
        Returns:
            str: a formatted string with a jinja placeholder for data"""
        if not multiple:
            return cls.templates.get(
                output_format, cls.list_templates.get(cls.fallback, None)
            )
        return cls.list_templates.get(
            output_format, cls.list_templates.get(cls.fallback, None)
        )

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

    templates = {
        "plain": """{{ ctx["Form"] }}""",
        "github": """_{{ ctx["Form"] }}_""",
        "latex": load_template("morpheme", "latex"),
        "html": """<i>{{ctx["Form"]}}</i>""",
    }

    list_templates = {
        "plain": load_template("morpheme", "plain_index"),
        "github": load_template("morpheme", "github_index"),
        "latex": load_template("morpheme", "latex_index"),
        "html": load_template("morpheme", "html_index"),
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

    templates = {
        "plain": load_template("example", "plain"),
        "latex": load_template("example", "latex"),
        "html": load_template("example", "html"),
    }

    list_templates = {
        "plain": load_template("example", "plain_index"),
        "github": load_template("example", "plain_index"),
        "html": load_template("example", "plain_index"),
        "latex": load_template("example", "latex_index"),
    }


class Language(Entity):

    name = "Language"
    fallback = None
    cldf_table = "LanguageTable"
    shortcut = "lg"

    list_templates = {
        "plain": load_template("base", "inline_list_orm"),
        "github": load_template("base", "inline_list_orm"),
        "html": load_template("base", "inline_list_orm"),
        "latex": load_template("base", "inline_list_orm"),
    }


class Text(Entity):

    name = "Text"
    cldf_table = "TextTable"
    shortcut = "txt"


models = [Morpheme, Morph, Example, Language]
