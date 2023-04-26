"""Various helpers"""
import importlib.util
import json
import logging
import re
import sys
from pathlib import Path
import pandas as pd
import panflute
import pybtex
import yaml
from cookiecutter.main import cookiecutter
from pycldf import Dataset
from pycldf import Source
from slugify import slugify
from pylingdocs import __version__
from pylingdocs.config import ABBREV_FILE
from pylingdocs.config import ADD_BIB
from pylingdocs.config import CLDF_MD
from pylingdocs.config import CLLD_URI
from pylingdocs.config import CONF_PATH
from pylingdocs.config import CONTENT_FILE_PREFIX
from pylingdocs.config import CONTENT_FOLDER
from pylingdocs.config import DATA_DIR
from pylingdocs.config import METADATA_FILE, EX_SHOW_LG, EX_SHOW_PRIMARY, EX_SRC_POS
from pylingdocs.config import FIGURE_DIR
from pylingdocs.config import FIGURE_MD
from pylingdocs.config import METADATA_FILE
from pylingdocs.config import STRUCTURE_FILE
from pylingdocs.config import TABLE_DIR
from pylingdocs.config import TABLE_MD
from pylingdocs.metadata import ORCID_STR
from pylingdocs.metadata import _load_bib
from pylingdocs.metadata import _load_metadata
from jinja2.runtime import Undefined
import tempfile

log = logging.getLogger(__name__)


def read_file(path, mode=None, encoding="utf-8"):
    with open(path, "r", encoding=encoding) as f:
        if mode == "yaml" or path.suffix == ".yaml":
            return yaml.load(f, Loader=yaml.SafeLoader)
        if mode == "json" or path.suffix == ".json":
            return json.load(f)
        return f.read()


def write_file(content, path, mode=None, encoding="utf-8"):
    with open(path, "w", encoding=encoding) as f:
        if mode == "yaml" or path.suffix == ".yaml":
            yaml.dump(f, content)
        elif mode == "json" or path.suffix == ".json":
            json.dump(content, f, ensure_ascii=False, indent=4)
        else:
            f.write(content)


def get_sections(content):
    for line in content.split("\n"):
        if line.startswith("#"):
            title = line.split(" ", 1)[1]
            level = line.count("#")
            tag = re.findall("{#(.*?)}", title)
            if len(tag) == 0:
                tag = slugify(title, allow_unicode=True)
            else:
                tag = tag[0]
                title = title.replace(tag, "")
            yield level, title, tag


def get_glosses(word, gloss_cands):
    parts = split_word(word)
    for j, part in enumerate(parts):
        if is_gloss_abbr_candidate(part, parts, j):
            # take care of numbered genders
            if not (part[0] == "G" and re.match(r"\d", part[1:])):
                for gloss in resolve_glossing_combination(part):
                    if gloss not in gloss_cands:
                        yield gloss


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
    if (Path(source_dir) / ABBREV_FILE).is_file():  # add abbreviations added locally
        for rec in pd.read_csv(Path(source_dir) / ABBREV_FILE).to_dict("records"):
            abbrev_dict[rec["ID"]] = rec["Description"]
    for table in dataset.tables:  # add abbreviations found in the CLDF dataset
        if str(table.url) == "abbreviations.csv":
            for rec in table:
                abbrev_dict[rec["ID"].lower()] = rec["Description"]
            dataset.write(
                **{
                    "abbreviations.csv": [
                        {"ID": k, "Description": v} for k, v in abbrev_dict.items()
                    ]
                }
            )
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


def _src(string, mode="cldfviz", full=False):
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
    if cite_input == "":
        log.warning("Empty citation")
        return ""
    if isinstance(cite_input, list):
        citations = [_src(x, mode=mode) for x in cite_input]
    else:
        citations = []
        for x in re.finditer(r"[A-Za-z0-9]+(\[[^\]]*])?", cite_input):
            citations.append(_src(x.group(0), mode=mode, full=full))
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
    fig_md = _get_relative_file(source_dir / FIGURE_DIR, FIGURE_MD)
    if fig_md.is_file():
        with open(fig_md, encoding="utf-8") as f:
            figures = yaml.load(f, Loader=yaml.SafeLoader)
    else:
        log.warning(f"Specified figures metadata file {FIGURE_MD} not found.")
        figures = []
    return figures


def load_table_metadata(source_dir):
    table_md = _get_relative_file(source_dir / TABLE_DIR, TABLE_MD)
    if table_md.is_file():
        with open(table_md, encoding="utf-8") as f:
            tables = yaml.load(f, Loader=yaml.SafeLoader)
    else:
        log.warning(f"Specified table metadatafile {TABLE_MD} not found.")
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
                if not pages or None in bibdict[bibkey]:
                    raise ValueError(f"Citing {bibkey} with and without pages")
                bibdict[bibkey].extend(pages.split(","))
            else:
                bibdict[bibkey] = [pages]
    out = []
    for bibkey, pages in bibdict.items():
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


def get_prefixed_filename(structure, file_id):
    return structure


def split_ref(s):
    if "[" in s:
        bibkey, pages = s.split("[")
        pages = pages.rstrip("]")
    else:
        bibkey, pages = s, None
    return bibkey, pages


def _load_cldf_dataset(cldf_path=CLDF_MD):
    try:
        ds = Dataset.from_metadata(cldf_path)
        temp_path = Path(tempfile.gettempdir()) / "cldf"
        ds.copy(dest=temp_path)
        orig_id = ds.metadata_dict.get("rdf:ID", None)
        ds = Dataset.from_metadata(temp_path / ds.filename)
        ds.add_provenance(wasDerivedFrom=orig_id)
        if Path(ADD_BIB).is_file():
            bib = pybtex.database.parse_file(ADD_BIB, bib_format="bibtex")
            sources = [Source.from_entry(k, e) for k, e in bib.entries.items()]
            ds.add_sources(*sources)
        return ds
    except FileNotFoundError as e:
        log.error(e)
        log.error(
            f"Could not load CLDF dataset from {Path(cldf_path).resolve()}. Please specify a path to a valid CLDF metadata file."  # noqa: E501
        )
        sys.exit(1)


def _load_structure(structure_file=STRUCTURE_FILE):
    structure_file = Path(structure_file)
    if not structure_file.is_file():
        log.error(f"Structure file {structure_file.resolve()} not found, aborting.")
        sys.exit(1)
    else:
        return yaml.load(open(structure_file, encoding="utf-8"), Loader=yaml.SafeLoader)


def get_structure(prefix_mode=None, structure_file=STRUCTURE_FILE):
    counters = {1: 0, 2: 0, 3: 0, 4: 0}
    files = _load_structure(structure_file)
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


def load_content(source_dir=CONTENT_FOLDER, structure_file=STRUCTURE_FILE):
    contents = get_structure(
        prefix_mode=CONTENT_FILE_PREFIX, structure_file=structure_file
    )
    for data in contents.values():
        with open(Path(source_dir) / data["filename"], "r", encoding="utf-8") as f:
            data["content"] = f.read()
    return contents


def write_content_file(
    file_id,
    content,
    prefix_mode=CONTENT_FILE_PREFIX,
    source_dir=CONTENT_FOLDER,
    structure_file=STRUCTURE_FILE,
):
    contents = get_structure(prefix_mode=prefix_mode, structure_file=structure_file)
    if file_id not in contents:
        log.error(
            f"File with handle {file_id} not found, please check your structure.yaml file and your content files"
        )
        raise ValueError
    w_path = Path(source_dir) / contents[file_id]["filename"]
    with open(w_path, "w", encoding="utf-8") as f:
        f.write(content)
        log.info(f"Wrote to file {w_path}")


def read_config_file(kind):
    def getfile(path, mode="yaml"):
        if Path(path).is_file():
            if mode == "yaml":
                return yaml.load(
                    open(path, "r", encoding="utf-8"), Loader=yaml.SafeLoader
                )
            if mode == "plain":
                return open(path, "r", encoding="utf-8").read()
            raise ValueError(f"Unknown mode for reading config files: '{mode}'")
        log.warning(f"File {path} does not exist.")
        return []

    if kind == "settings":
        return getfile(CONF_PATH, mode="plain")
    if kind == "metadata":
        return getfile(METADATA_FILE)
    if kind == "structure":
        return getfile(CONTENT_FOLDER / STRUCTURE_FILE)
    if kind == "figures":
        return getfile(FIGURE_DIR / FIGURE_MD)
    if kind == "tables":
        return getfile(TABLE_DIR / TABLE_MD)
    log.error(f"Invalid config file name: {kind}")
    raise ValueError


def write_config_file(kind, content):
    def writefile(file, content):
        with open(file, "w", encoding="utf-8") as f:
            f.write(content)

    if kind == "settings":
        writefile(CONF_PATH, content)
    elif kind == "metadata":
        writefile(METADATA_FILE, content)
    elif kind == "structure":
        writefile(CONTENT_FOLDER / STRUCTURE_FILE, content)
    elif kind == "figures":
        writefile(FIGURE_DIR / FIGURE_MD, content)
    elif kind == "tables":
        writefile(TABLE_DIR / TABLE_MD, content)
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
    """Create a new pylingdocs project"""
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


def latexify_table(cell):
    cell = str(cell)
    if "_" in cell or "*" in cell:
        return panflute.convert_text(
            cell, output_format="latex", input_format="markdown"
        )
    return cell


def write_readme(metadata_file=METADATA_FILE, release=False):
    bib = _load_bib(metadata_file)
    citation = bib.to_string("bibtex")
    md = _load_metadata(metadata_file)
    author_string = []
    for author in md["authors"]:
        paren_string = []
        if "orcid" in author:
            orcid = author["orcid"].replace(ORCID_STR, "")
            paren_string.append(f"[{orcid}]({author['orcid']})")
        if "affiliation" in author:
            paren_string.append(f"{author['affiliation']}")
        if len(paren_string) > 0:
            paren_string = f"({', '.join(paren_string)})"
        author_string.append(
            f'{author["given-names"]} {author["family-names"]} {paren_string}'
        )
    if len(author_string) > 1:
        author_string = "\n".join([f"  * {s}" for s in author_string])
        author_string = f"authors:\n{author_string}"
    else:
        author_string = f"author: {author_string[0]}"
    if not release:
        readme_text = "## Do not cite from this branch!"
        if "url" in md:
            readme_text += (
                f"\nUse [the most recent citeable version]({md['url']}) instead."
            )
    else:
        readme_text = f"""# {md["title"]}

* {author_string}

* version: `{md["version"]}`

Created using [pylingdocs](https://github.com/fmatter/pylingdocs/) v{__version__}.
The available output formats are in [output](./output); if you are viewing this readme
in a browser, you probably want the [github formatted output](./output/github).

To cite the latest version:

```
{citation}```"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_text)


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


# Splits a word up into morphemes and glossing_delimiters
def split_word(word):
    parts = re.split(r"([" + "|".join(glossing_delimiters) + "])", word)
    parts = [x for x in parts if x != ""]
    return parts
    # old code
    # output = []
    # char_list = list(word)
    # for char in char_list:
    #     if len(output) == 0 or (
    #         char in glossing_delimiters or output[-1] in glossing_delimiters
    #     ):
    #         output.append(char)
    #     else:
    #         output[-1] += char
    # return output


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
    words_list = input_string.split(" ")
    for i, word in enumerate(words_list):  # pylint: disable=too-many-nested-blocks
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
                        output += decoration(part.lower())#decoration(part[0].lower()) + part[1:] # if the number should not be part of the abbreviation
                    else:
                        for gloss in resolve_glossing_combination(part):
                            output += decoration(gloss.lower())
                else:
                    output += part
        words_list[i] = output[1:]
    gloss_text_upcased = " ".join(words_list)
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

        refresh_documents(CLLD_URI, chapters)
    else:
        log.error("clld-document-plugin not found")


bool_dic = {"true": True, "True": True, 1: True}


def _resolve_jinja(var, default, name):
    if isinstance(var, Undefined) or var is None:
        return default
    elif not isinstance(var, bool):
        if var in bool_dic:
            return bool_dic[var]
        else:
            log.warning(f"Invalid value for [{name}]: {var} ({type(var)}).")
            return default


def _build_example(
    obj,
    gls,
    ftr,
    txt=None,
    lng=None,
    src=None,
    ex_id="example",
    title=None,
    show_language=EX_SHOW_LG,
    ftr_explanation=None,
    additional_translations=None,
    comment=None,
    source_position=EX_SRC_POS,
    show_primary=True,
    quotes=("‘", "’"),
    parentheses=("(", ")"),
    translation_sep=" / ",
):
    ex_dic = {"obj": obj, "gls": gls, "id": ex_id}
    preamble = []
    postamble = []

    show_primary = _resolve_jinja(show_primary, EX_SHOW_PRIMARY, "show_primary")
    source_position = source_position or EX_SRC_POS
    show_language = _resolve_jinja(show_language, EX_SHOW_LG, "show_language")

    if title:
        title = title
    elif lng and show_language:
        title = lng
    else:
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
    return ex_dic


def build_example(data):
    obj = data.pop("obj")
    gls = data.pop("gls")
    ftr = data.pop("ftr")
    return _build_example(obj, gls, ftr, **data)


def build_examples(datas):
    ex_dicts = []
    single_language = True
    first_language = datas[0].get("lng", None)
    full_preamble = ""
    for data in datas[1::]:
        if data.get("lng", None) != first_language:
            single_language = False
    if single_language:
        full_preamble += first_language
    for data in datas:
        if single_language:
            data["show_language"] = False
        ex_dicts.append(build_example(data))
    return ex_dicts, full_preamble
