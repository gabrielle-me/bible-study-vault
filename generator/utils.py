from pathlib import Path


def normalize_book_name(name: str) -> str:
    """
    Converts a book title into its canonical filename.

    Example:
        Genesis -> genesis
    """
    return name.strip().lower()


def ensure_list(value):
    """
    Returns a list.

    None becomes [].
    """

    if value is None:
        return []

    return value


def unique(values):
    """
    Removes duplicates while preserving order.
    """

    return list(dict.fromkeys(values))


def write_text(path: Path, content: str):
    """
    Writes UTF-8 text, creating folders if necessary.
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        content,
        encoding="utf-8",
    )