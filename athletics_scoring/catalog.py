"""Felles øvelseskatalog: engelske navn og menygruppe per ``event_id``.

Data: ``data/event_catalog.json``.
"""

import json
from dataclasses import dataclass
from functools import cache
from importlib import resources
from typing import Literal

type Category = Literal["run", "hurdles", "racewalk", "jump", "throw"]


@dataclass(frozen=True, slots=True)
class CatalogEntry:
    event_id: str
    name_no: str
    name_en: str
    category: Category


@cache
def event_catalog() -> dict[str, CatalogEntry]:
    """Alle øvelsene som noen motor tilbyr, med ``event_id`` som nøkkel."""
    path = resources.files("athletics_scoring").joinpath("data", "event_catalog.json")
    text = path.read_text("utf-8")
    events: dict[str, dict[str, str]] = json.loads(text)["events"]
    return {
        event_id: CatalogEntry(
            event_id,
            e["name_no"],
            e["name_en"],
            e["category"],  # type: ignore[arg-type]
        )
        for event_id, e in events.items()
    }
