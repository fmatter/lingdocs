import logging
import sys
import jinja2
from pathlib import Path
import keepachangelog
from writio import dump, load
import re
import shutil

from pylingdocs.config import config, DATA_DIR

log = logging.getLogger(__name__)


def bump_version(version, step="patch"):
    # print(version)
    # print(step)
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


def release(source, cldf, output_dir, bump):
    print(source)
    config.load_from_dir(source)
    metadata = load(source / "metadata.yaml")
    if config["output"]["changelog"]:
        release_changelog(metadata)
    metadata["version"] = bump_version(metadata["version"], bump)
    dump(metadata, source / "metadata.yaml")

    def _dedict(file):
        if isinstance(file, dict):
            name = list(file.values())[0]
            file = list(file.keys())[0]
        else:
            name = Path(file).name
        return file, name

    contents = {"cldf": []}
    build_path = Path(output_dir / "build")
    build_path.mkdir(exist_ok=True, parents=True)
    for fmt, target in config["releasing"]["zip"].items():
        if fmt == "cldf":
            if target is True:
                contents["cldf"].append(output_dir / fmt)
        else:
            fmt_path = output_dir / fmt
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
                fmt, target = _dedict(target)
                for f in fmt_path.iterdir():
                    if f.is_file():
                        if f.suffix == "." + target or f.name == target:
                            print("success, file", f)
                            contents.setdefault(fmt, [])
                            contents[fmt].append({f: rename})
                    else:
                        if f.name == target:
                            print("success folder", f)
                            contents.setdefault(fmt, [])
                            contents[fmt].append(({f: rename}))

    def _copy(file, fmt_dir):
        file, name = _dedict(file)
        if file.is_file():
            print("copying file", file, "to", fmt_dir, "/", name)
            shutil.copy(file, fmt_dir / name)
        elif file.is_dir():
            print("copying dir", file, "to", fmt_dir, "/", name)
            shutil.copytree(file, fmt_dir / name, dirs_exist_ok=True)

    for fmt, files in contents.items():
        if len(files) == 1:
            print(files[0])
            _copy(files[0], build_path)
        else:
            fmt_dir = build_path / fmt
            fmt_dir.mkdir(exist_ok=True, parents=True)
            for file in files:
                print(file)
                _copy(file, fmt_dir)


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
