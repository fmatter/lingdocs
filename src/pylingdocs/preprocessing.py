import logging
import re
import pandas as pd
from cldfviz.text import render
from clldutils import jsonlib
from jinja2 import DictLoader
from pylingdocs.config import TABLE_DIR
from pylingdocs.config import TABLE_MD
from pylingdocs.models import models
from pylingdocs.helpers import get_md_pattern
from io import StringIO

log = logging.getLogger(__name__)

MD_LINK_PATTERN = re.compile(r"\[(?P<label>[^]]*)]\((?P<url>[^)]+)\)")

TABLE_PATTERN = re.compile(
    r"PYLINGDOCS_RAW_TABLE_START(?P<label>[\s\S].*)CONTENT_START(?P<content>[\s\S]*)PYLINGDOCS_RAW_TABLE_END"
)

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

for output_format, env_dict in templates.items():
    for model in models:
        model_output = model.representation(output_format)
        if model_output is not None:
            env_dict[model.cldf_table + "_detail.md"] = model_output

for output_format, env_dict in templates.items():
    envs[output_format] = DictLoader(env_dict)


def preprocess_cldfviz(md):
    current = 0
    for m in MD_LINK_PATTERN.finditer(md):
        yield md[current : m.start()]
        current, key, url = get_md_pattern(m)
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


def load_tables(md):
    current = 0
    for m in MD_LINK_PATTERN.finditer(md):
        yield md[current : m.start()]
        current, key, url = get_md_pattern(m)
        if key == "table":
            with open(TABLE_DIR / f"{url}.csv", "r", encoding="utf-8") as f:
                yield "PYLINGDOCS_RAW_TABLE_START" + url + "CONTENT_START" + f.read() + "PYLINGDOCS_RAW_TABLE_END"
        else:
            yield md[m.start() : m.end()]
    yield md[current:]


def insert_tables(md, builder):
    current = 0
    for m in TABLE_PATTERN.finditer(md):
        yield md[current : m.start()]
        current = m.end()
        label = m.group("label")
        content = m.group("content")
        df = pd.read_csv(StringIO(content), keep_default_na=False)
        yield builder.table(df=df, caption=tables[label]["caption"], label=label)
    yield md[current:]


def preprocess(md_str):
    return "".join(load_tables(md_str))


def postprocess(md_str, builder):
    return "".join(insert_tables(md_str, builder))
