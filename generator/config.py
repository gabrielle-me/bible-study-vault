import os
from pathlib import Path

# ==========================================================
# PROJECT PATHS
# ==========================================================

# generator/
GENERATOR_DIR = Path(__file__).resolve().parent

# Repository root
PROJECT_ROOT = GENERATOR_DIR.parent

# ==========================================================
# DATA
# ==========================================================

DATA_DIR = PROJECT_ROOT / "data"

BOOK_DIR = DATA_DIR / "books"
SEED_DIR = DATA_DIR / "seeds"
RULE_DIR = DATA_DIR / "rules"
ONTOLOGY_DIR = DATA_DIR / "ontology"
TRANSLATION_DIR = DATA_DIR / "translations"

# ==========================================================
# TEMPLATES
# ==========================================================

TEMPLATE_DIR = PROJECT_ROOT / "templates"

# ==========================================================
# GENERATED VAULT
# ==========================================================

OUTPUT_DIR = Path(
    os.environ.get(
        "BIBLE_VAULT_OUTPUT",
        PROJECT_ROOT / "dist" / "starter-vault",
    )
).expanduser().resolve()

MOC_DIR = OUTPUT_DIR / "MOCs"

# ==========================================================
# HELPERS
# ==========================================================

def ensure_directory(path: Path) -> Path:
    """
    Creates a directory if it does not already exist.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_testament_folder(book: dict) -> Path:
    """
    Returns the Testament folder for a book.
    """

    testament = book["testament"]

    if testament in ("OT", "NT"):
        return OUTPUT_DIR / testament

    raise ValueError(f"Unknown testament: {testament}")


def get_book_folder(book: dict) -> Path:
    """
    Returns the folder containing a book and its chapters.

    Example:

    OT/
        Genesis/
    """

    return get_testament_folder(book) / book["title"]