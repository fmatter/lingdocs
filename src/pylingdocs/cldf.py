from pathlib import Path
import pycldf
from clldutils import jsonlib
from pycldf.dataset import SchemaError
from pylingdocs.config import DATA_DIR
from pylingdocs.models import models


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
    menu_data = {}
    for model in models:
        menu_data[model.name] = []
        try:
            for row in ds.iter_rows(model.cldf_table):
                menu_data[model.name].append(
                    {"id": row["ID"], "content": model.autocomplete_string(row)}
                )
                autocomplete_data.append(model.autocomplete_string(row))
        except SchemaError:
            del menu_data[model.name]
    menu_data["Source"] = []
    for src in ds.sources:
        menu_data["Source"].append(
            {"id": src.id, "content": [str(src), f"[src]({src.id})"]}
        )
        autocomplete_data.append([f"src:{src.id} {str(src)}", f"[src]({src.id})"])
        autocomplete_data.append([f"psrc:{src.id} {str(src)}", f"[psrc]({src.id})"])
    jsonlib.dump(autocomplete_data, output_dir / ".pld_autocomplete.json", indent=4)
    jsonlib.dump(menu_data, output_dir / ".pld_menudata.json", indent=4)
