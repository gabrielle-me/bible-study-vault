import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# ----------------------------
# PATHS
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "vault"

# ----------------------------
# TEMPLATES
# ----------------------------
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

book_template = env.get_template("book.md.j2")
chapter_template = env.get_template("chapter.md.j2")
book_moc_template = env.get_template("book_moc.md.j2")


# ----------------------------
# NAMING
# ----------------------------
def normalize_book_name(name: str) -> str:
    """Machine-readable name."""
    return name.strip().lower()


def display_name(name: str) -> str:
    """Human-readable name."""
    return name.strip().title()


# ----------------------------
# LOADERS
# ----------------------------
def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_books():
    path = DATA_DIR / "books"
    return [load_json(f) for f in path.glob("*.json")]


def load_seed(book: str):
    path = DATA_DIR / "seeds" / f"{normalize_book_name(book)}_seed.json"
    return load_json(path)


def load_rules(book: str):
    path = DATA_DIR / "rules" / f"{normalize_book_name(book)}_rules.json"
    return load_json(path)


# ----------------------------
# RULE ENGINE
# ----------------------------
def apply_rules(chapter_num, rules):
    themes = []
    events = []

    for rule in rules["chapter_rules"]:
        start, end = rule["range"]

        if start <= chapter_num <= end:
            themes.extend(rule.get("themes", []))
            events.extend(rule.get("events", []))

    return {
        "themes": sorted(set(themes)),
        "events": sorted(set(events))
    }


# ----------------------------
# SEED ENGINE
# ----------------------------
def build_chapter_map(seed):
    chapters = {}

    anchors = sorted(seed["anchors"], key=lambda x: x["chapter"])

    for i, anchor in enumerate(anchors):
        start = anchor["chapter"]
        end = (
            anchors[i + 1]["chapter"] - 1
            if i + 1 < len(anchors)
            else seed["chapters"]
        )

        for c in range(start, end + 1):
            chapters[c] = {
                "people": anchor.get("people", []),
                "places": anchor.get("places", []),
                "events": [anchor["event"]] if anchor.get("event") else []
            }

    return chapters


# ----------------------------
# BOOK BUILDERS
# ----------------------------
def build_books():
    books = load_books()

    for book in books:
        book["user_notes_link"] = f"{book['title']} - Notes.md"

        output = book_template.render(**book)

        path = OUTPUT_DIR / f"{book['title']} - {book['title_de']}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")

        print(f"Generated book {book['title']}")


def build_book_moc(book):
    output = book_moc_template.render(**book)

    path = OUTPUT_DIR / "01 Books" / f"{book['title']}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="utf-8")

    print(f"Generated MOC {book['title']}")


# ----------------------------
# CHAPTER BUILDER
# ----------------------------
def build_chapters(book_name: str):

    machine_name = normalize_book_name(book_name)
    human_name = display_name(book_name)

    seed = load_seed(machine_name)
    rules = load_rules(machine_name)

    chapter_map = build_chapter_map(seed)

    for chapter_num in range(1, seed["chapters"] + 1):

        data = chapter_map.get(chapter_num, {
            "people": [],
            "places": [],
            "events": []
        })

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

            "user_notes_link": f"{human_name} {chapter_num} - Notes.md"
        }

        output = chapter_template.render(**chapter)

        path = OUTPUT_DIR / "02 Chapters" / f"{human_name} {chapter_num}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")

        print(f"Generated chapter {human_name} {chapter_num}")


# ----------------------------
# PIPELINE
# ----------------------------
def build_all_books():
    books = load_books()

    for book in books:
        machine_name = normalize_book_name(book["title"])

        try:
            build_chapters(machine_name)
        except Exception as e:
            print(f"\n❌ ERROR generating {book['title']}")
            print(e)
            print()


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":

    books = load_books()

    for book in books:
        book["user_notes_link"] = f"{book['title']} - Notes.md"

        output = book_template.render(**book)

        path = OUTPUT_DIR / f"{book['title']} - {book['title_de']}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")

        build_book_moc(book)

    build_all_books()