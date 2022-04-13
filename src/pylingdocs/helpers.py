"""Various helpers"""
import logging
import yaml
from pylingdocs.config import METADATA_FILE, CITATION_FILE
from datetime import datetime
from jsonschema import validate as json_validate
from jsonschema.exceptions import ValidationError
from pathlib import Path
from cffconvert.root import get_package_root
import json
import sys

log = logging.getLogger(__name__)


def new():
    """Create a new pylingdocs project"""
    # TODO implement
    log.info("Hello world!")


def _load_metadata(metadata_file=METADATA_FILE):
    with open(metadata_file, encoding="utf-8") as f:
        md = yaml.load(f, Loader=yaml.SafeLoader)
    md["message"] = "Created with [pylingdocs](https://github.com/fmatter/pylingdocs/)"
    md["date-released"] = datetime.now().strftime("%Y-%m-%d")
    md["type"] = "dataset"
    md["cff-version"] = "1.2.0"
    md.pop("id", None)
    if "authors" in md:
        for author in md["authors"]:
            if "orcid" in author and "http" not in author["orcid"]:
                author["orcid"] = "https://orcid.org/" + author["orcid"]
    if "url" not in md and "repository" in md:
        md["url"] = md["repository"]
    return md


def _validate(metadata, metadata_file, citation_file):
    schema = Path(get_package_root(), "schemas", "1.2.0", "schema.json")
    with open(schema, "rt", encoding="utf-8") as f:
        schema = json.loads(f.read())
    try:
        json_validate(instance=metadata, schema=schema)
    except ValidationError as e:
        log.error(
            f"""The following error was found when converting {metadata_file} to {citation_file}:
{e.message}"""
        )
        sys.exit(1)


def render_cff(citation_file=CITATION_FILE, metadata_file=METADATA_FILE):
    metadata = _load_metadata(metadata_file)
    _validate(metadata, metadata_file, citation_file)
    with open(CITATION_FILE, "w", encoding="utf-8") as f:
        yaml.dump(metadata, f, sort_keys=False)


def render_readme():
    md = _load_metadata()
    readme_text = f"""# {md["title"]}
version: {md["version"]}
created: {md["date-released"]}"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_text)
