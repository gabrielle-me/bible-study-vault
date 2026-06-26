import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

# ----------------------------
# TRANSLATION
# ----------------------------

class Translator:

    def __init__(self):

        with open(DATA_DIR / "config.json", encoding="utf-8") as f:
            self.config = json.load(f)

        with open(DATA_DIR / "translations" / "en.json", encoding="utf-8") as f:
            self.en = json.load(f)

        with open(DATA_DIR / "translations" / "de.json", encoding="utf-8") as f:
            self.de = json.load(f)

        self.language = self.config["language"]

    def translate(self, category: str, key: str):

        en = self.en[category].get(key, key)
        de = self.de[category].get(key, key)

        if self.language == "en":
            return en

        if self.language == "de":
            return de

        return f"{en} - {de}"


translator = Translator()

# ----------------------------
# NAMING
# ----------------------------
def normalize_book_name(name: str) -> str:
    """Machine-readable name."""
    return name.strip().lower()


def display_name(name: str) -> str:
    """Human-readable name."""
    return name.strip().title()
