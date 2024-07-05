import logging
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import jinja2
import keepachangelog
from writio import dump, load

from lingdocs.config import (
    BUILD_DIR,
    CONTENT_FOLDER,
    DATA_DIR,
    EXTRA_DIR,
    MANEX_DIR,
    PLD_DIR,
    TABLE_DIR,
    config,
)

log = logging.getLogger(__name__)


class ReleaseMode:
    name = "release"

    @classmethod
    def version_list(cls):
        raise NotImplementedError(f"Do not use {cls.name} for releasing.")

    @classmethod
    def release(cls):
        raise NotImplementedError(f"Do not use {cls.name} for releasing.")


def zipdir(path, zipfile):
    for root, dirs, files in os.walk(path):
        for file in files:
            zipfile.write(
                os.path.join(root, file),
                os.path.relpath(os.path.join(root, file), os.path.join(path, "..")),
            )


class Mike:
    pass
    # - make sure mike is installed
    # - mike set-default latest
    # - mike deploy VERSION


class LocalZip:
    name = "zip"
    directory = "zips"

    @classmethod
    def version_list(cls, source):
        if (source / cls.directory).is_dir():
            return [
                f.name
                for f in (source / cls.directory).iterdir()
                if f.is_file() and f.suffix == ".zip"
            ]
        return []

    @classmethod
    def release(cls, name, source):
        (source / cls.directory).mkdir(exist_ok=True, parents=True)
        with zipfile.ZipFile(
            source / cls.directory / f"{name}.zip", "w", zipfile.ZIP_DEFLATED
        ) as zipf:
            zipdir(source / BUILD_DIR / name, zipf)


modes = [LocalZip]


def _version(v):
    return "v" + v.strip("v")


def run_releases(source, output_dir, bump, **kwargs):
    config.load_from_dir(source)
    metadata = load(source / "metadata.yaml")
    if config["output"]["changelog"]:
        release_changelog(metadata)
    version = _version(metadata["version"])
    build_archive(source, output_dir, metadata["id"] + "-" + version)
    for mode in modes:
        if version in mode.version_list(source):
            log.error(f"{version} already exists.")
            sys.exit()
    for mode in modes:
        print(f"releasing {mode}")
        mode.release(f'{metadata["id"]}-{version}', source)
    metadata["version"] = bump_version(metadata["version"], bump)
    dump(metadata, source / "metadata.yaml")


def bump_version(version, step="patch"):
    delimiters = [r"\.", r"-"]
    search = "|".join(delimiters)
    parts = re.split(rf"({search})", version)
    pos = {}
    steps = ["major", "minor", "patch"]
    s_idx = 0
    for i, part in enumerate(parts):
        if part not in [".", "-"]:
            pos[steps[s_idx]] = i
            s_idx += 1
    parts[pos[step]] = str(int(parts[pos[step]]) + 1)
    for target in range(steps.index(step) + 1, len(steps)):
        parts[pos[steps[target]]] = "0"
    return "".join(parts)


def release_changelog(metadata):
    clp = Path("CHANGELOG.md")
    if clp.is_file():
        clp.unlink()
    if clp.is_file():
        cl = load(clp)
    else:
        log.info("Creating CHANGELOG.md")
        loader = jinja2.FileSystemLoader(searchpath=DATA_DIR)
        env = jinja2.Environment(loader=loader)
        template = env.get_template("changelog_tpl.j2")
        cl = template.render(metadata)
        dump(cl, clp)
    keepachangelog.release(clp, new_version=metadata["version"])
    cl = load(clp)
    if "]: https" not in cl:
        cl = (
            cl
            + f"""

[Unreleased]: {metadata["repository"]}/compare/v{metadata["version"]}...HEAD
[{metadata["version"]}]: {metadata["repository"]}/releases/tag/{metadata["version"]}"""
        )
        dump(cl, clp)


def build_archive(source, output_dir, version):
    def _dedict(file):
        if isinstance(file, dict):
            name = list(file.values())[0]
            file = list(file.keys())[0]
        else:
            name = Path(file).name
        return file, name

    contents = {"cldf": []}
    build_path = source / BUILD_DIR / version
    build_path.mkdir(exist_ok=True, parents=True)
    for fmt, target in config["releasing"]["zip"].items():
        contents[fmt] = []
        if fmt == "cldf":
            if target is True:
                contents["cldf"].append(source / output_dir / fmt)
        else:
            fmt_path = source / output_dir / fmt
            if not fmt_path.is_dir():
                if not fmt_path.is_dir():
                    log.warning(
                        f"No directory {fmt_path.resolve()}.\nRemove {fmt} from the releasing>zip entry or build the format."
                    )
                sys.exit()
            if not isinstance(target, list):
                targets = [target]
            else:
                targets = target
            for target in targets:
                target, rename = _dedict(target)
                for f in fmt_path.iterdir():
                    if f.is_file() and f.suffix == "." + target:
                        contents[fmt].append({f: rename})
                    elif f.name == target:
                        contents[fmt].append(({f: rename}))

    def _copy(file, fmt_dir):
        file, name = _dedict(file)
        if file.is_file():
            print("copying file", file, "to", fmt_dir, "/", name)
            shutil.copy(file, fmt_dir / name)
        elif file.is_dir():
            print("copying dir", file, "to", fmt_dir, "/", name)
            shutil.copytree(file, fmt_dir / name, dirs_exist_ok=True)

    for content in [
        EXTRA_DIR,
        PLD_DIR,
        CONTENT_FOLDER,
        TABLE_DIR,
        MANEX_DIR,
        "metadata.yaml",
        "config.yaml",
        "CHANGELOG.md",
        "README.md",
    ]:
        src_dir = build_path / "src"
        target = source / output_dir / content
        if target.is_file():
            shutil.copy(target, src_dir / target.name)
            print("source file", target)
        elif target.is_dir():
            shutil.copytree(target, src_dir / target.name)
            print("source folder", target)
        else:
            print(f"Path not found: {target}")
        pass

    for fmt, files in contents.items():
        if len(files) == 1:
            _copy(files[0], build_path)
        else:
            fmt_dir = build_path / fmt
            fmt_dir.mkdir(exist_ok=True, parents=True)
            for file in files:
                _copy(file, fmt_dir)

    for _dir in build_path.iterdir():
        if _dir.is_dir() and not any(_dir.iterdir()):
            log.warning(
                f"Empty directory {_dir.resolve()}, not including in the archive."
            )
            _dir.rmdir()


#     info = json.loads(
#         subprocess.run(
#             ["mike", "list", "-j"],
#             universal_newlines=True,
#             check=True,
#             stdout=subprocess.PIPE,
#         ).stdout
#     )

#     for item in info:
#         version = item["version"]
#         if "dev" in version:
#             print(f"Deleting {version}")
#             subprocess.run(
#                 ["mike", "delete", version],
#                 universal_newlines=True,
#                 check=True,
#                 stdout=subprocess.PIPE,
#             )

#     subprocess.run(["mike", "deploy", "--push", "--update-aliases", current, "latest"])
#     subprocess.run(["mike", "set-default", "--push", "latest"])
# else:
#     subprocess.run(["mike", "deploy", current])
