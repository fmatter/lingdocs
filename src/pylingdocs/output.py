"""Builders producing different output formats"""
import logging
import re
import shutil
import subprocess
import threading
from http.server import SimpleHTTPRequestHandler, test
from pathlib import Path, PosixPath
from cldf_rel import get_table_name
from writio import dump
from jinja2 import Environment, FileSystemLoader, DictLoader

import hupper
from cldf_rel import CLDFDataset

from pylingdocs.config import (
    BENCH,
    CONTENT_FILE_PREFIX,
    CONTENT_FOLDER,
    OUTPUT_DIR,
    STRUCTURE_FILE,
    WRITE_DATA,
    RICH,
)
from tqdm import tqdm
from pylingdocs.formats import builders
from pylingdocs.helpers import (
    func_dict,
    _get_relative_file,
    _load_cldf_dataset,
    check_abbrevs,
    extract_chapters,
    get_structure,
    load_content,
    load_figure_metadata,
    process_labels,
    read_file,
    refresh_clld_db,
    write_file,
)
from pylingdocs.metadata import _load_metadata
from pylingdocs.postprocessing import postprocess
from pylingdocs.preprocessing import (
    loaders,
    preprocess,
    render_markdown,
    preprocess_cldfviz,
)
from cldfviz.text import render

NUM_PRE = re.compile(r"[\d]+\ ")
ABC_PRE = re.compile(r"[A-Z]+\ ")

log = logging.getLogger(__name__)


def update_structure(
    content_dir=CONTENT_FOLDER,
    bench_dir=BENCH,
    structure_file=STRUCTURE_FILE,
    prefix_mode=CONTENT_FILE_PREFIX,
):
    log.debug("Updating document structure")

    content_files = {}
    for file in content_dir.iterdir():
        if ".md" not in file.name:
            continue
        name = re.sub(NUM_PRE, "", file.stem)
        name = re.sub(ABC_PRE, "", name)
        content_files[name] = file

    bench_files = {}
    if Path(bench_dir).is_dir():
        for file in bench_dir.iterdir():
            if ".md" not in file.name:
                continue
            name = re.sub(NUM_PRE, "", file.stem)
            name = re.sub(ABC_PRE, "", name)
            bench_files[name] = file

    structure = get_structure(
        prefix_mode=prefix_mode,
        structure_file=_get_relative_file(content_dir, structure_file),
    )

    for part_id, data in structure.items():
        new_path = Path(content_dir, data["filename"])
        if part_id in content_files:
            if part_id in bench_files:
                log.warning(f"Conflict: {part_id}. Resolve manually.")
            else:
                if content_files[part_id] != new_path:
                    log.info(f"'{part_id}': {content_files[part_id]} > {new_path}")
                    content_files[part_id].rename(new_path)
                del content_files[part_id]
        elif part_id in bench_files:
            if bench_files[part_id] != new_path:
                log.info(f"'{part_id}': moving {bench_files[part_id]} > {new_path}")
                bench_files[part_id].rename(new_path)
            del bench_files[part_id]
        else:
            log.info(f"'{part_id}': creating file {new_path}")
            new_path.touch()

    for file in content_files.values():
        if not bench_dir.is_dir():
            log.info(f"Creating {bench_dir} for unused files.")
            bench_dir.mkdir()
        new_path = Path(bench_dir, file.name)
        log.info(f"Unlisted: moving {file} > {new_path}")
        file.rename(new_path)


def compile_latex(output_dir=OUTPUT_DIR):  # pragma: no cover
    log.info("Compiling LaTeX document.")
    with subprocess.Popen(
        "latexmk --quiet --xelatex main.tex", shell=True, cwd=output_dir / "latex"
    ) as proc:
        del proc  # help, prospector is forcing me


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(OUTPUT_DIR / "html"), **kwargs)


def run_server():
    test(Handler)


def run_preview(cldf, source_dir, output_dir, refresh=True, **kwargs):
    log.info("Rendering preview")
    watchfiles = [str(x) for x in source_dir.iterdir()]
    watchfiles += [str(x) for x in (source_dir / CONTENT_FOLDER).iterdir()]
    ds = _load_cldf_dataset(cldf)
    structure_file = _get_relative_file(
        folder=source_dir / CONTENT_FOLDER, file=STRUCTURE_FILE
    )
    contents = load_content(
        structure_file=structure_file, source_dir=source_dir / CONTENT_FOLDER
    )
    kwargs["cldf"] = cldf
    kwargs["dataset"] = ds
    kwargs["source_dir"] = source_dir
    kwargs["output_dir"] = output_dir
    if refresh:
        wkwargs = kwargs.copy()
        reloader = hupper.start_reloader(
            "pylingdocs.output.run_preview", worker_kwargs=wkwargs
        )
        reloader.watch_files(watchfiles)
    html = kwargs.pop("html", False)
    clld = kwargs.pop("clld", False)
    latex = kwargs.pop("latex", False)
    if clld and "clld" not in kwargs["formats"]:
        kwargs["formats"] = list(kwargs["formats"]) + ["clld"]
    if html and "html" not in kwargs["formats"]:
        kwargs["formats"] = list(kwargs["formats"]) + ["html"]
    if latex and "latex" not in kwargs["formats"]:
        kwargs["formats"] = list(kwargs["formats"]) + ["latex"]
    kwargs["contents"] = contents

    create_output(**kwargs)
    if html:
        threading.Thread(target=run_server).start()
    if clld:
        refresh_clld_db(OUTPUT_DIR / "clld")
    if latex:
        compile_latex()


def clean_output(output_dir):
    shutil.rmtree(output_dir)
    output_dir.mkdir()


def _write_file(part_id):
    log.debug(f"Writing {part_id}")


def check_ids(contents, dataset, source_dir):
    builder = builders["plain"]
    found = False
    for filename, x in contents.items():
        preprocessed = preprocess(x["content"], source_dir)
        preprocessed = builder.preprocess_commands(preprocessed)
        figure_metadata = load_figure_metadata(source_dir)
        builder.figure_metadata = figure_metadata
        for i, line in enumerate(preprocessed.split("\n")):
            try:
                render_markdown(line, dataset, builder=builder)
            except KeyError as e:
                log.error(f"Missing ID in file {filename}, L{i+1}:\n{str(e)} in {line}")
                found = True
    if not found:
        log.info("No missing IDs found.")


def write_details(builder, output_dir, dataset):
    loader = loaders[builder.name]["data"]
    text_loader = loaders[builder.name]["text"]
    output_dir = output_dir / builder.name / builder.data_dir
    output_dir.mkdir(exist_ok=True, parents=True)
    func_dict["decorate_gloss_string"] = builder.decorate_gloss_string
    func_dict["ref_labels"] = builder.ref_labels
    if RICH:
        data = CLDFDataset(dataset, orm=True)
        func_dict["data"] = data
        table_list = list((k, v, v.name) for k, v in data.tables.items())
    else:
        log.info(
            f"Writing data for {builder.name} to {output_dir.resolve()}, this may take a while. Set data = False in the [output] section of your config file to turn off."
        )
        table_list = [
            (str(table.url).replace(".csv", ""), table, get_table_name(table))
            for table in dataset.tables
        ]
    model_index = []
    data_nav = ["nav:"]
    for label, table, name in table_list:
        # if label not in ["derivationalprocesses"]:
        #     continue
        table_dir = output_dir / label
        if f"{name}_index.{builder.file_ext}" not in loader.list_templates():
            log.warning(f"Not writing index for {name}")
        else:
            model_index.append(f"* [{label}]({label})")
            data_nav.append(f"  - {label.capitalize()}: data/{label}")
            table_dir.mkdir(exist_ok=True, parents=True)
            index = f"[]({name}#cldf:__all__)"
            index = render(
                doc="".join(preprocess_cldfviz(index)),
                cldf_dict=dataset,
                loader=loader,
                func_dict=func_dict,
            )  # todo prettify
            if "#cldf" in index:
                index = render(
                    doc=index,
                    cldf_dict=dataset,
                    loader=text_loader,
                    func_dict=func_dict,
                )
            index = builder.preprocess(index)
            if index.strip() != "":
                dump(index, table_dir / f"index.{builder.file_ext}")

        if f"{name}_detail.md" not in loader.list_templates():
            log.warning(f"Not writing details for {name}")
        else:
            table_dir.mkdir(exist_ok=True, parents=True)
            # when in detail mode and listing examples, load the in-text example view (instead of linking))
            if label != "examples":
                detail_loader = loaders[builder.name]["example_in_detail"]
            else:
                detail_loader = loader

            if name.endswith("Table"):
                items = {
                    rec.id: f"[]({name}#cldf:{rec.id})" for rec in dataset.objects(name)
                }
            else:
                items = {
                    rec["ID"]: f"[]({name}#cldf:{rec['ID']})"
                    for rec in dataset.iter_rows(name)
                }
            i = 0
            for rid, detail in tqdm(items.items(), desc=name):
                i += 1
                if i > 5:
                    continue
                filepath = table_dir / f"{rid}.{builder.file_ext}"
                if filepath.is_file():
                    pass
                    continue
                detail = render(
                    doc="".join(preprocess_cldfviz(detail)),
                    cldf_dict=dataset,
                    loader=detail_loader,
                    func_dict=func_dict,
                )  # rodo prettify
                if "#cldf" in detail:
                    detail = render(
                        doc=detail,
                        cldf_dict=dataset,
                        loader=text_loader,
                        func_dict=func_dict,
                    )
                detail = builder.preprocess(detail)
                if detail.strip() != "":
                    dump(detail, filepath)
    if model_index:
        dump(
            "# Data\n\n" + "\n".join(model_index),
            output_dir / f"index.{builder.file_ext}",
        )
        dump("\n".join(data_nav), output_dir / ".pages")


def create_output(
    contents,
    source_dir,
    formats,
    dataset,
    output_dir,
    metadata=None,
    latex=False,
    **kwargs,
):  # pylint: disable=too-many-arguments
    """Run different builders.


    This is the extended description.

    Args:
        arg1 (int): Description of arg1

    Returns:
        bool: blabla

    """
    if isinstance(metadata, (str, PosixPath)):
        metadata = _load_metadata(metadata)
    if metadata is None:
        metadata = {}
    output_dir = Path(output_dir)
    if not output_dir.is_dir():
        log.info(f"Creating output folder {output_dir.resolve()}")
        output_dir.mkdir()
    abbrev_dict = check_abbrevs(
        dataset, source_dir, "\n\n".join([x["content"] for x in contents.values()])
    )
    figure_metadata = load_figure_metadata(source_dir)
    for output_format in formats:
        log.info(f"Building {output_format} output")
        with tqdm(total=10) as pbar:
            builder = builders[output_format]
            builder.figure_metadata = figure_metadata
            content = "\n\n".join([x["content"] for x in contents.values()])
            pbar.update(1)
            chapters = extract_chapters(content)
            pbar.update(1)
            ref_labels, ref_locations = process_labels(chapters)
            pbar.update(1)
            preprocessed = preprocess(content, source_dir)
            pbar.update(1)
            builder.ref_labels = ref_labels
            builder.ref_locations = ref_locations
            preprocessed = builder.preprocess_commands(preprocessed, **kwargs)
            pbar.update(1)
            preprocessed = render_markdown(
                preprocessed,
                dataset,
                builder,
                decorate_gloss_string=builder.decorate_gloss_string,
                **kwargs,
            )
            pbar.update(1)
            preprocessed += "\n\n" + builder.reference_list()
            # second run to insert reference list
            pbar.update(1)
            preprocessed = render_markdown(
                preprocessed,
                dataset,
                builder,
                decorate_gloss_string=builder.decorate_gloss_string,
                output_format=output_format,
                **kwargs,
            )
            pbar.update(1)
            preprocessed = postprocess(preprocessed, builder, source_dir)
            pbar.update(1)
            if builder.name == "latex":
                metadata["bibfile"] = dataset.bibpath.name
            if builder.single_output:
                builder.write_folder(
                    output_dir,
                    content=preprocessed,
                    metadata=metadata,
                    abbrev_dict=abbrev_dict,
                    ref_labels=ref_labels,
                    ref_locations=ref_locations,
                    parts=chapters,
                )
            pbar.update(1)
        if WRITE_DATA:
            write_details(builder, output_dir, dataset)
        if builder.name == "latex":
            bibcontents = read_file(dataset.bibpath)
            if bibcontents:
                write_file(
                    bibcontents.replace(" &", " \\&"),
                    output_dir / builder.name / dataset.bibpath.name,
                )
        log.info(
            f"Wrote format {output_format} to {(output_dir / builder.name).resolve()}"
        )
    if latex:
        compile_latex()
