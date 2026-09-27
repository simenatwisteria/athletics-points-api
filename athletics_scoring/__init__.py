"""Åpen, transparent beregningsmotor for norske friidrettspoeng."""

from athletics_scoring.masters_combined_events import MastersCombinedCalculator
from athletics_scoring.models import (
    CombinedEventInput,
    CombinedScoreResult,
    EventInfo,
    Gender,
    InputSpec,
    Result,
    ScoreResult,
)
from athletics_scoring.registry import Registry
from athletics_scoring.tyrving import TyrvingCalculator
from athletics_scoring.wa_combined_events import CombinedEventsCalculator
from athletics_scoring.wma_age_grading import WmaAgeGradingCalculator

__version__ = "0.1.0"

__all__ = [
    "CombinedEventInput",
    "CombinedEventsCalculator",
    "CombinedScoreResult",
    "EventInfo",
    "Gender",
    "InputSpec",
    "MastersCombinedCalculator",
    "Registry",
    "Result",
    "ScoreResult",
    "TyrvingCalculator",
    "WmaAgeGradingCalculator",
    "default_registry",
]


def default_registry() -> Registry:
    """Registry med alle poengsystemene pakken har i dag."""
    registry = Registry()
    registry.register(TyrvingCalculator())
    registry.register(CombinedEventsCalculator())
    registry.register(MastersCombinedCalculator())
    registry.register(WmaAgeGradingCalculator())
    return registry
