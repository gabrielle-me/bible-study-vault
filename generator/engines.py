"""
Bible generation engine.

This module combines:

- Seed data (people, places, anchor events)
- Rule data (themes, recurring events)

into complete chapter metadata.

The engine is completely book-agnostic and works for every
book of the Bible.
"""

from typing import Any, Dict, List


# ==========================================================
# HELPERS
# ==========================================================

def unique(values: List[str]) -> List[str]:
    """
    Removes duplicates while preserving order.
    """
    return list(dict.fromkeys(values))


# ==========================================================
# RULE ENGINE
# ==========================================================

def apply_rules(chapter: int, rules: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Applies all rule ranges that include the given chapter.

    Example:

    Rule:
        chapters 1-11
            theme = creation

    Genesis 5

        -> creation
    """

    themes: List[str] = []
    events: List[str] = []

    for rule in rules.get("chapter_rules", []):

        start, end = rule["range"]

        if start <= chapter <= end:
            themes.extend(rule.get("themes", []))
            events.extend(rule.get("events", []))

    return {
        "themes": unique(themes),
        "events": unique(events),
    }


# ==========================================================
# SEED ENGINE
# ==========================================================

def build_chapter_map(seed: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    """
    Converts anchor points into chapter metadata.

    Example

        Chapter 1
            Adam
            Eve

        Chapter 5
            Noah

    becomes

        1-4 -> Adam, Eve
        5-...
    """

    chapters: Dict[int, Dict[str, Any]] = {}

    anchors = sorted(
        seed.get("anchors", []),
        key=lambda anchor: anchor["chapter"]
    )

    if not anchors:
        return chapters

    total = seed["chapters"]

    for index, anchor in enumerate(anchors):

        start = anchor["chapter"]

        if index + 1 < len(anchors):
            end = anchors[index + 1]["chapter"] - 1
        else:
            end = total

        for chapter in range(start, end + 1):

            chapters[chapter] = {
                "people": unique(anchor.get("people", [])),
                "places": unique(anchor.get("places", [])),
                "events": unique(
                    [anchor["event"]]
                ) if anchor.get("event") else [],
            }

    return chapters


# ==========================================================
# MERGE ENGINE
# ==========================================================

def build_chapter_data(
    chapter_number: int,
    seed: Dict[str, Any],
    rules: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Returns the complete metadata for a chapter.

    Combines

        Seed
            people
            places
            anchor events

    with

        Rules
            themes
            recurring events
    """

    chapter_map = build_chapter_map(seed)

    seed_data = chapter_map.get(
        chapter_number,
        {
            "people": [],
            "places": [],
            "events": [],
        },
    )

    rule_data = apply_rules(chapter_number, rules)

    return {
        "people": unique(seed_data["people"]),
        "places": unique(seed_data["places"]),
        "themes": unique(rule_data["themes"]),
        "events": unique(
            seed_data["events"] +
            rule_data["events"]
        ),
    }