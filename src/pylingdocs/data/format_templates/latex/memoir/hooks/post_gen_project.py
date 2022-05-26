import shutil
from pathlib import Path
from pylingdocs.config import DATA_DIR


latex_dir = Path.cwd().resolve()

shutil.copyfile(
    DATA_DIR / "format_templates/latex/shared_preamble.tex", latex_dir / "preamble.tex"
)
