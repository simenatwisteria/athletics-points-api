import pytest

from athletics_scoring.engine import ScoringEngine
from athletics_scoring.errors import (
    DuplicateEngineError,
    ScoringError,
    UnknownSystemError,
    UnknownVersionError,
)
from athletics_scoring.models import EventInfo, Gender, Parameters, Result, ScoreResult
from athletics_scoring.registry import Registry


def _engine(system_: str, version_: str) -> ScoringEngine:
    class Dummy(ScoringEngine):
        system = system_
        version = version_

        def calculate(
            self, event_id: str, gender: Gender, age_class: str, result: Result
        ) -> ScoreResult:
            raise NotImplementedError

        def list_events(
            self, gender: Gender | None = None, age_class: str | None = None
        ) -> list[EventInfo]:
            return []

        def get_parameters(self, event_id: str, gender: Gender, age_class: str) -> Parameters:
            return {}

    return Dummy()


def test_get_without_version_returns_newest() -> None:
    registry = Registry()
    old, new = _engine("tyrving", "2014"), _engine("tyrving", "2025")
    registry.register(new)
    registry.register(old)
    assert registry.get("tyrving") is new
    assert registry.get("tyrving", "2014") is old


def test_unknown_system() -> None:
    with pytest.raises(UnknownSystemError):
        Registry().get("finnes-ikke")


def test_unknown_version() -> None:
    registry = Registry()
    registry.register(_engine("tyrving", "2014"))
    with pytest.raises(UnknownVersionError, match="2014"):
        registry.get("tyrving", "1999")


def test_duplicate_registration() -> None:
    registry = Registry()
    registry.register(_engine("wa", "2025"))
    with pytest.raises(DuplicateEngineError):
        registry.register(_engine("wa", "2025"))


def test_errors_share_base_class() -> None:
    assert issubclass(UnknownSystemError, ScoringError)
    assert issubclass(UnknownSystemError, LookupError)


def test_systems_listing() -> None:
    registry = Registry()
    registry.register(_engine("wa", "2025"))
    registry.register(_engine("tyrving", "2014"))
    assert registry.systems() == {"tyrving": ["2014"], "wa": ["2025"]}


def test_reverse_is_optional() -> None:
    with pytest.raises(NotImplementedError):
        _engine("tyrving", "2014").reverse("60m", Gender.MALE, "15", 1000)
