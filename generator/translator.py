from typing import Any, Dict

try:
    from .loaders import (
        load_config,
        load_translation,
    )
except ImportError:  # Allows direct execution
    from loaders import (
        load_config,
        load_translation,
    )


class Translator:
    """
    Handles translation of ontology IDs into
    human-readable names.

    Supported languages:

        en
        de
        bilingual
    """

    def __init__(self) -> None:

        self.config: Dict[str, Any] = load_config()

        self.en: Dict[str, Any] = load_translation("en")
        self.de: Dict[str, Any] = load_translation("de")

        self.language = self.config.get(
            "language",
            "bilingual"
        )

    # ======================================================
    # Generic translator
    # ======================================================

    def translate(self, category: str, key: str) -> str:
        """
        Translates one ontology ID.

        Example

            translate("themes", "creation")
        """

        en = self.en.get(category, {}).get(key, key)
        de = self.de.get(category, {}).get(key, key)

        if self.language == "en":
            return en

        if self.language == "de":
            return de

        return f"{en} - {de}"

    # ======================================================
    # Convenience wrappers
    # ======================================================

    def person(self, key: str) -> str:
        return self.translate("people", key)

    def place(self, key: str) -> str:
        return self.translate("places", key)

    def theme(self, key: str) -> str:
        return self.translate("themes", key)

    def event(self, key: str) -> str:
        return self.translate("events", key)

    def book(self, key: str) -> str:
        return self.translate("books", key)


translator = Translator()