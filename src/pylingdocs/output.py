"""Builders producing different output formats"""
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path
import hupper
import markdown
import panflute
import yaml
from cookiecutter.main import cookiecutter
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2.exceptions import TemplateNotFound
from pycldf import Dataset
from pylingdocs.config import BENCH
from pylingdocs.config import CLDF_MD
from pylingdocs.config import CONTENT_FOLDER
from pylingdocs.config import DATA_DIR
from pylingdocs.config import OUTPUT_DIR
from pylingdocs.config import PREVIEW
from pylingdocs.config import STRUCTURE_FILE
from pylingdocs.helpers import write_cff
from pylingdocs.helpers import write_readme
from pylingdocs.metadata import PROJECT_TITLE
from pylingdocs.pandoc_filters import fix_header
from pylingdocs.preprocessing import preprocess
from pylingdocs.preprocessing import render_markdown


NUM_PRE = re.compile(r"[\d]+\ ")

log = logging.getLogger(__name__)


class OutputFormat:
    name = "boilerplate"
    file_ext = "txt"

    @classmethod
    def write_folder(cls, output_dir, parts=None, metadata=None):
        # log.debug(f"Writing {cls.name} to {output_dir} (from {DATA_DIR})")
        extra = {
            "name": cls.name,
            "parts": {"list": parts},
            "project_title": PROJECT_TITLE,
        }
        extra.update(**metadata)
        cookiecutter(
            str(DATA_DIR / "format_templates" / cls.name),
            output_dir=output_dir,
            extra_context=extra,
            overwrite_if_exists=True,
            no_input=True,
        )

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


def _iterate_structure(structure, level, depths):
    for child_id, child_data in structure.items():
        depths[level] += 1
        yield child_id, level, child_data["title"], "".join(
            [str(x) for x in depths.values()]
        )
        if isinstance(child_data, dict) and "parts" in child_data:
            for x in _iterate_structure(child_data["parts"], level + 1, depths):
                yield x


def iterate_structure(structure):
    for x in _iterate_structure(
        structure["document"]["parts"], level=0, depths={0: 0, 1: 0, 2: 0, 3: 0}
    ):
        yield x


def update_structure(
    content_dir=CONTENT_FOLDER, bench_dir=BENCH, structure_file=STRUCTURE_FILE
):
    log.info("Updating document structure")

    content_files = {}
    for file in content_dir.iterdir():
        if ".md" not in file.name:
            continue
        name = re.sub(NUM_PRE, "", file.stem)
        content_files[name] = file

    bench_files = {}
    for file in bench_dir.iterdir():
        if ".md" not in file.name:
            continue
        name = re.sub(NUM_PRE, "", file.stem)
        bench_files[name] = file

    structure = _load_structure(structure_file)

    for part_id, level, title, fileno in iterate_structure(structure):
        del level  # unused
        del title  # unused
        fname = f"{fileno} {part_id}.md"
        new_path = Path(content_dir, fname)
        if part_id in content_files:
            if part_id in bench_files:
                log.warning(f"Conflict: {part_id}. Resolve manually.")
            else:
                if content_files[part_id] != new_path:
                    log.info(f"'{part_id}': {content_files[part_id]} > {new_path}")
                    content_files[part_id].rename(new_path)
                del content_files[part_id]
        elif part_id in bench_files:
            if bench_files[part_id] != new_path:
                log.info(f"'{part_id}': moving {bench_files[part_id]} > {new_path}")
                bench_files[part_id].rename(new_path)
            del bench_files[part_id]
        else:
            log.info(f"'{part_id}': creating file {new_path}")
            new_path.touch()

    for file in content_files.values():
        new_path = Path(bench_dir, file.name)
        log.info(f"Unlisted: moving {file} > {new_path}")
        file.rename(new_path)


def _load_structure(structure_file=STRUCTURE_FILE):
    if not structure_file.is_file():
        log.error(f"{STRUCTURE_FILE} not found, aborting.")
        sys.exit(1)
    else:
        return yaml.load(open(structure_file, encoding="utf-8"), Loader=yaml.SafeLoader)


def compose_latex(output_dir=OUTPUT_DIR):  # pragma: no cover
    log.info("Compiling LaTeX document.")
    with subprocess.Popen(
        "latexmk --xelatex main.tex", shell=True, cwd=output_dir / "latex"
    ) as proc:
        del proc  # help, prospector is forcing me


def _load_content(source_dir=CONTENT_FOLDER, structure_file=STRUCTURE_FILE):
    structure = _load_structure(structure_file)

    contents = {}
    parts = {}
    for part_id, level, title, fileno in iterate_structure(structure):
        del level  # unused
        filename = f"{fileno} {part_id}.md"
        try:
            with open(source_dir / filename, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            log.error(f"File {source_dir/filename} does not exist.")
            sys.exit(1)
        contents[part_id] = content
        parts[part_id] = title
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
    write_cff()
    write_readme()
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
        # log.debug(f"Writing skeleton to folder {output_dir}")
        builder.write_folder(output_dir, parts=parts, metadata={})
        for part_id, content in contents.items():
            preprocessed = preprocess(content, builder)
            output = render_markdown(preprocessed, dataset, output_format=output_format)
            builder.write_part(
                content=output, path=output_dest / f"{part_id}.{builder.file_ext}"
            )
