from clldutils import jsonlib
from pylingdocs.config import DATA_DIR


def get_metadata(table_name):
    return jsonlib.load(DATA_DIR / "cldf" / f"{table_name}-metadata.json")
