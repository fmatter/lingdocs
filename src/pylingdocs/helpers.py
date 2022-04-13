"""Various helpers"""
import logging
from pylingdocs import __version__
from pylingdocs.config import CITATION_FILE
from pylingdocs.config import METADATA_FILE
from pylingdocs.metadata import ORCID_STR
from pylingdocs.metadata import _load_metadata
from pylingdocs.metadata import _sort_metadata


log = logging.getLogger(__name__)


def split_ref(s):
    if "[" in s:
        bibkey, pages = s.split("[")
        pages = pages.rstrip("]")
    else:
        bibkey, pages = s, None
    return bibkey, pages


def new():
    """Create a new pylingdocs project"""
    # TODO implement
    log.info("Hello world!")


def write_cff(citation_file=CITATION_FILE, metadata_file=METADATA_FILE):
    cff_output, bib = _load_metadata(citation_file, metadata_file)
    del bib  # unused
    with open(CITATION_FILE, "w", encoding="utf-8") as f:
        f.write(cff_output)


def write_readme(metadata_file=METADATA_FILE):
    md, bib = _sort_metadata(metadata_file)
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
    readme_text = f"""# {md["title"]}

* {author_string}

* version: `{md["version"]}`

Created using [pylingdocs](https://github.com/fmatter/pylingdocs/) v{__version__}.
The available output formats are in [output](./output).
The [github](./output/github) format is most suitable for github(-like) repos.


To refer to the content of unreleased versions:

```
{citation}```"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_text)
