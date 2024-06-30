from lingdocs.config import (
    CONTENT_FOLDER,
    DATA_DIR,
    EXTRA_DIR,
    FIGURE_DIR,
    STRUCTURE_FILE,
    TABLE_DIR,
    config,
)
from pathlib import Path
import yaml


def load_table_metadata(source_dir):
    table_md = Path(source_dir) / TABLE_DIR / "metadata.yaml"
    if table_md.is_file():
        with open(table_md, encoding="utf-8") as f:
            tables = yaml.load(f, Loader=yaml.SafeLoader)
    else:
        log.warning(f"Inexistent table metadata file: {table_md}")
        tables = {}
    return tables
