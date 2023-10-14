"""Builders producing different output formats"""
import logging
import re
import shutil
import subprocess
from pathlib import Path, PosixPath

import hupper
from cldf_rel import CLDFDataset, get_table_name
from cldfviz.text import render
from tqdm import tqdm
from writio import dump, load

from pylingdocs.config import BENCH, CONTENT_FOLDER, EXTRA_DIR, STRUCTURE_FILE, config
from pylingdocs.formats import builders
from pylingdocs.helpers import (
    _get_relative_file,
    check_abbrevs,
    extract_chapters,
    func_dict,
    get_structure,
    load_content,
    load_figure_metadata,
    process_labels,
    read_file,
    write_file,
)
from pylingdocs.postprocessing import postprocess
from pylingdocs.preprocessing import (
    loaders,
    preprocess,
    preprocess_cldfviz,
    render_markdown,
)

NUM_PRE = re.compile(r"[\d]+\ ")
ABC_PRE = re.compile(r"[A-Z]+\ ")

log = logging.getLogger(__name__)


def update_structure(
    content_dir=CONTENT_FOLDER,
    bench_dir=BENCH,
    structure_file=STRUCTURE_FILE,
    prefix_mode=config["input"]["content_file_prefix"],
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


def compile_latex(output_dir=config["paths"]["output"]):  # pragma: no cover
    log.info("Compiling LaTeX document.")
    with subprocess.Popen(
        "latexmk --quiet --xelatex main.tex", shell=True, cwd=output_dir / "latex"
    ) as proc:
        del proc  # help, prospector is forcing me


def preview(output_format, **kwargs):
    builder = builders[output_format]()
    builder.open_preview()
    _preview(builder=builder, **kwargs)


def _preview(dataset, source_dir, output_dir, builder, refresh=True, **kwargs):
    log.info("Rendering preview")
    watchfiles = [str(x) for x in source_dir.iterdir()]
    watchfiles += [str(x) for x in (source_dir / CONTENT_FOLDER).iterdir()]
    extra = source_dir / EXTRA_DIR
    if extra.is_dir():
        watchfiles += [str(x) for x in extra.iterdir()]
    structure_file = _get_relative_file(
        folder=source_dir / CONTENT_FOLDER, file=STRUCTURE_FILE
    )
    config.load_from_dir(source_dir)
    contents = load_content(
        structure_file=structure_file, source_dir=source_dir / CONTENT_FOLDER
    )
    kwargs["dataset"] = dataset
    kwargs["source_dir"] = source_dir
    kwargs["output_dir"] = output_dir
    if refresh:
        wkwargs = kwargs.copy()
        wkwargs["builder"] = builder
        reloader = hupper.start_reloader(
            "pylingdocs.output._preview", worker_kwargs=wkwargs
        )
        reloader.watch_files(watchfiles)
    kwargs["contents"] = contents

    create_output(formats=[builder.name], **kwargs)
    builder.run_preview()


def clean_output(output_dir):
    shutil.rmtree(output_dir)
    output_dir.mkdir()


def _write_file(part_id):
    log.debug(f"Writing {part_id}")


def check_ids(contents, dataset, source_dir):
    builder = builders["plain"]()
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
    if config["output"]["rich"]:
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
            # i = 0
            for rid, detail in tqdm(items.items(), desc=name):
                # i += 1
                # if i > 5:
                #     continue
                filepath = table_dir / f"{rid}.{builder.file_ext}"
                if filepath.is_file():
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
        metadata = load(metadata) or None
    output_dir = Path(output_dir)
    source_dir = Path(source_dir)
    if not output_dir.is_dir():
        log.info(f"Creating output folder {output_dir.resolve()}")
        output_dir.mkdir()
    abbrev_dict = check_abbrevs(
        dataset, source_dir, "\n\n".join([x["content"] for x in contents.values()])
    )

    figure_metadata = load_figure_metadata(source_dir)
    for output_format in formats:
        with tqdm(total=6, desc=f"Building {output_format} output") as pbar:
            builder = builders[output_format]()
            builder.figure_metadata = figure_metadata
            content = "\n\n".join([x["content"] for x in contents.values()])
            pbar.update(1)
            chapters = extract_chapters(content)
            ref_labels, ref_locations = process_labels(chapters)
            preprocessed = preprocess(content, source_dir)
            builder.ref_labels = ref_labels
            builder.ref_locations = ref_locations
            preprocessed = builder.preprocess_commands(preprocessed, **kwargs)
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
                    source_dir=source_dir,
                    content=preprocessed,
                    metadata=metadata,
                    abbrev_dict=abbrev_dict,
                    ref_labels=ref_labels,
                    ref_locations=ref_locations,
                    chapters=chapters,
                )
            pbar.update(1)
        if config["output"]["data"]:
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
