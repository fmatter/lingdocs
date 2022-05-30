"""Various helpers"""
import json
import logging
from datetime import datetime
from pathlib import Path
import yaml
from pybtex.database import BibliographyData
from pybtex.database import Entry
from slugify import slugify
from pylingdocs.config import DATA_DIR
from pylingdocs.config import METADATA_FILE


ORCID_STR = "https://orcid.org/"
log = logging.getLogger(__name__)


def _read_metadata_file(metadata_file=METADATA_FILE, source_dir="."):
    metadata_file = source_dir / Path(metadata_file)
    if metadata_file.is_file():
        with open(metadata_file, encoding="utf-8") as f:
            return yaml.load(f, Loader=yaml.SafeLoader)
    else:
        log.warning(
            f"Metadata file {metadata_file.resolve()} not found, please create one."
        )
        return {}


bibtex_repl = {"location": "address"}
bibtex_rev = {y: x for x, y in bibtex_repl.items()}
remove_fields = []


def _license_url(s):
    license_dic = {"CC-BY-SA-4.0": "http://creativecommons.org/licenses/by/4.0/"}
    return license_dic.get(s, "")


def _load_bib(metadata_file=METADATA_FILE):
    md = _read_metadata_file(metadata_file)
    entry_type = md.get("type", "article")
    with open(DATA_DIR / "bibtex_schemes.json", "r", encoding="utf-8") as f:
        bibschemes = json.loads(f.read())
    if entry_type not in bibschemes:
        log.error(
            f"Don't know how to handle type '{entry_type}', defaulting to 'article'"
        )
        entry_type = "article"
    good_fields = (
        bibschemes[entry_type]["required"] + bibschemes[entry_type]["optional"]
    )
    good_fields = [bibtex_rev.get(x, x) for x in good_fields] + ["url"]
    year = datetime.now().strftime("%Y")
    date = datetime.now().strftime("%Y-%m-%d")
    author_string = []
    if "authors" in md:
        for author in md["authors"]:
            author_string.append(f'{author["family-names"]}, {author["given-names"]}')
        bibkey = (
            slugify(md["authors"][0]["family-names"])
            + year
            + slugify(md.pop("id", "new-pylingdocs-project"))
        )
    else:
        author_string.append("Anonymous")
        bibkey = "anonymous" + year + slugify(md.pop("id", "new-pylingdocs-project"))
        md["authors"] = [{"family-names": "Anonymous", "given-names": "A."}]

    md["title"] = md.get("title", "Put your title here.")
    if "version" in md:
        md["title"] += f' (version {md["version"]})'
    else:
        md["version"] = "0.0.0"
    if "repository" in md:
        if "version" in md:
            md["url"] = md["repository"] + f"/tree/{md['version']}"
        elif "url" not in md:
            md["url"] = md["repository"]
    bibtex_fields = {
        "author": " and ".join(author_string),
        "year": year,
        "urldate": date,
    }
    for field, value in md.items():
        if field in good_fields:
            bibtex_fields[field] = value
    for field in remove_fields:
        bibtex_fields[field] = md.pop(field)
    bib_data = BibliographyData(
        {bibkey: Entry(entry_type, list(bibtex_fields.items()))}
    )
    return bib_data


def _load_metadata(metadata_file=METADATA_FILE):
    md = _read_metadata_file(metadata_file)
    if "repository" in md:
        if "version" in md:
            md["url"] = md["repository"] + f"/tree/{md['version']}"
        elif "url" not in md:
            md["url"] = md["repository"]
    if "authors" in md:
        for author in md["authors"]:
            if "orcid" in author and "http" not in author["orcid"]:
                author["orcid"] = ORCID_STR + author["orcid"]
    if "license" in md:
        md["license"] = _license_url(md["license"])
    return md
