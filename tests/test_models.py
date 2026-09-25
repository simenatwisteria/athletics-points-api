import pytest

from athletics_scoring.models import Gender, Result


def test_total_seconds_includes_minutes() -> None:
    assert Result(time_minutes=2, time_seconds=4.5).total_seconds == 124.5
    assert Result(time_seconds=7.55).total_seconds == 7.55
    assert Result(distance_meters=5.2).total_seconds is None


@pytest.mark.parametrize(
    "kwargs",
    [{"time_seconds": -1.0}, {"distance_meters": -0.1}, {"time_minutes": 1}],
)
def test_invalid_results_rejected(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        Result(**kwargs)  # type: ignore[arg-type]


def test_gender_values() -> None:
    assert Gender("M") is Gender.MALE
    assert Gender("F") is Gender.FEMALE
