import json
from typing import Any, Dict

try:
    from .config import DATA_DIR
except ImportError:  # pragma: no cover - allows direct script execution
    from config import DATA_DIR


class Translator:
    def __init__(self) -> None:
        with open(DATA_DIR / "config.json", encoding="utf-8") as handle:
            self.config: Dict[str, Any] = json.load(handle)

        with open(DATA_DIR / "translations" / "en.json", encoding="utf-8") as handle:
            self.en: Dict[str, Any] = json.load(handle)

        with open(DATA_DIR / "translations" / "de.json", encoding="utf-8") as handle:
            self.de: Dict[str, Any] = json.load(handle)

        self.language = self.config["language"]

    def translate(self, category: str, key: str) -> str:
        en = self.en[category].get(key, key)
        de = self.de[category].get(key, key)

        if self.language == "en":
            return en

        if self.language == "de":
            return de

        return f"{en} - {de}"


translator = Translator()