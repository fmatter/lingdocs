import logging
import re
import pandas as pd
from cldfviz.text import render
from clldutils import jsonlib
from jinja2 import Environment, DictLoader
from pylingdocs.config import TABLE_DIR
from pylingdocs.config import TABLE_MD
from pylingdocs.models import models

log = logging.getLogger(__name__)

MD_LINK_PATTERN = re.compile(r"\[(?P<label>[^]]*)]\((?P<url>[^)]+)\)")

if TABLE_MD.is_file():
    tables = jsonlib.load(TABLE_MD)
else:
    tables = {}

labels = {}
templates = {}
envs = {}

for model in models:
    labels[model.shortcut] = model.query_string
    for output_format in model.formats:
        if output_format not in templates:
            templates[output_format] = {}

for output_format in templates.keys():
    for model in models:
        templates[output_format][
            model.cldf_table + "_detail.md"
        ] = model.representation(output_format)

for output_format in templates.keys():
    envs[output_format] = DictLoader(templates[output_format])


def preprocess_cldfviz(md):
    current = 0
    for m in MD_LINK_PATTERN.finditer(md):
        yield md[current : m.start()]
        current = m.end()
        key = m.group("label")
        url = m.group("url")
        if key in labels:
            yield labels[key](url)
        else:
            yield md[m.start() : m.end()]
    yield md[current:]


def render_markdown(md_str, ds, data_format="cldf", output_format="github"):
    if data_format == "cldf":
        preprocessed = render(
            "".join(preprocess_cldfviz(md_str)), ds, loader=envs[output_format]
        )
        return preprocessed
    log.error(f"Unknown data format {data_format}")
    return ""


def insert_tables(md, builder):
    current = 0
    for m in MD_LINK_PATTERN.finditer(md):
        yield md[current : m.start()]
        current = m.end()
        key = m.group("label")
        url = m.group("url")
        if key == "table":
            table = pd.read_csv(TABLE_DIR / f"{url}.csv", keep_default_na=False)
            yield builder.table(df=table, caption=tables[url]["caption"], label=url)
        else:
            yield md[m.start() : m.end()]
    yield md[current:]


def preprocess(md_str, builder):
    return "".join(insert_tables(md_str, builder))
