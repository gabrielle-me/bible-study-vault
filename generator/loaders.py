import json
from pathlib import Path
from typing import Any, Dict, List

try:
    from .config import (
        DATA_DIR,
        BOOK_DIR,
        SEED_DIR,
        RULE_DIR,
        ONTOLOGY_DIR,
        TRANSLATION_DIR,
    )
    from .utils import normalize_book_name
except ImportError:  # Allows direct execution
    from config import (
        DATA_DIR,
        BOOK_DIR,
        SEED_DIR,
        RULE_DIR,
        ONTOLOGY_DIR,
        TRANSLATION_DIR,
    )
    from utils import normalize_book_name


# ==========================================================
# Generic JSON Loader
# ==========================================================

def load_json(path: Path) -> Any:
    """
    Loads a JSON file and returns its contents.
    """
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


# ==========================================================
# Configuration
# ==========================================================

def load_config() -> Dict[str, Any]:
    """
    Loads the global project configuration.
    """
    return load_json(DATA_DIR / "config.json")


# ==========================================================
# Book Catalog
# ==========================================================

def load_book_catalog() -> List[Dict[str, Any]]:
    """
    Loads the canonical list of Bible books.
    """
    catalog_path = BOOK_DIR / "books.json"

    catalog = load_json(catalog_path)

    if not isinstance(catalog, list):
        raise ValueError("books.json must contain a JSON list.")

    return catalog


def load_book(book_id: str) -> Dict[str, Any]:
    """
    Loads a complete book by ID.

    Metadata comes from books.json.

    Additional information comes from
    data/books/<book>.json
    """

    catalog = load_book_catalog()

    for entry in catalog:

        if entry["id"] != book_id:
            continue

        book_file = entry.get("file")

        if not book_file:
            raise ValueError(
                f"Book {book_id} has no file assigned."
            )

        book_path = BOOK_DIR / book_file

        if not book_path.exists():
            return dict(entry)

        book_data = load_json(book_path)

        if not isinstance(book_data, dict):
            raise ValueError(
                f"{book_file} must contain a JSON object."
            )

        merged = dict(entry)
        merged.update(book_data)

        return merged

    raise KeyError(f"Unknown book ID: {book_id}")


# ==========================================================
# Seeds & Rules
# ==========================================================

def load_seed(book: str) -> Dict[str, Any]:
    """
    Loads the seed file for a book.
    """

    filename = f"{normalize_book_name(book)}_seed.json"

    return load_json(SEED_DIR / filename)


def load_rules(book: str) -> Dict[str, Any]:
    """
    Loads the rule file for a book.
    """

    filename = f"{normalize_book_name(book)}_rules.json"

    return load_json(RULE_DIR / filename)


# ==========================================================
# Ontology
# ==========================================================

def load_ontology(name: str) -> Dict[str, Any]:
    """
    Loads one ontology.

    Examples:

        load_ontology("people")

        load_ontology("places")

        load_ontology("themes")

        load_ontology("events")
    """

    return load_json(
        ONTOLOGY_DIR / f"{name}.json"
    )


def load_people():
    return load_ontology("people")


def load_places():
    return load_ontology("places")


def load_themes():
    return load_ontology("themes")


def load_events():
    return load_ontology("events")


# ==========================================================
# Translations
# ==========================================================

def load_translation(language: str) -> Dict[str, Any]:
    """
    Loads a translation file.

    Example:

        load_translation("en")

        load_translation("de")
    """

    return load_json(
        TRANSLATION_DIR / f"{language}.json"
    )