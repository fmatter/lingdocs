"""Builders producing different output formats"""
import logging
import re
import shutil
import subprocess
import sys
import threading
from http.server import SimpleHTTPRequestHandler
from http.server import test
from pathlib import Path
from pathlib import PosixPath
import hupper
import pandas as pd
import panflute
from cookiecutter.main import cookiecutter
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2.exceptions import TemplateNotFound
from slugify import slugify
from pylingdocs.config import BENCH
from pylingdocs.config import CONTENT_FOLDER
from pylingdocs.config import DATA_DIR
from pylingdocs.config import FIGURE_DIR
from pylingdocs.config import GLOSS_ABBREVS
from pylingdocs.config import LATEX_TOPLEVEL
from pylingdocs.config import OUTPUT_DIR
from pylingdocs.config import OUTPUT_TEMPLATES
from pylingdocs.config import STRUCTURE_FILE
from pylingdocs.helpers import _get_relative_file
from pylingdocs.helpers import _load_cldf_dataset
from pylingdocs.helpers import _load_structure
from pylingdocs.helpers import decorate_gloss_string
from pylingdocs.helpers import html_example_wrap
from pylingdocs.helpers import html_gloss
from pylingdocs.helpers import latexify_table
from pylingdocs.helpers import load_content
from pylingdocs.helpers import refresh_clld_db
from pylingdocs.helpers import src
from pylingdocs.metadata import _load_metadata
from pylingdocs.models import models
from pylingdocs.preprocessing import MD_LINK_PATTERN
from pylingdocs.preprocessing import postprocess
from pylingdocs.preprocessing import preprocess
from pylingdocs.preprocessing import render_markdown


NUM_PRE = re.compile(r"[\d]+\ ")

log = logging.getLogger(__name__)


def blank_todo(url, **_kwargs):
    del url
    return ""


def html_todo(url, **kwargs):
    if kwargs.get("release", False):
        return ""
    if "?" in str(url):
        return f"<span title='{url}'>❓</span>"
    return f"<span title='{url}'>❗️</span>"


def latex_todo(url, **kwargs):
    if kwargs.get("release", False):
        return ""
    return f"\\todo{{{url}}}"


def html_ref(url, **kwargs):
    kw_str = " ".join([f"""{x}="{y}" """ for x, y in kwargs.items()])
    return f"<a href='#{url}' class='crossref' name='{url}' {kw_str}>ref</a>"


text_commands = ["todo"]


class OutputFormat:
    name = "boilerplate"
    file_ext = "txt"
    single_output = True

    def ref_element(url, **kwargs):
        end = kwargs.pop("end", None)
        if end:
            return f"[ref:{url}–{end}]"
        return f"[ref:{url}]"

    def label_element(url, **_kwargs):
        return f"[lbl:{url}]"

    def gloss_element(url, **_kwargs):
        return url.upper()

    def blank_exref(url, **kwargs):
        end = kwargs.pop("end", None)
        if end:
            return f"[ex:{url}–{end}]"
        return f"[ex:{url}]"

    doc_elements = {
        "ref": ref_element,
        "label": label_element,
        "gl": gloss_element,
        "todo": blank_todo,
        "exref": blank_exref,
    }

    @classmethod
    def decorate_gloss_string(cls, x):
        return decorate_gloss_string(x, decoration=lambda x: x.upper())

    @classmethod
    def write_folder(
        cls, output_dir, content=None, parts=None, metadata=None, abbrev_dict=None
    ):  # pylint: disable=too-many-arguments
        # log.debug(f"Writing {cls.name} to {output_dir} (from {DATA_DIR})")
        if not abbrev_dict:
            abbrev_dict = {}
        extra = {
            "name": cls.name,
            "parts": {"list": parts},
            "project_title": metadata.get("title", "A beautiful title"),
            "glossing_abbrevs": cls.register_glossing_abbrevs(abbrev_dict),
        }
        if "authors" in metadata:
            extra["author"] = cls.author_list(metadata["authors"])
        else:
            extra["author"] = cls.author_list([])

        if content is not None:
            content = content.replace("![](", "![](images/")
            content = cls.preprocess(content)
            extra.update({"content": content})

        extra.update(**metadata)
        local_template_path = (
            Path("pld") / "output_templates" / cls.name / OUTPUT_TEMPLATES[cls.name]
        )
        if local_template_path.is_dir():
            template_path = str(local_template_path)
        else:
            template_path = str(
                DATA_DIR / "format_templates" / cls.name / OUTPUT_TEMPLATES[cls.name]
            )
        cookiecutter(
            template_path,
            output_dir=output_dir,
            extra_context=extra,
            overwrite_if_exists=True,
            no_input=True,
        )
        if FIGURE_DIR.is_dir():
            target_dir = output_dir / cls.name / FIGURE_DIR.name
            if not target_dir.is_dir():
                target_dir.mkdir()
            for file in FIGURE_DIR.iterdir():
                target = target_dir / file.name
                if not target.is_file():
                    shutil.copy(file, target)

    @classmethod
    def register_glossing_abbrevs(cls, abbrev_dict):
        del abbrev_dict
        return ""

    @classmethod
    def glossing_abbrevs_list(cls, arg_string):
        del arg_string
        return ""

    @classmethod
    def write_part(cls, content, path):  # pragma: no cover (not used ATM)
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
    def replace_commands(cls, content, **kwargs):
        current = 0
        for m in MD_LINK_PATTERN.finditer(content):
            yield content[current : m.start()]
            current = m.end()
            key = m.group("label")
            url = m.group("url")
            args = []
            element_kwargs = {**{}, **kwargs}
            if "?" in url and key not in text_commands:
                url, arguments = url.split("?")
                for arg in arguments.split("&"):
                    if "=" in arg:
                        k, v = arg.split("=")
                        element_kwargs[k] = v
                    else:
                        args.append(arg)
            if key == "src":
                yield src(url.split(","))
            elif key == "psrc":
                yield src(url.split(","), parens=True)
            elif key in cls.doc_elements:
                yield cls.doc_elements[key](url, *args, **element_kwargs)
            elif key == "abbrev_list":
                yield cls.glossing_abbrevs_list(url)
            else:
                yield content[m.start() : m.end()]
        yield content[current:]

    @classmethod
    def preprocess_commands(cls, content, **kwargs):
        processed = "".join(cls.replace_commands(content, **kwargs))
        return processed

    @classmethod
    def preprocess(cls, content):
        return content

    @classmethod
    def table(cls, df, caption, label):
        # del label  # unused
        tabular = df.to_markdown(index=False, tablefmt="grid")
        if not caption:
            return tabular
        return caption + f": [lbl:{label}]\n\n" + tabular

    @classmethod
    def manex(cls, tag, content, kind):
        del tag  # unused
        del kind  # unused
        return content

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
        res = panflute.convert_text(
            content, output_format="plain", input_format="markdown"
        )
        return res.replace("|WHITESPACE|", " ")


class HTML(OutputFormat):
    name = "html"
    file_ext = "html"

    def exref(url, *args, **kwargs):
        del args  # unused
        kw_str = " ".join([f"""{x}="{y}" """ for x, y in kwargs.items()])
        return f'<a class="exref" example_id="{url}"{kw_str}></a>'

    def html_gl(url, **_kwargs):
        return decorate_gloss_string(url.upper(), decoration=html_gloss)

    def html_label(url, **_kwargs):
        return "{#" + url + "}" + f"\n <a id='{url}'></a>"

    @classmethod
    def decorate_gloss_string(cls, x):
        return decorate_gloss_string(
            x,
            decoration=lambda x: f'<span class="gloss">{x} <span class="tooltiptext gloss-{x}" ></span></span>',
        )

    doc_elements = {
        "exref": exref,
        "gl": html_gl,
        "ref": html_ref,
        "label": html_label,
        "todo": html_todo,
    }

    @classmethod
    def register_glossing_abbrevs(cls, abbrev_dict):
        return f"""<script>var abbrev_dict={abbrev_dict}; for (var key in abbrev_dict){{
var targets = document.getElementsByClassName('gloss-'+key)
for (var i = 0; i < targets.length; i++) {{
    targets[i].innerHTML = abbrev_dict[key];
}}
}};</script>"""

    @classmethod
    def glossing_abbrevs_list(cls, arg_string):
        return """<dl id="glossing_abbrevs"></dl>"""

    @classmethod
    def table(cls, df, caption, label):
        table = df.to_html(escape=False, index=False)
        if not caption:
            return table
        return table.replace(
            "<thead",
            f"<caption class='table' id ='tab:{label}'>{caption}</caption><thead",
        )

    @classmethod
    def preprocess(cls, content):
        if OUTPUT_TEMPLATES["html"] == "slides":
            return panflute.convert_text(
                content,
                output_format="revealjs",
                input_format="markdown",
                extra_args=["--shift-heading-level-by=1"],
            )
        return panflute.convert_text(
            content,
            output_format="html",
            input_format="markdown",
            extra_args=["--shift-heading-level-by=1"],
        )

    @classmethod
    def manex(cls, tag, content, kind):
        if content.strip().startswith("PYLINGDOCS_RAW_TABLE_START"):
            content = " \n \n" + content
        return html_example_wrap(tag, content, kind=kind)


class GitHub(OutputFormat):
    name = "github"
    file_ext = "md"

    def ref_element(url, **_kwargs):
        if "tab:" in str(url):
            return "[Table]"
        return f"<a href='#{url}'>click</a>"

    def label_element(url, **_kwargs):
        return f"<a id='{url}'><a/>"

    def gloss_element(url, **_kwargs):
        return url.upper()

    def blank_exref(url, **kwargs):
        end = kwargs.pop("end", None)
        if end:
            return f"[ex:{url}–{end}]"
        return f"[ex:{url}]"

    doc_elements = {
        "ref": ref_element,
        "label": label_element,
        "gl": gloss_element,
        "todo": blank_todo,
        "exref": blank_exref,
    }

    @classmethod
    def table(cls, df, caption, label):
        del label  # unused
        tabular = df.to_markdown(index=False)
        if not caption:
            return tabular
        return df.to_markdown(index=False)

    @classmethod
    def preprocess(cls, content):
        res = panflute.convert_text(
            content, output_format="gfm", input_format="markdown"
        )
        return res.replace("WHITESPACE", " ").replace(r"\|", "")


class CLLD(OutputFormat):
    name = "clld"
    file_ext = "md"
    single_output = False

    def clld_label(url, **_kwargs):
        return f"{{#{url}}}"

    def clld_gloss(url, **_kwargs):
        return "<span class='smallcaps'>" + url + "</span>"

    def clld_exref(url, **kwargs):
        kw_str = " ".join([f"""{x}="{y}" """ for x, y in kwargs.items()])
        return f'<a class="exref" example_id="{url}"{kw_str}></a>'

    doc_elements = {
        "ref": html_ref,
        "label": clld_label,
        "gl": clld_gloss,
        "exref": clld_exref,
        "todo": html_todo,
    }

    @classmethod
    def table(cls, df, caption, label):
        if not caption:
            if len(df) == 0:
                df = df.append({x: "" for x in df.columns}, ignore_index=True)
            return df.to_markdown(index=False)
        return (
            f"<a id='tab:{label}'></a><div class='caption table' id='tab:{label}'>{caption}</div>\n\n"
            + df.to_markdown(index=False)
        )

    @classmethod
    def reference_list(cls):
        return ""

    @classmethod
    def manex(cls, tag, content, kind):
        if content.strip().startswith("PYLINGDOCS_RAW_TABLE_START"):
            content = " \n \n" + content
        return html_example_wrap(tag, content, kind=kind)

    @classmethod
    def write_folder(
        cls, output_dir, content=None, parts=None, metadata=None, abbrev_dict=None
    ):  # pylint: disable=too-many-arguments disable=too-many-locals
        my_output_dir = output_dir / cls.name
        if not (my_output_dir).is_dir():
            (my_output_dir).mkdir()
        tent = "\n" + content
        tent = tent.replace(
            "![](", "![](/static/images/"
        )  # rudely assume that all images live in the static dir
        delim = "\n# "
        parts = tent.split(delim)[1::]
        if len(parts) == 0 or OUTPUT_TEMPLATES["clld"] in ["slides", "article"]:
            # these use # as section markers, so we add a level for the html output
            tent = tent.replace("\n#", "\n##")
            with open(my_output_dir / "content.txt", "w", encoding="utf-8") as f:
                f.write(tent)
        else:
            tag_dic = {}
            content_dic = {}
            for (i, part) in enumerate(parts):
                title, content = part.split("\n", 1)
                tag = re.findall("{#(.*?)}", title)
                title = title.split("{#")[0].strip()
                if len(tag) == 0:
                    tag = slugify(title)
                else:
                    tag = tag[0]
                content_dic[tag] = {
                    "title": title,
                    "content": f"<a id='{tag}'></a>" + content,
                }

                tags = re.findall("{#(.*?)}", content_dic[tag]["content"])
                table_tags = re.findall(
                    "<div class='caption table' id='(.*?)'>",
                    content_dic[tag]["content"],
                )
                for subtag in tags + table_tags:
                    if subtag in tag_dic:
                        log.warning(
                            f"duplicate tag {subtag} in {tag}: {tag_dic[subtag]}"
                        )
                    tag_dic[subtag] = tag
                tag_dic[tag] = tag

            for tag, data in content_dic.items():
                refs = re.findall(r"<a href='#(.*?)' .*?</a>", tent)
                for ref in refs:
                    if ref not in tag_dic:
                        log.error(f"Tag {ref} not found.")
                    elif tag_dic[ref] != tag:
                        data["content"] = re.sub(
                            rf"<a href='#{ref}'.*?</a>",
                            f"[crossref](ChapterTable?_anchor={ref}#cldf:{tag_dic[ref]})",
                            data["content"],
                        )

            for i, (chapter, data) in enumerate(content_dic.items()):
                content = data.pop("content")
                number = i + 1
                filename = f"{number}_{chapter}.txt"
                data["Filename"] = filename
                data["Number"] = number
                with open(my_output_dir / filename, "w", encoding="utf-8") as f:
                    f.write(content)
            chapter_data = pd.DataFrame.from_dict(content_dic, orient="index")
            chapter_data.index.name = "ID"
            chapter_data.to_csv(my_output_dir / "chapters.csv")


class Latex(OutputFormat):
    name = "latex"
    file_ext = "tex"

    def latex_exref(url, end=None, suffix="", **_kwargs):
        if end:
            return f"\\exref[{suffix}][{end}]{{{url}}}"
        return f"\\exref[{suffix}]{{{url}}}"

    def latex_label(url, **_kwargs):
        return f"\\label{{{url}}}"

    def latex_ref(url, **kwargs):
        end = kwargs.pop("end", None)
        if end:
            return f"\\crefrange{{{url}}}{{{end}}}"
        return f"\\cref{{{url}}}"

    @classmethod
    def decorate_gloss_string(cls, x):
        return decorate_gloss_string(x)

    def latex_gloss(url, **_kwargs):
        return decorate_gloss_string(url.upper())

    doc_elements = {
        "exref": latex_exref,
        "ref": latex_ref,
        "label": latex_label,
        "gl": latex_gloss,
        "todo": latex_todo,
    }

    @classmethod
    def manex(cls, tag, content, kind):
        if kind == "multipart":
            return f"\\pex\\label{{{tag}}}{content}\\xe"
        if kind == "subexample":
            return f"\\a\\label{{{tag}}} {content}"
        return f"\\ex\\label{{{tag}}} {content} \\xe"

    @classmethod
    def table(cls, df, caption, label):
        if len(df) == 0:
            df = df.append({x: x for x in df.columns}, ignore_index=True)
            df = df.applymap(latexify_table)
            tabular = df.to_latex(escape=False, index=False, header=False)
        else:
            df = df.applymap(latexify_table)
            df.columns = list(map(latexify_table, df.columns))
            tabular = df.to_latex(escape=False, index=False)

        if not caption:  # tables in examples are handled differently
            return (
                tabular.replace("\\toprule", "")  # the only rule is: no rules
                .replace("\\midrule", "")
                .replace("\\bottomrule", "")
                .replace("\\begin{tabular}{", "\\begin{tabular}[t]{")  # top aligned
            )
        return f"""\\begin{{table}}
\\caption{{{panflute.convert_text(
            caption, output_format="latex", input_format="markdown"
        )}}}
\\label{{tab:{label}}}
\\centering
{tabular}
\\end{{table}}
"""

    @classmethod
    def register_glossing_abbrevs(cls, abbrev_dict):
        return "\n".join(
            [
                f"\\newGlossingAbbrev{{{x.lower()}}}{{{y}}}"
                for x, y in abbrev_dict.items()
            ]
        )

    @classmethod
    def glossing_abbrevs_list(cls, arg_string):
        return "\\glossingAbbrevsList"

    @classmethod
    def preprocess(cls, content):
        doc = panflute.convert_text(
            content,
            output_format="latex",
            input_format="markdown-auto_identifiers",
            extra_args=[f"--top-level-division={LATEX_TOPLEVEL}"],
        )
        doc = doc.replace("\\pex\n\n", "\\pex\n")
        doc = doc.replace("\n\n\\begin{tabular", "\n\\begin{tabular")
        doc = doc.replace("\\begin{tabular}[t]", "\n\\begin{tabular}[t]")
        doc = doc.replace("}\n\n\\begin{tabular}[t]", "}\\begin{tabular}[t]")
        return doc

    @classmethod
    def reference_list(cls):
        return "\\printbibliography"

    @classmethod
    def author_list(cls, authors):
        if len(authors) == 0:
            return "Anonymous"
        out = []
        for author in authors:
            out.append(f'{author["given-names"]} {author["family-names"]}')
        if OUTPUT_TEMPLATES["latex"] == "memoir":
            return ";".join(out)  # may want to use this for all templates at some point
        return " and ".join(out)

    @classmethod
    def replace_commands(cls, content, **kwargs):
        current = 0
        for m in MD_LINK_PATTERN.finditer(content):
            yield content[current : m.start()]
            current = m.end()
            key = m.group("label")
            url = m.group("url")
            args = []
            element_kwargs = {**{}, **kwargs}
            if "?" in url and key not in text_commands:
                url, arguments = url.split("?")
                for arg in arguments.split("&"):
                    if "=" in arg:
                        k, v = arg.split("=")
                        element_kwargs[k] = v
                    else:
                        args.append(arg)
            if key == "src":
                yield src(url, mode="biblatex")
            elif key == "psrc":
                yield src(url, parens=True, mode="biblatex")
            elif key in cls.doc_elements:
                yield cls.doc_elements[key](url, *args, **element_kwargs)
            elif key == "abbrev_list":
                yield cls.glossing_abbrevs_list(url)
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

    structure = _load_structure(
        _get_relative_file(folder=content_dir, file=structure_file)
    )

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
        "latexmk --quiet --xelatex main.tex", shell=True, cwd=output_dir / "latex"
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
            log.error(f"File {(source_dir/filename).resolve()} does not exist.")
            sys.exit(1)
        contents[part_id] = content
        parts[part_id] = title
    return contents, parts


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(OUTPUT_DIR / "html"), **kwargs)


def run_server():
    test(Handler)


def run_preview(cldf, source_dir, output_dir, refresh=True, **kwargs):
    log.info("Rendering preview")
    watchfiles = [str(x) for x in source_dir.iterdir()]
    watchfiles += [str(x) for x in (source_dir / CONTENT_FOLDER).iterdir()]
    ds = _load_cldf_dataset(cldf)
    structure_file = _get_relative_file(
        folder=source_dir / CONTENT_FOLDER, file=STRUCTURE_FILE
    )
    contents = load_content(
        structure_file=structure_file, source_dir=source_dir / CONTENT_FOLDER
    )
    kwargs["dataset"] = ds
    kwargs["source_dir"] = source_dir
    kwargs["output_dir"] = output_dir
    if refresh:
        wkwargs = kwargs.copy()
        reloader = hupper.start_reloader(
            "pylingdocs.output.run_preview", worker_kwargs=wkwargs
        )
        reloader.watch_files(watchfiles)
    html = kwargs.pop("html", False)
    clld = kwargs.pop("clld", False)
    latex = kwargs.pop("latex", False)
    if clld and "clld" not in kwargs["formats"]:
        kwargs["formats"] = list(kwargs["formats"]) + ["clld"]
    if html and "html" not in kwargs["formats"]:
        kwargs["formats"] = list(kwargs["formats"]) + ["html"]
    if latex and "latex" not in kwargs["formats"]:
        kwargs["formats"] = list(kwargs["formats"]) + ["latex"]
    kwargs["contents"] = contents
    create_output(**kwargs)
    if html:
        threading.Thread(target=run_server).start()
    if clld:
        refresh_clld_db(OUTPUT_DIR / "clld")
    if latex:
        compile_latex()


def clean_output(output_dir):
    shutil.rmtree(output_dir)
    output_dir.mkdir()


def _write_file(part_id):
    log.debug(f"Writing {part_id}")


def check_ids(source_dir, dataset, structure):

    if isinstance(structure, (str, PosixPath)):
        structure = _load_structure(source_dir / CONTENT_FOLDER / structure)

    source_dir = Path(source_dir)
    contents, parts = _load_content(structure, source_dir / CONTENT_FOLDER)
    del parts

    builder = builders["plain"]
    content = "\n\n".join(contents.values())
    preprocessed = preprocess(content, source_dir)
    preprocessed = builder.preprocess_commands(preprocessed)
    running = True
    bad_ids = []
    while running:
        try:
            render_markdown(preprocessed, dataset, output_format="plain")
        except KeyError as e:
            bad_id = str(e).strip("'")
            preprocessed = preprocessed.replace(bad_id, "")
            bad_ids.append(bad_id)
        else:
            running = False
    if len(bad_ids) > 0:
        bad_ids = "\n".join(bad_ids)
        log.error(f"""IDs missing from the dataset:\n{bad_ids}""")
    else:
        log.info("All good!")


def create_output(
    contents,
    source_dir,
    formats,
    dataset,
    output_dir,
    metadata=None,
    latex=False,
    **kwargs,
):  # pylint: disable=too-many-arguments
    """Run different builders.


    This is the extended description.

    Args:
        arg1 (int): Description of arg1

    Returns:
        bool: blabla

    """
    if isinstance(metadata, (str, PosixPath)):
        metadata = _load_metadata(metadata)
    if metadata is None:
        metadata = {}
    metadata.update({"bibfile": Path(dataset.bibpath).resolve()})
    output_dir = Path(output_dir)
    if not output_dir.is_dir():
        log.info(f"Creating output folder {output_dir.resolve()}")
        output_dir.mkdir()
    for output_format in formats:
        for m in models:
            m.reset_cnt()
        log.info(f"Rendering format [{output_format}]")
        builder = builders[output_format]
        content = "\n\n".join([x["content"] for x in contents.values()])
        preprocessed = preprocess(content, source_dir)
        preprocessed = builder.preprocess_commands(preprocessed, **kwargs)
        preprocessed = render_markdown(
            preprocessed,
            dataset,
            decorate_gloss_string=builder.decorate_gloss_string,
            output_format=output_format,
        )
        preprocessed += "\n\n" + builder.reference_list()
        preprocessed = render_markdown(
            preprocessed,
            dataset,
            decorate_gloss_string=builder.decorate_gloss_string,
            output_format=output_format,
        )
        preprocessed = postprocess(preprocessed, builder, source_dir)
        if builder.single_output:
            builder.write_folder(
                output_dir,
                content=preprocessed,
                metadata=metadata,
                abbrev_dict=GLOSS_ABBREVS,
            )
        elif builder.name == "clld":
            builder.write_folder(
                output_dir,
                content=preprocessed,
                metadata=metadata,
                abbrev_dict=GLOSS_ABBREVS,
            )
            # builder.create_app()
            # write_clld(preprocessed)
            # with open("clld_output.txt", "w", encoding="utf-8") as f:
            #     f.write(preprocessed)
        else:
            pass
    if latex:
        compile_latex()
