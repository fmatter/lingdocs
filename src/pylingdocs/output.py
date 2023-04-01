"""Builders producing different output formats"""
import logging
import re
import shutil
import subprocess
import threading
from http.server import SimpleHTTPRequestHandler
from http.server import test
from pathlib import Path
from pathlib import PosixPath
import hupper
from pylingdocs.config import BENCH
from pylingdocs.config import CONTENT_FILE_PREFIX
from pylingdocs.config import CONTENT_FOLDER
from pylingdocs.config import OUTPUT_DIR
from pylingdocs.config import STRUCTURE_FILE
from pylingdocs.formats import builders
from pylingdocs.helpers import _get_relative_file, read_file, write_file
from pylingdocs.helpers import _load_cldf_dataset
from pylingdocs.helpers import check_abbrevs
from pylingdocs.helpers import get_structure
from pylingdocs.helpers import load_content
from pylingdocs.helpers import refresh_clld_db
from pylingdocs.metadata import _load_metadata
from pylingdocs.models import models
from pylingdocs.postprocessing import postprocess
from pylingdocs.preprocessing import preprocess
from pylingdocs.preprocessing import render_markdown


NUM_PRE = re.compile(r"[\d]+\ ")
ABC_PRE = re.compile(r"[A-Z]+\ ")

log = logging.getLogger(__name__)


def update_structure(
    content_dir=CONTENT_FOLDER,
    bench_dir=BENCH,
    structure_file=STRUCTURE_FILE,
    prefix_mode=CONTENT_FILE_PREFIX,
):
    log.info("Updating document structure")

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
        for i, line in enumerate(preprocessed.split("\n")):
            try:
                render_markdown(line, dataset, output_format="plain")
            except KeyError as e:
                log.error(f"Missing ID in file {filename}, L{i+1}:\n{str(e)} in {line}")
                found = True
    if not found:
        log.info("No missing IDs found.")


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
    for output_format in formats:
        for m in models:
            m.reset_cnt()
        log.info(f"Rendering format [{output_format}]")
        builder = builders[output_format]
        content = "\n\n".join([x["content"] for x in contents.values()])
        preprocessed = preprocess(content, source_dir)
        preprocessed = builder.preprocess_commands(preprocessed, **kwargs)
        preprocessed = render_markdown(
            preprocessed,
            dataset,
            decorate_gloss_string=builder.decorate_gloss_string,
            output_format=output_format,
            **kwargs
        )
        preprocessed += "\n\n" + builder.reference_list()
        # second run to insert reference list
        preprocessed = render_markdown(
            preprocessed,
            dataset,
            decorate_gloss_string=builder.decorate_gloss_string,
            output_format=output_format,
            **kwargs
        )
        preprocessed = postprocess(preprocessed, builder, source_dir)
        if builder.name == "latex":
            metadata["bibfile"] = dataset.bibpath.name
        if builder.single_output:
            builder.write_folder(
                output_dir,
                content=preprocessed,
                metadata=metadata,
                abbrev_dict=abbrev_dict,
            )
        if builder.name == "latex":
            bibcontents = read_file(dataset.bibpath)
            write_file(bibcontents.replace(" &", " \\&"), output_dir / builder.name / dataset.bibpath.name)
    if latex:
        compile_latex()
