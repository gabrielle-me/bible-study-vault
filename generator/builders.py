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

