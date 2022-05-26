"""Various helpers"""
import logging
import re
import sys
from pathlib import Path
import panflute
import yaml
from cookiecutter.main import cookiecutter
from pycldf import Dataset
from pylingdocs import __version__
from pylingdocs.config import CLDF_MD
from pylingdocs.config import DATA_DIR
from pylingdocs.config import METADATA_FILE
from pylingdocs.config import STRUCTURE_FILE
from pylingdocs.metadata import ORCID_STR
from pylingdocs.metadata import _load_bib
from pylingdocs.metadata import _load_metadata


log = logging.getLogger(__name__)


def html_gloss(s):
    return (
        f'<span class="gloss">{s} <span class="tooltiptext gloss-{s}" ></span></span>'
    )


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


def _load_cldf_dataset(cldf_path=CLDF_MD):
    try:
        return Dataset.from_metadata(cldf_path)
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


def comma_and_list(entries, sep1=", ", sep2=", and "):
    output = entries[0]
    for entry in entries[1:-1]:
        output += sep1 + entry
    output += sep2 + entries[-1]
    return output


def new():
    """Create a new pylingdocs project"""
    cookiecutter(str(DATA_DIR / "project_template"), overwrite_if_exists=True)


def get_md_pattern(m):
    return m.end(), m.group("label"), m.group("url")


def latexify_table(cell):
    if "_" in cell or "*" in cell:
        return panflute.convert_text(
            cell, output_format="latex", input_format="markdown"
        )
    return cell


def write_readme(metadata_file=METADATA_FILE, release=False):
    bib = _load_bib(metadata_file)
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
    citation = bib.to_string("bibtex")
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
        and part != "?"  # question marks may be used for unknown or ambiguous analyses
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
                        output += f"\\gl{{{part.lower()}}}"
                    else:
                        for gloss in resolve_glossing_combination(part):
                            output += decoration(gloss.lower())
                else:
                    output += part
        words_list[i] = output[1:]
    gloss_text_upcased = " ".join(words_list)
    return gloss_text_upcased
