from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = PROJECT_ROOT / "vault"


def ensure_output_dir(path: Optional[Path] = None) -> Path:
    target = path or OUTPUT_DIR
    target.mkdir(parents=True, exist_ok=True)
    return target