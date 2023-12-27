"""Builders producing different output formats"""
import logging
import re
import shutil
import sys
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, test
from pathlib import Path

import panflute
from cookiecutter.main import cookiecutter
from jinja2 import Environment, PackageLoader
from jinja2.exceptions import TemplateNotFound
from mkdocs.commands.serve import serve
from mkdocs.config import load_config
from slugify import slugify
from tqdm import tqdm
from writio import dump, load

from lingdocs.config import (
    COLDIV,
    COLEND,
    COLSTART,
    DATA_DIR,
    EXTRA_DIR,
    MD_LINK_PATTERN,
    PLD_DIR,
    config,
    merge_dicts,
)
from lingdocs.helpers import (
    Enumerator,
    decorate_gloss_string,
    extract_chapters,
    get_sections,
    html_example_wrap,
    html_gloss,
    latexify_table,
    src,
)

FIGURE_DIR = "figures"
NUM_PRE = re.compile(r"[\d]+\ ")
ABC_PRE = re.compile(r"[A-Z]+\ ")

log = logging.getLogger(__name__)


def blank_todo(url, **_kwargs):
    del url
    return ""


col_pattern = rf"{COLSTART}(?s:.*?){COLEND}"

media_base = config["media_url"] or "site:assets/audio/"
if not media_base.endswith("/"):
    media_base += "/"


def slide_columns(text):
    text = text.replace(COLSTART, "")
    text = text.replace(COLEND, "")
    cols = text.split(COLDIV)
    if len(cols) > 2:
        log.warning("Too many columns:")
        log.warning(text)
    return f""".cols[\n.fifty[
{cols[0]}
]
.fifty[
{cols[1]}
]
]"""


def html_todo(url, **kwargs):
    if kwargs.get("release", False):
        return ""
    return f"<span class='sidenote'>to do: {url}</span>"
    if "?" in str(url):
        return "sidenote<span class='sidenote'>{url}</span>"
        return f"<span title='{url}'>❓</span>"
    return f"<span title='{url}'>❗️</span>"


def mkdocs_todo(url, **kwargs):
    if kwargs.get("release", False):
        return ""
    if "?" in str(url):
        return f"<span title='{url}'>❔</span>"
    return f"<span title='{url}'>❕</span>"


def latex_todo(url, **kwargs):
    return ""
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
    figure_dir = "figures"
    ref_labels = {}
    ref_locations = {}
    data_dir = "data"
    topic_dir = "topics"
    fallback_layout = "basic"
    audio_path = "audio"

    @property
    def label(cls):
        return cls.name

    def ref_cmd(cls, url, *_args, **_kwargs):
        end = _kwargs.pop("end", None)
        if end:
            if cls.ref_labels:
                return cls.ref_labels[url] + f"–{end}"
            return f"[ref/{url}–{end}]"
        if cls.ref_labels and url in cls.ref_labels:
            return cls.ref_labels[url]
        return f"[N/A: {url}]"

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
        if not cls.ref_labels:
            return "[No figure references found]"
        filename = cls.figure_metadata.get(url, {}).get("filename", "")
        return f"({cls.ref_labels[f'fig:{url}']}: {cls.figure_dir}/{filename})"

    def decorate_gloss_string(cls, x):
        return decorate_gloss_string(x, decoration=lambda x: x.upper())

    def get_layout_path(cls):
        base = DATA_DIR / "format_templates"
        cbase = PLD_DIR / "formats" / "layouts"
        for b in [cbase, base]:
            tpl_path = b / cls.name / config["output"]["layout"]
            if not tpl_path.is_dir():
                tpl_path = b / cls.name / cls.fallback_layout
            if not tpl_path.is_dir():
                tpl_path = (
                    b / cls.__class__.__bases__[0].name / config["output"]["layout"]
                )
            if not tpl_path.is_dir():
                tpl_path = b / cls.__class__.__bases__[0].name / cls.fallback_layout
            if tpl_path.is_dir():
                return str(tpl_path)
        log.error(f"Could not find cookiecutter folder for {cls.name}")
        sys.exit()

    def adjust_layout(cls, content, metadata, source_dir):
        pass

    def get_audio(cls, dic, url):
        pass

    def write_folder(
        cls,
        output_dir,
        source_dir,
        content=None,
        chapters=None,
        metadata=None,
        abbrev_dict=None,
        ref_labels=None,
        ref_locations=None,
        audio=None,
    ):  # pylint: disable=too-many-arguments
        # log.debug(f"Writing {cls.name} to {output_dir} (from {DATA_DIR})")
        abbrev_dict = abbrev_dict or {}
        extra = {
            "name": cls.name,
            "chapters": chapters,
            "project_title": metadata.get("title", "A beautiful title"),
            "glossing_abbrevs": cls.register_glossing_abbrevs(abbrev_dict),
            "ref_labels": str(ref_labels),
            "ref_locations": str(ref_locations),
            "data": config["data"]["data"],
            "layout": config["output"]["layout"],
            "conf": config.data.get(cls.name, {}),
        }
        if "authors" in metadata:
            extra["author"] = cls.author_list(metadata["authors"])
        else:
            extra["author"] = cls.author_list([])
        if content is not None:
            content = content.replace("![](", "![](images/")
            content = cls.preprocess(content)
            extra.update({"content": content})

        landingpage_path = source_dir / EXTRA_DIR / f"landingpage_{cls.name}.md"
        if landingpage_path.is_file():
            extra["landingpage"] = load(landingpage_path)
        else:
            extra["landingpage"] = ""
        extra.update(**metadata)
        template_path = cls.get_layout_path()
        cookiecutter(
            template_path,
            output_dir=output_dir,
            extra_context=extra,
            overwrite_if_exists=True,
            no_input=True,
        )

        cls.adjust_layout(content, metadata=extra, source_dir=source_dir)

        figure_dir = source_dir / FIGURE_DIR
        if figure_dir.is_dir():
            target_dir = output_dir / cls.name / cls.figure_dir
            if not target_dir.is_dir():
                target_dir.mkdir()
            for file in figure_dir.iterdir():
                target = target_dir / file.name
                if not target.is_file():
                    shutil.copy(file, target)

        def _iterdir(d):
            if d.is_file():
                yield d
            elif d.name not in [".", ".."] and d.is_dir():
                for sd in d.iterdir():
                    for sdi in _iterdir(sd):
                        yield sdi

        if source_dir / EXTRA_DIR / cls.name:
            for d in _iterdir(source_dir / EXTRA_DIR / cls.name):
                parents = str(d.parents[0]).replace(str(EXTRA_DIR) + "/", "", 1)
                (output_dir / parents).mkdir(exist_ok=True, parents=True)
                out_path = output_dir / parents / d.name
                shutil.copy(d, out_path)

        cls.copy_audio(audio, output_dir)

    def copy_audio(cls, audio, out_path):
        if config["paths"]["audio"].is_dir():
            (out_path / cls.name / cls.audio_path).mkdir(exist_ok=True, parents=True)
            for media in tqdm(audio.values(), desc="Audio"):
                src_path = config["paths"]["audio"] / media["Download_URL"].path
                target_path = out_path / cls.name / cls.audio_path / Path(src_path).name
                if src_path.is_file() and not target_path.is_file():
                    shutil.copy(src_path, target_path)

    def register_glossing_abbrevs(cls, abbrev_dict):
        del abbrev_dict
        return ""

    def glossing_abbrevs_list(cls, arg_string):
        del arg_string
        return ""

    def write_part(cls, content, path):  # pragma: no cover (not used ATM)
        content = cls.preprocess(content)
        env = Environment(
            loader=PackageLoader("lingdocs", f"data/format_templates/{cls.name}"),
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

    def postprocess(cls, content, metadata=None):
        del metadata
        return content

    def table(cls, df, caption, label):
        label = f"tab:{label}"
        if label in cls.ref_labels:
            caption = f"{cls.ref_labels[label]}: {caption}"
        else:
            log.warning(f"Unknown table {label}")
        tabular = df.to_markdown(index=False, tablefmt="grid")
        if not caption:
            return tabular
        return f"{caption}:\n\n{tabular}"

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

    def run_preview(cls):
        log.warning(
            f"Not rendering live preview for format {cls.name} {config['paths']['output'].resolve()}"
        )


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

    def postprocess(cls, content, metadata=None):
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
        extra = ["--shift-heading-level-by=1"]
        if config["output"]["layout"] != "slides":
            extra.append("--section-divs")
        hits = re.findall(col_pattern, content)
        for hit in hits:
            content = content.replace(hit, slide_columns(hit))
        html_output = panflute.convert_text(
            content,
            output_format="html",
            input_format="markdown",
            extra_args=extra,
        )
        unresolved_labels = re.findall(r"{#(.*?)}", html_output)
        if unresolved_labels:
            log.warning("Unresolved labels:")
        for label in unresolved_labels:
            log.warning(label)
            html_output = html_output.replace(f"{{#{label}}}", "")
        if config["output"]["layout"] == "slides":
            sep = "(<h2)"
            processed_slides = []
            slides = re.split(sep, html_output)
            slides = slides[1::]
            i = 0
            while i < len(slides) - 1:
                content = slides[i] + slides[i + 1]
                processed_slides.append(f"\n{content}\n---")
                i += 2
            return "\n".join(processed_slides)
        return html_output

    def manex(cls, tag, content, kind):
        if content.strip().startswith("PYLINGDOCS_RAW_TABLE_START"):
            content = " \n \n" + content
        return html_example_wrap(tag, content, kind=kind)

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(
                *args, directory=str(config["paths"]["output"] / "html"), **kwargs
            )

    def run_server(cls):
        test(cls.Handler)

    def run_preview(cls):
        threading.Thread(target=cls.run_server).start()


class MkDocs(HTML):
    name = "mkdocs"
    figure_dir = "docs/figures"
    data_dir = "docs/data"
    topic_dir = "docs/index/topics"
    file_ext = "md"
    audio_path = "docs/assets/audio"

    def preprocess(cls, content):
        content = re.sub(
            r"\[(.*?)\]{.smallcaps}",
            r'<span class="smallcaps">\g<1></span>',
            content,
        )
        return (
            content.replace("```{=html}", "")
            .replace("```", "")
            .replace("(#source-", "(site:references/#source-")
        )

    def get_audio(cls, dic, url):
        if url not in dic:
            return ""
        return {"url": f"{media_base}{dic[url]['url']}", "type": dic[url]["url"]}

    def postprocess(cls, content, metadata=None):
        metadata = metadata or {}
        if config["output"]["layout"] == "article":
            enm = Enumerator()
            out = []
            i = 1
            for line in content.split("\n"):
                if line.startswith("#"):
                    out.append(line.replace("# ", f"## {enm.parse(line)} "))
                    if line.startswith("# "):
                        i += 1
                else:
                    out.append(line)
            content = "#" + metadata["title"] + "\n\n" + "\n".join(out)
        return content

    def adjust_layout(cls, content, metadata, source_dir):
        if config["output"]["layout"] in ["book"]:
            chapters = extract_chapters(content, mode="pandoc")
            doc_path = config["paths"]["output"] / "mkdocs" / "docs"
            for k, v in chapters.items():
                dump(v, doc_path / f"{k}.md")
            index = f"""---
hide:
    - navigation
---
{metadata.get("landingpage", "")}"""
            dump(index, doc_path / "index.md")

        custom_conf = source_dir / EXTRA_DIR / "mkdocs.yml"
        if custom_conf.is_file():
            custom_conf = load(custom_conf)
            out_path = Path(config["paths"]["output"]) / cls.name / "mkdocs.yml"
            out_conf = load(out_path)
            nconf = merge_dicts(out_conf, custom_conf)
            dump(nconf, out_path)

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
        return f"![{url}](/figures/{url}.jpg)"

    def label_cmd(cls, url, *_args, **_kwargs):
        return f"{{ #{url} }}"

    def ref_cmd(cls, url, *_args, **_kwargs):
        if url in cls.ref_labels and url in cls.ref_locations:
            # kw_str = " ".join([f"""{x}="{y}" """ for x, y in _kwargs.items()]) # todo: is this needed for refs?
            return f"[{cls.ref_labels[url]}](site:/{cls.ref_locations[url]}#{url})"
        log.warning(f"Could not find reference {url}")
        return f"(n/a: {url})"

    def todo_cmd(cls, url, *_args, **_kwargs):
        return mkdocs_todo(url, **_kwargs)

    def run_preview(cls):
        log.warning(f"Not rendering live preview for format {cls.name}.")


class GitHub(PlainText):
    name = "github"
    file_ext = "md"

    def ref_cmd(cls, url, *_args, **_kwargs):
        end = _kwargs.pop("end", None)
        if end:
            if cls.ref_labels:
                return f"<a href='#{url}'>{cls.ref_labels[url]}–{end}</a>"
            return f"[n/a:{url}–{end}]"
        if cls.ref_labels and url in cls.ref_labels:
            return f"[{cls.ref_labels[url]}](#{url})"
        return f"[n/a: {url}]"

    def label_cmd(cls, url, *_args, **_kwargs):
        return ""

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

    def figure_cmd(cls, url, *_args, **_kwargs):
        if not cls.ref_labels:
            return f"(n/a: {url})"
        caption = cls.figure_metadata.get(url, {}).get("caption", "")
        filename = cls.figure_metadata.get(url, {}).get("filename", "")
        return f"""\\begin{{figure}}
\\centering
\\includegraphics{{{cls.figure_dir}/{filename}}}
\\caption{{{caption}\\label{{fig:{url}}}}}
\\end{{figure}}
"""

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
        out = []
        for line in content.split("\n"):
            if line.startswith("#") and "\\label" not in line:
                line = line + f"\\label{{{slugify(line)}}}"
            out.append(line)
        if config["output"]["layout"] == "book":
            toplevel = "chapter"
        else:
            toplevel = "section"
        doc = panflute.convert_text(
            "\n".join(out),
            output_format="latex",
            input_format="markdown-auto_identifiers",
            extra_args=[f"--top-level-division={toplevel}"],
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
        if config["output"]["layout"] == "book":
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


builders = {x.name: x for x in [PlainText, GitHub, Latex, HTML, CLLD, MkDocs]}


if Path(f"{PLD_DIR}/formats.py").is_file():
    sys.path.insert(1, str(PLD_DIR))
    from formats import formats

    for fmt in formats:
        builders[fmt.name] = fmt
