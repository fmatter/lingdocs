from pathlib import Path
import pycldf
from clldutils import jsonlib
from pylingdocs.config import DATA_DIR


def metadata(table_name):
    path = DATA_DIR / "cldf" / f"{table_name}-metadata.json"
    if not path.is_file():
        path = (
            Path(pycldf.__file__).resolve().parent
            / "components"
            / f"{table_name}-metadata.json"
        )
    return jsonlib.load(path)
