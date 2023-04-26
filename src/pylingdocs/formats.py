"""Builders producing different output formats"""
import logging
import re
import shutil
from pathlib import Path
import panflute
from cookiecutter.main import cookiecutter
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2.exceptions import TemplateNotFound
from pylingdocs.config import DATA_DIR
from pylingdocs.config import FIGURE_DIR
from pylingdocs.config import LATEX_TOPLEVEL
from pylingdocs.config import OUTPUT_TEMPLATES
from pylingdocs.helpers import decorate_gloss_string
from pylingdocs.helpers import get_sections
from pylingdocs.helpers import html_example_wrap
from pylingdocs.helpers import html_gloss
from pylingdocs.helpers import latexify_table
from pylingdocs.helpers import read_config_file
from pylingdocs.helpers import src
from pylingdocs.preprocessing import MD_LINK_PATTERN


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


def latex_todo(url, **kwargs):
    if kwargs.get("release", False):
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

    @classmethod
    def ref_cmd(cls, url, *_args, **_kwargs):
        end = _kwargs.pop("end", None)
        if end:
            return f"[ref/{url}–{end}]"
        return f"[ref/{url}]"

    @classmethod
    def label_cmd(cls, url, *_args, **_kwargs):
        return f"[{url}]"

    @classmethod
    def todo_cmd(cls, url, *_args, **_kwargs):
        return f"[todo: {url}]"

    @classmethod
    def gloss_cmd(cls, url, *_args, **_kwargs):
        return url.upper()

    @classmethod
    def exref_cmd(cls, url, *_args, **_kwargs):
        end = _kwargs.pop("end", None)
        if end:
            return f"[ex:{url}–{end}]"
        return f"[ex:{url}]"

    @classmethod
    def figure_cmd(cls, url, *_args, **_kwargs):
        caption = cls.figure_metadata[url].get("caption", "")
        filename = cls.figure_metadata[url].get("filename", "")
        return f"[{caption}: {filename}]"

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
        return caption + f": [{label}]\n\n" + tabular

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

    @classmethod
    def exref_cmd(cls, url, *_args, **_kwargs):
        kw_str = " ".join([f"""{x}="{y}" """ for x, y in _kwargs.items()]) + " ".join(
            _args
        )
        return f'<a class="exref" example_id="{url}" {kw_str}></a>'

    @classmethod
    def gloss_cmd(cls, url, *_args, **_kwargs):
        return decorate_gloss_string(url.upper(), decoration=html_gloss)

    @classmethod
    def label_cmd(cls, url, *_args, **_kwargs):
        return "{#" + url + "}" + f"\n <a id='{url}'></a>"

    @classmethod
    def ref_cmd(cls, url, *_args, **_kwargs):
        return html_ref(url, *_args, **_kwargs)

    @classmethod
    def todo_cmd(cls, url, *_args, **_kwargs):
        return html_todo(url, **_kwargs)

    @classmethod
    def figure_cmd(cls, url, *_args, **_kwargs):
        if url in cls.figure_metadata:
            caption = cls.figure_metadata[url].get("caption", "")
            filename = cls.figure_metadata[url].get("filename", "")
            return f"""<figure>
<img src="figures/{filename}" alt="{caption}" />
<figcaption id="fig:{url}" aria-hidden="true">{caption}</figcaption>
</figure>"""
        return f"![Alt text](figures/{url}.jpg)"

    @classmethod
    def decorate_gloss_string(cls, x):
        return decorate_gloss_string(
            x,
            decoration=lambda x: f'<span class="gloss">{x}<span class="tooltiptext gloss-{x}" ></span></span>',
        )

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

    @classmethod
    def manex(cls, tag, content, kind):
        if content.strip().startswith("PYLINGDOCS_RAW_TABLE_START"):
            content = " \n \n" + content
        return html_example_wrap(tag, content, kind=kind)


class GitHub(OutputFormat):
    name = "github"
    file_ext = "md"

    @classmethod
    def ref_cmd(cls, url, *_args, **_kwargs):
        if "tab:" in str(url):
            return "[Table]"
        return f"<a href='#{url}'>click</a>"

    @classmethod
    def label_cmd(cls, url, *_args, **_kwargs):
        return f"<a id>='{url}'><a/>"

    @classmethod
    def gloss_cmd(cls, url, *_args, **_kwargs):
        return url.upper()

    @classmethod
    def exref_cmd(cls, url, *_args, **_kwargs):
        end = _kwargs.pop("end", None)
        if end:
            return f"[ex:{url}–{end}]"
        return f"[ex:{url}]"

    @classmethod
    def table(cls, df, caption, label):
        del label  # unused
        tabular = df.to_markdown(index=False)
        if not caption:
            return tabular
        return df.to_markdown(index=False)

    @classmethod
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


class CLLD(OutputFormat):
    name = "clld"
    file_ext = "md"
    single_output = False

    @classmethod
    def label_cmd(cls, url, *_args, **_kwargs):
        return f"{{#{url}}}"

    @classmethod
    def gloss_cmd(cls, url, *_args, **_kwargs):
        return "<span class='smallcaps'>" + url + "</span>"

    @classmethod
    def exref_cmd(cls, url, *_args, **_kwargs):
        kw_str = " ".join([f"""{x}="{y}" """ for x, y in _kwargs.items()])
        return f'<a class="exref" example_id="{url}"{kw_str}></a>'

    @classmethod
    def ref_cmd(cls, url, *_args, **_kwargs):
        return html_ref(url, *_args, **_kwargs)

    @classmethod
    def todo_cmd(cls, url, *_args, **_kwargs):
        return html_todo(url, **_kwargs)

    @classmethod
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

    @classmethod
    def reference_list(cls):
        return ""

    @classmethod
    def manex(cls, tag, content, kind):
        if content.strip().startswith("PYLINGDOCS_RAW_TABLE_START"):
            content = " \n \n" + content
        return html_example_wrap(tag, content, kind=kind)


class Latex(OutputFormat):
    name = "latex"
    file_ext = "tex"

    @classmethod
    def exref_cmd(cls, url, *_args, **_kwargs):
        end = _kwargs.get("end", None)
        suffix = _kwargs.get("suffix", "")
        bare = "bare" in _args
        if bare:
            return f"\\ref{{{url}}}"
        if end:
            return f"\\exref[{suffix}][{end}]{{{url}}}"
        return f"\\exref[{suffix}]{{{url}}}"

    @classmethod
    def label_cmd(cls, url, *_args, **_kwargs):
        return f"\\label{{{url}}}"

    @classmethod
    def ref_cmd(cls, url, *_args, **_kwargs):
        end = _kwargs.pop("end", None)
        if end:
            return f"\\crefrange{{{url}}}{{{end}}}"
        return f"\\cref{{{url}}}"

    @classmethod
    def gloss_cmd(cls, url, *_args, **_kwargs):
        return decorate_gloss_string(url.upper())

    @classmethod
    def decorate_gloss_string(cls, x):
        return decorate_gloss_string(x)

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
                f"\\newGlossingAbbrev{{{x.lower()}}}{{{y.split('(')[0].replace(',', ';')}}}"
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
        if OUTPUT_TEMPLATES["latex"] == "book":
            return ";".join(out)  # may want to use this for all templates at some point
        return " and ".join(out)

    @classmethod
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


builders = {x.name: x for x in [PlainText, GitHub, Latex, HTML, CLLD]}
try:
    from custom_pld_builders import builders as custom_builders

    for k, v in custom_builders.items():
        builders[k] = v
except ImportError:
    pass
