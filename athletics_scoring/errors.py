"""Unntak for athletics_scoring."""


class ScoringError(Exception):
    """Felles basisklasse for alle feil fra pakken."""


class UnknownSystemError(ScoringError, LookupError):
    """Poengsystemet er ikke registrert."""


class UnknownVersionError(ScoringError, LookupError):
    """Poengsystemet finnes, men ikke i den etterspurte versjonen."""


class DuplicateEngineError(ScoringError, ValueError):
    """En motor for samme (system, versjon) er allerede registrert."""


class UnknownEventError(ScoringError, LookupError):
    """Øvelsen finnes ikke for dette kjønnet og denne klassen."""


class AmbiguousEventError(ScoringError, LookupError):
    """Øvelsen finnes med flere utstyrsvarianter; ``implement`` må oppgis."""


class InvalidResultError(ScoringError, ValueError):
    """Resultatet mangler, er 0 eller har feil type for øvelsen."""


class InvalidCombinedEventError(ScoringError, ValueError):
    """Mangekampen er tom, har samme øvelse to ganger, eller gjelder feil klasse."""


class UnsupportedManualTimingError(ScoringError, ValueError):
    """Regelverket har ikke tillegg for manuell tid på denne øvelsen."""
