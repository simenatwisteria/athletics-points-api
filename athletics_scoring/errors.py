"""Unntak for athletics_scoring."""


class ScoringError(Exception):
    """Felles basisklasse for alle feil fra pakken."""


class UnknownSystemError(ScoringError, LookupError):
    """Poengsystemet er ikke registrert."""


class UnknownVersionError(ScoringError, LookupError):
    """Poengsystemet finnes, men ikke i den etterspurte versjonen."""


class DuplicateEngineError(ScoringError, ValueError):
    """En motor for samme (system, versjon) er allerede registrert."""
