import logging
import os
import re
import sys
from io import StringIO
from pathlib import Path
import pandas as pd
import yaml
from cldfviz.text import render
from jinja2 import DictLoader
from pylingdocs.config import DATA_DIR
from pylingdocs.config import MANEX_DIR
from pylingdocs.config import TABLE_DIR
from pylingdocs.config import TABLE_MD
from pylingdocs.helpers import _get_relative_file
from pylingdocs.helpers import comma_and_list
from pylingdocs.helpers import get_md_pattern
from pylingdocs.helpers import sanitize_latex
from pylingdocs.helpers import split_ref
from pylingdocs.helpers import src
from pylingdocs.models import models


log = logging.getLogger(__name__)

MD_LINK_PATTERN = re.compile(r"\[(?P<label>[^]]*)]\((?P<url>[^)]+)\)")

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


if Path("custom_pld_models.py").is_file():
    sys.path.append(os.getcwd())
    from custom_pld_models import models as custom_models  # noqa

    models += custom_models


log.info("Loading templates")
labels = {}
templates = {}
list_templates = {}
envs = {}

for model in models:
    labels[model.shortcut] = model.query_string
    for output_format in model.templates:
        if output_format not in templates:
            templates[output_format] = {}
    for output_format in model.list_templates:
        if output_format not in list_templates:
            list_templates[output_format] = {}

with open(DATA_DIR / "util.md", "r", encoding="utf-8") as f:
    pylingdocs_util = f.read()

for templ in templates.values():
    templ["pylingdocs_util.md"] = pylingdocs_util
    templ["ParameterTable_detail.md"] = "{{ctx.cldf.name}}"

for output_format, env_dict in templates.items():
    for model in models:
        model_output = model.representation(output_format)
        if model_output is not None:
            env_dict[model.cldf_table + "_detail.md"] = model_output

for output_format, env_dict in list_templates.items():
    for model in models:
        model_output = model.representation(output_format, multiple=True)
        if model_output is not None:
            env_dict[model.cldf_table + "_index.md"] = model_output

if Path("pld/model_templates").is_dir():
    for model in Path("pld/model_templates").iterdir():
        for output_format, template_collection in templates.items():

            templ_path = model / output_format / "detail.md"
            if not templ_path.is_file():
                templ_path = model / "plain" / "detail.md"
            if templ_path.is_file():
                with open(templ_path, "r", encoding="utf-8") as f:
                    templ_content = f.read()
                template_collection[model.name + "_detail.md"] = templ_content

            templ_path = model / output_format / "index.md"
            if not templ_path.is_file():
                templ_path = model / "plain" / "index.md"
            if templ_path.is_file():
                with open(templ_path, "r", encoding="utf-8") as f:
                    templ_content = f.read()
                template_collection[model.name + "_index.md"] = templ_content


with open(DATA_DIR / "model_templates" / "latex_util.md", "r", encoding="utf-8") as f:
    latex_util = f.read()

templates["latex"]["latex_util.md"] = latex_util

with open(DATA_DIR / "model_templates" / "html_util.md", "r", encoding="utf-8") as f:
    html_util = f.read()

templates["html"]["html_util.md"] = html_util

for output_format, env_dict in templates.items():
    env_dict.update(list_templates[output_format])
    envs[output_format] = DictLoader(env_dict)

bool_dic = {"True": True, "False": False}
abbrev_dic = {"nt": "no_translation"}


def preprocess_cldfviz(md):
    current = 0
    for m in MD_LINK_PATTERN.finditer(md):
        yield md[current : m.start()]
        current, key, url = get_md_pattern(m)
        if key in labels:
            args = []
            kwargs = {}
            if "?" in url:
                url, arguments = url.split("?")
                for arg in arguments.split("&"):
                    if "=" in arg:
                        k, v = arg.split("=")
                        kwargs[k] = bool_dic.get(v, v)
                    else:
                        args.append(abbrev_dic.get(arg, arg))
            if "," in url:
                kwargs.update({"ids": url})
                yield labels[key](
                    url, visualizer="cldfviz", multiple=True, *args, **kwargs
                )
            else:
                yield labels[key](url, visualizer="cldfviz", *args, **kwargs)
        else:
            yield md[m.start() : m.end()]
    yield md[current:]


def render_markdown(
    md_str,
    ds,
    decorate_gloss_string=lambda x: x,
    data_format="cldf",
    output_format="plain",
):
    if data_format == "cldf":
        if output_format != "clld":
            preprocessed = render(
                doc="".join(preprocess_cldfviz(md_str)),
                cldf_dict=ds,
                loader=envs[output_format],
                func_dict={
                    "comma_and_list": comma_and_list,
                    "sanitize_latex": sanitize_latex,
                    "split_ref": split_ref,
                    "decorate_gloss_string": decorate_gloss_string,
                    "src": src,
                },
            )
            preprocessed = render(
                doc=preprocessed,
                cldf_dict=ds,
                loader=envs[output_format],
                func_dict={"comma_and_list": comma_and_list},
            )
            if "#cldf" in preprocessed:
                preprocessed = render(
                    doc=preprocessed,
                    cldf_dict=ds,
                    loader=envs[output_format],
                    func_dict={"comma_and_list": comma_and_list},
                )
            if "#cldf" in preprocessed:
                preprocessed = render(
                    doc=preprocessed,
                    cldf_dict=ds,
                    loader=envs[output_format],
                    func_dict={"comma_and_list": comma_and_list},
                )
        else:
            preprocessed = "".join(preprocess_cldfviz(md_str))
        return preprocessed
    log.error(f"Unknown data format {data_format}")
    return ""


def load_tables(md, tables, source_dir="."):
    current = 0
    for m in MD_LINK_PATTERN.finditer(md):
        yield md[current : m.start()]
        current, key, url = get_md_pattern(m)
        if key == "table":
            table_path = source_dir / TABLE_DIR / f"{url}.csv"
            if not table_path.is_file():
                log.error(f"Table file <{table_path.resolve()}> does not exist.")
                sys.exit(1)
            else:
                temp_df = pd.read_csv(table_path, keep_default_na=False)
                this_table_metadata = tables.get(url, {})
                temp_df = temp_df.apply(
                    lambda x: this_table_metadata.get(  # pylint: disable=cell-var-from-loop
                        "pre_cell", ""
                    )
                    + x
                    + this_table_metadata.get(  # pylint: disable=cell-var-from-loop
                        "post_cell", ""
                    )
                )
                csv_buffer = StringIO()
                temp_df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                yield "\nPYLINGDOCS_RAW_TABLE_START" + url + "CONTENT_START" + csv_buffer.read() + "PYLINGDOCS_RAW_TABLE_END"  # noqa: E501
        else:
            yield md[m.start() : m.end()]
    yield md[current:]


def load_manual_examples(md, source_dir="."):
    current = 0
    for m in MD_LINK_PATTERN.finditer(md):
        yield md[current : m.start()]
        current, key, url = get_md_pattern(m)
        if key == "manex":
            manex__yaml_path = source_dir / MANEX_DIR / f"{url}.yaml"
            if manex__yaml_path.is_file():
                with open(manex__yaml_path, encoding="utf-8") as f:
                    mex_list = yaml.load(f, Loader=yaml.SafeLoader)
                output = []
                for mex in mex_list:
                    if mex.startswith("ex:"):
                        output.append(f"[ex]({mex.split(':', 1)[1]}?format=subexample)")
                    else:
                        manex_md_path = source_dir / MANEX_DIR / f"{mex}.md"
                        with open(manex_md_path, "r", encoding="utf-8") as f:
                            output.append(
                                "PYLINGDOCS_MANPEXITEM_START"
                                + mex
                                + "CONTENT_START"
                                + f.read()
                                + "PYLINGDOCS_MANPEXITEM_END"
                            )
                yield "PYLINGDOCS_MANPEX_START" + url + "CONTENT_START\n" + "\n".join(
                    output
                ) + "\nPYLINGDOCS_MANPEX_END"
            else:
                manex_md_path = source_dir / MANEX_DIR / f"{url}.md"
                if not manex_md_path.is_file():
                    log.error(
                        f"Manual example file <{manex_md_path.resolve()}> does not exist."
                    )
                    sys.exit(1)
                else:
                    with open(manex_md_path, "r", encoding="utf-8") as f:
                        yield "PYLINGDOCS_MANEX_START" + url + "CONTENT_START" + f.read() + "PYLINGDOCS_MANEX_END"  # noqa: E501
        else:
            yield md[m.start() : m.end()]
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


def insert_manex(md, builder, pattern, kind="plain"):
    current = 0
    for m in pattern.finditer(md):
        yield md[current : m.start()]
        current = m.end()
        label = m.group("label")
        content = m.group("content")
        yield builder.manex(label, content=content, kind=kind)
    yield md[current:]


def load_table_metadata(source_dir):
    table_md = _get_relative_file(source_dir / TABLE_DIR, TABLE_MD)
    if table_md.is_file():
        with open(table_md, encoding="utf-8") as f:
            tables = yaml.load(f, Loader=yaml.SafeLoader)
    else:
        log.warning(f"Specified table metadatafile {TABLE_MD} not found.")
        tables = {}
    return tables


def preprocess(md_str, source_dir="."):
    tables = load_table_metadata(source_dir)
    temp_str = "".join(load_manual_examples(md_str, source_dir))
    return "".join(load_tables(temp_str, tables, source_dir))


def postprocess(md_str, builder, source_dir="."):
    tables = load_table_metadata(source_dir)
    md_str = "".join(insert_manex(md_str, builder, MANPEX_PATTERN, kind="multipart"))
    md_str = "".join(
        insert_manex(md_str, builder, MANPEX_ITEM_PATTERN, kind="subexample")
    )
    md_str = "".join(insert_manex(md_str, builder, MANEX_PATTERN))
    return "".join(insert_tables(md_str, builder, tables))
