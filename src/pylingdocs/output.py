"""Builders producing different output formats"""
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path
import hupper
import panflute
from cookiecutter.main import cookiecutter
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2.exceptions import TemplateNotFound
from pylingdocs.config import BENCH
from pylingdocs.config import CLDF_MD
from pylingdocs.config import CONTENT_FOLDER
from pylingdocs.config import DATA_DIR
from pylingdocs.config import OUTPUT_DIR
from pylingdocs.config import OUTPUT_TEMPLATES
from pylingdocs.config import STRUCTURE_FILE
from pylingdocs.helpers import _load_structure
from pylingdocs.helpers import split_ref
from pylingdocs.metadata import PROJECT_SLUG
from pylingdocs.metadata import PROJECT_TITLE
from pylingdocs.metadata import _read_metadata_file
from pylingdocs.pandoc_filters import fix_header
from pylingdocs.preprocessing import MD_LINK_PATTERN
from pylingdocs.preprocessing import postprocess
from pylingdocs.preprocessing import preprocess
from pylingdocs.preprocessing import render_markdown


NUM_PRE = re.compile(r"[\d]+\ ")

log = logging.getLogger(__name__)


class OutputFormat:
    name = "boilerplate"
    file_ext = "txt"
    single_output = True
    doc_elements = {"ref": "(crossref placeholder)", "label": "(label placeholder)"}

    @classmethod
    def write_folder(cls, output_dir, content=None, parts=None, metadata=None):
        # log.debug(f"Writing {cls.name} to {output_dir} (from {DATA_DIR})")
        extra = {
            "name": cls.name,
            "parts": {"list": parts},
            "project_title": PROJECT_TITLE,
        }
        if "authors" in metadata:
            extra["author"] = cls.author_list(metadata["authors"])
        else:
            extra["author"] = cls.author_list([])

        if content is not None:
            content = cls.preprocess(content)
            extra.update({"content": content})
        extra.update(**metadata)
        cookiecutter(
            str(DATA_DIR / "format_templates" / cls.name / OUTPUT_TEMPLATES[cls.name]),
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
    def replace_commands(cls, content):
        current = 0
        for m in MD_LINK_PATTERN.finditer(content):
            yield content[current : m.start()]
            current = m.end()
            key = m.group("label")
            url = m.group("url")
            if key in ["src", "psrc"]:
                bibkey, pages = split_ref(url)
                if pages:
                    page_str = f": {pages}"
                else:
                    page_str = ""
                if key == "src":
                    yield f"[{bibkey}](sources.bib?with_internal_ref_link&ref#cldf:{bibkey}){page_str}"
                elif key == "psrc":
                    yield f"([{bibkey}](sources.bib?with_internal_ref_link&ref#cldf:{bibkey}){page_str})"
            elif key in cls.doc_elements:
                yield cls.doc_elements[key]
            else:
                yield content[m.start() : m.end()]
        yield content[current:]

    @classmethod
    def preprocess_commands(cls, content):
        processed = "".join(cls.replace_commands(content))
        return processed

    @classmethod
    def preprocess(cls, content):
        return content

    @classmethod
    def table(cls, df, caption, label):
        del label  # unused
        return caption + ":\n\n" + df.to_markdown(index=False, tablefmt="grid")

    @classmethod
    def reference_list(cls):
        return "# References \n[References](Source?cited_only#cldf:__all__)"

    @classmethod
    def author_list(cls, authors):
        if len(authors) == 0:
            return "Anonymous"
        out = []
        for author in authors:
            out.append(f'{author["given-names"]} {author["family-names"]}')
        return " and ".join(out)


class PlainText(OutputFormat):
    name = "plain"

    @classmethod
    def preprocess(cls, content):
        return panflute.convert_text(
            content, output_format="plain", input_format="markdown"
        )


class HTML(OutputFormat):
    name = "html"
    file_ext = "html"

    @classmethod
    def table(cls, df, caption, label):
        return df.to_html(escape=False, index=False)

    @classmethod
    def preprocess(cls, content):
        return panflute.convert_text(
            content,
            output_format="html",
            input_format="markdown",
            extra_args=["--shift-heading-level-by=1"],
        )


class GitHub(OutputFormat):
    name = "github"
    file_ext = "md"

    @classmethod
    def table(cls, df, caption, label):
        return df.to_markdown(index=False)

    @classmethod
    def preprocess(cls, content):
        return panflute.convert_text(
            content, output_format="gfm", input_format="markdown"
        )


class CLLD(OutputFormat):
    name = "clld"
    file_ext = "md"
    single_output = False

    @classmethod
    def create_app(cls):
        extra = {
            "name": cls.name,
            "project_title": PROJECT_TITLE,
            "clld_slug": PROJECT_SLUG.replace("-", "_") + "_clld",
            "cldf_paths": "['" + str(CLDF_MD.resolve()) + "']",
        }
        # extra.update(**metadata)
        cookiecutter(
            str(DATA_DIR / "format_templates" / cls.name / OUTPUT_TEMPLATES[cls.name]),
            output_dir="clld",
            extra_context=extra,
            overwrite_if_exists=True,
            no_input=True,
        )

    @classmethod
    def table(cls, df, caption, label):
        del label  # unused
        return caption + ":\n\n" + df.to_markdown(index=False)


class Latex(OutputFormat):
    name = "latex"
    file_ext = "tex"
    doc_elements = {
        "ref": lambda url: f"\\cref{{{url}}}",
        "label": lambda url: f"\\label{{{url}}}",
    }

    @classmethod
    def table(cls, df, caption, label):
        return f"""\\begin{{table}}
\\caption{{{caption}}}
\\label{{tab:{label}}}
\\centering
{df.to_latex(escape=False, index=False)}
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

    @classmethod
    def reference_list(cls):
        return "\\printbibliography"

    @classmethod
    def replace_commands(cls, content):
        current = 0
        for m in MD_LINK_PATTERN.finditer(content):
            yield content[current : m.start()]
            current = m.end()
            key = m.group("label")
            url = m.group("url")
            if key in ["src", "psrc"]:
                bibkey, pages = split_ref(url)
                if pages:
                    page_str = f"[{pages}]"
                else:
                    page_str = ""
                if key == "src":
                    yield f"\\textcite{page_str}{{{bibkey}}}"
                elif key == "psrc":
                    yield f"\\parencite{page_str}{{{bibkey}}}"
            elif key in cls.doc_elements:
                yield cls.doc_elements[key](url)
            else:
                yield content[m.start() : m.end()]
        yield content[current:]


builders = {x.name: x for x in [PlainText, GitHub, Latex, HTML, CLLD]}


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
        if not bench_dir.is_dir():
            log.info(f"Creating {bench_dir} for unused files.")
            bench_dir.mkdir()
        new_path = Path(bench_dir, file.name)
        log.info(f"Unlisted: moving {file} > {new_path}")
        file.rename(new_path)


def compile_latex(output_dir=OUTPUT_DIR):  # pragma: no cover
    log.info("Compiling LaTeX document.")
    with subprocess.Popen(
        "latexmk --xelatex main.tex", shell=True, cwd=output_dir / "latex"
    ) as proc:
        del proc  # help, prospector is forcing me


def _load_content(structure, source_dir=CONTENT_FOLDER):
    source_dir = Path(source_dir)
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


def run_preview(refresh=True, **kwargs):
    log.info("Rendering preview")
    watchfiles = [str(x) for x in kwargs["source_dir"].iterdir()]
    if refresh:
        reloader = hupper.start_reloader(
            "pylingdocs.output.run_preview", worker_kwargs=kwargs
        )
        reloader.watch_files(watchfiles)
    create_output(**kwargs)


def clean_output(output_dir):
    shutil.rmtree(output_dir)
    output_dir.mkdir()


def create_output(
    source_dir, formats, dataset, output_dir, structure, metadata=None
):  # pylint: disable=too-many-arguments
    """Run different builders.


    This is the extended description.

    Args:
        arg1 (int): Description of arg1

    Returns:
        bool: blabla

    """
    if isinstance(structure, str):
        structure = _load_structure(structure)
    if isinstance(metadata, str):
        metadata = _read_metadata_file(metadata)
    if metadata is None:
        metadata = {}
    metadata.update({"bibfile": Path(dataset.bibpath).resolve()})
    # if metadata_file:
    #     write_cff()
    #     write_readme()
    #     metadata.update(all_metadata)
    output_dir = Path(output_dir)
    source_dir = Path(source_dir)
    if not output_dir.is_dir():
        log.info(f"Creating output folder {output_dir}")
        output_dir.mkdir()

    contents, parts = _load_content(structure, source_dir)

    for output_format in formats:
        log.info(f"Rendering format [{output_format}]")
        builder = builders[output_format]
        # log.debug(f"Writing skeleton to folder {output_dir}")
        content = "\n\n".join(contents.values())
        preprocessed = preprocess(content)
        preprocessed = builder.preprocess_commands(preprocessed)
        preprocessed += "\n\n" + builder.reference_list()
        preprocessed = render_markdown(
            preprocessed, dataset, output_format=output_format
        )
        preprocessed = postprocess(preprocessed, builder)
        if builder.single_output:
            builder.write_folder(
                output_dir, content=preprocessed, parts=parts, metadata=metadata
            )
        elif builder.name == "clld":
            # builder.create_app()
            with open("clld_output.txt", "w", encoding="utf-8") as f:
                f.write(preprocessed)
        else:
            pass
