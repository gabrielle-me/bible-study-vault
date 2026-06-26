def normalize_book_name(name: str) -> str:
    """Machine-readable name."""
    return name.strip().lower()


def display_name(name: str) -> str:
    """Human-readable name."""
    return name.strip().title()
