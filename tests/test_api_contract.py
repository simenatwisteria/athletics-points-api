"""API-kontrakten (AP-020): gyldig OpenAPI 3.1, og eksemplene gir de samme tallene som motorene."""

import copy
import sys
from pathlib import Path
from typing import Any

import pytest

from athletics_scoring import Result, ScoreResult, __version__, default_registry
from athletics_scoring.errors import AmbiguousEventError, ScoringError, UnknownEventError
from athletics_scoring.models import Gender

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import openapi_check  # noqa: E402

REGISTRY = default_registry()
SPEC = openapi_check.load_spec()

ERROR_CODES = {
    "UnknownSystemError": "unknown_system",
    "UnknownVersionError": "unknown_version",
    "UnknownEventError": "unknown_event",
    "InvalidResultError": "invalid_result",
    "UnsupportedManualTimingError": "unsupported_manual_timing",
}


# --- hjelpere: slik API-laget skal oversette til og fra motorene ---------------------------------


def _examples(route: str, method: str, status: str | None = None) -> dict[str, Any]:
    op = SPEC["paths"][route][method]
    media = (
        op["requestBody"]["content"]["application/json"]
        if status is None
        else op["responses"][status]["content"]["application/json"]
    )
    return {name: example["value"] for name, example in media["examples"].items()}


def _select(request: dict[str, Any]) -> tuple[str, str, dict[str, Any] | None]:
    """System, klasse og ``selection``. ``auto`` følger reglene i skjemaet ``Selection``."""
    if request["system"] != "auto":
        return request["system"], request["age_class"], None
    age = request["age"]
    if age < 15:
        system, age_class = "tyrving", str(age)
    elif age <= 17:
        system = "wa_combined_events"
        age_class = f"{'G' if request['gender'] == 'M' else 'J'}{age}"
    else:
        system, age_class = "wa_combined_events", "senior"
    selection = {"requested_system": "auto", "age": age, "system": system, "age_class": age_class}
    return system, age_class, selection


def _result(system: str, request: dict[str, Any], age_class: str) -> Result:
    engine = REGISTRY.get(system, request.get("version"))
    gender = Gender(request["gender"])
    measures = {
        e.input.measure
        for e in engine.list_events(gender, age_class)
        if e.event_id == request["event_id"]
    }
    manual = request.get("manual_timing", False)
    if measures == {"distance"}:
        return Result(distance_meters=request["result"], manual_timing=manual)
    return Result(time_seconds=request["result"], manual_timing=manual)


def _serialize(score: ScoreResult) -> dict[str, Any]:
    return {
        "points": score.points,
        "result_kind": "age_adjusted_result"
        if score.scoring_system == "wma_age_grading"
        else "points",
        "scoring_system": score.scoring_system,
        "version": score.version,
        "event_id": score.event_id,
        "event_name": score.event_name,
        "gender": score.gender.value,
        "age_class": score.age_class,
        "implement": score.implement,
        "result_used": score.result_used,
        "parameters": dict(score.parameters),
        "formula_type": score.formula_type,
        "calculation_detail": score.calculation_detail,
        "calculation_steps": [
            {"label": s.label, "value": s.value, "formula": s.formula, "ref": s.ref}
            for s in score.calculation_steps
        ],
        "within_plausible_range": score.within_plausible_range,
    }


def _calculate(request: dict[str, Any]) -> dict[str, Any]:
    system, age_class, selection = _select(request)
    engine = REGISTRY.get(system, request.get("version"))
    score = engine.calculate(
        request["event_id"],
        Gender(request["gender"]),
        age_class,
        _result(system, request, age_class),
        implement=request.get("implement"),
    )
    out = _serialize(score)
    if selection is not None:
        out["selection"] = selection
    return out


def _without(value: dict[str, Any], *keys: str) -> dict[str, Any]:
    return {k: v for k, v in value.items() if k not in keys}


def _batch_row(row: dict[str, Any]) -> dict[str, Any]:
    """Status, melding og feilkode for én batch-rad, etter reglene i beskrivelsen av /batch."""
    out: dict[str, Any] = {"row_id": row.get("row_id"), "error": None, "calculation": None}
    if row["result"] is None:
        return {**out, "status": "no_result", "message": row.get("result_status")}
    try:
        calculation = _calculate(row)
    except AmbiguousEventError as exc:
        return {**out, "status": "ambiguous_implement", "message": str(exc)}
    except UnknownEventError as exc:
        if row.get("implement") is not None:
            try:
                _calculate(_without(row, "implement"))
            except ScoringError:
                pass
            else:
                return {**out, "status": "implement_mismatch", "message": str(exc)}
        error = {"code": "unknown_event", "message": str(exc), "details": None}
        return {**out, "status": "invalid", "message": str(exc), "error": error}
    except ScoringError as exc:
        code = ERROR_CODES[type(exc).__name__]
        error = {"code": code, "message": str(exc), "details": None}
        return {**out, "status": "invalid", "message": str(exc), "error": error}
    return {**out, "status": "ok", "message": None, "calculation": calculation}


# --- gyldig kontrakt -----------------------------------------------------------------------------


def test_spec_is_valid_openapi_31() -> None:
    assert SPEC["openapi"] == "3.1.0"
    assert openapi_check.check(SPEC) == []


def test_checker_finds_broken_example_and_ref() -> None:
    spec = copy.deepcopy(SPEC)
    example = spec["paths"]["/calculate"]["post"]["responses"]["200"]["content"][
        "application/json"
    ]["examples"]["wa_200m"]["value"]
    del example["points"]
    example["unexpected"] = 1
    spec["paths"]["/health"]["get"]["responses"]["200"]["content"]["application/json"][
        "schema"
    ]["$ref"] = "#/components/schemas/Missing"
    errors = openapi_check.check(spec)
    assert any("Missing" in e for e in errors)
    spec["paths"]["/health"]["get"]["responses"]["200"]["content"]["application/json"][
        "schema"
    ]["$ref"] = "#/components/schemas/Health"
    errors = openapi_check.check(spec)
    assert any("mangler påkrevd felt 'points'" in e for e in errors)
    assert any("ukjent felt 'unexpected'" in e for e in errors)


def test_yaml_subset() -> None:
    text = (
        "a:\n"
        '  "no": 800 m\n'
        "  n: 3\n"
        "  f: -5.0\n"
        '  s: "2014"\n'
        "  l: [x, \"null\"]\n"
        "  e: []\n"
        "  items:\n"
        "    - k: 1\n"
        "      v: null\n"
        "    - 11,74\n"
        "  text: |\n"
        "    linje 1\n"
        "    linje 2\n"
        "b: true\n"
    )
    assert openapi_check.load_yaml(text) == {
        "a": {
            "no": "800 m",
            "n": 3,
            "f": -5.0,
            "s": "2014",
            "l": ["x", "null"],
            "e": [],
            "items": [{"k": 1, "v": None}, "11,74"],
            "text": "linje 1\nlinje 2\n",
        },
        "b": True,
    }


@pytest.mark.parametrize(
    "text", ["a: b: c\n", "a: {x: 1}\n", "a: 1 # kommentar\n", "a: 1\na: 2\n", "a:\n\tb: 1\n"]
)
def test_yaml_subset_rejects_what_it_does_not_understand(text: str) -> None:
    with pytest.raises(openapi_check.YamlSubsetError):
        openapi_check.load_yaml(text)


def test_all_endpoints_and_interpret_is_planned() -> None:
    assert set(SPEC["paths"]) == {
        "/health",
        "/systems",
        "/events",
        "/calculate",
        "/combined",
        "/batch",
        "/interpret",
    }
    assert SPEC["servers"] == [{"url": "/api/v1"}]
    assert SPEC["paths"]["/interpret"]["post"]["x-status"] == "planned"
    planned = [
        route
        for route, item in SPEC["paths"].items()
        for op in item.values()
        if isinstance(op, dict) and op.get("x-status") == "planned"
    ]
    assert planned == ["/interpret"]
    assert "https://5kamp.minfriidrett.no" in SPEC["x-cors-allowed-origins"]


def test_error_codes_cover_every_scoring_error() -> None:
    from athletics_scoring import errors

    documented = SPEC["components"]["schemas"]["ErrorBody"]["description"]
    for name in dir(errors):
        cls = getattr(errors, name)
        if isinstance(cls, type) and issubclass(cls, ScoringError) and cls is not ScoringError:
            assert name in documented, f"{name} mangler i feiltabellen"


# --- eksemplene gir de samme tallene som motorene ------------------------------------------------


def test_control_numbers() -> None:
    responses = _examples("/calculate", "post", "200")
    assert responses["wa_200m"]["points"] == 712
    assert responses["tyrving_800m"]["points"] == 991
    assert "BV-011" in {s["ref"] for s in responses["tyrving_800m"]["calculation_steps"]}
    assert responses["masters_100m"]["points"] == 681
    auto = responses["auto_16"]
    assert (auto["scoring_system"], auto["age_class"], auto["points"]) == (
        "wa_combined_events",
        "G16",
        712,
    )


def test_calculate_examples_match_engines() -> None:
    requests = _examples("/calculate", "post")
    responses = _examples("/calculate", "post", "200")
    assert set(requests) == set(responses)
    for name, request in requests.items():
        expected = responses[name]
        actual = _calculate(request)
        if "selection" in expected:
            assert set(expected["selection"]) - set(actual["selection"]) == {"rule", "ref"}
            actual["selection"] |= {k: expected["selection"][k] for k in ("rule", "ref")}
        assert actual == expected, name


def test_combined_example_matches_engine() -> None:
    request = _examples("/combined", "post")["femkamp_menn"]
    expected = _examples("/combined", "post", "200")["femkamp_menn"]
    rows = [
        _calculate({**e, "system": request["system"], "version": request.get("version"),
                    "gender": request["gender"], "age_class": request["age_class"]})
        for e in request["events"]
    ]
    assert expected["total"] == sum(r["points"] for r in rows)
    assert [_without(e, "calculation_steps") for e in expected["events"]] == [
        _without(r, "calculation_steps") for r in rows
    ]
    assert expected["total"] == sum(e["points"] for e in expected["events"])


def test_batch_example_matches_engines() -> None:
    request = _examples("/batch", "post")["blandet"]
    expected = _examples("/batch", "post", "200")["blandet"]
    assert len(expected["rows"]) == len(request["rows"])
    for row, want in zip(request["rows"], expected["rows"], strict=True):
        got = _batch_row(row)
        if want["calculation"] is not None:
            got["calculation"] = _without(got["calculation"], "calculation_steps", "selection")
            want = {**want, "calculation": _without(
                want["calculation"], "calculation_steps", "selection"
            )}
        assert got == want, row["row_id"]
    statuses = [r["status"] for r in expected["rows"]]
    assert expected["summary"] == {s: statuses.count(s) for s in expected["summary"]}


def test_events_examples_match_engines() -> None:
    for name, entries in _examples("/events", "get", "200").items():
        for entry in entries:
            engine = REGISTRY.get(entry["system"], entry["version"])
            gender = Gender(entry["gender"])
            infos = [
                e
                for e in engine.list_events(gender, entry["age_class"])
                if e.event_id == entry["event_id"] and e.implement == entry["implement"]
            ]
            assert len(infos) == 1, name
            info = infos[0]
            assert entry["name"]["no"] == info.event_name
            assert entry["formula_type"] == info.formula_type
            assert entry["input"] == {
                "measure": info.input.measure,
                "resolution": info.input.resolution,
                "uses_minutes": info.input.uses_minutes,
                "manual_timing_allowed": info.input.manual_timing_allowed,
                "plausible_min": info.input.plausible_min,
                "plausible_max": info.input.plausible_max,
            }
            request = {**entry, "result": entry["points_1000_result"]}
            assert _calculate(request)["points"] == 1000, name


def test_systems_example_matches_registry() -> None:
    [systems] = _examples("/systems", "get", "200").values()
    ready = {s["id"]: s for s in systems if s["ready"]}
    assert {k: [v["version"] for v in s["versions"]] for k, s in ready.items()} == (
        REGISTRY.systems()
    )
    for system_id, info in ready.items():
        engine = REGISTRY.get(system_id)
        assert info["latest_version"] == engine.version
        for gender in Gender:
            classes = list(dict.fromkeys(e.age_class for e in engine.list_events(gender)))
            assert sorted(info["classes"][gender.value]) == sorted(classes), system_id
        assert info["supports_combined"] == hasattr(engine, "calculate_combined")
        for version in info["versions"]:
            for source in version["sources"]:
                assert source in engine.sources()


def test_health_example_matches_registry() -> None:
    [health] = _examples("/health", "get", "200").values()
    assert health["systems"] == REGISTRY.systems()
    assert health["package_version"] == __version__


def test_interpret_example_matches_engine() -> None:
    [response] = _examples("/interpret", "post", "200").values()
    for row in response["rows"]:
        actual = _without(_calculate(row["interpretation"]), "calculation_steps")
        assert actual == _without(row["calculation"], "calculation_steps")
