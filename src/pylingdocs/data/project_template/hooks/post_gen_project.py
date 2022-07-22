from pathlib import Path
import cookiecutter


PROJECT_DIR = Path.cwd().resolve()


def remove_file(filename):
    (PROJECT_DIR / filename).unlink()


def create_file(file, no=1):
    number = f"{no}000"
    filename = number + " " + file + ".md"
    with open((PROJECT_DIR / "content" / filename), "w") as f:
        f.write(f"# {file.capitalize()} [label](sec:{file})\n\nInsert content")


if "No license" == "{{ cookiecutter.license }}":
    remove_file("LICENSE")

for i, file in enumerate({{cookiecutter.files.split(",")}}):
    create_file(file, no=i + 1)
