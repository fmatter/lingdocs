import logging
from pathlib import Path
import pandas as pd
import pycldf
from clldutils import jsonlib
from pycldf import Source
from pycldf.dataset import SchemaError
from slugify import slugify
from pylingdocs import __version__
from pylingdocs.config import DATA_DIR
from pylingdocs.metadata import _load_bib
from pylingdocs.metadata import _load_metadata
from pylingdocs.models import models


log = logging.getLogger(__name__)


def metadata(table_name):
    path = DATA_DIR / "cldf" / f"{table_name}-metadata.json"
    if not path.is_file():
        path = (
            Path(pycldf.__file__).resolve().parent
            / "components"
            / f"{table_name}-metadata.json"
        )
    return jsonlib.load(path)


def get_contributors(metadata_dict):
    contributor_list = []
    for contributor in metadata_dict["authors"]:
        name = contributor["given-names"] + " " + contributor["family-names"]
        c_id = contributor.get("id", slugify(name))
        c_dict = {"ID": c_id, "Name": name}
        for k, v in contributor.items():
            c_dict[k.capitalize()] = v
        contributor_list.append(c_dict)
    return contributor_list


def get_chapters(output_dir):
    clld_path = output_dir / "clld"
    chapters = pd.read_csv(clld_path / "chapters.csv")
    chapter_list = []
    for chapter in chapters.to_dict("records"):
        with open(clld_path / chapter["Filename"], "r", encoding="utf-8") as f:
            chapter_content = f.read()
            chapter_list.append(
                {
                    "ID": chapter["ID"],
                    "Name": chapter["title"],
                    "Number": chapter["Number"],
                    "Description": chapter_content,
                }
            )
    return chapter_list


def create_cldf(ds, output_dir, metadata_file):
    ds.copy(dest=output_dir / "cldf")
    orig_id = ds.metadata_dict.get("rdf:ID", None)
    ds = pycldf.Dataset.from_metadata(output_dir / "cldf/metadata.json")
    ds.add_provenance(wasDerivedFrom=orig_id)

    bib_data = _load_bib(metadata_file)
    for key, entry in bib_data.entries.items():
        ds.properties["dc:bibliographicCitation"] = Source.from_entry(key, entry)

    metadata_dict = _load_metadata(metadata_file)
    ds.properties[
        "dc:title"
    ] = f"""{metadata_dict["title"]} (v{metadata_dict["version"]})"""
    if "domain" in metadata_dict:
        domain = metadata_dict["domain"]
        if "http" not in domain:
            domain = "https://" + domain
        ds.properties["dc:identifier"] = domain
    elif "id" in metadata_dict:
        ds.properties["dc:identifier"] = metadata_dict["id"]

    ds.properties["dc:license"] = metadata_dict["license"]
    ds.properties["dc:description"] = metadata_dict["abstract"]
    ds.properties["rdf:ID"] = metadata_dict["id"]

    ds.add_provenance(
        wasGeneratedBy=[
            {
                "dc:title": "pylingdocs",
                "dc:description": __version__,
                "dc:url": "https://pypi.org/project/pylingdocs",
            }
        ]
    )

    ds.add_component(metadata("ChapterTable"))
    if "ContributorTable" in list(ds.components.keys()) + [
        str(x.url) for x in ds.tables
    ]:  # a list of tables in the dataset
        ds.remove_table("ContributorTable")
    ds.add_component(metadata("ContributorTable"))

    ds.write(
        ChapterTable=get_chapters(output_dir),
        ContributorTable=get_contributors(metadata_dict),
    )
    log.info(
        f"Wrote CLDF dataset with ChapterTable to {(ds.directory / ds.filename).resolve()}"
    )


def generate_autocomplete(ds, output_dir):
    output_dir = Path(output_dir)
    autocomplete_data = []
    menu_data = {}
    for model in models:
        menu_data[model.name] = []
        try:
            for row in ds.iter_rows(model.cldf_table):
                menu_data[model.name].append(
                    {"id": row["ID"], "content": model.autocomplete_string(row)}
                )
                autocomplete_data.append(model.autocomplete_string(row))
        except SchemaError:
            del menu_data[model.name]
    menu_data["Source"] = []
    for src in ds.sources:
        menu_data["Source"].append(
            {"id": src.id, "content": [str(src), f"[src]({src.id})"]}
        )
        autocomplete_data.append([f"src:{src.id} {str(src)}", f"[src]({src.id})"])
        autocomplete_data.append([f"psrc:{src.id} {str(src)}", f"[psrc]({src.id})"])
    jsonlib.dump(autocomplete_data, output_dir / ".pld_autocomplete.json", indent=4)
    jsonlib.dump(menu_data, output_dir / ".pld_menudata.json", indent=4)
