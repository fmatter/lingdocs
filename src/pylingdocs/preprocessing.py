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
from jinja2.runtime import Undefined
from writio import load
from pylingdocs.config import DATA_DIR
from pylingdocs.config import LFTS_SHOW_FTR
from pylingdocs.config import LFTS_SHOW_LG
from pylingdocs.config import LFTS_SHOW_SOURCE
from pylingdocs.config import MANEX_DIR
from pylingdocs.config import MD_LINK_PATTERN
from pylingdocs.config import TABLE_DIR
from pylingdocs.helpers import build_example
from pylingdocs.helpers import build_examples
from pylingdocs.helpers import comma_and_list
from pylingdocs.helpers import func_dict
from pylingdocs.helpers import get_md_pattern
from pylingdocs.helpers import load_table_metadata
from pylingdocs.helpers import sanitize_latex
from pylingdocs.helpers import split_ref
from pylingdocs.helpers import src
from pylingdocs.models import models
import sys

log = logging.getLogger(__name__)

model_dict = {x.name.lower(): x for x in models}


if Path("pld/models.py").is_file():
    sys.path.insert(1, 'pld')
    from models import models as custom_models
    for mm in custom_models:
        model_dict[mm.name.lower()] = mm

models = model_dict.values()

log.info("Loading templates")
views = ["inline", "list", "detail", "index"]
labels = {}
loaders = {}


for model in models:
    labels[model.shortcut] = model.query_string
    for view, templates in model.templates.items():
        for output_format, template in templates.items():
            loaders.setdefault(output_format, {})
            if view == "inline":
                loaders[output_format][model.cldf_table + f"_detail.md"] = template
            elif view == "list":
                loaders[output_format][model.cldf_table + f"_index.md"] = template
            elif view == "detail":
                loaders[output_format][model.cldf_table + f"_page.md"] = template
            elif view == "index":
                loaders[output_format][model.cldf_table + f"_indexpage.md"] = template

if Path("pld/model_templates").is_dir():
    for model in Path("pld/model_templates").iterdir():
        for output_format, templates in loaders.items():
            for target_file, template_handle in [
                (
                    f"{output_format}.md",
                    f"{model_dict[model.name].cldf_table}_detail.md",
                ),
                (
                    f"{output_format}_index.md",
                    f"{model_dict[model.name].cldf_table}_index.md",
                ),
                (
                    f"{output_format}_page.md",
                    f"{model_dict[model.name].cldf_table}_page.md",
                ),
            ]:
                if (model / target_file).is_file():
                    log.info(
                        f"Using custom template {target_file} for model {model.name} for format {output_format}"
                    )
                    templates[template_handle] = load(model / target_file)

pylingdocs_util = load(DATA_DIR / "util.j2")

for output_format, templates in loaders.items():
    templates["pylingdocs_util.md"] = pylingdocs_util
    templates["ParameterTable_detail.md"] = "{{ctx.cldf.name}}"
    util_path = Path(f"pld/model_templates/{output_format}_util.md")
    if not util_path.is_file():
        util_path = DATA_DIR / "model_templates" / f"{output_format}_util.md"
    templates["pld_util.md"] = load(util_path)
    loaders[output_format] = DictLoader(templates)


bool_dic = {"True": True, "False": False}


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
                    elif arg == "nt":
                        kwargs["with_translation"] = False
                    else:
                        args.append(arg)
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
    builder,
    decorate_gloss_string=lambda x: x,
    data_format="cldf",
    **kwargs,
):
    if data_format == "cldf":
        if builder.name != "clld":
            if "MediaTable" in ds.components:
                audio_dict = {
                    x["ID"]: {
                        "url": x.get("Download_URL", "").unsplit(),
                        "type": x["Media_Type"],
                    }
                    for x in ds.iter_rows("MediaTable")
                }
            else:
                audio_dict = {}
            func_dict["get_audio"] = lambda x: audio_dict.get(x, None)
            func_dict["decorate_gloss_string"] = decorate_gloss_string
            for func, val in kwargs.get("func_dict", {}).items():
                func_dict[func] = val
            func_dict["ref_labels"] = builder.ref_labels
            from pylingdocs.config import MKDOCS_RICH

            if builder.name == "mkdocs" and MKDOCS_RICH:
                from cldfrels import CLDFDataset

                data = CLDFDataset(ds)
                print(data)
                func_dict["data"] = data.tables
            preprocessed = render(
                doc="".join(preprocess_cldfviz(md_str)),
                cldf_dict=ds,
                loader=loaders[builder.name],
                func_dict=func_dict,
            )
            preprocessed = render(
                doc=preprocessed,
                cldf_dict=ds,
                loader=loaders[builder.name],
                func_dict=func_dict,
            )
            if "#cldf" in preprocessed:
                preprocessed = render(
                    doc=preprocessed,
                    cldf_dict=ds,
                    loader=loaders[builder.name],
                    func_dict={"comma_and_list": comma_and_list},
                )
            if "#cldf" in preprocessed:
                preprocessed = render(
                    doc=preprocessed,
                    cldf_dict=ds,
                    loader=loaders[builder.name],
                    func_dict={"comma_and_list": comma_and_list},
                )
        else:
            preprocessed = "".join(preprocess_cldfviz(md_str))
        return preprocessed
    log.error(f"Unknown data format {data_format}")
    exit()
    return ""


def load_tables(md, tables, source_dir="."):
    def decorate_cell(x):
        if x != "":
            return (
                this_table_metadata.get("pre_cell", "")
                + str(x)
                + this_table_metadata.get("post_cell", "")
            )
        return x

    current = 0
    for m in MD_LINK_PATTERN.finditer(md):
        yield md[current : m.start()]
        current, key, url = get_md_pattern(m)
        if key == "table":
            table_path = source_dir / TABLE_DIR / f"{url}.csv"
            if not table_path.is_file():
                log.info(
                    f"Table file <{table_path.resolve()}> does not exist, creating..."
                )
                with open(table_path.resolve(), "w", encoding="utf-8") as new_file:
                    new_file.write("Header,row\nContent,row")
            this_table_metadata = tables.get(url, {})
            temp_df = pd.read_csv(table_path, index_col=0, keep_default_na=False)
            temp_df = temp_df.applymap(decorate_cell)
            with_header_col = this_table_metadata.get("header_column", True)
            if not with_header_col:
                temp_df.index = temp_df.index.map(decorate_cell)
            csv_buffer = StringIO()
            temp_df.to_csv(csv_buffer, index=True)
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


def preprocess(md_str, source_dir="."):
    tables = load_table_metadata(source_dir)
    temp_str = "".join(load_manual_examples(md_str, source_dir))
    return "".join(load_tables(temp_str, tables, source_dir))
