"""Åpen, transparent beregningsmotor for norske friidrettspoeng."""

from athletics_scoring.models import Gender, Result, ScoreResult
from athletics_scoring.registry import Registry
from athletics_scoring.tyrving import TyrvingCalculator

__version__ = "0.1.0"

__all__ = ["Gender", "Registry", "Result", "ScoreResult", "TyrvingCalculator", "default_registry"]


def default_registry() -> Registry:
    """Registry med alle poengsystemene pakken har i dag."""
    registry = Registry()
    registry.register(TyrvingCalculator())
    return registry
