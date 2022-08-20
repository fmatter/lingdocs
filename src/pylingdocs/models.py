import logging
from pathlib import Path
import pycldf
from clldutils import jsonlib
from pylingdocs.config import DATA_DIR
from pylingdocs.config import LATEX_EX_TEMPL


try:
    from importlib.resources import files  # pragma: no cover
except ImportError:  # pragma: no cover
    from importlib_resources import files  # pragma: no cover

log = logging.getLogger(__name__)


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
    """The model's name."""
    cldf_table = "ChangeMeTable"
    """The CLDF table corresponding to the model."""
    shortcut = "chgme"
    """The shortcut which will be used when writing: ``[<shortcut>](<id>)``."""
    fallback = "plain"
    """The fallback for the builder in case no builder-specific template is defined
    for a given model."""
    templates = {"plain": "{{ ctx.name }}"}
    """A dictionary of long jinja templates (not shown here)

       :meta hide-value:"""
    list_templates = {"plain": "{% for x in ctx %} {{ x['Name'] }}{% endfor %}"}
    """A dictionary of long jinja templates (not shown here)

       :meta hide-value:"""
    cnt = 0
    """A counter, useful for numbered entities like examples"""

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
        return f"[Unknown visualizer]({url})"

    @classmethod
    def representation(cls, output_format: str = "plain", multiple=False) -> str:
        """Gives the representation of this model for a given output format.

        Args:
            output_format: the chosen format
        Returns:
            str: a formatted string with a jinja placeholder for data"""
        if not multiple:
            return cls.templates.get(
                output_format, cls.templates.get(cls.fallback, None)
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

    @classmethod
    def autocomplete_string(cls, entry):
        for label in ["Name", "Form", "Title"]:
            if label in entry:
                return (
                    f"{cls.shortcut}:{entry[label]}",
                    f"[{cls.shortcut}]({entry['ID']})",
                )
        log.warning(f"Nothing found for {entry['ID']}")
        return entry["ID"]

    @classmethod
    def reset_cnt(cls):
        pass


class Morpheme(Entity):

    name = "Morpheme"
    cldf_table = "MorphsetTable"
    shortcut = "mp"

    templates = {
        "plain": load_template("morpheme", "plain"),
        "github": load_template("morpheme", "github"),
        "latex": load_template("morpheme", "latex"),
        "html": load_template("morpheme", "html"),
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
    cnt = 0

    templates = {
        "plain": load_template("example", "plain"),
        "latex": load_template("example", f"latex_{LATEX_EX_TEMPL}"),
        "html": load_template("example", "html"),
    }

    list_templates = {
        "plain": load_template("example", "plain_index"),
        "github": load_template("example", "plain_index"),
        "html": load_template("example", "html_index"),
        "latex": load_template("example", f"latex_index_{LATEX_EX_TEMPL}"),
    }

    @classmethod
    def autocomplete_string(cls, entry):
        return (
            f"ex:{entry['ID']} {' '.join(entry['Analyzed_Word'])}\n‘{entry['Translated_Text']}’",  # noqa: E501
            f"[ex]({entry['ID']})",
        )

    @classmethod
    def query_string(cls, url, *args, multiple=False, visualizer="cldfviz", **kwargs):
        if visualizer == "cldfviz":
            cls.cnt += 1
            kwargs.update({"example_counter": cls.cnt})
            if not multiple:
                arg_str = cls._compile_cldfviz_args(args, kwargs)
                return f"[{cls.name} {url}]({cls.cldf_table}{arg_str}#cldf:{url})"
            arg_str = cls._compile_cldfviz_args(args, kwargs)
            return f"[{cls.name} {url}]({cls.cldf_table}{arg_str}#cldf:__all__)"
        return f"[Unknown visualizer]({url})"

    @classmethod
    def reset_cnt(cls):
        cls.cnt = 0


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
    templates = {"plain": "“{{ ctx['Title'] }}”"}


class Cognateset(Entity):

    name = "Cognate set"
    cldf_table = "CognatesetTable"
    shortcut = "cogset"
    # templates = {"plain": "{{ ctx.name }}"}
    templates = {
        "plain": open(  # pylint: disable=consider-using-with
            files("cldfviz") / "templates/text/CognatesetTable_detail.md",
            "r",
            encoding="utf-8",
        ).read(),
        "html": load_template("cognateset", "html_detail"),
    }


class Form(Entity):
    name = "Form"
    cldf_table = "FormTable"
    shortcut = "wf"
    templates = {
        "html": load_template("wordform", "html"),
        "plain": load_template("wordform", "plain"),
        "latex": load_template("wordform", "latex"),
    }

    list_templates = {
        "plain": load_template("wordform", "plain_index"),
        "html": load_template("wordform", "html_index"),
    }


models = [Morpheme, Morph, Example, Language, Text, Cognateset, Form]
