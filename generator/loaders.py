import json
from pathlib import Path
from typing import Any, Dict, List

try:
    from .config import DATA_DIR
    from .utils import normalize_book_name
except ImportError:  # pragma: no cover - allows direct script execution
    from config import DATA_DIR
    from utils import normalize_book_name


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_book_catalog() -> List[Dict[str, Any]]:
    catalog_path = DATA_DIR / "books" / "books.json"
    catalog = load_json(catalog_path)
    if not isinstance(catalog, list):
        raise ValueError("The book catalog must be a JSON list.")
    return catalog


def load_book(book_id: str) -> Dict[str, Any]:
    catalog = load_book_catalog()

    for entry in catalog:
        if entry.get("id") != book_id:
            continue

        book_file = entry.get("file")
        if not book_file:
            raise ValueError(f"Book entry {book_id} is missing a file reference.")

        book_path = DATA_DIR / "books" / book_file
        if not book_path.exists():
            return dict(entry)

        book_data = load_json(book_path)
        if not isinstance(book_data, dict):
            raise ValueError(f"Book data for {book_id} must be a JSON object.")

        merged_book = dict(entry)
        merged_book.update(book_data)
        return merged_book

    raise KeyError(f"Book not found in catalog: {book_id}")


def load_seed(book: str) -> Dict[str, Any]:
    seed_path = DATA_DIR / "seeds" / f"{normalize_book_name(book)}_seed.json"
    return load_json(seed_path)


def load_rules(book: str) -> Dict[str, Any]:
    rules_path = DATA_DIR / "rules" / f"{normalize_book_name(book)}_rules.json"
    return load_json(rules_path)
