"""
Template Manager

Centralizes all Jinja templates used to generate the vault.
"""

from jinja2 import Environment, FileSystemLoader

try:
    from .config import TEMPLATE_DIR
except ImportError:
    from config import TEMPLATE_DIR


class TemplateManager:

    def __init__(self):

        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR))
        )

        self._cache = {}

    def get(self, template_name: str):
        """
        Returns a cached template.

        Example

            templates.get("book")

        loads

            book.md.j2
        """

        if template_name not in self._cache:

            self._cache[template_name] = self.env.get_template(
                f"{template_name}.md.j2"
            )

        return self._cache[template_name]


templates = TemplateManager()