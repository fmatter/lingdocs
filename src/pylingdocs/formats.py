"""Builders producing different output formats"""
import logging
import re
import shutil
import sys
from pathlib import Path

import jinja2
import panflute
from cldfviz.text import render
from cookiecutter.main import cookiecutter
from jinja2 import Environment, FileSystemLoader, PackageLoader
from jinja2.exceptions import TemplateNotFound
from tqdm import tqdm
from writio import dump, load

from pylingdocs.config import (
    DATA_DIR,
    FIGURE_DIR,
    LATEX_EX_TEMPL,
    LATEX_TOPLEVEL,
    MD_LINK_PATTERN,
    WRITE_DATA,
    RICH,
    OUTPUT_TEMPLATES,
)
from pylingdocs.helpers import (
    decorate_gloss_string,
    func_dict,
    get_sections,
    html_example_wrap,
    html_gloss,
    latexify_table,
    src,
)

NUM_PRE = re.compile(r"[\d]+\ ")
ABC_PRE = re.compile(r"[A-Z]+\ ")

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


def mkdocs_todo(url, **kwargs):
    if kwargs.get("release", False):
        return ""
    if "?" in str(url):
        return f"<span title='{url}'>❔</span>"
    return f"<span title='{url}'>❕</span>"


def latex_todo(url, **kwargs):
    if kwargs.get("release", False):
        return ""
    return ""
    return f"\\todo{{{url}}}"


def html_ref(url, *_args, **_kwargs):
    kw_str = " ".join([f"""{x}="{y}" """ for x, y in _kwargs.items()])
    return f"<a href='#{url}' class='crossref' name='{url}' {kw_str}>ref</a>"


text_commands = ["todo"]


class OutputFormat:
    name = "boilerplate"
    file_ext = "txt"
    single_output = True
    figure_metadata = {}
    figure_dir = "figures"
    ref_labels = None
    ref_locations = None
    data_dir = "data"

    @property
    def label(cls):
        return cls.name

    def ref_cmd(cls, url, *_args, **_kwargs):
        end = _kwargs.pop("end", None)
        if end:
            if cls.ref_labels:
                return cls.ref_labels[url] + f"–{end}"
            return f"[ref/{url}–{end}]"
        if cls.ref_labels:
            return cls.ref_labels[url]
        return f"[ref/{url}]"

    def label_cmd(cls, url, *_args, **_kwargs):
        return f"[{url}]"

    def todo_cmd(cls, url, *_args, **_kwargs):
        return f"[todo: {url}]"

    def gloss_cmd(cls, url, *_args, **_kwargs):
        return url.upper()

    def exref_cmd(cls, url, *_args, **_kwargs):
        end = _kwargs.pop("end", None)
        if end:
            return f"[ex:{url}–{end}]"
        return f"[ex:{url}]"

    def figure_cmd(cls, url, *_args, **_kwargs):
        caption = cls.figure_metadata[url].get("caption", "")
        filename = cls.figure_metadata[url].get("filename", "")
        return f"({cls.ref_labels[f'fig:{url}']}: {filename})"

    def decorate_gloss_string(cls, x):
        return decorate_gloss_string(x, decoration=lambda x: x.upper())

    def write_folder(
        cls,
        output_dir,
        content=None,
        parts=None,
        metadata=None,
        abbrev_dict=None,
        ref_labels=None,
        ref_locations=None,
    ):  # pylint: disable=too-many-arguments
        # log.debug(f"Writing {cls.name} to {output_dir} (from {DATA_DIR})")
        if not abbrev_dict:
            abbrev_dict = {}

        extra = {
            "name": cls.name,
            "chapters": parts,
            "project_title": metadata.get("title", "A beautiful title"),
            "glossing_abbrevs": cls.register_glossing_abbrevs(abbrev_dict),
            "ref_labels": str(ref_labels),
            "ref_locations": str(ref_locations),
            "data": WRITE_DATA,
            "site_url": metadata.get("site_url", None),
        }
        if "authors" in metadata:
            extra["author"] = cls.author_list(metadata["authors"])
        else:
            extra["author"] = cls.author_list([])

        if content is not None:
            content = content.replace("![](", "![](images/")
            content = cls.preprocess(content)
            extra.update({"content": content})

        landingpage_path = Path("pld") / f"{cls.name}_index.md"
        if landingpage_path.is_file():
            extra["landingpage"] = load(landingpage_path)

        extra.update(**metadata)

        template_path = Path("format_templates") / cls.name / OUTPUT_TEMPLATES[cls.name]
        local_template_path = Path("pld") / template_path
        if local_template_path.is_dir():
            template_path = str(local_template_path)
        else:
            template_path = str(DATA_DIR / template_path)

        cookiecutter(
            template_path,
            output_dir=output_dir,
            extra_context=extra,
            overwrite_if_exists=True,
            no_input=True,
        )
        if FIGURE_DIR.is_dir():
            target_dir = output_dir / cls.name / cls.figure_dir
            if not target_dir.is_dir():
                target_dir.mkdir()
            for file in FIGURE_DIR.iterdir():
                target = target_dir / file.name
                if not target.is_file():
                    shutil.copy(file, target)

    def register_glossing_abbrevs(cls, abbrev_dict):
        del abbrev_dict
        return ""

    def glossing_abbrevs_list(cls, arg_string):
        del arg_string
        return ""

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

    def replace_commands(cls, content, **_kwargs):
        doc_elements = {
            "ref": cls.ref_cmd,  # crossreferences
            "label": cls.label_cmd,  # anchors for crossreferences
            "gl": cls.gloss_cmd,  # a glossing abbreviation
            "todo": cls.todo_cmd,  # a todo
            "exref": cls.exref_cmd,  # an example reference
            "figure": cls.figure_cmd,  # an image with a caption
        }
        current = 0
        for m in MD_LINK_PATTERN.finditer(content):
            yield content[current : m.start()]
            current = m.end()
            key = m.group("label")
            url = m.group("url")
            args = []
            cmd_kwargs = {}
            if "?" in url and key not in text_commands:
                url, arguments = url.split("?")
                for arg in arguments.split("&"):
                    if "=" in arg:
                        k, v = arg.split("=")
                        cmd_kwargs[k] = v
                    else:
                        args.append(arg)
            if key == "src":
                yield src(url)
            elif key == "psrc":
                yield src(url, parens=True)
            elif key in doc_elements:
                yield doc_elements[key](url, *args, **cmd_kwargs)
            elif key == "abbrev_list":
                yield cls.glossing_abbrevs_list(url)
            else:
                yield content[m.start() : m.end()]
        yield content[current:]

    def preprocess_commands(cls, content, **kwargs):
        processed = "".join(cls.replace_commands(content, **kwargs))
        return processed

    def preprocess(cls, content):
        return content

    def postprocess(cls, content):
        return content

    def table(cls, df, caption, label):
        # del label  # unused
        tabular = df.to_markdown(index=False, tablefmt="grid")
        if not caption:
            return tabular
        return caption + f":\n\n" + tabular

    def manex(cls, tag, content, kind):
        del kind  # unused
        return f"[ex-{tag}]\n\n{content}"

    def reference_list(cls):
        return "# References \n[References](Source?cited_only#cldf:__all__)"

    def author_list(cls, authors):
        if len(authors) == 0:
            return "Anonymous"
        out = []
        for author in authors:
            out.append(f'{author["given-names"]} {author["family-names"]}')
        return " and ".join(out)


class PlainText(OutputFormat):
    name = "plain"

    def preprocess(cls, content):
        res = panflute.convert_text(
            content, output_format="plain", input_format="markdown"
        )
        return res.replace("|WHITESPACE|", " ")

    def label_cmd(cls, url, *_args, **_kwargs):
        return ""

    def exref_cmd(cls, url, *_args, **_kwargs):
        end = _kwargs.pop("end", None)
        if end:
            return f"[exref-{url}]({end})"
        return f"[exref-{url}]"

    def postprocess(cls, content):
        output = []
        examples = []
        exref_pattern = r"\[exref-(?P<url>.*?)\](\((?P<end>.+)\))?"
        ex_pattern = r"\[(sub)?ex-(?P<url>.*?)\]"
        ex_cnt = 0
        subex_cnt = 0
        for line in content.split("\n"):
            ex_res = re.search(ex_pattern, line)
            if ex_res:
                url = ex_res.group("url")
                if "sub" in ex_res.group(0):
                    subex_cnt += 1
                    letter = chr(ord("`") + subex_cnt)
                    line = re.sub(ex_pattern, f"({letter})", line)
                    examples.append((url, f"{ex_cnt}{letter}"))
                else:
                    ex_cnt += 1
                    line = re.sub(ex_pattern, f"({ex_cnt})", line)
                    subex_cnt = 0
                    examples.append((url, str(ex_cnt)))
            for hit in re.finditer(exref_pattern, line):
                hdic = hit.groupdict()
                hdic["string"] = hit.group(0)
                examples.append(hdic)
            output.append(line)
        content = "\n".join(output)
        for i, example in enumerate(examples):
            if isinstance(example, dict):
                candidates = [
                    tc
                    for tc, x in enumerate(examples)
                    if (isinstance(x, tuple) and x[0] == example["url"])
                ]
                if not candidates:
                    log.warning(
                        f"Could not resolve example reference {example['string']}"
                    )
                else:
                    best = min(candidates, key=lambda x: abs(x - i))
                    log.debug(
                        f"Best candidate for example {example['url']} at position {i}: {best}"
                    )
                    content = content.replace(
                        example["string"], f"({examples[best][1]})", 1
                    )
        return content


class HTML(PlainText):
    name = "html"
    file_ext = "html"

    def exref_cmd(cls, url, *_args, **_kwargs):
        kw_str = " ".join([f"""{x}="{y}" """ for x, y in _kwargs.items()]) + " ".join(
            _args
        )
        return f'<a class="exref" example_id="{url}" {kw_str}></a>'

    def gloss_cmd(cls, url, *_args, **_kwargs):
        return decorate_gloss_string(url.upper(), decoration=html_gloss)

    def label_cmd(cls, url, *_args, **_kwargs):
        return f"{{ #{url} }}"

    def ref_cmd(cls, url, *_args, **_kwargs):
        return html_ref(url, *_args, **_kwargs)

    def todo_cmd(cls, url, *_args, **_kwargs):
        return html_todo(url, **_kwargs)

    def figure_cmd(cls, url, *_args, **_kwargs):
        if url in cls.figure_metadata:
            caption = cls.figure_metadata[url].get("caption", "")
            filename = cls.figure_metadata[url].get("filename", "")
            return f"""<figure>
<img src="figures/{filename}" alt="{caption}" />
<figcaption id="fig:{url}" aria-hidden="true">{caption}</figcaption>
</figure>"""
        return f"![Alt text](figures/{url}.jpg)"

    def decorate_gloss_string(cls, x):
        return decorate_gloss_string(
            x,
            decoration=lambda x: f'<span class="gloss">{x}<span class="tooltiptext gloss-{x}" ></span></span>',
        )

    def register_glossing_abbrevs(cls, abbrev_dict):
        return f"""var abbrev_dict={abbrev_dict}; for (var key in abbrev_dict){{
var targets = document.getElementsByClassName('gloss-'+key)
for (var i = 0; i < targets.length; i++) {{
    targets[i].innerHTML = abbrev_dict[key];
}}
}};"""

    def glossing_abbrevs_list(cls, arg_string):
        return """<dl id="glossing_abbrevs"></dl>"""

    def table(cls, df, caption, label):
        table = df.to_html(escape=False, index=False)
        if not caption:
            return table
        return table.replace(
            "<thead",
            f"<caption class='table' id ='tab:{label}'>{caption}</caption><thead",
        )

    def preprocess(cls, content):
        html_output = panflute.convert_text(
            content,
            output_format="html",
            input_format="markdown",
            extra_args=["--shift-heading-level-by=1"],
        )
        unresolved_labels = re.findall(r"{#(.*?)}", html_output)
        if unresolved_labels:
            log.warning("Unresolved labels:")
        for label in unresolved_labels:
            log.warning(label)
            html_output = html_output.replace(f"{{#{label}}}", "")
        if OUTPUT_TEMPLATES["html"] == "slides":
            return html_output.replace("\n<h", "\n---\n<h")
        return html_output

    def manex(cls, tag, content, kind):
        if content.strip().startswith("PYLINGDOCS_RAW_TABLE_START"):
            content = " \n \n" + content
        return html_example_wrap(tag, content, kind=kind)


class MkDocs(HTML):
    name = "mkdocs"
    figure_dir = "docs/figures"
    data_dir = "docs/data"
    file_ext = "md"

    def preprocess(cls, content):
        return content.replace("```{=html}", "").replace("```", "")

    def postprocess(cls, content):
        return content.replace("(#source-", "(/references/#source-")

    def table(cls, df, caption, label):
        tabular = df.to_html(escape=False, index=False)
        tabular = panflute.convert_text(
            tabular,
            output_format="html",
            input_format="markdown",
        )
        tabular = re.sub('style="(.*)"', "", tabular)
        if not caption:
            return "<br>" + tabular
        return tabular.replace(
            "<thead",
            f"<caption class='table' id ='tab:{label}'>{caption}</caption><thead",
        )

    def figure_cmd(cls, url, *_args, **_kwargs):
        if url in cls.figure_metadata:
            caption = cls.figure_metadata[url].get("caption", "")
            filename = cls.figure_metadata[url].get("filename", "")
            return f"""<figure>
<img src="/figures/{filename}" alt="{caption}" />
<figcaption id="fig:{url}" aria-hidden="true">{caption}</figcaption>
</figure>"""
        return f"![{caption}](/figures/{url}.jpg)"

    def label_cmd(cls, url, *_args, **_kwargs):
        return f"{{ #{url} }}"

    def todo_cmd(cls, url, *_args, **_kwargs):
        return mkdocs_todo(url, **_kwargs)


class GitHub(PlainText):
    name = "github"
    file_ext = "md"

    def ref_cmd(cls, url, *_args, **_kwargs):
        if "tab:" in str(url):
            return "[Table]"
        return f"<a href='#{url}'>click</a>"

    def label_cmd(cls, url, *_args, **_kwargs):
        return f"<a id>='{url}'><a/>"

    def gloss_cmd(cls, url, *_args, **_kwargs):
        return url.upper()

    def exref_cmd(cls, url, *_args, **_kwargs):
        end = _kwargs.pop("end", None)
        if end:
            return f"[ex:{url}–{end}]"
        return f"[ex:{url}]"

    def table(cls, df, caption, label):
        del label  # unused
        tabular = df.to_markdown(index=False)
        if not caption:
            return tabular
        return df.to_markdown(index=False)

    def preprocess(cls, content):
        toc = []
        for level, title, tag in get_sections(content):
            toc.append("   " * level + f"1. [{title}](#{tag})")
        res = panflute.convert_text(
            "\n".join(toc) + "\n\n" + content,
            output_format="gfm",
            input_format="markdown",
        )
        return res.replace("WHITESPACE", " ").replace(r"\|", "")


class CLLD(PlainText):
    name = "clld"
    file_ext = "md"
    single_output = False

    def label_cmd(cls, url, *_args, **_kwargs):
        return f"{{#{url}}}"

    def gloss_cmd(cls, url, *_args, **_kwargs):
        return "<span class='smallcaps'>" + url + "</span>"

    def exref_cmd(cls, url, *_args, **_kwargs):
        kw_str = " ".join([f"""{x}="{y}" """ for x, y in _kwargs.items()])
        return f'<a class="exref" example_id="{url}"{kw_str}></a>'

    def ref_cmd(cls, url, *_args, **_kwargs):
        return html_ref(url, *_args, **_kwargs)

    def todo_cmd(cls, url, *_args, **_kwargs):
        return html_todo(url, **_kwargs)

    def table(cls, df, caption, label):
        if not caption:
            if len(df) == 0:
                df = df.append({x: "" for x in df.columns}, ignore_index=True)
            return df.to_markdown(index=False)
        cap = "".join(cls.replace_commands(caption))
        return (
            f"<a id='tab:{label}'></a><div class='caption table' id='tab:{label}'>{cap}</div>\n\n"
            + df.to_markdown(index=False)
        )

    def figure_cmd(cls, url, *_args, **_kwargs):
        if url in cls.figure_metadata:
            caption = cls.figure_metadata[url].get("caption", "")
            filename = cls.figure_metadata[url].get("filename", "")
            return f"""<figure>
<img src="/static/{filename}" alt="{caption}" />
<figcaption id="fig:{url}" aria-hidden="true">{caption}</figcaption>
</figure>"""
        return f"![Alt text]({url})"

    def reference_list(cls):
        return ""

    def manex(cls, tag, content, kind):
        if content.strip().startswith("PYLINGDOCS_RAW_TABLE_START"):
            content = " \n \n" + content
        return html_example_wrap(tag, content, kind=kind)


class Latex(PlainText):
    name = "latex"
    file_ext = "tex"

    def exref_cmd(cls, url, *_args, **_kwargs):
        end = _kwargs.get("end", None)
        suffix = _kwargs.get("suffix", "")
        bare = "bare" in _args
        if bare:
            return f"\\ref{{{url}}}"
        if end:
            return f"\\exref[{suffix}][{end}]{{{url}}}"
        return f"\\exref[{suffix}]{{{url}}}"

    def label_cmd(cls, url, *_args, **_kwargs):
        return f"\\label{{{url}}}"

    def todo_cmd(cls, url, *_args, **_kwargs):
        return latex_todo(url, **_kwargs)

    def ref_cmd(cls, url, *_args, **_kwargs):
        end = _kwargs.pop("end", None)
        if end:
            return f"\\crefrange{{{url}}}{{{end}}}"
        return f"\\cref{{{url}}}"

    def gloss_cmd(cls, url, *_args, **_kwargs):
        return decorate_gloss_string(url.upper())

    def decorate_gloss_string(cls, x):
        return decorate_gloss_string(x)

    def manex(cls, tag, content, kind):
        if kind == "multipart":
            return f"\\pex\\label{{{tag}}}{content}\\xe"
        if kind == "subexample":
            return f"\\a\\label{{{tag}}} {content}"
        return f"\\ex\\label{{{tag}}} {content} \\xe"

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

    def register_glossing_abbrevs(cls, abbrev_dict):
        return "\n".join(
            [
                f"\\newGlossingAbbrev{{{x.lower()}}}{{{y.split('(')[0].replace(',', ';')}}}"
                for x, y in abbrev_dict.items()
            ]
        )

    def glossing_abbrevs_list(cls, arg_string):
        return "\\glossingAbbrevsList"

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

    def reference_list(cls):
        return "\\printbibliography"

    def author_list(cls, authors):
        if len(authors) == 0:
            return "Anonymous"
        out = []
        for author in authors:
            out.append(f'{author["given-names"]} {author["family-names"]}')
        if OUTPUT_TEMPLATES["latex"] == "book":
            return ";".join(out)  # may want to use this for all templates at some point
        return " and ".join(out)

    def replace_commands(cls, content, **kwargs):
        doc_elements = {
            "ref": cls.ref_cmd,  # crossreferences
            "label": cls.label_cmd,  # anchors for crossreferences
            "gl": cls.gloss_cmd,  # a glossing abbreviation
            "todo": cls.todo_cmd,  # a todo
            "exref": cls.exref_cmd,  # an example reference
            "figure": cls.figure_cmd,  # an image with a caption
        }
        current = 0
        for m in MD_LINK_PATTERN.finditer(content):
            yield content[current : m.start()]
            current = m.end()
            key = m.group("label")
            url = m.group("url")
            args = []
            elementkwargs = {**{}, **kwargs}
            if "?" in url and key not in text_commands:
                url, arguments = url.split("?")
                for arg in arguments.split("&"):
                    if "=" in arg:
                        k, v = arg.split("=")
                        elementkwargs[k] = v
                    else:
                        args.append(arg)
            if key == "src":
                yield src(url, mode="biblatex", full="full" in args)
            elif key == "psrc":
                yield src(url, parens=True, mode="biblatex", full="full" in args)
            elif key in doc_elements:
                yield doc_elements[key](url, *args, **elementkwargs)
            elif key == "abbrev_list":
                yield cls.glossing_abbrevs_list(url)
            else:
                yield content[m.start() : m.end()]
        yield content[current:]


builders = {x.name: x() for x in [PlainText, GitHub, Latex, HTML, CLLD, MkDocs]}


if Path("pld/formats.py").is_file():
    sys.path.insert(1, "pld")
    from formats import formats

    for fmt in formats:
        builders[fmt.name] = fmt
