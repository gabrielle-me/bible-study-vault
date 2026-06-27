"""
Bible Study Vault Generator

Entry point for generating the Obsidian vault.
"""

try:
    from .builders import (
        build_books,
        build_chapters,
    )

    from .loaders import (
        load_book_catalog,
    )

except ImportError:  # Allows direct execution

    from builders import (
        build_books,
        build_chapters,
    )

    from loaders import (
        load_book_catalog,
    )


# ==========================================================
# Chapter Builder
# ==========================================================

def build_all_chapters(catalog):
    """
    Generates every chapter in the catalog.
    """

    for book in catalog:

        try:

            build_chapters(book["id"])

        except Exception as exc:

            print(
                f"\n❌ ERROR generating {book['title']}"
            )

            print(exc)
            print()


# ==========================================================
# Main
# ==========================================================

def main():

    print("\n====================================")
    print(" Bible Study Vault Generator")
    print("====================================\n")

    catalog = load_book_catalog()

    print("Generating books...\n")
    build_books()

    print("\nGenerating chapters...\n")
    build_all_chapters(catalog)

    print("\n====================================")
    print(" Generation complete!")
    print("====================================\n")


if __name__ == "__main__":
    main()