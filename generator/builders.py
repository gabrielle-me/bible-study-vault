from jinja2 import Environment, FileSystemLoader

try:
    from .config import OUTPUT_DIR, TEMPLATE_DIR
    from .engines import apply_rules, build_chapter_map
    from .loaders import load_book, load_book_catalog, load_rules, load_seed
    from .utils import display_name, normalize_book_name
except ImportError:  # pragma: no cover - allows direct script execution
    from config import OUTPUT_DIR, TEMPLATE_DIR
    from engines import apply_rules, build_chapter_map
    from loaders import load_book, load_book_catalog, load_rules, load_seed
    from utils import display_name, normalize_book_name


env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
book_template = env.get_template("book.md.j2")
chapter_template = env.get_template("chapter.md.j2")


def build_books(catalog=None):
    catalog = catalog or load_book_catalog()

    for entry in catalog:
        book = load_book(entry["id"])
        book_data = dict(book)
        book_data.setdefault("chapters", 0)
        book_data.setdefault("themes", [])
        book_data.setdefault("characters", [])
        book_data.setdefault("places", [])
        book_data["user_notes_link"] = f"{book_data['title']} - Notes.md"

        output = book_template.render(**book_data)

        path = OUTPUT_DIR / "01 Books" / f"{book_data['title']}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")

        print(f"Generated book {book_data['title']}")

    return catalog


def build_chapters(book_id: str):
    book = load_book(book_id)
    machine_name = normalize_book_name(book["title"])
    human_name = display_name(book["title"])

    seed = load_seed(book["title"])
    rules = load_rules(book["title"])

    chapter_map = build_chapter_map(seed)

    for chapter_num in range(1, seed["chapters"] + 1):
        data = chapter_map.get(
            chapter_num,
            {"people": [], "places": [], "events": []},
        )

        rule_data = apply_rules(chapter_num, rules)

        chapter = {
            "book": human_name,
            "chapter": chapter_num,
            "title": f"{human_name} {chapter_num}",
            "people": data["people"],
            "places": data["places"],
            "themes": rule_data["themes"],
            "events": sorted(set(data["events"] + rule_data["events"])),
            "cross_references": [],
            "user_notes_link": f"{human_name} {chapter_num} - Notes.md",
        }

        output = chapter_template.render(**chapter)

        path = OUTPUT_DIR / "02 Chapters" / f"{human_name} {chapter_num}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")

        print(f"Generated chapter {human_name} {chapter_num}")

    return None

