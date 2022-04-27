from pathlib import Path
import pycldf
from clldutils import jsonlib
from pycldf import Dataset
from pycldf.dataset import SchemaError
from pylingdocs.config import DATA_DIR
from pylingdocs.models import models


ds = Dataset.from_metadata(
    "/home/florianm/Dropbox/research/cariban/yawarana/yaw_cldf/cldf/metadata.json"
)


def metadata(table_name):
    path = DATA_DIR / "cldf" / f"{table_name}-metadata.json"
    if not path.is_file():
        path = (
            Path(pycldf.__file__).resolve().parent
            / "components"
            / f"{table_name}-metadata.json"
        )
    return jsonlib.load(path)


def generate_autocomplete(ds, output_dir):
    output_dir = Path(output_dir)
    autocomplete_data = []
    for model in models:
        try:
            for row in ds.iter_rows(model.cldf_table):
                autocomplete_data.append(model.autocomplete_string(row))
        except SchemaError:
            pass

    jsonlib.dump(autocomplete_data, output_dir / ".pld_autocomplete.json", indent=4)
