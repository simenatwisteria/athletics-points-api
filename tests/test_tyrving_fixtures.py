"""Tyrving-fasiten (tests/fixtures/tyrving_cases.json) er komplett, sporbar og oppdatert.

Testene her sjekker fasiten, ikke motoren. Motoren testes mot fasiten i AP-008.
"""

import hashlib
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "tests" / "fixtures" / "tyrving_cases.json"
PARAMS = ROOT / "athletics_scoring" / "data" / "tyrving_parameters_2014.json"

# Caser der regnearket har en flyttallsfeil i nedrundingen (docs/KILDEAVVIK.md).
EXPECTED_FLOAT_EDGES = {("Jenter 11 år", 16)}


@pytest.fixture(scope="module")
def fixture() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(CASES.read_text(encoding="utf-8"))
    return data


@pytest.fixture(scope="module")
def params() -> dict[tuple[str, int], dict[str, Any]]:
    entries = json.loads(PARAMS.read_text(encoding="utf-8"))["entries"]
    return {(e["source"]["sheet"], e["source"]["row"]): e for e in entries}


def test_meta(fixture: dict[str, Any]) -> None:
    meta = fixture["meta"]
    source = ROOT / meta["source_file"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == meta["source_sha256"]
    assert meta["case_count"] == len(fixture["cases"])
    assert {p["sheet"] for p in meta["patches"]} == {
        "Gutter 19 år",
        "Jenter 17 år",
        "Jenter 15 år",
    }


def test_every_combination_has_cases(
    fixture: dict[str, Any], params: dict[tuple[str, int], dict[str, Any]]
) -> None:
    per_row = Counter((c["source"]["sheet"], c["source"]["row"]) for c in fixture["cases"])
    assert set(per_row) == set(params)
    for key, entry in params.items():
        assert per_row[key] == (6 if entry["formula_type"] == "three_interval" else 4), key


def test_identity_matches_parameters(
    fixture: dict[str, Any], params: dict[tuple[str, int], dict[str, Any]]
) -> None:
    for case in fixture["cases"]:
        entry = params[(case["source"]["sheet"], case["source"]["row"])]
        for field in ("event_id", "gender", "age", "implement"):
            assert case[field] == entry[field], (case["source"], field)


def test_result_fields_match_measure(
    fixture: dict[str, Any], params: dict[tuple[str, int], dict[str, Any]]
) -> None:
    for case in fixture["cases"]:
        entry = params[(case["source"]["sheet"], case["source"]["row"])]
        expected = {"distance_meters"} if entry["measure"] == "distance" else {"time_seconds"}
        if entry["measure"] == "time" and entry["scale"] == 10:
            expected = {"time_minutes", "time_seconds"}
        assert set(case["result"]) == expected, case["source"]


def test_result_at_1000_level_gives_1000(
    fixture: dict[str, Any], params: dict[tuple[str, int], dict[str, Any]]
) -> None:
    hits = 0
    for case in fixture["cases"]:
        entry = params[(case["source"]["sheet"], case["source"]["row"])]
        result = case["result"]
        value = result.get("distance_meters")
        if value is None:
            value = result.get("time_minutes", 0) * 60 + result["time_seconds"]
        if abs(value - entry["params"]["h1000"]) < 1e-9:
            assert case["points"] == 1000, case["source"]
            hits += 1
    assert hits == len(params)


def test_points_are_non_negative_integers(fixture: dict[str, Any]) -> None:
    assert all(isinstance(c["points"], int) and c["points"] >= 0 for c in fixture["cases"])


def test_float_edges_are_the_known_ones(fixture: dict[str, Any]) -> None:
    edges = {
        (c["source"]["sheet"], c["source"]["row"]) for c in fixture["cases"] if "float_edge" in c
    }
    assert edges == EXPECTED_FLOAT_EDGES
    assert fixture["meta"]["float_edge_count"] == len(EXPECTED_FLOAT_EDGES)


@pytest.mark.skipif(shutil.which("soffice") is None, reason="krever LibreOffice (soffice)")
def test_fixture_is_reproducible() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "oracle_tyrving.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
