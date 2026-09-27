"""HTTP-API-et (AP-021) mot kontrakten. Eksemplene i kontrakten er allerede kontrollert mot motorene
i ``test_api_contract.py``; her sjekkes at API-et gir det samme."""

import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from athletics_api.main import create_app
from athletics_api.ratelimit import SlidingWindowLimiter
from athletics_api.service import Service
from athletics_api.settings import Settings
from athletics_scoring import errors

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import openapi_check  # noqa: E402

SPEC = openapi_check.load_spec()
SERVICE = Service()
FIVEKAMP = "https://5kamp.minfriidrett.no"


def _client(**settings: Any) -> TestClient:
    return TestClient(create_app(Settings(**settings), service=SERVICE))


@pytest.fixture(scope="module")
def client() -> TestClient:
    return _client()


def _examples(route: str, method: str, status: str | None = None) -> dict[str, Any]:
    op = SPEC["paths"][route][method]
    media = (
        op["requestBody"]["content"]["application/json"]
        if status is None
        else op["responses"][status]["content"]["application/json"]
    )
    return {name: example["value"] for name, example in media["examples"].items()}


def _without(value: dict[str, Any], *keys: str) -> dict[str, Any]:
    return {k: v for k, v in value.items() if k not in keys}


def _error(response: Any, status: int, code: str) -> dict[str, Any]:
    assert response.status_code == status, response.text
    body: dict[str, Any] = response.json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message", "details"}
    assert body["error"]["code"] == code
    assert body["error"]["message"]
    return body["error"]


def _schema_errors(value: Any, schema_name: str) -> list[str]:
    schema = {"$ref": f"#/components/schemas/{schema_name}"}
    return openapi_check.validate(SPEC, schema, value, schema_name)


# --- kontrolltallene i oppgavefila ---------------------------------------------------------------


WA_200M = {
    "system": "wa_combined_events",
    "event_id": "sprint_200m",
    "gender": "M",
    "age_class": "senior",
    "result": 23.79,
}


def test_calculate_wa_200m(client: TestClient) -> None:
    response = client.post("/api/v1/calculate", json=WA_200M)
    assert response.status_code == 200
    assert response.json()["points"] == 712
    assert response.headers["cache-control"] == "no-cache"


def test_calculate_with_version_is_immutable(client: TestClient) -> None:
    response = client.post("/api/v1/calculate", json={**WA_200M, "version": "2001"})
    assert response.status_code == 200
    assert response.json()["points"] == 712
    assert response.headers["cache-control"] == "public, max-age=31536000, immutable"


def test_calculate_tyrving_800m_drops_hundredths(client: TestClient) -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"system": "tyrving", "event_id": "middle_800m", "gender": "M", "age_class": "15",
              "result": 124.56},
    )
    body = response.json()
    assert body["points"] == 991
    [step] = [s for s in body["calculation_steps"] if s["label"] == "hundredths_dropped"]
    assert step["ref"] == "BV-011"


def test_calculate_auto_16(client: TestClient) -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"system": "auto", "event_id": "sprint_200m", "gender": "M", "age": 16,
              "result": 23.79},
    )
    body = response.json()
    assert body["points"] == 712
    assert body["selection"]["system"] == "wa_combined_events"
    assert body["age_class"] == body["selection"]["age_class"] == "G16"


@pytest.mark.parametrize(
    ("age", "gender", "system", "age_class"),
    [(10, "F", "tyrving", "10"), (14, "M", "tyrving", "14"), (15, "F", "wa_combined_events", "J15"),
     (17, "M", "wa_combined_events", "G17"), (18, "M", "wa_combined_events", "senior"),
     (60, "F", "wa_combined_events", "senior")],
)
def test_auto_selection_rules(
    client: TestClient, age: int, gender: str, system: str, age_class: str
) -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"system": "auto", "event_id": "sprint_60m", "gender": gender, "age": age,
              "result": 9.0},
    )
    selection = response.json()["selection"]
    assert (selection["system"], selection["age_class"]) == (system, age_class)
    assert selection["ref"] == "BV-021"
    assert _schema_errors(selection, "Selection") == []


def test_combined_femkamp(client: TestClient) -> None:
    request = _examples("/combined", "post")["femkamp_menn"]
    expected = _examples("/combined", "post", "200")["femkamp_menn"]
    response = client.post("/api/v1/combined", json=request)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3190
    assert response.headers["cache-control"] == "public, max-age=31536000, immutable"
    assert _without(body, "events") == _without(expected, "events")
    assert [_without(e, "calculation_steps") for e in body["events"]] == [
        _without(e, "calculation_steps") for e in expected["events"]
    ]
    assert all(e["calculation_steps"] for e in body["events"])
    assert _schema_errors(body, "CombinedResult") == []


def test_batch_one_row_per_status(client: TestClient) -> None:
    request = _examples("/batch", "post")["blandet"]
    expected = _examples("/batch", "post", "200")["blandet"]
    response = client.post("/api/v1/batch", json=request)
    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == expected["summary"]
    for got, want in zip(body["rows"], expected["rows"], strict=True):
        if want["calculation"] is not None:
            got = {**got, "calculation": _without(got["calculation"], "calculation_steps")}
            want = {**want, "calculation": _without(want["calculation"], "calculation_steps")}
        assert got == want, want["row_id"]
    assert _schema_errors(body, "BatchResult") == []
    assert response.headers["cache-control"] == "no-cache"


def test_cors_allowed_origin(client: TestClient) -> None:
    response = client.get("/api/v1/health", headers={"Origin": FIVEKAMP})
    assert response.headers["access-control-allow-origin"] == FIVEKAMP


def test_cors_preflight(client: TestClient) -> None:
    response = client.options(
        "/api/v1/calculate",
        headers={"Origin": FIVEKAMP, "Access-Control-Request-Method": "POST",
                 "Access-Control-Request-Headers": "content-type"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FIVEKAMP


def test_cors_other_origin_gets_no_header(client: TestClient) -> None:
    response = client.get("/api/v1/health", headers={"Origin": "https://evil.example"})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_cors_origins_from_settings() -> None:
    settings = Settings.from_env({"CORS_ALLOWED_ORIGINS": "https://a.example, *, https://b.example"})
    assert settings.cors_allowed_origins == ("https://a.example", "https://b.example")
    client = _client(cors_allowed_origins=settings.cors_allowed_origins)
    response = client.get("/api/v1/health", headers={"Origin": "https://b.example"})
    assert response.headers["access-control-allow-origin"] == "https://b.example"
    response = client.get("/api/v1/health", headers={"Origin": FIVEKAMP})
    assert "access-control-allow-origin" not in response.headers


def test_rate_limit() -> None:
    client = _client(rate_limit_per_minute=3)
    for _ in range(3):
        assert client.get("/api/v1/systems").status_code == 200
    response = client.get("/api/v1/systems", headers={"Origin": FIVEKAMP})
    error = _error(response, 429, "rate_limited")
    retry_after = int(response.headers["retry-after"])
    assert 1 <= retry_after <= 60
    assert error["details"] == {"retry_after_seconds": retry_after}
    assert response.headers["access-control-allow-origin"] == FIVEKAMP
    assert client.get("/api/v1/health").status_code == 200


def test_rate_limit_per_forwarded_ip_only_behind_proxy() -> None:
    client = _client(rate_limit_per_minute=1, trust_proxy=True)
    assert client.get("/api/v1/systems", headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 200
    assert client.get("/api/v1/systems", headers={"X-Forwarded-For": "2.2.2.2"}).status_code == 200
    assert client.get("/api/v1/systems", headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 429
    client = _client(rate_limit_per_minute=1)
    assert client.get("/api/v1/systems", headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 200
    assert client.get("/api/v1/systems", headers={"X-Forwarded-For": "2.2.2.2"}).status_code == 429


def test_sliding_window() -> None:
    now = [0.0]
    limiter = SlidingWindowLimiter(2, window=60, clock=lambda: now[0])
    assert limiter.hit("a") is None
    now[0] = 30
    assert limiter.hit("a") is None
    assert limiter.hit("a") == 30
    assert limiter.hit("b") is None
    now[0] = 60
    assert limiter.hit("a") is None
    assert limiter.hit("a") == 30


def test_interpret_is_not_implemented(client: TestClient) -> None:
    request = _examples("/interpret", "post")["liveres"]
    response = client.post("/api/v1/interpret", json=request)
    _error(response, 501, "not_implemented")


def test_wrong_implement_is_implement_mismatch(client: TestClient) -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"system": "tyrving", "event_id": "javelin", "gender": "F", "age_class": "17",
              "implement": "0,6kg", "result": 40.0},
    )
    _error(response, 422, "implement_mismatch")


# --- alle eksemplene i kontrakten ----------------------------------------------------------------


def test_calculate_examples(client: TestClient) -> None:
    requests = _examples("/calculate", "post")
    responses = _examples("/calculate", "post", "200")
    for name, request in requests.items():
        response = client.post("/api/v1/calculate", json=request)
        assert response.status_code == 200, name
        body = response.json()
        assert body == responses[name], name
        assert _schema_errors(body, "Calculation") == [], name


def test_health(client: TestClient) -> None:
    [expected] = _examples("/health", "get", "200").values()
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == expected


def test_systems(client: TestClient) -> None:
    [expected] = _examples("/systems", "get", "200").values()
    response = client.get("/api/v1/systems")
    assert response.status_code == 200
    body = response.json()
    assert all(_schema_errors(s, "SystemInfo") == [] for s in body)
    assert [s["id"] for s in body] == [s["id"] for s in expected]
    for got, want in zip(body, expected, strict=True):
        assert _without(got, "versions") == _without(want, "versions"), want["id"]
        assert [v["version"] for v in got["versions"]] == [v["version"] for v in want["versions"]]
        for got_version, want_version in zip(got["versions"], want["versions"], strict=True):
            for source in want_version["sources"]:
                assert source in got_version["sources"]


def test_events_examples(client: TestClient) -> None:
    for name, entries in _examples("/events", "get", "200").items():
        first = entries[0]
        response = client.get(
            "/api/v1/events",
            params={"system": first["system"], "version": first["version"],
                    "gender": first["gender"], "age_class": first["age_class"]},
        )
        assert response.status_code == 200, name
        body = response.json()
        for entry in entries:
            assert entry in body, name
        assert all(_schema_errors(e, "EventEntry") == [] for e in body), name


@pytest.mark.parametrize("system", ["tyrving", "wa_combined_events", "masters_combined_events",
                                    "wma_age_grading"])
def test_events_all_systems_match_schema(client: TestClient, system: str) -> None:
    response = client.get("/api/v1/events", params={"system": system, "gender": "F"})
    assert response.status_code == 200
    body = response.json()
    assert body
    assert {e["gender"] for e in body} == {"F"}
    assert all(_schema_errors(e, "EventEntry") == [] for e in body[:200])


def test_events_errors(client: TestClient) -> None:
    _error(client.get("/api/v1/events", params={"system": "nope"}), 422, "unknown_system")
    _error(client.get("/api/v1/events", params={"system": "tyrving", "version": "1999"}), 422,
           "unknown_version")
    _error(client.get("/api/v1/events", params={"system": "tyrving", "gender": "X"}), 422,
           "validation_error")
    _error(client.get("/api/v1/events"), 422, "validation_error")


# --- feil -----------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("request_body", "code"),
    [
        ({**WA_200M, "system": "series_table"}, "validation_error"),
        ({**WA_200M, "version": "1999"}, "unknown_version"),
        ({**WA_200M, "event_id": "triple_jump"}, "unknown_event"),
        ({**WA_200M, "age_class": "G14"}, "unknown_event"),
        ({"system": "tyrving", "event_id": "hurdles_110m", "gender": "M", "age_class": "17",
          "result": 15.2}, "ambiguous_implement"),
        ({"system": "masters_combined_events", "event_id": "shot_put", "gender": "M",
          "age_class": "M50", "implement": "7,26kg", "result": 11.2}, "implement_mismatch"),
        ({**WA_200M, "result": 0}, "invalid_result"),
        ({**WA_200M, "result": -1.0}, "invalid_result"),
        ({"system": "tyrving", "event_id": "sprint_40m", "gender": "M", "age_class": "11",
          "result": 6.5, "manual_timing": True}, "unsupported_manual_timing"),
        ({**WA_200M, "result": "23,79"}, "validation_error"),
        ({**WA_200M, "unexpected": 1}, "validation_error"),
        (_without(WA_200M, "age_class"), "validation_error"),
        ({**WA_200M, "age": 30}, "validation_error"),
        ({**_without(WA_200M, "age_class"), "system": "auto"}, "validation_error"),
        ({**WA_200M, "system": "auto", "age": 16}, "validation_error"),
        ({**_without(WA_200M, "age_class"), "system": "auto", "age": 9}, "validation_error"),
    ],
)
def test_calculate_errors(client: TestClient, request_body: dict[str, Any], code: str) -> None:
    error = _error(client.post("/api/v1/calculate", json=request_body), 422, code)
    assert _schema_errors({"error": error}, "Error") == []


def test_ambiguous_implement_lists_implements(client: TestClient) -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"system": "tyrving", "event_id": "hurdles_110m", "gender": "M", "age_class": "17",
              "result": 15.2},
    )
    error = _error(response, 422, "ambiguous_implement")
    assert error["details"] == {"implements": ["91,4cm/9,14m", "100,0cm/9,14m"]}


def test_auto_requires_age_field(client: TestClient) -> None:
    response = client.post("/api/v1/calculate", json={**_without(WA_200M, "age_class"),
                                                       "system": "auto"})
    assert _error(response, 422, "validation_error")["details"] == {"field": "age"}


def test_malformed_json(client: TestClient) -> None:
    response = client.post("/api/v1/calculate", content=b"{not json",
                           headers={"Content-Type": "application/json"})
    _error(response, 422, "validation_error")


@pytest.mark.parametrize(
    ("request_body", "code"),
    [
        ({"system": "wa_combined_events", "gender": "M", "age_class": "senior", "events": []},
         "validation_error"),
        ({"system": "wa_combined_events", "gender": "M", "age_class": "senior",
          "events": [{"event_id": "long_jump", "result": 6.0},
                     {"event_id": "long_jump", "result": 6.1}]}, "invalid_combined_event"),
        ({"system": "wma_age_grading", "gender": "M", "age_class": "50",
          "events": [{"event_id": "long_jump", "result": 6.0}]}, "invalid_combined_event"),
        ({"system": "tyrving", "gender": "M", "age_class": "15",
          "events": [{"event_id": "long_jump", "result": 6.0}]}, "invalid_combined_event"),
        ({"system": "wa_combined_events", "gender": "M", "age_class": "senior",
          "events": [{"event_id": "triple_jump", "result": 13.0}]}, "unknown_event"),
    ],
)
def test_combined_errors(client: TestClient, request_body: dict[str, Any], code: str) -> None:
    _error(client.post("/api/v1/combined", json=request_body), 422, code)


def test_combined_auto_under_15_uses_tyrving(client: TestClient) -> None:
    response = client.post(
        "/api/v1/combined",
        json={"system": "auto", "gender": "F", "age": 13,
              "events": [{"event_id": "sprint_60m", "result": 8.9},
                         {"event_id": "long_jump", "result": 4.5}]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["scoring_system"] == "tyrving"
    assert body["selection"]["age_class"] == "13"
    assert body["total"] == sum(e["points"] for e in body["events"])
    assert response.headers["cache-control"] == "no-cache"


def test_batch_errors(client: TestClient) -> None:
    _error(client.post("/api/v1/batch", json={"rows": []}), 422, "validation_error")
    row = {**WA_200M}
    _error(client.post("/api/v1/batch", json={"rows": [row] * 2001}), 422, "validation_error")
    _error(client.post("/api/v1/batch", json={"rows": [_without(row, "result")]}), 422,
           "validation_error")


def test_batch_max_rows_and_versioned_cache(client: TestClient) -> None:
    row = {**WA_200M, "version": "2001"}
    response = client.post("/api/v1/batch", json={"rows": [row] * 2000})
    assert response.status_code == 200
    assert response.json()["summary"]["ok"] == 2000
    assert response.headers["cache-control"] == "public, max-age=31536000, immutable"


def test_batch_row_level_validation_is_invalid(client: TestClient) -> None:
    response = client.post(
        "/api/v1/batch",
        json={"rows": [{**_without(WA_200M, "age_class"), "system": "auto", "row_id": "x"}]},
    )
    assert response.status_code == 200
    [row] = response.json()["rows"]
    assert row["status"] == "invalid"
    assert row["error"]["code"] == "validation_error"


# --- hver feiltype gir kontraktens kode og status -----------------------------------------------


ERROR_TABLE = {
    "UnknownSystemError": (422, "unknown_system"),
    "UnknownVersionError": (422, "unknown_version"),
    "UnknownEventError": (422, "unknown_event"),
    "ImplementMismatchError": (422, "implement_mismatch"),
    "AmbiguousEventError": (422, "ambiguous_implement"),
    "InvalidResultError": (422, "invalid_result"),
    "UnsupportedManualTimingError": (422, "unsupported_manual_timing"),
    "InvalidCombinedEventError": (422, "invalid_combined_event"),
    "DuplicateEngineError": (500, "internal_error"),
}


class _Raising(Service):
    def __init__(self, exc: Exception) -> None:
        super().__init__(SERVICE.registry)
        self.exc = exc

    def systems(self) -> list[dict[str, Any]]:
        raise self.exc


def test_every_scoring_error_has_a_code() -> None:
    names = {
        name
        for name in dir(errors)
        if isinstance(getattr(errors, name), type)
        and issubclass(getattr(errors, name), errors.ScoringError)
        and getattr(errors, name) is not errors.ScoringError
    }
    assert names == set(ERROR_TABLE)


@pytest.mark.parametrize("name", sorted(ERROR_TABLE))
def test_error_type_maps_to_contract(name: str) -> None:
    status, code = ERROR_TABLE[name]
    exc = getattr(errors, name)("melding")
    app = create_app(Settings(), service=_Raising(exc))
    client = TestClient(app, raise_server_exceptions=False)
    _error(client.get("/api/v1/systems"), status, code)


def test_unexpected_error_is_internal_error() -> None:
    client = TestClient(create_app(Settings(), service=_Raising(RuntimeError("boom"))),
                        raise_server_exceptions=False)
    _error(client.get("/api/v1/systems"), 500, "internal_error")
