"""Builders producing different output formats"""
import logging
import shutil
import subprocess
import sys
import hupper
import markdown
import panflute
from cookiecutter.main import cookiecutter
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2.exceptions import TemplateNotFound
from pycldf import Dataset
from pylingdocs.config import CLDF_MD
from pylingdocs.config import CONTENT_FOLDER
from pylingdocs.config import DATA_DIR
from pylingdocs.config import OUTPUT_DIR
from pylingdocs.config import PREVIEW
from pylingdocs.pandoc_filters import fix_header
from pylingdocs.preprocessing import preprocess
from pylingdocs.preprocessing import render_cldf


log = logging.getLogger(__name__)


class OutputFormat:
    name = "boilerplate"
    file_ext = "txt"

    @classmethod
    def write_folder(cls, output_dir, parts=None, metadata=None):
        log.debug(f"Writing {cls.name} to {output_dir}")
        extra = {"name": cls.name, "parts": {"list": parts}, "project_title": "WHAT"}
        extra.update(**metadata)
        cookiecutter(
            str(DATA_DIR / "format_templates" / cls.name),
            output_dir=output_dir,
            extra_context=extra,
            overwrite_if_exists=True,
            no_input=True,
        )
        log.debug("Cookiecutter completed.")

    @classmethod
    def write_part(cls, content, path):
        content = cls.preprocess(content)
        env = Environment(
            loader=PackageLoader("pylingdocs", f"data/format_templates/{cls.name}"),
            autoescape=False,
        )
        try:
            template = env.get_template("part_template")
        except TemplateNotFound:
            template = env.from_string("{{ content }}")
        with open(path, "w", encoding="utf-8") as f:
            f.write(template.render(content=content))

    @classmethod
    def preprocess(cls, content):
        return content

    @classmethod
    def table(cls, df, caption, label):
        del label  # unused
        return caption + "\n" + df.to_markdown(index=False, tablefmt="grid")


class PlainText(OutputFormat):
    name = "plain"


class HTML(OutputFormat):
    name = "html"
    file_ext = "html"

    @classmethod
    def table(cls, df, caption, label):
        return df.to_html(index=False)

    @classmethod
    def preprocess(cls, content):
        return markdown.markdown(content)


class GitHub(OutputFormat):
    name = "github"
    file_ext = "md"

    @classmethod
    def table(cls, df, caption, label):
        return df.to_markdown(index=False)


class Latex(OutputFormat):
    name = "latex"
    file_ext = "tex"

    @classmethod
    def table(cls, df, caption, label):
        return f"""\\begin{{table}}
\\caption{{{caption}}}
\\label{{{label}}}
\\centering
{df.to_latex(index=False)}
\\end{{table}}
"""

    @classmethod
    def preprocess(cls, content):
        doc = fix_header(
            panflute.convert_text(
                content, output_format="json", input_format="markdown"
            )
        )
        return doc


builders = {x.name: x for x in [PlainText, GitHub, Latex, HTML]}


def compose_latex(output_dir=OUTPUT_DIR):  # pragma: no cover
    log.info("Compiling LaTeX document.")
    with subprocess.Popen(
        "latexmk --xelatex main.tex", shell=True, cwd=output_dir / "latex"
    ) as proc:
        del proc  # help, prospector is forcing me


def _load_content(source_dir):
    contents = {}
    parts = {}
    for file in source_dir.iterdir():
        if ".md" not in file.name:
            continue
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        contents[file.stem] = content
        parts[file.stem] = file.stem
    return contents, parts


def run_preview(refresh=True):
    log.info("Rendering preview")
    try:
        ds = Dataset.from_metadata(CLDF_MD)
    except FileNotFoundError as e:
        log.error(e)
        log.error("Please specify a path to a valid CLDF metadata file.")
        sys.exit()
    watchfiles = [str(x) for x in CONTENT_FOLDER.iterdir()]
    if refresh:
        reloader = hupper.start_reloader("pylingdocs.output.run_preview")
        reloader.watch_files(watchfiles)
    create_output(CONTENT_FOLDER, PREVIEW, ds)


def clean_output(output_dir):
    shutil.rmtree(output_dir)
    output_dir.mkdir()


def create_output(source_dir, formats, dataset, output_dir=OUTPUT_DIR):
    """Run different builders.


    This is the extended description.

    Args:
        arg1 (int): Description of arg1

    Returns:
        bool: blabla

    """
    if not output_dir.is_dir():
        log.info(f"Creating output folder {output_dir}")
        output_dir.mkdir()
    if not source_dir.is_dir():
        log.error(f"Content folder {source_dir} does not exist")
        sys.exit(1)
    contents, parts = _load_content(source_dir)
    for output_format in formats:
        log.info(f"Rendering format [{output_format}]")
        output_dest = output_dir / output_format
        builder = builders[output_format]
        log.debug(f"Writing skeleton to folder {output_dir}")
        builder.write_folder(
            output_dir, parts=parts, metadata={"project_title": "A test"}
        )
        log.debug("Iterating parts")
        for label, part in contents.items():
            preprocessed = preprocess(part, builder)
            output = render_cldf(preprocessed, dataset, output_format=output_format)
            builder.write_part(
                content=output, path=output_dest / f"{label}.{builder.file_ext}"
            )
