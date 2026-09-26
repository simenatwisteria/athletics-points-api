"""Dataklasser som deles av alle poengsystemer (TEKNISK_FORSLAG_v2.1 kap. 7.1)."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

type Parameters = Mapping[str, float]
"""Parametre for én (øvelse, kjønn, klasse), f.eks. ``{"points_1000": 7.55, "quotient": 2.7}``."""


class Gender(StrEnum):
    MALE = "M"
    FEMALE = "F"


@dataclass(frozen=True, slots=True)
class Result:
    """Et oppnådd resultat. Løp bruker tid, tekniske øvelser bruker distanse/høyde."""

    time_seconds: float | None = None
    time_minutes: int | None = None
    distance_meters: float | None = None
    manual_timing: bool = False

    def __post_init__(self) -> None:
        for name in ("time_seconds", "time_minutes", "distance_meters"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} kan ikke være negativ: {value}")
        if self.time_minutes is not None and self.time_seconds is None:
            raise ValueError("time_minutes krever time_seconds")

    @property
    def total_seconds(self) -> float | None:
        """Tid i sekunder, med minutter regnet inn. ``None`` hvis resultatet ikke er en tid."""
        if self.time_seconds is None:
            return None
        return (self.time_minutes or 0) * 60 + self.time_seconds


@dataclass(frozen=True, slots=True)
class CalculationStep:
    """Ett steg i beregningen, for strukturert respons (B-6)."""

    label: str
    value: float
    formula: str


@dataclass(frozen=True, slots=True)
class InputSpec:
    """Hvordan et resultat for øvelsen skal tastes inn. Styrer inndatafeltet i en frontend."""

    measure: Literal["time", "distance"]
    resolution: float
    """Minste enhet som teller: 0.01 (hundredeler/centimeter) eller 0.1 (tideler)."""
    uses_minutes: bool
    """Tiden oppgis naturlig som minutter og sekunder (lange løp)."""
    manual_timing_allowed: bool
    """Regelverket har tillegg for manuell tid på øvelsen."""
    plausible_min: float
    plausible_max: float
    """Rimelig område for resultatet (sekunder eller meter). Brukerhjelp, ikke en regel: utenfor
    området er resultatet trolig ufullstendig eller feiltastet, men poeng beregnes likevel."""


@dataclass(frozen=True, slots=True)
class EventInfo:
    """En øvelse slik et poengsystem tilbyr den for et gitt kjønn og en klasse."""

    event_id: str
    event_name: str
    gender: Gender
    age_class: str
    formula_type: str
    input: InputSpec
    implement: str | None = None


@dataclass(frozen=True, slots=True)
class ScoreResult:
    points: int
    scoring_system: str
    version: str
    event_id: str
    event_name: str
    gender: Gender
    age_class: str
    result_used: float
    parameters: Parameters
    formula_type: str
    calculation_detail: str
    calculation_steps: tuple[CalculationStep, ...] = field(default_factory=tuple)
    implement: str | None = None
    within_plausible_range: bool = True
    """Om resultatet er innenfor øvelsens rimelige område (se ``InputSpec``)."""


@dataclass(frozen=True, slots=True)
class CombinedEventInput:
    """Én øvelse i en mangekamp."""

    event_id: str
    result: Result
    implement: str | None = None


@dataclass(frozen=True, slots=True)
class CombinedScoreResult:
    """Mangekamp: poeng per øvelse og summen."""

    total: int
    scoring_system: str
    version: str
    gender: Gender
    age_class: str
    events: tuple[ScoreResult, ...]
