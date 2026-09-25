"""Oppslag fra (poengsystem, versjon) til motor."""

from athletics_scoring.engine import ScoringEngine
from athletics_scoring.errors import DuplicateEngineError, UnknownSystemError, UnknownVersionError


class Registry:
    """Holder registrerte motorer.

    Versjoner sammenlignes som strenger. Det stemmer så lenge versjoner er årstall (``"2014"``,
    ``"2025"``), som er konvensjonen i prosjektet (B-5).
    """

    def __init__(self) -> None:
        self._engines: dict[str, dict[str, ScoringEngine]] = {}

    def register(self, engine: ScoringEngine) -> None:
        versions = self._engines.setdefault(engine.system, {})
        if engine.version in versions:
            raise DuplicateEngineError(f"{engine.system} {engine.version} er allerede registrert")
        versions[engine.version] = engine

    def get(self, scoring_system: str, version: str | None = None) -> ScoringEngine:
        """Motoren for systemet. ``version=None`` gir nyeste registrerte versjon."""
        versions = self._engines.get(scoring_system)
        if not versions:
            raise UnknownSystemError(f"Ukjent poengsystem: {scoring_system!r}")
        if version is None:
            return versions[max(versions)]
        try:
            return versions[version]
        except KeyError:
            known = ", ".join(sorted(versions))
            raise UnknownVersionError(
                f"{scoring_system} finnes ikke i versjon {version!r} (kjente: {known})"
            ) from None

    def systems(self) -> dict[str, list[str]]:
        """Alle registrerte systemer med versjoner, sortert."""
        return {name: sorted(versions) for name, versions in sorted(self._engines.items())}
