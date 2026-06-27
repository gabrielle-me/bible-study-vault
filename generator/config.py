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

OUTPUT_DIR = PROJECT_ROOT / "vault"

# Root files
HOME_FILE = OUTPUT_DIR / "Home.md"

# Main folders

OLD_TESTAMENT_DIR = OUTPUT_DIR / "02 Old Testament"
NEW_TESTAMENT_DIR = OUTPUT_DIR / "03 New Testament"

CHARACTER_DIR = OUTPUT_DIR / "04 Characters"
THEME_DIR = OUTPUT_DIR / "05 Themes"
PLACE_DIR = OUTPUT_DIR / "06 Places"
EVENT_DIR = OUTPUT_DIR / "07 Events"

STUDY_NOTES_DIR = OUTPUT_DIR / "08 Study Notes"

ATTACHMENT_DIR = OUTPUT_DIR / "09 Attachments"

# ==========================================================
# BOOK GROUPS
# ==========================================================

BOOK_GROUPS = {
    "Pentateuch": "Pentateuch",
    "Historical Books": "Historical Books",
    "Wisdom": "Wisdom",
    "Major Prophets": "Major Prophets",
    "Minor Prophets": "Minor Prophets",
    "Gospels": "Gospels",
    "History": "History",
    "Pauline Epistles": "Pauline Epistles",
    "General Epistles": "General Epistles",
    "Apocalypse": "Apocalypse",
}


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

    if testament == "OT":
        return OLD_TESTAMENT_DIR

    if testament == "NT":
        return NEW_TESTAMENT_DIR

    raise ValueError(f"Unknown testament: {testament}")


def get_book_folder(book: dict) -> Path:
    """
    Returns the folder containing a book and its chapters.

    Example:

    02 Old Testament/
        Pentateuch/
            Genesis/
    """

    testament = get_testament_folder(book)

    group = book["group"]

    return testament / group / book["title"]