"""Felles grensesnitt for alle poengsystemer."""

from abc import ABC, abstractmethod
from typing import ClassVar

from athletics_scoring.models import EventInfo, Gender, Parameters, Result, ScoreResult


class ScoringEngine(ABC):
    """Én motor per (poengsystem, versjon), f.eks. ``("tyrving", "2014")``."""

    system: ClassVar[str]
    version: ClassVar[str]

    @abstractmethod
    def calculate(
        self,
        event_id: str,
        gender: Gender,
        age_class: str,
        result: Result,
        implement: str | None = None,
    ) -> ScoreResult:
        """Poeng for ``result``.

        ``implement`` skiller varianter av samme øvelse, f.eks. hekkehøyde.
        """

    @abstractmethod
    def list_events(
        self, gender: Gender | None = None, age_class: str | None = None
    ) -> list[EventInfo]: ...

    @abstractmethod
    def get_parameters(
        self, event_id: str, gender: Gender, age_class: str, implement: str | None = None
    ) -> Parameters: ...

    def reverse(
        self, event_id: str, gender: Gender, age_class: str, target_points: int
    ) -> Result | None:
        """Resultat som trengs for ``target_points`` (B-8). Valgfritt for motorer."""
        raise NotImplementedError(f"{self.system} {self.version} støtter ikke reverse")
