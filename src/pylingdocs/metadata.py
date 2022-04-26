"""Various helpers"""
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
import yaml
from cffconvert.root import get_package_root
from jsonschema import validate as json_validate
from jsonschema.exceptions import ValidationError
from pybtex.database import BibliographyData
from pybtex.database import Entry
from slugify import slugify
from pylingdocs.config import CITATION_FILE
from pylingdocs.config import DATA_DIR
from pylingdocs.config import METADATA_FILE


ORCID_STR = "https://orcid.org/"
log = logging.getLogger(__name__)


def _read_metadata_file(metadata_file=METADATA_FILE):
    metadata_file = Path(metadata_file)
    if metadata_file.is_file():
        with open(metadata_file, encoding="utf-8") as f:
            md = yaml.load(f, Loader=yaml.SafeLoader)
        return md
    else:
        log.warning(f"Metadata file {metadata_file.resolve()} not found, please create one.")


if METADATA_FILE.is_file():
    PROJECT_TITLE = _read_metadata_file()["title"]
    PROJECT_SLUG = _read_metadata_file()["id"]
else:
    PROJECT_TITLE = "<TITLE PLACEHOLDER>"
    PROJECT_SLUG = "pylingdocs_app"

bibtex_repl = {"location": "address"}
bibtex_rev = {y: x for x, y in bibtex_repl.items()}
cff_fields = ["title", "url"]
remove_fields = []


def _extract_bib(md):
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
    author_string = []
    for author in md["authors"]:
        author_string.append(f'{author["family-names"]}, {author["given-names"]}')
    year = datetime.now().strftime("%Y")
    bibkey = slugify(md["authors"][0]["family-names"]) + year + slugify(md.pop("id"))
    title_string = md["title"]
    if "version" in md:
        title_string += f' (version {md["version"]})'
    bibtex_fields = {
        "author": " and ".join(author_string),
        "year": year,
        "title": title_string,
    }
    skip_fields = ["title"]
    for field, value in md.items():
        if field in good_fields and field not in skip_fields:
            if field not in cff_fields:
                remove_fields.append(field)
            else:
                bibtex_fields[field] = value
    for field in remove_fields:
        bibtex_fields[field] = md.pop(field)
    bib_data = BibliographyData(
        {bibkey: Entry(entry_type, list(bibtex_fields.items()))}
    )
    return md, bib_data


def _sort_metadata(metadata_file=METADATA_FILE):
    md = _read_metadata_file(metadata_file)
    if "url" not in md and "repository" in md:
        md["url"] = md["repository"]
    md, bib = _extract_bib(md)
    md["message"] = "Created with [pylingdocs](https://github.com/fmatter/pylingdocs/)"
    md["date-released"] = datetime.now().strftime("%Y-%m-%d")
    for del_field in []:
        md.pop(del_field, None)
    md["type"] = "dataset"
    md["cff-version"] = "1.2.0"
    if "authors" in md:
        for author in md["authors"]:
            if "orcid" in author and "http" not in author["orcid"]:
                author["orcid"] = ORCID_STR + author["orcid"]
    return md, bib


def _validate(metadata, metadata_file, citation_file):
    schema = Path(get_package_root(), "schemas", "1.2.0", "schema.json")
    with open(schema, "r", encoding="utf-8") as f:
        schema = json.loads(f.read())
    try:
        json_validate(instance=metadata, schema=schema)
    except ValidationError as e:
        log.error(
            f"""The following error was found when converting {metadata_file} to {citation_file}:
{e.message}"""
        )
        sys.exit(1)


def _load_metadata(citation_file=CITATION_FILE, metadata_file=METADATA_FILE):
    metadata, bib = _sort_metadata(metadata_file)
    _validate(metadata, metadata_file, citation_file)
    return yaml.dump(metadata, sort_keys=False), bib
