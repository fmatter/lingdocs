"""Various helpers"""
import importlib.util
import json
import logging
import re
import sys
import tempfile
from pathlib import Path

import pandas as pd
import panflute
import pybtex
import pycldf
import yaml
from clldutils import jsonlib
from cookiecutter.main import cookiecutter
from jinja2.runtime import Undefined
from pycldf import Dataset, Source
from slugify import slugify
from writio import dump, load

from lingdocs.config import (
    CONTENT_FOLDER,
    DATA_DIR,
    EXTRA_DIR,
    FIGURE_DIR,
    STRUCTURE_FILE,
    TABLE_DIR,
    config,
)
from lingdocs.metadata import ORCID_STR

log = logging.getLogger(__name__)


def read_file(path, mode=None, encoding="utf-8"):
    path = Path(path)
    if path.is_file():
        with open(path, "r", encoding=encoding) as f:
            if mode == "yaml" or path.suffix == ".yaml":
                return yaml.load(f, Loader=yaml.SafeLoader)
            if mode == "json" or path.suffix == ".json":
                return json.load(f)
            return f.read()
    else:
        return None


def write_file(content, path, mode=None, encoding="utf-8"):
    with open(path, "w", encoding=encoding) as f:
        if mode == "yaml" or path.suffix == ".yaml":
            yaml.dump(f, content)
        elif mode == "json" or path.suffix == ".json":
            json.dump(content, f, ensure_ascii=False, indent=4)
        else:
            f.write(content)


def parse_heading(string, mode="pandoc"):
    prefix = string.split(" ")[0]
    level = prefix.count("#")
    title = string.split(" ", 1)[1]
    if mode == "pandoc":
        attr_list = re.search("({.*?})", title)
        if attr_list:
            attr_list = attr_list.group()
            tag = re.findall(r"{\s?\#(.*?)\s?}", attr_list)[0]
            title = title.replace(attr_list, "")
        else:
            tag = slugify(title, allow_unicode=True)
    elif mode == "pld":
        res = re.findall(r"(.*?) \[label\]\((.*?)\)", title)
        if not res:
            tag = slugify(title, allow_unicode=True)
        else:
            title, tag = res[0]
    return level, title.strip(" "), tag


def get_sections(content, mode="pandoc"):
    for line in content.split("\n"):
        if line.startswith("#"):
            yield parse_heading(line, mode=mode)


def get_glosses(word, gloss_cands):
    parts = split_word(word)
    for j, part in enumerate(parts):
        if is_gloss_abbr_candidate(part, parts, j):
            # take care of numbered genders
            if not (part[0] == "G" and re.match(r"\d", part[1:])):
                for gloss in resolve_glossing_combination(part):
                    if gloss not in gloss_cands:
                        yield gloss


def print_counter(counters):
    out = []
    for value in counters.values():
        if value != 0:
            out.append(str(value))
        else:
            return ".".join(out)
    return ".".join(out)


SECDEPTH = 5


def extract_chapters(content, mode="pld"):
    chapters = {}
    if mode == "pld":
        label_pattern = re.compile(r"(?P<title>.*?)\s+\[label\]\((?P<id>.*?)\)")
    elif mode == "pandoc":
        label_pattern = re.compile(r"(?P<title>.*?)\s+\{\s?\#(?P<id>.*?)\s?\}")
    for line in content.split("\n"):
        if line.startswith("# "):
            title = line.split("# ", 1)[1]
            attr_list = label_pattern.search(title)
            if attr_list:
                attr_list = attr_list.groupdict()
                tag = attr_list["id"]
                title = attr_list["title"]
            else:
                tag = slugify(title, allow_unicode=True)
            chapters[tag] = ""
        chapters[tag] += "\n" + line
    return chapters


def process_labels(chapters, float_ch_prefixes=True):
    labels = {}
    locations = {}
    counters = {str(i): 0 for i in range(1, SECDEPTH)}
    counters["table"] = 0
    counters["figure"] = 0
    heading_pattern = re.compile(r"#+ (?P<title>.*?) \[label\]\((?P<id>.*?)\)")
    tpattern = re.compile(r"\[table\]\((?P<id>.*?)\)")
    fpattern = re.compile(r"\[figure\]\((?P<id>.*?)\)")
    for chid, chapter in chapters.items():
        if float_ch_prefixes:
            counters["table"] = 0
            counters["figure"] = 0
        for line in chapter.split("\n"):
            if line.startswith("#"):
                heading = heading_pattern.search(line)
                if heading:
                    heading = heading.groupdict()
                else:
                    heading = {"id": slugify(line), "title": line.split("# ")[1]}
                heading["lvl"] = str(line.count("#"))
                counters[heading["lvl"]] += 1
                for cc in range(int(heading["lvl"]) + 1, SECDEPTH):
                    counters[str(cc)] = 0
                labels[heading["id"]] = print_counter(counters)
                locations[heading["id"]] = chid
        for tcaption in tpattern.finditer(chapter):
            tcaption = tcaption.groupdict()
            counters["table"] += 1
            if float_ch_prefixes:
                tstring = f"Table {counters['1']}.{counters['table']}"
            else:
                tstring = f"Table {counters['table']}"
            labels["tab:" + tcaption["id"]] = tstring
            locations["tab:" + tcaption["id"]] = chid
        for fcaption in fpattern.finditer(chapter):
            fcaption = fcaption.groupdict()
            counters["figure"] += 1
            if float_ch_prefixes:
                fstring = f"Figure {counters['1']}.{counters['figure']}"
            else:
                fstring = f"Figure {counters['figure']}"
            labels["fig:" + fcaption["id"]] = fstring
            locations["fig:" + fcaption["id"]] = chid
    return labels, locations


def check_abbrevs(dataset, source_dir, content):
    with open(DATA_DIR / "leipzig.yaml", encoding="utf-8") as f:
        leipzig = yaml.load(f, Loader=yaml.SafeLoader)
    gloss_cands = []
    if "ExampleTable" in dataset:
        for ex in dataset.iter_rows("ExampleTable"):
            for word in ex["Gloss"]:
                if not word:
                    continue
                gloss_cands.extend(get_glosses(word, gloss_cands))
    for text_gloss in re.findall(r"\[gl\]\((.*?)\)", content):
        gloss_cands.append(text_gloss)
    abbrev_dict = {}

    for table in dataset.tables:  # add abbreviations found in the CLDF dataset
        if str(table.url) == "abbreviations.csv":
            for rec in table:
                abbrev_dict[rec["ID"].lower()] = rec["Description"]

    abbrev_path = source_dir / EXTRA_DIR / "abbreviations.csv"
    if abbrev_path.is_file():  # add abbreviations added locally
        for rec in pd.read_csv(abbrev_path).to_dict("records"):
            abbrev_dict[rec["ID"]] = rec["Description"]
    gloss_cands = list(dict.fromkeys(gloss_cands))
    for x in map(str.lower, gloss_cands):
        if x not in abbrev_dict:
            abbrev_dict[x] = leipzig.get(x, "unknown abbreviation")
    unaccounted = [
        x for x in gloss_cands if abbrev_dict[x.lower()] == "unknown abbreviation"
    ]
    if len(unaccounted) > 0:
        log.warning(
            "Glosses identified as abbreviations but not specified in glossing abbreviation table:"
        )
        print("\n".join(unaccounted))
    return abbrev_dict


def _src(string, mode="cldfviz"):
    bibkey, pages = split_ref(string)
    if mode == "cldfviz":
        if pages:
            page_str = f": {pages}"
        else:
            page_str = ""
        return f"[{bibkey}](sources.bib?with_internal_ref_link&ref#cldf:{bibkey}){page_str}"  # noqa: E501
    if mode == "biblatex":
        if pages:
            page_str = f"[{pages}]"
        else:
            page_str = ""
        return f"{page_str}{{{bibkey}}}"
    log.error("mode=(cldfviz,biblatex)")
    sys.exit()


def src(cite_input, mode="cldfviz", parens=False, full=False):
    if cite_input in ["", []]:
        log.warning("Empty citation")
        return ""
    if isinstance(cite_input, list):
        citations = [_src(x, mode=mode) for x in cite_input]
    else:
        citations = []
        for x in re.finditer(r"[A-Za-z0-9]+(\[[^\]]*])?", cite_input):
            citations.append(_src(x.group(0), mode=mode))
    if mode == "biblatex":
        if full:
            return "\\fullcite" + "".join(citations)
        if parens:
            return "\\parencites" + "".join(citations)
        return "\\textcites" + "".join(citations)
    if parens and citations:
        return "(" + ", ".join(citations) + ")"
    return ", ".join(citations)


def load_figure_metadata(source_dir):
    fig_md = Path(source_dir) / FIGURE_DIR / "metadata.yaml"
    if fig_md.is_file():
        with open(fig_md, encoding="utf-8") as f:
            figures = yaml.load(f, Loader=yaml.SafeLoader)
    else:
        log.warning(f"Inexistent figure metadata file: {fig_md}")
        figures = {}
    return figures


def load_table_metadata(source_dir):
    table_md = Path(source_dir) / TABLE_DIR / "metadata.yaml"
    if table_md.is_file():
        with open(table_md, encoding="utf-8") as f:
            tables = yaml.load(f, Loader=yaml.SafeLoader)
    else:
        log.warning(f"Inexistent table metadata file: {table_md}")
        tables = {}
    return tables


def expand_pages(pages):
    out_pages = []
    for pranges in pages:
        for page in pranges.split(","):
            page = page.strip()
            page = page.replace("–", "-")
            if "-" in page:
                ps = page.split("-")
                if ps[0].isdigit() and ps[1].isdigit():
                    out_pages.extend(list(range(int(ps[0]), int(ps[1]))))
                else:
                    out_pages.append(page)
            else:
                out_pages.append(page)
    out_pages = [
        int(x) if (isinstance(x, int) or x.isdigit()) else x for x in out_pages
    ]
    numeric = [x for x in out_pages if isinstance(x, int)]
    non_numeric = [x for x in out_pages if not isinstance(x, int)]
    return sorted(set(numeric)), list(set(non_numeric))


def combine_pages(pages):
    numeric, non_numeric = expand_pages(pages)
    out_pages = []
    for page in numeric:
        if not out_pages:
            out_pages.append([page, page])
        else:
            if out_pages[-1][-1] == page - 1:
                out_pages[-1][-1] = page
            else:
                out_pages.append([page, page])
    return ", ".join(
        non_numeric
        + [f"{x[0]}-{x[1]}" if x[0] != x[1] else str(x[0]) for x in out_pages]
    )


def combine_sources(source_list, sep="; "):
    bibdict = {}
    for source_entry in source_list:
        for source in source_entry.split(sep):
            bibkey, pages = split_ref(source)
            if bibkey in bibdict:
                if pages:
                    if not bibdict[bibkey]:
                        raise ValueError(f"Citing {bibkey} with and without pages")
                    bibdict[bibkey].extend(pages.split(","))
                elif bibdict[bibkey]:
                    raise ValueError(f"Citing {bibkey} with and without pages")
            else:
                if pages:
                    bibdict[bibkey] = [pages]
                else:
                    bibdict[bibkey] = []
    out = []
    for bibkey, pages in bibdict.items():
        if not pages:
            out.append(bibkey)
            continue
        out_string = bibkey
        if bibkey != "pc":
            page_string = combine_pages(pages)
        else:
            page_string = ", ".join(list(set(pages)))
        if pages:
            out_string += f"[{page_string}]"
        out.append(out_string)
    return out


def html_gloss(s):
    return f"<span class='gloss'>{s}<span class='tooltiptext gloss-{s}'></span></span>"


def html_example_wrap(tag, content, kind="example"):
    if kind == "multipart":
        return f"""<ol markdown="block" class="example">
<li class="example" markdown="block" id="{tag}">
<ol markdown="block" class="subexample">
{content}
</ol>
</li>
</ol>"""
    if kind == "subexample":
        return f"""<li class="subexample" markdown="block" id="{tag}">
<div markdown="block">{content}</div>
</li>"""
    return f"""<ol markdown="block" class="example">
<li class="example" markdown="block" id="{tag}"><div markdown="block">{content}</div>
</li>
</ol>"""


def _get_relative_file(folder, file):
    folder = Path(folder)
    file = Path(file)
    if file.name == str(file):
        return folder / file
    return file


def sanitize_latex(unsafe_str):
    for o, r in (
        ("\\\\", "\\textbackslash{}\\"),
        ("\\ ", "\\textbackslash{} "),
        ("_", "\\_"),
        ("%", "\\%"),
        ("#", "\\#"),
        ("&", "\\&"),
        ("~", "\\textasciitilde{}"),
    ):
        unsafe_str = unsafe_str.replace(o, r)
    return unsafe_str


def split_ref(s):
    if "[" in s:
        bibkey, pages = s.split("[")
        pages = pages.rstrip("]")
    else:
        bibkey, pages = s, None
    return bibkey, pages


def compile_crossrefs(contents):
    title_dic = {}
    tag_dic = {}
    for label, cdata in contents.items():
        ctag = re.findall(r"^# (.*?) \[label\]\((.*?)\)", cdata["content"])
        if not ctag:
            ctag = label
            ctitle = cdata.get("title")
        else:
            ctitle, ctag = ctag[0]
        title_dic[ctag] = ctitle
        tag_dic[ctag] = ctag
        for lvl, title, tag in get_sections(cdata["content"], mode="pld"):
            title_dic[tag] = title
            tag_dic[tag] = ctag
        for table_tag in re.findall(
            r"\[table\]\((.*?)\)",
            cdata["content"],
        ):
            tag_dic["tab:" + table_tag] = ctag
        for fig_tag in re.findall(
            r"\[figure\]\((.*?)\)",
            cdata["content"],
        ):
            tag_dic[fig_tag] = ctag
    return tag_dic, title_dic


def get_topics(path, title_dic, tag_dic):
    topics = []
    topic_index = pd.read_csv(path)
    for topic in topic_index.to_dict("records"):
        topic["ID"] = slugify(topic["Name"])
        topic["References"] = [
            {
                "Chapter": tag_dic[section],
                "ID": section,
                "Label": title_dic[section],
            }
            for section in topic["Sections"].split(",")
        ]
        topic["Tags"] = topic["Tags"].split(",")
        topics.append(topic)
    return topics


def table_metadata(table_name):
    path = DATA_DIR / "cldf" / f"{table_name}-metadata.json"
    if not path.is_file():
        path = (
            Path(pycldf.__file__).resolve().parent
            / "components"
            / f"{table_name}-metadata.json"
        )
    return jsonlib.load(path)


def load_cldf_dataset(cldf_path, source_dir=None):
    try:
        ds = Dataset.from_metadata(cldf_path)
        temp_path = Path(tempfile.gettempdir()) / "cldf"
        ds.copy(dest=temp_path)
        orig_id = ds.metadata_dict.get("rdf:ID", None)
        ds = Dataset.from_metadata(temp_path / ds.filename)
        ds.add_provenance(wasDerivedFrom=orig_id)
        if not source_dir:
            return ds
        source_dir = Path(source_dir)
        config.load_from_dir(source_dir)
        if Path(config["paths"]["add_bib"]).is_file():
            bib = pybtex.database.parse_file(
                config["paths"]["add_bib"], bib_format="bibtex"
            )
            sources = [Source.from_entry(k, e) for k, e in bib.entries.items()]
            ds.add_sources(*sources)

        table_dic = {}
        topic_path = source_dir / EXTRA_DIR / "topics.csv"
        if topic_path.is_file():
            content = load_content(
                source_dir=source_dir / CONTENT_FOLDER,
                structure_file=source_dir / CONTENT_FOLDER / STRUCTURE_FILE,
            )
            # content = "\n".join([x["content"] for x in content.values()])
            tag_dic, title_dic = compile_crossrefs(content)
            TopicTable = table_metadata("TopicTable")
            ds.add_component(TopicTable)
            table_dic[TopicTable["url"]] = get_topics(topic_path, title_dic, tag_dic)
            ds.write(**table_dic)
        return ds
        extra_cldf_p = source_dir / EXTRA_DIR / "cldf"
        if extra_cldf_p.is_dir():
            for file in extra_cldf_p.iterdir():
                print(file)
    except FileNotFoundError as e:
        raise e
        log.error(e)
        log.error(
            f"Could not load CLDF dataset from {Path(cldf_path).resolve()}. Please specify a path to a valid CLDF metadata file."  # noqa: E501
        )
        sys.exit(1)


def get_structure(structure_file, prefix_mode=None):
    counters = {1: 0, 2: 0, 3: 0, 4: 0}
    print(structure_file)
    files = load(structure_file)
    if not files:
        log.error(
            f"Please create a {STRUCTURE_FILE} file in your {CONTENT_FOLDER} folder."
        )
        sys.exit()
    contents = {}
    prefix_choices = ["alpha", "numerical"]
    for file, values in files.items():
        contents[file] = values
        if prefix_mode not in prefix_choices:
            prefix = ""
        else:
            level = values.get("level", 1)
            i = 4
            while i > level:
                counters[i] = 0
                i -= 1
            counters[level] += 1
            numbering = ".".join([str(x) for x in counters.values() if x > 0])
            if prefix_mode == "numerical":
                prefix = "".join([str(x) for x in counters.values()]) + " "
            else:
                prefix = (
                    "".join([chr(x + 64) for x in counters.values() if x > 0]) + " "
                )
            contents[file]["numbering"] = numbering
        contents[file]["filename"] = prefix + file + ".md"
    return contents


def load_content(source_dir=CONTENT_FOLDER, structure_file="docs/structure.yaml"):
    contents = get_structure(
        prefix_mode="", structure_file=structure_file
    )  # todo config
    for data in contents.values():
        with open(Path(source_dir) / data["filename"], "r", encoding="utf-8") as f:
            data["content"] = f.read()
    return contents


def write_content_file(
    file_id,
    content,
    prefix_mode="",
    source_dir="",
    structure_file="",
):  # todo config
    contents = get_structure(prefix_mode=prefix_mode, structure_file=structure_file)
    if file_id not in contents:
        log.error(
            f"File with handle {file_id} not found, please check your {CONTENT_FOLDER}/{STRUCTURE_FILE} file and your content files"
        )
        raise ValueError
    w_path = Path(source_dir) / contents[file_id]["filename"]
    with open(w_path, "w", encoding="utf-8") as f:
        f.write(content)
        log.info(f"Wrote to file {w_path}")


def read_config_file(kind):
    if kind == "settings":
        return load("config.yaml")
    if kind == "metadata":
        return load("metadata.yaml")
    if kind == "structure":
        return load(CONTENT_FOLDER / STRUCTURE_FILE)
    if kind == "figures":
        return load(FIGURE_DIR / "metadata.yaml")
    if kind == "tables":
        return load(TABLE_DIR / "metadata.yaml")
    log.error(f"Invalid config file name: {kind}")
    raise ValueError


class Enumerator:
    def __init__(self):
        self.counters = {1: 0, 2: 0, 3: 0, 4: 0}

    def string(self):
        res = []
        for value in self.counters.values():
            if value != 0:
                res.append(str(value))
        return ".".join(res) + "."

    def parse(self, line):
        lvl = len(line) - len(line.lstrip("#"))
        self.counters[lvl] += 1
        for k in self.counters:
            if k > lvl:
                self.counters[k] = 0
        return self.string()


def write_config_file(kind, content):
    if kind == "settings":
        dump(content, "config.yaml")
    elif kind == "metadata":
        dump(content, "metadata.yaml")
    elif kind == "structure":
        dump(content, CONTENT_FOLDER / STRUCTURE_FILE)
    elif kind == "figures":
        dump(content, FIGURE_DIR / "metadata.yaml")
    elif kind == "tables":
        dump(content, TABLE_DIR / "metadata.yaml")
    else:
        log.error(f"Invalid config file name: {kind}")
        raise ValueError


def comma_and_list(entries, sep1=", ", sep2=" and ", oxford=True):
    output = entries[0]
    for entry in entries[1:-1]:
        output += sep1 + entry
    if oxford and len(entries) > 2:
        output += sep1.strip()
    output += sep2 + entries[-1]
    return output


def new():
    """Create a new lingdocs project"""
    conf_path = Path.home() / ".config/pld" / "author_config.yaml"
    if conf_path.is_file():
        with open(conf_path, "r", encoding="utf-8") as f:
            extra = yaml.load(f, Loader=yaml.SafeLoader)
    else:
        extra = {}
    cookiecutter(
        str(DATA_DIR / "project_template"),
        extra_context=extra,
        overwrite_if_exists=True,
    )


def get_md_pattern(m):
    return m.end(), m.group("label"), m.group("url")


latex_repl = {"%": "\\%"}


def latexify_table(cell):
    cell = str(cell)
    for a, b in latex_repl.items():
        cell = cell.replace(a, b)
    if "_" in cell or "*" in cell:
        return panflute.convert_text(
            cell, output_format="latex", input_format="markdown"
        )
    return cell


def write_readme(metadata_file, release=False):
    log.warning("readmes are not implemented")
    # bib = ""# todo: _load_bib(metadata_file)
    # citation = bib.to_string("bibtex")
    # md = load(metadata_file)
    # author_string = []
    # for author in md["authors"]:
    #     paren_string = []
    #     if "orcid" in author:
    #         orcid = author["orcid"].replace(ORCID_STR, "")
    #         paren_string.append(f"[{orcid}]({author['orcid']})")
    #     if "affiliation" in author:
    #         paren_string.append(f"{author['affiliation']}")
    #     if len(paren_string) > 0:
    #         paren_string = f"({', '.join(paren_string)})"
    #     author_string.append(
    #         f'{author["given-names"]} {author["family-names"]} {paren_string}'
    #     )
    # if len(author_string) > 1:
    #     author_string = "\n".join([f"  * {s}" for s in author_string])
    #     author_string = f"authors:\n{author_string}"
    # else:
    #     author_string = f"author: {author_string[0]}"
    # if not release:
    #     readme_text = "## Do not cite from this branch!"
    #     if "url" in md:
    #         readme_text += (
    #             f"\nUse [the most recent citeable version]({md['url']}) instead."
    #         )
    # else:
    #     readme_text = f"""# {md["title"]}


#
# * {author_string}
#
# * version: `{md["version"]}`
#
# Created using [lingdocs](https://github.com/fmatter/lingdocs/) v{__version__}.
# The available output formats are in [output](./output); if you are viewing this readme
# in a browser, you probably want the [github formatted output](./output/github).
#
# To cite the latest version:
#
# ```
# {citation}```"""
# with open("README.md", "w", encoding="utf-8") as f:
# f.write(readme_text)


# These symbols could potentially be used to split up morphemes.
# Some of them are standard, some not.
glossing_delimiters = [
    "-",
    "–",
    ".",
    "=",
    ";",
    ":",
    "*",
    "~",
    "<",
    ">",
    r"\[",
    r"\]",
    "(",
    ")",
    "/",
    r"\\",
]


def is_gloss_abbr_candidate(part, parts, j):
    return (
        part == part.upper()  # needs to be uppercase
        and part not in glossing_delimiters + ["[", "]", "\\"]  # and not a delimiter
        and part != "I"  # english lol
        and part
        not in [
            "?",
            "???",
        ]  # question marks may be used for unknown or ambiguous analyses
        and not (
            len(parts) > j + 2
            and parts[j + 2] in glossing_delimiters
            and parts[j + 1] not in [">", "-"]
        )
    )


def split_word(word):
    """Splits a word up into morphemes and glossing_delimiters"""
    parts = re.split(r"([" + "|".join(glossing_delimiters) + "])", word)
    parts = [x for x in parts if x != ""]
    return parts


def resolve_glossing_combination(input_string):
    output = []
    temp_text = ""
    for i, char in enumerate(list(input_string)):
        if re.match(r"[1-3]+", char):
            if i < len(input_string) - 1 and input_string[i + 1] == "+":
                temp_text += char
            elif input_string[i - 1] == "+":
                temp_text += char
                output.append(temp_text)
                temp_text = ""
            else:
                if temp_text != "":
                    output.append(temp_text)
                output.append(char)
                temp_text = ""
        else:
            temp_text += char
    if temp_text != "":
        output.append(temp_text)
    return output


def decorate_gloss_string(input_string, decoration=lambda x: f"\\gl{{{x}}}"):
    if not input_string:
        return ""
    gloss_list = input_string.split(" ")
    for i, gloss in enumerate(gloss_list):  # pylint: disable=too-many-nested-blocks
        res = []
        for word in gloss.split("_"):
            output = " "
            # take proper nouns into account
            if len(word) == 2 and word[0] == word[0].upper() and word[1] == ".":
                output += word
            else:
                parts = split_word(word)
                for j, part in enumerate(parts):
                    if is_gloss_abbr_candidate(part, parts, j):
                        # take care of numbered genders
                        if part[0] == "G" and re.match(r"\d", part[1:]):
                            output += decoration(part.lower())
                            # if the number should not be part of the abbreviation:
                            # output += (
                            #     decoration(part[0].lower()) + part[1:]
                            # )
                        else:
                            for glosspart in resolve_glossing_combination(part):
                                output += decoration(glosspart.lower())
                    else:
                        output += part
            res.append(output[1:])
        gloss_list[i] = "_".join(res)
    gloss_text_upcased = " ".join(gloss_list)
    return gloss_text_upcased


def refresh_clld_db(clld_folder):
    df = pd.read_csv(clld_folder / "chapters.csv", keep_default_na=False)
    chapters = []
    for chapter in df.to_dict("records"):
        with open(clld_folder / chapter["Filename"], "r", encoding="utf-8") as f:
            content = f.read()
        chapters.append(
            {
                "ID": chapter["ID"],
                "Name": chapter["title"],
                "Number": chapter["Number"],
                "Description": content,
            }
        )
    spec = importlib.util.find_spec("clld_document_plugin")
    if spec:
        from clld_document_plugin.util import refresh_documents  # noqa: E402

        refresh_documents(config["clld"]["db_uri"], chapters)
    else:
        log.error("clld-document-plugin not found")


bool_dic = {"true": True, "True": True, 1: True}


def _resolve_jinja(var, default, name):
    if isinstance(var, Undefined) or var is None:
        return default
    if not isinstance(var, bool):
        if var in bool_dic:
            return bool_dic[var]
        log.warning(f"Invalid value for [{name}]: {var} ({type(var)}).")
    else:
        return var
    return default


def _build_example(
    obj,
    gls,
    ftr,
    txt=None,
    lng=None,
    src=None,
    obj2=None,
    ex_id="example",
    title=None,
    show_language=None,
    ftr_explanation=None,
    additional_translations=None,
    comment=None,
    source_position=None,
    show_primary=True,
    quotes=("‘", "’"),
    parentheses=("(", ")"),
    translation_sep=" / ",
    audio=None,
):
    ex_dic = {"obj": obj, "gls": gls, "id": ex_id}
    preamble = []
    postamble = []

    show_primary = _resolve_jinja(
        show_primary, config["examples"]["show_primary"], "show_primary"
    )
    source_position = source_position or config["examples"]["source_position"]
    show_language = _resolve_jinja(
        show_language, config["examples"]["show_language"], "show_language"
    )

    if not title and lng and show_language:
        title = lng
    elif not title:
        title = ""
    if comment:
        postamble.append(comment)
    if source_position == "in_preamble":
        preamble.append(src)
    elif source_position == "after_translation":
        postamble.append(src)
    else:
        raise ValueError(source_position)
    if txt and show_primary:
        ex_dic["srf"] = txt
    else:
        ex_dic["srf"] = None
    if ftr_explanation:
        ftr += f" ({ftr_explanation})"
    if obj2 and set(obj2) != set(["&nbsp;"]):
        ex_dic["obj2"] = obj2
    trans_string = [f"{quotes[0]}{ftr}{quotes[1]}"]
    if additional_translations:
        trans_string.extend(
            [quotes[0] + add + quotes[1] for add in additional_translations]
        )
    ex_dic["ftr"] = translation_sep.join(trans_string)
    ex_dic["title"] = title
    ex_dic["posttitle"] = " ".join(preamble)
    if preamble:
        ex_dic["posttitle"] = parentheses[0] + ex_dic["posttitle"] + parentheses[1]
    ex_dic["postamble"] = " ".join(postamble)
    if postamble:
        ex_dic["postamble"] = parentheses[0] + ex_dic["postamble"] + parentheses[1]
    if audio:
        ex_dic["audio"] = audio
    return ex_dic


def build_example(data):
    obj = data.pop("obj")
    gls = data.pop("gls")
    ftr = data.pop("ftr")
    return _build_example(obj, gls, ftr, **data)


def resolve_jinja(var, default):
    if isinstance(var, Undefined):
        return default
    return var


def pad_ex(*lines, sep=" "):
    out = {}
    for glossbundle in zip(*lines):
        longest = len(max(glossbundle, key=len))
        for i, obj in enumerate(glossbundle):
            diff = longest - len(obj)
            out.setdefault(i, [])
            out[i].append(obj + " " * diff)
    for k in out.copy():
        out[k] = sep.join(out[k])
    return tuple(out.values())


def build_examples(datas):
    if len(datas) == 0:
        return [], ""
    ex_dicts = []
    single_language = True
    first_language = datas[0].get("lng", None)
    full_preamble = ""
    for data in datas[1::]:
        if data.get("lng", None) != first_language:
            single_language = False
    if single_language and resolve_jinja(
        datas[0]["show_language"], config["examples"]["show_language"]
    ):
        full_preamble += first_language
    for data in datas:
        if single_language:
            data["show_language"] = False
        ex_dicts.append(build_example(data))
    return ex_dicts, full_preamble


def resolve_lfts(with_language, with_source, with_translation):
    if isinstance(with_language, Undefined):
        with_language = config["lfts"]["show_language"]
    if isinstance(with_source, Undefined):
        with_source = config["lfts"]["show_source"]
    if isinstance(with_translation, Undefined):
        with_translation = config["lfts"]["show_translation"]
    return with_language, with_source, with_translation


def debug(item, msg=""):
    log.debug(f"jinja: {item} {msg}")


def get_rich_label(item, preferred="Name"):
    non_obj_labels = ["Name", "Title", "ID"]
    for cand in [preferred, "Form", "Primary_Text", "Title", "ID"]:
        if item.get(cand, None):
            if cand not in non_obj_labels:
                return f"<i>{item[cand]}</i>"
            if cand == "Title":
                return f"“{item[cand]}”"
            return item[cand]
    return "(n/a)"


def link(item, anchor=None, mode="html", preferred="Name", label=None):
    anchor_text = ""
    if anchor is not None:
        anchor_text = "#" + anchor
    if label is None:
        label = get_rich_label(item, preferred=preferred)
    if item is not None:
        if mode == "html":
            return f"""<a href="site:data/{item.table.label}/{item['ID']}/{anchor_text}">{label}</a>"""
        raise ValueError(mode)
    return ""


def lfts_link(
    rich,
    with_language=config["lfts"]["show_language"],
    with_source=config["lfts"]["show_source"],
    with_translation=config["lfts"]["show_translation"],
    source=None,
    translation=None,
    italicize=True,
):
    out = []
    if with_language:
        out.append(link(rich.language))
    label = get_rich_label(rich)
    if italicize:
        label = "*" + label + "*"
    out.append(link(rich, label=label))
    if with_translation:
        trans = translation or rich["Parameter_ID"]
        if isinstance(trans, list):
            out.append(f"‘{', '.join(trans)}‘")
        else:
            out.append(f"‘{trans}‘")
    if with_source and (source or rich.get("Source")):
        out.append(src(source or rich["Source"][0], parens=True))
    return " ".join(out)


def table_label(string, source="filename", target="multi"):
    if source == "filename" or "csv" in string:
        string = string.replace(".csv", "").rstrip("s")
    if source == "name" or "Table" in string:
        string = string.replace("Table", "").lower()
    if source != "single":
        name = string.rstrip("s")
    else:
        name = string
    if "parts" in name:
        plural = "{name}"
    else:
        plural = "{name}s"
    patterns = {
        "single": "{name}",
        "multi": plural,
        "name": "{name}",
        "filename": f"{plural}.csv",
    }
    return patterns[target].format(name=name)


# def table_label(string):
#     if string.endswith(".csv"):
#         return string.replace(".csv", "")
#     if string.endswith("Table"):
#         return string.replace("Table", "s").lower()
#     raise ValueError(f"Cannot parse component name {string}")


func_dict = {
    "comma_and_list": comma_and_list,
    "sanitize_latex": sanitize_latex,
    "split_ref": split_ref,
    "decorate_gloss_string": decorate_gloss_string,
    "build_example": build_example,
    "build_examples": build_examples,
    "src": src,
    "flexible_pad_ex": pad_ex,
    "resolve_lfts": resolve_lfts,
    "debug": debug,
    "get_rich_label": get_rich_label,
    "lfts_link": lfts_link,
    "table_label": table_label,
}
