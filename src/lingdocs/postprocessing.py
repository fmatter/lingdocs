import logging
import re
from io import StringIO

import pandas as pd
from writio import load

from lingdocs.io import load_table_metadata
from lingdocs.preprocessing import process_metadata

log = logging.getLogger(__name__)


TABLE_PATTERN = re.compile(
    r"LINGDOCS_RAW_TABLE_START(?P<label>[\s\S].*)CONTENT_START(?P<content>[\s\S]*?)LINGDOCS_RAW_TABLE_END"  # noqa: E501
)

MANEX_PATTERN = re.compile(
    r"LINGDOCS_MANEX_START(?P<label>[\s\S].*)CONTENT_START(?P<content>[\s\S]*?)LINGDOCS_MANEX_END"  # noqa: E501
)

MANPEX_PATTERN = re.compile(
    r"LINGDOCS_MANPEX_START(?P<label>[\s\S].*)CONTENT_START(?P<content>[\s\S]*?)LINGDOCS_MANPEX_END"  # noqa: E501
)

MANPEX_ITEM_PATTERN = re.compile(
    r"LINGDOCS_MANPEXITEM_START(?P<label>[\s\S].*)CONTENT_START(?P<content>[\s\S]*?)LINGDOCS_MANPEXITEM_END"  # noqa: E501
)


def insert_manex(md, builder, pattern, kind="plain"):
    current = 0
    for m in pattern.finditer(md):
        yield md[current : m.start()]
        current = m.end()
        label = m.group("label")
        content = m.group("content")
        yield builder.manex(label, content=content, kind=kind)
    yield md[current:]


def insert_tables(md, builder, tables):
    current = 0
    subtables = []
    for tbl, tbl_data in tables.items():
        for x in tbl_data.get("subtables", []):
            subtables.append(x)
    for m in TABLE_PATTERN.finditer(md):
        yield md[current : m.start()]
        current = m.end()
        label = m.group("label")
        content = m.group("content")
        if content:
            df = pd.read_csv(StringIO(content), keep_default_na=False)
            df.columns = [col if "Unnamed: " not in col else "" for col in df.columns]
        else:
            df = None
        if label not in tables:
            log.warning(f"Could not find metadata for table {label}.")
            yield builder.table(
                df=df,
                caption=None,
                label=None,
                tnotes=None,
                subtable=label in subtables,
            )
        else:
            yield builder.table(
                df=df,
                caption=tables[label].get("caption"),
                label=label,
                tnotes=tables[label].get("tnotes"),
                subtable=label in subtables,
            )
    yield md[current:]


def postprocess(md_str, dataset, builder, source_dir="."):
    tables = process_metadata(load_table_metadata(source_dir), dataset, builder)
    md_str = "".join(insert_manex(md_str, builder, MANPEX_PATTERN, kind="multipart"))
    md_str = "".join(
        insert_manex(md_str, builder, MANPEX_ITEM_PATTERN, kind="subexample")
    )
    md_str = "".join(insert_manex(md_str, builder, MANEX_PATTERN))
    md_str = "".join(insert_tables(md_str, builder, tables))
    return builder.postprocess(md_str, load(source_dir / "metadata.yaml"))
