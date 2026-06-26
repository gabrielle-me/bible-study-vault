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
