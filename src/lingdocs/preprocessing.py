import logging
import sys
from io import StringIO
from pathlib import Path

import pandas as pd
import yaml
from cldf_rel import CLDFDataset
from cldfviz.text import render
from jinja2 import DictLoader
from writio import load

from lingdocs.config import (
    DATA_DIR,
    MANEX_DIR,
    MD_LINK_PATTERN,
    PLD_DIR,
    TABLE_DIR,
    config,
)
from lingdocs.helpers import (
    comma_and_list,
    func_dict,
    get_md_pattern,
    load_table_metadata,
)
from lingdocs.models import models
from lingdocs.templates import load_templates

log = logging.getLogger(__name__)

tables = {}
for model in models:
    tables[model.shortcut] = {
        "query": model.query_string,
        "label": model.name.lower() + "s",
    }

log.debug("Loading templates")
loaders = {}


def _load_templates(builder, rich=None):
    templates = load_templates(builder, models, rich=rich)
    pld_util = load(DATA_DIR / "util.j2")

    def resolve_path(base, in_path, builder):
        path = base / in_path.format(name=builder.name)
        if not path.is_file() and builder.__class__.__bases__[0] != object:
            parent_path = base / in_path.format(
                name=builder.__class__.__bases__[0].name
            )
            if not parent_path.is_file():
                return path
            return parent_path
        return path

    # for output_format, f_templates in templates.items():
    util_path = resolve_path(PLD_DIR, "model_templates/{name}_util.md", builder)
    if not util_path.is_file():
        util_path = resolve_path(DATA_DIR, "model_templates/{name}_util.md", builder)
    for loader in ["text", "data"]:
        templates[loader]["pld_util.md"] = pld_util
        templates[loader][
            "ParameterTable_detail.md"
        ] = "{{ctx.cldf.name}}"  # todo is this needed?
        templates[loader]["fmt_util.md"] = load(util_path)
    loaders[builder.name] = {
        "text": DictLoader(templates["text"]),
        "data": DictLoader(templates["data"]),
        "example_in_detail": DictLoader(
            {
                **templates["data"],
                **{
                    "ExampleTable_detail.md": templates["text"][
                        "ExampleTable_detail.md"
                    ]
                },
            }
        ),
    }


bool_dic = {"True": True, "False": False}

shortcuts = {"ftr": "translation"}


def preprocess_cldfviz(md):
    current = 0
    for m in MD_LINK_PATTERN.finditer(md):
        yield md[current : m.start()]
        current, key, url = get_md_pattern(m)
        if key in tables:
            args = []
            kwargs = {}
            if "?" in url:
                url, arguments = url.split("?")
                for arg in arguments.split("&"):
                    if "=" in arg:
                        k, v = arg.split("=")
                        if k in shortcuts:
                            k = shortcuts[k]
                        kwargs[k] = bool_dic.get(v, v)
                    elif arg == "nt":
                        kwargs["with_translation"] = False
                    elif arg == "nl":
                        kwargs["with_language"] = False
                    else:
                        args.append(arg)
            if "," in url:
                kwargs.update({"ids": url})
                yield tables[key]["query"](
                    url, visualizer="cldfviz", multiple=True, *args, **kwargs
                )
            else:
                yield tables[key]["query"](url, visualizer="cldfviz", *args, **kwargs)
        else:
            yield md[m.start() : m.end()]
    yield md[current:]


def render_markdown(
    md_str,
    ds,
    builder,
    decorate_gloss_string=lambda x: x,
    data_format="cldf",
    rich=None,
    **kwargs,
):
    _load_templates(builder, rich=rich)
    config.load_from_dir()
    rich = rich or config["data"]["rich"]
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
            func_dict["get_audio"] = lambda x: builder.get_audio(audio_dict, x)
            func_dict["decorate_gloss_string"] = decorate_gloss_string
            for func, val in kwargs.get("func_dict", {}).items():
                func_dict[func] = val
            func_dict["ref_labels"] = builder.ref_labels
            if rich:
                data = CLDFDataset(ds)
                func_dict["data"] = data.tables
            preprocessed = render(
                doc="".join(preprocess_cldfviz(md_str)),
                cldf_dict=ds,
                loader=loaders[builder.name]["text"],
                func_dict=func_dict,
            )
            preprocessed = render(
                doc=preprocessed,
                cldf_dict=ds,
                loader=loaders[builder.name]["text"],
                func_dict=func_dict,
            )  # todo this can be made prettier
            if "#cldf" in preprocessed:
                preprocessed = render(
                    doc=preprocessed,
                    cldf_dict=ds,
                    loader=loaders[builder.name]["text"],
                    func_dict={"comma_and_list": comma_and_list},
                )
            if "#cldf" in preprocessed:
                preprocessed = render(
                    doc=preprocessed,
                    cldf_dict=ds,
                    loader=loaders[builder.name]["text"],
                    func_dict={"comma_and_list": comma_and_list},
                )
        else:
            preprocessed = "".join(preprocess_cldfviz(md_str))
        return preprocessed
    log.error(f"Unknown data format {data_format}")
    sys.exit()


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
