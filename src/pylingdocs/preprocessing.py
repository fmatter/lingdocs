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
from pylingdocs.helpers import src, load_table_metadata
from pylingdocs.models import models


log = logging.getLogger(__name__)

MD_LINK_PATTERN = re.compile(r"\[(?P<label>[^]]*)]\((?P<url>[^)]+)\)")


model_dict = {x.name.lower(): x for x in models}
if Path("custom_pld_models.py").is_file():
    sys.path.append(os.getcwd())
    from custom_pld_models import models as custom_models  # noqa

    for model in custom_models:
        model_dict[model.__name__.lower()] = model
models = model_dict.values()

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

with open(DATA_DIR / "util.j2", "r", encoding="utf-8") as f:
    pylingdocs_util = f.read()

for templ in templates.values():
    templ["pylingdocs_util.md"] = pylingdocs_util
    templ["ParameterTable_detail.md"] = "{{ctx.cldf.name}}"

for output_format, env_dict in templates.items():
    for model in models:
        model_output = model.representation(output_format)
        # if output_format == "github" and model.name == "Example":
        #     log.debug(f"Format {output_format} for model {model}")
        #     log.debug(model_output)
        if model_output is not None:
            env_dict[model.cldf_table + "_detail.md"] = model_output
            # log.debug(f"Format {output_format} for model {model}")

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
                continue
            if templ_path.is_file():
                with open(templ_path, "r", encoding="utf-8") as f:
                    templ_content = f.read()
                log.info(
                    f"Using custom template {templ_path} for model {model.name} for format {output_format}"
                )
                template_collection[
                    f"{model_dict[model.name].cldf_table}_detail.md"
                ] = templ_content
        for output_format, template_collection in list_templates.items():
            templ_path = model / output_format / "index.md"
            if not templ_path.is_file():
                continue
            if templ_path.is_file():
                with open(templ_path, "r", encoding="utf-8") as f:
                    templ_content = f.read()
                # log.debug(f"Using custom template {templ_path} for model {model.name} for format {output_format}")
                template_collection[
                    f"{model.name.capitalize()}Table_index.md"
                ] = templ_content

with open(DATA_DIR / "model_templates" / "latex_util.md", "r", encoding="utf-8") as f:
    latex_util = f.read()

templates["latex"]["latex_util.md"] = latex_util

if Path("pld/model_templates/html_util.md").is_file():
    html_util_path = Path("pld/model_templates/html_util.md")
else:
    html_util_path = DATA_DIR / "model_templates" / "html_util.md"

with open(html_util_path, "r", encoding="utf-8") as f:
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


def pad_ex(*lines, sep=" "):
    out = {}
    for glossbundle in zip(*lines):
        longest = len(max(glossbundle, key=len))
        for i, obj in enumerate(glossbundle):
            diff = longest - len(obj)
            out.setdefault(i, [])
            out[i].append(obj + " " * diff)
    for k in out.copy():
        out[k] = sep.join(out[k])
    return tuple(out.values())


def render_markdown(
    md_str,
    ds,
    decorate_gloss_string=lambda x: x,
    data_format="cldf",
    output_format="plain",
):
    if data_format == "cldf":
        if output_format != "clld":
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
                    "flexible_pad_ex": pad_ex,
                    "get_audio": lambda x: audio_dict.get(x, None),
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
