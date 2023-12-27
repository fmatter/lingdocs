import logging
import sys
from pathlib import Path

import pycldf
from clldutils import jsonlib

from lingdocs.config import DATA_DIR, PLD_DIR

log = logging.getLogger(__name__)


class Base:
    """The base class for entities. Only this to create entirely new concepts,
    with not enough similarity to existing models.
    Refer to this class for documentation of the methods."""

    name = "Base"
    """The model's name."""
    cldf_table = "change_me.csv"
    """The CLDF table corresponding to the model."""
    shortcut = "chgme"
    """The shortcut which will be used when writing: ``[<shortcut>](<id>)``."""

    def _compile_cldfviz_args(self, args, kwargs):
        arguments = "&".join(args)
        kwarguments = "&".join([f"{x}={y}" for x, y in kwargs.items()])
        arg_str = "&".join([arguments, kwarguments])
        if arg_str != "":
            arg_str = "?" + arg_str.strip("&")
        return arg_str

    def query_string(self, url, *args, multiple=False, visualizer="cldfviz", **kwargs):
        """This method returns what commands in running text will be replaced with."""
        if visualizer == "cldfviz":
            if not multiple:
                arg_str = self._compile_cldfviz_args(args, kwargs)
                return f"[{self.name} {url}]({self.cldf_table}{arg_str}#cldf:{url})"
            arg_str = self._compile_cldfviz_args(args, kwargs)
            return f"[{self.name} {url}]({self.cldf_table}{arg_str}#cldf:__all__)"
        return f"[Unknown visualizer]({url})"

    def representation(self, output_format: str = "plain", view: str = "inline") -> str:
        """Gives the representation of this model for a given output format and a given view.

        Args:
            output_format: the chosen format
        Returns:
            str: a formatted string with a jinja placeholder for data"""
        return self.templates[view][output_format]

    def cldf_metadata(self):
        """Loads the CLDF table specification for this model. If none is present
        in lingdocs, it will search in pycldf"""
        path = DATA_DIR / "cldf" / f"{self.cldf_table}-metadata.json"
        if not path.is_file():
            path = (
                Path(pycldf.__file__).resolve().parent
                / "components"
                / f"{self.cldf_table}-metadata.json"
            )
        return jsonlib.load(path)

    def autocomplete_string(self, entry):
        for label in ["Name", "Form", "Title"]:
            if label in entry:
                return (
                    f"{self.shortcut}:{entry[label]}",
                    f"[{self.shortcut}]({entry['ID']})",
                )
        log.warning(f"Unable to generate preview string for {self.name} {entry['ID']}")
        return entry["ID"]


class Base_ORM(Base):
    name = "Base_ORM"


class Morpheme(Base):
    name = "Morpheme"
    cldf_table = "morphemes.csv"
    shortcut = "mp"

    def autocomplete_string(self, entry):
        return (
            f"{self.shortcut}:{entry['Name']} '{entry['Parameter_ID']}'",
            f"[{self.shortcut}]({entry['ID']})",
        )


class Morph(Morpheme):
    name = "Morph"
    cldf_table = "morphs.csv"
    shortcut = "m"


class Wordform(Morpheme):
    name = "Wordform"
    cldf_table = "wordforms.csv"
    shortcut = "wf"

    def autocomplete_string(self, entry):
        return (
            f"{self.shortcut}:{entry['Form']} '{entry['Parameter_ID']}'",
            f"[{self.shortcut}]({entry['ID']})",
        )


class Example(Base_ORM):
    name = "Example"
    cldf_table = "ExampleTable"
    shortcut = "ex"

    def autocomplete_string(self, entry):
        objs = [x if x else "" for x in entry["Analyzed_Word"]]
        return (
            f"ex:{entry['ID']} {' '.join(objs)}\n‘{entry['Translated_Text']}’",  # noqa: E501
            f"[ex]({entry['ID']})",
        )

    def query_string(self, url, *args, multiple=False, visualizer="cldfviz", **kwargs):
        if visualizer == "cldfviz":
            if not multiple:
                arg_str = self._compile_cldfviz_args(args, kwargs)
                return f"[{self.name} {url}]({self.cldf_table}{arg_str}#cldf:{url})"
            arg_str = self._compile_cldfviz_args(args, kwargs)
            return f"[{self.name} {url}]({self.cldf_table}{arg_str}#cldf:__all__)"
        return f"[Unknown visualizer]({url})"


class Language(Base_ORM):
    name = "Language"
    cldf_table = "LanguageTable"
    shortcut = "lg"


class Text(Base):
    name = "Text"
    cldf_table = "texts.csv"
    shortcut = "txt"


class Cognateset(Base_ORM):
    name = "Cognate set"
    cldf_table = "CognatesetTable"
    shortcut = "cogset"


class Form(Base_ORM):
    name = "Form"
    cldf_table = "FormTable"
    shortcut = "f"


class Topic(Base):
    name = "Topic"
    cldf_table = "topics.csv"
    shortcut = "top"


models = [
    Morpheme(),
    Morph(),
    Wordform(),
    Example(),
    Language(),
    Text(),
    Cognateset(),
    Form(),
    Topic(),
]

if Path(f"{PLD_DIR}/models.py").is_file():
    sys.path.insert(1, str(PLD_DIR))
    from models import models as custom_models

    for mm in custom_models:
        log.info(f"Using custom model {mm.name.lower()}")
        models.append(mm())
