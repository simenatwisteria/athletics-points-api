"""Regeltolkningen (tests/fixtures/tyrving_rules.json) er velformet og peker på ekte kombinasjoner.

Motoren testes mot disse casene i AP-008, etter Simens review (AP-007).
"""

import json
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "tests" / "fixtures" / "tyrving_rules.json"
PARAMS = ROOT / "athletics_scoring" / "data" / "tyrving_parameters_2014.json"


@pytest.fixture(scope="module")
def rules() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(RULES.read_text(encoding="utf-8"))
    return data


@pytest.fixture(scope="module")
def entries() -> dict[tuple[Any, ...], dict[str, Any]]:
    data = json.loads(PARAMS.read_text(encoding="utf-8"))
    return {(e["event_id"], e["gender"], e["age"], e["implement"]): e for e in data["entries"]}


def test_case_ids_are_unique(rules: dict[str, Any]) -> None:
    ids = [c["id"] for c in rules["cases"]] + [q["id"] for q in rules["open_questions"]]
    assert len(ids) == len(set(ids))


def test_every_case_is_documented(rules: dict[str, Any]) -> None:
    levels = set(rules["meta"]["interpretation_levels"])
    for case in rules["cases"]:
        assert case["rule"] in rules["rules"], case["id"]
        assert case["interpretation"] in levels, case["id"]
        assert case["note"] and case["calculation"], case["id"]
        assert isinstance(case["points"], int) and case["points"] >= 0, case["id"]


def test_every_rule_has_cases(rules: dict[str, Any]) -> None:
    covered = {c["rule"] for c in rules["cases"]} | {q["rule"] for q in rules["open_questions"]}
    assert covered == set(rules["rules"])


def test_inputs_exist_and_match_measure(
    rules: dict[str, Any], entries: dict[tuple[Any, ...], dict[str, Any]]
) -> None:
    for case in rules["cases"]:
        given = case["input"]
        key = (given["event_id"], given["gender"], given["age"], given["implement"])
        assert key in entries, case["id"]
        measure = entries[key]["measure"]
        fields = set(given["result"])
        if measure == "distance":
            assert fields == {"distance_meters"}, case["id"]
        else:
            assert fields in ({"time_seconds"}, {"time_minutes", "time_seconds"}), case["id"]
        assert isinstance(given["manual_timing"], bool), case["id"]
