from pathlib import Path

from jinja2 import Environment, FileSystemLoader

try:
    from .config import (
        TEMPLATE_DIR,
        get_book_folder,
        get_testament_folder,
        ensure_directory,
    )

    from .loaders import (
        load_book,
        load_book_catalog,
        load_seed,
        load_rules,
    )

    from .engines import build_chapter_data

except ImportError:
    from config import (
        TEMPLATE_DIR,
        get_book_folder,
        get_testament_folder,
        ensure_directory,
    )

    from loaders import (
        load_book,
        load_book_catalog,
        load_seed,
        load_rules,
    )

    from engines import build_chapter_data


# ==========================================================
# Templates
# ==========================================================

try:
    from .template_manager import templates
except ImportError:
    from template_manager import templates

# ==========================================================
# Helpers
# ==========================================================

def write_markdown(path: Path, content: str):

    ensure_directory(path.parent)

    path.write_text(
        content,
        encoding="utf-8",
    )


# ==========================================================
# Book Builder
# ==========================================================

def build_book(book: dict):

    output_folder = (
        get_testament_folder(book)
        / book["group"]
    )

    ensure_directory(output_folder)

    data = dict(book)

    data.setdefault("chapters", 0)
    data.setdefault("people", [])
    data.setdefault("places", [])
    data.setdefault("themes", [])
    data.setdefault("key_events", [])

    data["user_notes_link"] = (
        f"{book['title']} - Notes"
    )

    output = templates.get("book").render(**data)

    write_markdown(
        output_folder /
        f"{book['title']} - {book['title_de']}.md",
        output,
    )

    print(f"Generated {book['title']}")


# ==========================================================
# Chapter Builder
# ==========================================================

def build_chapters(book_id: str):

    book = load_book(book_id)

    seed = load_seed(book["title"])

    rules = load_rules(book["title"])

    chapter_folder = get_book_folder(book)

    ensure_directory(chapter_folder)

    for chapter_number in range(
        1,
        seed["chapters"] + 1,
    ):

        metadata = build_chapter_data(
            chapter_number,
            seed,
            rules,
        )

        chapter = {
            "book": book["title"],

            "chapter": chapter_number,

            "title": (
                f"{book['title']} "
                f"{chapter_number}"
            ),

            "people": metadata["people"],

            "places": metadata["places"],

            "themes": metadata["themes"],

            "events": metadata["events"],

            "cross_references": [],

            "user_notes_link":
                f"{book['title']} {chapter_number}",
        }

        output = templates.get("chapter").render(**chapter)

        write_markdown(

            chapter_folder /
            f"{book['title']} {chapter_number}.md",

            output,
        )

    print(
        f"Generated {book['title']} chapters"
    )


# ==========================================================
# Full Builder
# ==========================================================

def build_books():

    catalog = load_book_catalog()

    for entry in catalog:

        build_book(
            load_book(entry["id"])
        )

    return catalog