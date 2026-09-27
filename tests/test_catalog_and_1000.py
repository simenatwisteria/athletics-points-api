"""Øvelseskatalogen, 1000-poengsresultatet og ImplementMismatchError (AP-021)."""

import math

import pytest

from athletics_scoring import Gender, Result, default_registry
from athletics_scoring.catalog import event_catalog
from athletics_scoring.errors import ImplementMismatchError, UnknownEventError

REGISTRY = default_registry()
CATEGORIES = {"run", "hurdles", "racewalk", "jump", "throw"}


def test_catalog_covers_every_event_the_engines_offer() -> None:
    catalog = event_catalog()
    for system, versions in REGISTRY.systems().items():
        for version in versions:
            names: dict[str, set[str]] = {}
            for info in REGISTRY.get(system, version).list_events():
                names.setdefault(info.event_id, set()).add(info.event_name)
            missing = set(names) - set(catalog)
            assert not missing, f"{system} {version}: {sorted(missing)}"


def test_catalog_names_come_from_the_engines() -> None:
    names: dict[str, set[str]] = {}
    for system in REGISTRY.systems():
        for info in REGISTRY.get(system).list_events():
            names.setdefault(info.event_id, set()).add(info.event_name)
    for event_id, entry in event_catalog().items():
        assert entry.name_no in names.get(event_id, set()), event_id
        assert entry.name_en
        assert entry.category in CATEGORIES


def _result(measure: str, value: float) -> Result:
    return Result(distance_meters=value) if measure == "distance" else Result(time_seconds=value)


def test_tyrving_1000_result_gives_exactly_1000() -> None:
    engine = REGISTRY.get("tyrving")
    for info in engine.list_events():
        value = engine.points_1000_result(
            info.event_id, info.gender, info.age_class, info.implement
        )
        assert value is not None
        score = engine.calculate(
            info.event_id, info.gender, info.age_class, _result(info.input.measure, value),
            implement=info.implement,
        )
        assert score.points == 1000, info


def test_wa_1000_result_is_weakest_result_with_at_least_1000() -> None:
    engine = REGISTRY.get("wa_combined_events")
    for info in engine.list_events():
        value = engine.points_1000_result(info.event_id, info.gender, info.age_class)
        assert value is not None
        assert math.isclose(value * 100, round(value * 100))
        points = engine.calculate(
            info.event_id, info.gender, info.age_class, _result(info.input.measure, value)
        ).points
        weaker = value + 0.01 if info.input.measure == "time" else value - 0.01
        weaker_points = engine.calculate(
            info.event_id, info.gender, info.age_class, _result(info.input.measure, weaker)
        ).points
        assert points >= 1000 > weaker_points, info


def test_1000_result_control_numbers() -> None:
    wa = REGISTRY.get("wa_combined_events")
    assert wa.points_1000_result("sprint_200m", Gender.MALE, "senior") == 20.86
    assert REGISTRY.get("tyrving").points_1000_result("middle_800m", Gender.MALE, "15") == 124.0


@pytest.mark.parametrize("system", ["masters_combined_events", "wma_age_grading"])
def test_1000_result_is_none_where_not_defined(system: str) -> None:
    engine = REGISTRY.get(system)
    info = engine.list_events(Gender.MALE)[0]
    assert engine.points_1000_result(info.event_id, info.gender, info.age_class) is None
    with pytest.raises(UnknownEventError):
        engine.points_1000_result("no_such_event", Gender.MALE, info.age_class)


@pytest.mark.parametrize(
    ("system", "event_id", "gender", "age_class", "implement"),
    [
        ("tyrving", "javelin", Gender.FEMALE, "17", "0,6kg"),
        ("masters_combined_events", "shot_put", Gender.MALE, "M50", "7,26kg"),
        ("masters_combined_events", "sprint_100m", Gender.MALE, "M50", "1kg"),
        ("wma_age_grading", "shot_put", Gender.MALE, "50", "6kg"),
    ],
)
def test_wrong_implement_raises_implement_mismatch(
    system: str, event_id: str, gender: Gender, age_class: str, implement: str
) -> None:
    engine = REGISTRY.get(system)
    with pytest.raises(ImplementMismatchError):
        engine.calculate(event_id, gender, age_class, Result(distance_meters=10.0),
                         implement=implement)


def test_implement_mismatch_is_unknown_event() -> None:
    assert issubclass(ImplementMismatchError, UnknownEventError)
