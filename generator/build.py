try:
    from .builders import build_books, build_chapters
    from .loaders import load_book, load_book_catalog
except ImportError:  # pragma: no cover - allows direct script execution
    from builders import build_books, build_chapters
    from loaders import load_book, load_book_catalog


def build_all_books(catalog=None):
    catalog = catalog or load_book_catalog()

    for entry in catalog:
        try:
            build_chapters(entry["id"])
        except Exception as exc:
            print(f"\n❌ ERROR generating {entry['title']}")
            print(exc)
            print()

    return catalog


def main():
    catalog = load_book_catalog()
    build_books(catalog)
    build_all_books(catalog)


if __name__ == "__main__":
    main()