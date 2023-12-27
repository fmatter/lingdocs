import importlib
import logging
import re
from pathlib import Path

import pandas as pd
import pycldf
from clldutils import jsonlib
from pycldf.dataset import SchemaError
from slugify import slugify
from writio import load

from lingdocs.config import DATA_DIR, EXTRA_DIR, config
from lingdocs.formats import CLLD
from lingdocs.helpers import (
    check_abbrevs,
    get_sections,
    get_topics,
    load_figure_metadata,
    read_file,
    table_metadata,
)
from lingdocs.models import models
from lingdocs.postprocessing import postprocess
from lingdocs.preprocessing import preprocess, render_markdown

log = logging.getLogger(__name__)

TOPIC_PATH = Path(EXTRA_DIR) / "topic_index.csv"


ContributorTable = table_metadata("ContributorTable")
ChapterTable = table_metadata("ChapterTable")
TopicTable = table_metadata("TopicTable")
AbbreviationTable = table_metadata("AbbreviationTable")
tables = [ContributorTable, ChapterTable, AbbreviationTable, TopicTable]

Reference_Column = {
    "name": "References",
    "required": False,
    "dc:description": "Locations in the grammar relevant for the entity",
    "datatype": "json",
}


def get_contributors(metadata_dict):
    contributor_list = []
    for order, contributor in enumerate(metadata_dict["authors"]):
        name = contributor["given-names"] + " " + contributor["family-names"]
        c_id = contributor.get("id", slugify(name))
        c_dict = {"ID": c_id, "Name": name, "Order": order}
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


def create_cldf(
    chapter_dic, ds, source_dir, output_dir, metadata_file, add_documents=None, **kwargs
):
    content = "\n\n".join([x["content"] for x in chapter_dic.values()])
    check_abbrevs(ds, source_dir, content)
    metadata_dict = load(metadata_file)
    clld = CLLD()
    clld.figure_metadata = load_figure_metadata(source_dir)
    preprocessed = preprocess(content, source_dir)
    preprocessed = clld.preprocess_commands(preprocessed, **kwargs)
    preprocessed = render_markdown(
        preprocessed,
        ds,
        decorate_gloss_string=CLLD.decorate_gloss_string,
        builder=clld,
    )
    preprocessed = "\n" + postprocess(preprocessed, clld, source_dir)
    tent = preprocessed.replace(
        "![](", "![](/static/images/"
    )  # rudely assume that all images live in the static dir
    delim = "\n# "
    chapters = []
    if config["output"]["layout"] in ["slides", "article"]:
        # these use # as section markers, so we add a level for the html output
        tent = tent.replace("\n#", "\n##")
        chapters.append(
            {
                "ID": "landingpage",
                "Description": tent,
                "Name": " ",
            }
        )
    else:
        parts = tent.split(delim)[1::]
        title_dic = {}
        tag_dic = {}
        chapter_dic = {}
        for part in parts:
            chtitle, content = part.split("\n", 1)
            chtag = re.findall("{#(.*?)}", chtitle)
            if len(chtag) == 0:
                chtag = slugify(chtitle)
            else:
                chtag = chtag[0]
            chtitle = chtitle.split("{#")[0].strip()
            title_dic[chtag] = chtitle
            tag_dic[chtag] = chtag

            for lvl, title, tag in get_sections(part):
                del lvl
                title_dic[tag] = title.split("{#")[0].strip()
                tag_dic[tag] = chtag

            for table_tag in re.findall(
                "<div class='caption table' id='(.*?)'>",
                content,
            ):
                tag_dic[table_tag] = chtag
            for fig_tag in re.findall(
                '<figcaption id="(.*?)"',
                content,
            ):
                tag_dic[fig_tag] = chtag

            chapter_dic[chtag] = content

        for i, (tag, content) in enumerate(chapter_dic.items()):
            refs = re.findall(r"<a href='#(.*?)' .*?</a>", content)
            for ref in refs:
                if ref not in tag_dic:
                    log.error(f"Tag {ref} not found.")
                elif tag_dic[ref] != tag:
                    label = title_dic.get(ref, "")
                    content = re.sub(
                        rf"<a href='#{ref}'.*?</a>",
                        f"[crossref](chapters.csv?_anchor={ref}&label={label}#cldf:{tag_dic[ref]})",
                        content,
                    )
            chapters.append(
                {
                    "ID": slugify(tag),
                    "Description": content,
                    "Name": title_dic[tag],
                    "Number": i + 1,
                }
            )
        landingpage_path = source_dir / EXTRA_DIR / f"landingpage_cldf.md"
        if landingpage_path.is_file():
            lp_tent = load(landingpage_path)
            lp_tent = preprocess(lp_tent, source_dir)
            lp_tent = clld.preprocess_commands(lp_tent, **kwargs)
            lp_tent = render_markdown(
                lp_tent,
                ds,
                decorate_gloss_string=CLLD.decorate_gloss_string,
                builder=clld,
            )
            lp_tent = "\n" + postprocess(lp_tent, clld, source_dir)
            lp_tent = lp_tent.replace(
                "![](", "![](/static/images/"
            )  # rudely assume that all images live in the static dir
            chapters.append(
                {
                    "ID": "landingpage",
                    "Description": lp_tent,
                    "Name": "Landing page",
                }
            )

    ds.write()  # todo: is this necessary?
    ds.copy(dest=output_dir / "cldf")
    ds = pycldf.Dataset.from_metadata(output_dir / "cldf" / ds.filename)

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

    ds.properties["dc:abstract"] = metadata_dict["abstract"]
    ds.properties["dc:license"] = metadata_dict["license"]
    ds.properties["dc:description"] = metadata_dict["abstract"]
    ds.properties["rdf:ID"] = metadata_dict["id"]

    ds.add_provenance(
        wasGeneratedBy=[
            {
                "dc:title": "lingdocs",
                "dc:description": importlib.metadata.version("lingdocs"),
                "dc:url": "https://pypi.org/project/lingdocs",
            }
        ]
    )

    if add_documents:
        for d in add_documents:
            d["Description"] = postprocess(
                render_markdown(
                    CLLD.preprocess_commands(
                        preprocess(d["Description"], source_dir), **kwargs
                    ),
                    ds,
                    builder=clld,
                    decorate_gloss_string=CLLD.decorate_gloss_string,
                    output_format="clld",
                ),
                CLLD,
                source_dir,
            )
            chapters.append(d)

    if (source_dir / "entity_refs.yaml").is_file():
        add_dic = read_file(source_dir / "entity_refs.yaml")
        for table, repl in add_dic.items():
            records = []
            ds.add_columns(table, Reference_Column)
            for row in ds.iter_rows(table):
                if row["ID"] in repl:
                    row["References"] = [
                        {
                            "Chapter": tag_dic[sec],
                            "ID": sec,
                            "Label": title_dic[sec],
                        }
                        for sec in repl[row["ID"]].split(",")
                    ]
                records.append(row)
            ds.write(**{table: records})

    table_dic = {
        ChapterTable["url"]: chapters,
    }

    ds.add_component(ChapterTable)
    if TOPIC_PATH.is_file():
        ds.add_component(TopicTable)
        table_dic[TopicTable["url"]] = get_topics(title_dic, tag_dic)
    if ContributorTable["url"] in list(ds.components.keys()) + [
        str(x.url) for x in ds.tables
    ]:  # a list of tables in the dataset
        ds.remove_table(ContributorTable["url"])
    table_dic[ContributorTable["url"]] = get_contributors(metadata_dict)
    ds.add_component(ContributorTable)

    ds.write(**table_dic)

    log.info(
        f"Wrote CLDF dataset with ChapterTable to {(ds.directory / ds.filename).resolve()}"
    )

    ds.validate(log=log)


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
