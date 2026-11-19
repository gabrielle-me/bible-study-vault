from pathlib import Path
import re

try:
    from .config import (
        BOOK_DIR,
        DATA_DIR,
        MOC_DIR,
        OUTPUT_DIR,
        get_book_folder,
        ensure_directory,
    )

    from .loaders import (
        load_book,
        load_book_catalog,
        load_events,
        load_people,
        load_places,
        load_seed,
        load_rules,
        load_themes,
        load_translation,
    )

    from .engines import build_chapter_data

except ImportError:
    from config import (
        BOOK_DIR,
        DATA_DIR,
        MOC_DIR,
        OUTPUT_DIR,
        get_book_folder,
        ensure_directory,
    )

    from loaders import (
        load_book,
        load_book_catalog,
        load_events,
        load_people,
        load_places,
        load_seed,
        load_rules,
        load_themes,
        load_translation,
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

    output_folder = get_book_folder(book)

    ensure_directory(output_folder)

    data = dict(book)

    data.setdefault("chapters", 0)
    data.setdefault("people", [])
    data.setdefault("places", [])
    data.setdefault("themes", [])
    data.setdefault("key_events", [])
    ontology = {
        "people": load_people(),
        "places": load_places(),
        "themes": load_themes(),
        "events": load_events(),
    }
    translation = load_translation("en")
    data["theme_links"] = [
        _entity_label("themes", value, ontology["themes"], translation)
        for value in data["themes"]
    ]
    data["people_links"] = [
        _entity_label("people", value, ontology["people"], translation)
        for value in data["people"]
    ]
    data["place_links"] = [
        _entity_label("places", value, ontology["places"], translation)
        for value in data["places"]
    ]
    data["event_links"] = [
        _entity_label("events", value, ontology["events"], translation)
        for value in data["key_events"]
    ]

    output = templates.get("book").render(**data)

    write_markdown(
        output_folder /
        f"{book['title']}.md",
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
    ontology = {
        "people": load_people(),
        "places": load_places(),
        "themes": load_themes(),
        "events": load_events(),
    }
    translation = load_translation("en")

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
        }
        chapter["theme_links"] = [
            _entity_label("themes", value, ontology["themes"], translation)
            for value in metadata["themes"]
        ]
        chapter["people_links"] = [
            _entity_label("people", value, ontology["people"], translation)
            for value in metadata["people"]
        ]
        chapter["place_links"] = [
            _entity_label("places", value, ontology["places"], translation)
            for value in metadata["places"]
        ]
        chapter["event_links"] = [
            _entity_label("events", value, ontology["events"], translation)
            for value in metadata["events"]
        ]

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

def available_books():
    books = []

    for entry in load_book_catalog():
        book_path = BOOK_DIR / entry["file"]
        seed_path = DATA_DIR / "seeds" / f"{entry['title'].lower()}_seed.json"
        rules_path = DATA_DIR / "rules" / f"{entry['title'].lower()}_rules.json"

        if book_path.exists() and seed_path.exists() and rules_path.exists():
            books.append(load_book(entry["id"]))

    return books


def _entity_key(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("_", " ").strip()).casefold()


def _title_label(value: str) -> str:
    small_words = {"a", "an", "and", "as", "of", "the", "in", "on", "to"}
    words = value.replace("_", " ").split()
    return " ".join(
        word.casefold() if index and word.casefold() in small_words else word.capitalize()
        for index, word in enumerate(words)
    )


def _entity_label(category: str, value: str, ontology: dict, translation: dict) -> str:
    entry = ontology.get(value)
    if entry is None:
        entry = next(
            (
                entity
                for key, entity in ontology.items()
                if _entity_key(key) == _entity_key(value)
            ),
            None,
        )
    if isinstance(entry, dict) and entry.get("display"):
        return entry["display"]
    if category in ("themes", "events"):
        label = translation.get(category, {}).get(value)
        if label:
            return label
    if "_" in value:
        return _title_label(value)
    return value


def _add_reference(index: dict, category: str, value: str, reference: str, ontology: dict, translation: dict) -> None:
    key = _entity_key(value)
    item = index[category].setdefault(
        key,
        {
            "label": _entity_label(category, value, ontology[category], translation),
            "references": set(),
        },
    )
    item["references"].add(reference)


def build_mocs(books: list[dict]) -> None:
    ensure_directory(MOC_DIR)
    ontology = {
        "people": load_people(),
        "places": load_places(),
        "themes": load_themes(),
        "events": load_events(),
    }
    translation = load_translation("en")
    index = {category: {} for category in ontology}
    testament_sections = {"OT": [], "NT": []}

    for book in books:
        testament = book["testament"]
        book_link = f"{testament}/{book['title']}/{book['title']}"
        testament_sections[testament].append(
            {"label": book["title"], "link": book_link}
        )
        reference = f"[[{book_link}|{book['title']}]]"

        for category in index:
            book_values = (
                book.get("key_events", [])
                if category == "events"
                else book.get(category, [])
            )
            for value in book_values:
                _add_reference(index, category, value, reference, ontology, translation)

        seed = load_seed(book["title"])
        rules = load_rules(book["title"])
        for chapter_number in range(1, seed["chapters"] + 1):
            metadata = build_chapter_data(chapter_number, seed, rules)
            chapter_link = f"{testament}/{book['title']}/{book['title']} {chapter_number}"
            chapter_reference = f"[[{chapter_link}|{book['title']} {chapter_number}]]"
            for category in index:
                for value in metadata[category]:
                    _add_reference(
                        index,
                        category,
                        value,
                        chapter_reference,
                        ontology,
                        translation,
                    )

    book_sections = [
        {
            "title": title,
            "items": sorted(testament_sections[testament], key=lambda item: item["label"]),
        }
        for testament, title in (("OT", "Old Testament"), ("NT", "New Testament"))
    ]
    _write_moc("Books MOC", book_sections)

    for category, title in (
        ("themes", "Themes"),
        ("people", "Characters"),
        ("places", "Places"),
        ("events", "Events"),
    ):
        items = []
        for item in index[category].values():
            items.append(
                {
                    "label": item["label"],
                    "references": sorted(item["references"]),
                }
            )
        items.sort(key=lambda item: item["label"].casefold())
        _write_moc(
            f"{title} MOC",
            [{"title": title, "items": items}],
        )


def _write_moc(title: str, sections: list[dict]) -> None:
    output = templates.get("moc").render(title=title, sections=sections)
    write_markdown(MOC_DIR / f"{title}.md", output)


def build_starter_vault() -> list[dict]:
    ensure_directory(OUTPUT_DIR)
    books = available_books()

    for book in books:
        build_book(book)
        build_chapters(book["id"])

    build_mocs(books)
    readme = templates.get("starter_readme").render()
    write_markdown(OUTPUT_DIR / "README.md", readme)
    print(f"Starter vault generated at {OUTPUT_DIR}")
    return books


def build_books():
    books = available_books()
    for book in books:
        build_book(book)
    return books