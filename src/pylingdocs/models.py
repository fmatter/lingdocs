import logging
from pathlib import Path
import pycldf
from clldutils import jsonlib
from writio import load
from pylingdocs.config import DATA_DIR
from pylingdocs.formats import builders


try:
    from importlib.resources import files  # pragma: no cover
except ImportError:  # pragma: no cover
    from importlib_resources import files  # pragma: no cover

log = logging.getLogger(__name__)
log.level = logging.DEBUG



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
    # templates = {
    #     "inline": {"plain": "{{ ctx.name }}"},
    #     "list": {"plain": "{% for x in ctx %} {{ x['Name'] }}{% endfor %}"},
    #     "detail": {"plain": "# {{ ctx.name }}"},
    # }
    """A dictionary of long jinja templates (not shown here)

       :meta hide-value:"""
    cnt = 0
    """A counter, useful for numbered entities like examples"""

    def __init__(self):
        self.templates = {"inline": {}, "list": {}, "detail": {}, "index": {}}
        self.load_templates()

    def load_template(self, view, builder):
        model_base = Path(DATA_DIR / "model_templates" / self.name.lower())
        parent_model = self.__class__.__bases__[0]
        if parent_model != object:
            parent_base = Path(DATA_DIR / "model_templates" / parent_model.name.lower())
        else:
            parent_base = Path(DATA_DIR / "model_templates" / "base")

        parent_builder = builder.__bases__[0]

        def _filename(base, builder, view):
            return base / f"{builder.label()}_{view}.md"

        tar = _filename(model_base, builder, view)  # e.g. morph/mkdocs_index.md
        if not tar.is_file():
            # log.debug(f"No {tar} (basic)")
            if parent_builder.name != "boilerplate":
                tar = _filename(
                    model_base, parent_builder, view
                )  # e.g. morph/html_index.md
        if not tar.is_file():
            # log.debug(f"No {tar} (builder inherited)")
            tar = _filename(parent_base, builder, view)  # e.g. morpheme/mkdocs_index.md
        if not tar.is_file():
            # log.debug(f"No {tar} (model inherited)")
            tar = _filename(
                parent_base, parent_builder, view
            )  # e.g. morpheme/html_index.md
        if not tar.is_file():
            # log.debug(f"No {tar} (both inherited)")
            if parent_model == object:
                # log.debug(
                #     f"Cannot find template for {self.name}/{view}/{builder.label()}: parent is {parent_model}"
                # )
                x = ""
            else:
                # now search deeper, for base/mkdocs_index.md and base/html_index.md and finall base/plain_index.md
                x = parent_model.load_template(parent_model, view, builder)
            return x
        # log.debug(f"Using {tar} for {self.name}/{view}/{builder.label()}")
        return load(tar)

    def load_templates(self):
        for name, builder in builders.items():
            for view in ["inline", "list", "detail", "index"]:
                self.templates[view][name] = self.load_template(view, builder)

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
        in pylingdocs, it will search in pycldf"""
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
        log.warning(f"Unable to generate preview string for {entry['ID']}")
        return entry["ID"]

    def reset_cnt(self):
        pass


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


class Example(Base):
    name = "Example"
    cldf_table = "ExampleTable"
    shortcut = "ex"
    cnt = 0

    def autocomplete_string(self, entry):
        return (
            f"ex:{entry['ID']} {' '.join(entry['Analyzed_Word'])}\n‘{entry['Translated_Text']}’",  # noqa: E501
            f"[ex]({entry['ID']})",
        )

    def query_string(self, url, *args, multiple=False, visualizer="cldfviz", **kwargs):
        if visualizer == "cldfviz":
            self.cnt += 1
            kwargs.update({"example_counter": self.cnt})
            if not multiple:
                arg_str = self._compile_cldfviz_args(args, kwargs)
                return f"[{self.name} {url}]({self.cldf_table}{arg_str}#cldf:{url})"
            arg_str = self._compile_cldfviz_args(args, kwargs)
            return f"[{self.name} {url}]({self.cldf_table}{arg_str}#cldf:__all__)"
        return f"[Unknown visualizer]({url})"

    def reset_cnt(self):
        self.cnt = 0


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


models = [
    # Base(),
    Morpheme(),
    Morph(),
    Wordform(),
    Example(),
    Language(),
    Text(),
    Cognateset(),
    Form(),
]
