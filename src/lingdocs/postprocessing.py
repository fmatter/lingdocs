import logging
import re
from io import StringIO

import pandas as pd
from writio import load

from lingdocs.helpers import load_table_metadata

log = logging.getLogger(__name__)


TABLE_PATTERN = re.compile(
    r"PYLINGDOCS_RAW_TABLE_START(?P<label>[\s\S].*)CONTENT_START(?P<content>[\s\S]*?)PYLINGDOCS_RAW_TABLE_END"  # noqa: E501
)

MANEX_PATTERN = re.compile(
    r"PYLINGDOCS_MANEX_START(?P<label>[\s\S].*)CONTENT_START(?P<content>[\s\S]*?)PYLINGDOCS_MANEX_END"  # noqa: E501
)

MANPEX_PATTERN = re.compile(
    r"PYLINGDOCS_MANPEX_START(?P<label>[\s\S].*)CONTENT_START(?P<content>[\s\S]*?)PYLINGDOCS_MANPEX_END"  # noqa: E501
)

MANPEX_ITEM_PATTERN = re.compile(
    r"PYLINGDOCS_MANPEXITEM_START(?P<label>[\s\S].*)CONTENT_START(?P<content>[\s\S]*?)PYLINGDOCS_MANPEXITEM_END"  # noqa: E501
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
    for m in TABLE_PATTERN.finditer(md):
        yield md[current : m.start()]
        current = m.end()
        label = m.group("label")
        content = m.group("content")
        df = pd.read_csv(StringIO(content), keep_default_na=False)
        df.columns = [col if "Unnamed: " not in col else "" for col in df.columns]
        if label not in tables:
            log.warning(f"Could not find metadata for table {label}.")
            yield builder.table(df=df, caption=None, label=None)
        else:
            yield builder.table(
                df=df, caption=tables[label].get("caption", None), label=label
            )
    yield md[current:]


def postprocess(md_str, builder, source_dir="."):
    tables = load_table_metadata(source_dir)
    md_str = "".join(insert_manex(md_str, builder, MANPEX_PATTERN, kind="multipart"))
    md_str = "".join(
        insert_manex(md_str, builder, MANPEX_ITEM_PATTERN, kind="subexample")
    )
    md_str = "".join(insert_manex(md_str, builder, MANEX_PATTERN))
    md_str = "".join(insert_tables(md_str, builder, tables))
    return builder.postprocess(md_str, load(source_dir / "metadata.yaml"))
