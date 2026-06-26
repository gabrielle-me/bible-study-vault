from typing import Any, Dict, List


def apply_rules(chapter_num: int, rules: Dict[str, Any]) -> Dict[str, List[str]]:
    themes: List[str] = []
    events: List[str] = []

    for rule in rules.get("chapter_rules", []):
        start, end = rule["range"]

        if start <= chapter_num <= end:
            themes.extend(rule.get("themes", []))
            events.extend(rule.get("events", []))

    return {
        "themes": sorted(set(themes)),
        "events": sorted(set(events)),
    }


def build_chapter_map(seed: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    chapters: Dict[int, Dict[str, Any]] = {}
    anchors = sorted(seed.get("anchors", []), key=lambda item: item["chapter"])

    for index, anchor in enumerate(anchors):
        start = anchor["chapter"]
        end = (
            anchors[index + 1]["chapter"] - 1
            if index + 1 < len(anchors)
            else seed["chapters"]
        )

        for chapter_num in range(start, end + 1):
            chapters[chapter_num] = {
                "people": anchor.get("people", []),
                "places": anchor.get("places", []),
                "events": [anchor["event"]] if anchor.get("event") else [],
            }

    return chapters
