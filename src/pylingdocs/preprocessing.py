import logging
import re
import pandas as pd
from cldfviz.text import render
from clldutils import jsonlib
from pylingdocs.config import DATA_DIR
from pylingdocs.config import TABLE_DIR
from pylingdocs.config import TABLE_MD


log = logging.getLogger(__name__)

MD_LINK_PATTERN = re.compile(r"\[(?P<label>[^]]*)]\((?P<url>[^)]+)\)")

if TABLE_MD.is_file():
    tables = jsonlib.load(TABLE_MD)
else:
    tables = {}


def preprocess_cldfviz(md):
    current = 0
    for m in MD_LINK_PATTERN.finditer(md):
        yield md[current : m.start()]
        current = m.end()
        key = m.group("label")
        url = m.group("url")
        md_keys = {
            "mp": f"[Morpheme {url}](MorphsetTable#cldf:{url})",
            "ex": f"[Example {url}](ExampleTable#cldf:{url})",
            "m": f"[Morph {url}](MorphTable#cldf:{url})",
        }
        if key in md_keys:
            yield md_keys[key]
        else:
            yield md[m.start() : m.end()]
    yield md[current:]


def render_cldf(md_str, ds, data_format="cldf", output_format="github"):
    if data_format == "cldf":
        preprocessed = render(
            "".join(preprocess_cldfviz(md_str)),
            ds,
            template_dir=DATA_DIR / "model_templates" / output_format,
            fallback_template_dir=DATA_DIR / "model_templates" / "plain",
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
