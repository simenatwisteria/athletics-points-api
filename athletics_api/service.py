"""Oversetting mellom kontrakten og motorene. All beregning skjer i athletics_scoring."""

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from athletics_api.errors import ApiError, error_body, scoring_error_code
from athletics_api.schemas import BatchRow, CalculateRequest, CombinedRequest
from athletics_scoring import (
    CombinedEventInput,
    Gender,
    Registry,
    Result,
    ScoreResult,
    __version__,
    default_registry,
)
from athletics_scoring.catalog import event_catalog
from athletics_scoring.engine import ScoringEngine
from athletics_scoring.errors import (
    AmbiguousEventError,
    ImplementMismatchError,
    InvalidCombinedEventError,
    InvalidResultError,
    ScoringError,
)

AUTO = "auto"
SELECTION_REF = "BV-021"
RULE_TYRVING = "Under 15 år gjelder Tyrvingtabellen, med klassealderen som klasse (10–14)."
RULE_COMBINED = "Fra 15 år gjelder mangekamptabellen, G/J15–17 som egne klasser, ellers senior."

# Visningsdata for GET /systems, i rekkefølgen frontenden viser dem (ungdom, senior, masters).
SYSTEM_INFO: tuple[dict[str, Any], ...] = (
    {
        "id": "tyrving",
        "name": {"no": "Tyrvingtabellen", "en": "Tyrving table"},
        "description": {
            "no": "NFIFs poengtabell for gutter og jenter 10–19 år.",
            "en": "The Norwegian Athletics Federation's points table for boys and girls "
            "aged 10–19.",
        },
        "group": "youth",
        "class_type": "age",
        "result_kind": "points",
    },
    {
        "id": "wa_combined_events",
        "name": {"no": "Mangekamptabellen (WA)", "en": "Combined events (World Athletics)"},
        "description": {
            "no": "IAAF/WA Scoring Tables for Combined Events 2001, senior og ungdom fra 15 år.",
            "en": "IAAF/WA Scoring Tables for Combined Events 2001, senior and youth from age 15.",
        },
        "group": "senior",
        "class_type": "class",
        "result_kind": "points",
    },
    {
        "id": "masters_combined_events",
        "name": {"no": "Masters mangekamp (NFIF)", "en": "Masters combined events (NFIF)"},
        "description": {
            "no": "Resultat × WMA-aldersfaktor for femårsklassen, deretter mangekamptabellen.",
            "en": "Result × WMA age factor for the five-year class, then the combined events "
            "table.",
        },
        "group": "masters",
        "class_type": "masters_class",
        "result_kind": "points",
    },
    {
        "id": "wma_age_grading",
        "name": {"no": "WMA aldersgradering", "en": "WMA age grading"},
        "description": {
            "no": "Aldersjustert resultat med ettårige WMA-faktorer. Gir ikke poeng eller prosent.",
            "en": "Age-graded result with WMA single-age factors. Gives no points or percentage.",
        },
        "group": "masters",
        "class_type": "age",
        "result_kind": "age_adjusted_result",
    },
    {
        "id": "series_table",
        "name": {"no": "Serietabellen", "en": "Norwegian series table"},
        "description": {
            "no": "Kommer når NFIF har bekreftet en offisiell kilde.",
            "en": "Coming when the federation has confirmed an official source.",
        },
        "group": "senior",
        "class_type": "class",
        "result_kind": "points",
    },
)

ROW_STATUSES = ("ok", "no_result", "ambiguous_implement", "implement_mismatch", "invalid")


@dataclass(frozen=True, slots=True)
class Target:
    """Systemet og klassen en forespørsel regnes i, og ``selection`` når ``auto`` valgte dem."""

    engine: ScoringEngine
    gender: Gender
    age_class: str
    selection: dict[str, Any] | None


class Service:
    def __init__(self, registry: Registry | None = None) -> None:
        self.registry = registry or default_registry()
        self._measure = lru_cache(maxsize=4096)(self._measure_uncached)
        self._events = lru_cache(maxsize=512)(self._events_uncached)
        self._systems: list[dict[str, Any]] | None = None

    # --- katalog -------------------------------------------------------------------------------

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "package_version": __version__, "systems": self.registry.systems()}

    def systems(self) -> list[dict[str, Any]]:
        if self._systems is None:
            self._systems = [self._system(info) for info in SYSTEM_INFO]
        return self._systems

    def _system(self, info: dict[str, Any]) -> dict[str, Any]:
        versions = self.registry.systems().get(info["id"], [])
        if not versions:
            return {
                **info,
                "ready": False,
                "classes": {"M": [], "F": []},
                "supports_combined": False,
                "latest_version": None,
                "versions": [],
            }
        latest = self.registry.get(info["id"])
        return {
            "id": info["id"],
            "name": info["name"],
            "description": info["description"],
            "group": info["group"],
            "ready": True,
            "class_type": info["class_type"],
            "classes": {g.value: _classes(latest, g) for g in Gender},
            "supports_combined": hasattr(latest, "calculate_combined"),
            "result_kind": info["result_kind"],
            "latest_version": latest.version,
            "versions": [
                {"version": v, "sources": self.registry.get(info["id"], v).sources()}
                for v in versions
            ],
        }

    def events(
        self, system: str, version: str | None, gender: str | None, age_class: str | None
    ) -> list[dict[str, Any]]:
        engine = self.registry.get(system, version)
        return self._events(engine.system, engine.version, gender, age_class)

    def _events_uncached(
        self, system: str, version: str, gender: str | None, age_class: str | None
    ) -> list[dict[str, Any]]:
        engine = self.registry.get(system, version)
        catalog = event_catalog()
        out = []
        for info in engine.list_events(None if gender is None else Gender(gender), age_class):
            entry = catalog[info.event_id]
            out.append(
                {
                    "system": engine.system,
                    "version": engine.version,
                    "event_id": info.event_id,
                    "name": {"no": info.event_name, "en": entry.name_en},
                    "category": entry.category,
                    "gender": info.gender.value,
                    "age_class": info.age_class,
                    "implement": info.implement,
                    "formula_type": info.formula_type,
                    "input": {
                        "measure": info.input.measure,
                        "resolution": info.input.resolution,
                        "uses_minutes": info.input.uses_minutes,
                        "manual_timing_allowed": info.input.manual_timing_allowed,
                        "plausible_min": info.input.plausible_min,
                        "plausible_max": info.input.plausible_max,
                    },
                    "points_1000_result": engine.points_1000_result(
                        info.event_id, info.gender, info.age_class, info.implement
                    ),
                }
            )
        return out

    # --- beregning -----------------------------------------------------------------------------

    def _target(
        self,
        system: str,
        version: str | None,
        gender: str,
        age_class: str | None,
        age: int | None,
    ) -> Target:
        g = Gender(gender)
        if system != AUTO:
            if age is not None:
                raise ApiError(
                    422, "validation_error", "Feltet age brukes bare med system auto.",
                    {"field": "age"},
                )
            if age_class is None:
                raise ApiError(
                    422, "validation_error", "Feltet age_class er påkrevd.", {"field": "age_class"}
                )
            return Target(self.registry.get(system, version), g, age_class, None)
        if age is None:
            raise ApiError(
                422, "validation_error", "Feltet age er påkrevd når system er auto.",
                {"field": "age"},
            )
        if age_class is not None:
            raise ApiError(
                422, "validation_error", "Feltet age_class brukes ikke med system auto.",
                {"field": "age_class"},
            )
        if age < 15:
            chosen, cls, rule = "tyrving", str(age), RULE_TYRVING
        elif age <= 17:
            chosen, cls, rule = "wa_combined_events", f"{'G' if g is Gender.MALE else 'J'}{age}", (
                RULE_COMBINED
            )
        else:
            chosen, cls, rule = "wa_combined_events", "senior", RULE_COMBINED
        selection = {
            "requested_system": AUTO,
            "age": age,
            "system": chosen,
            "age_class": cls,
            "rule": rule,
            "ref": SELECTION_REF,
        }
        return Target(self.registry.get(chosen, version), g, cls, selection)

    def _measure_uncached(
        self, system: str, version: str, gender: Gender, age_class: str, event_id: str
    ) -> str | None:
        engine = self.registry.get(system, version)
        measures = {
            e.input.measure for e in engine.list_events(gender, age_class) if e.event_id == event_id
        }
        return measures.pop() if len(measures) == 1 else None

    def _result(self, target: Target, event_id: str, value: float, manual: bool) -> Result:
        """``result`` er ett tall i kontrakten: meter for lengder, ellers sekunder totalt."""
        if value < 0:
            raise InvalidResultError("Resultatet kan ikke være negativt")
        measure = self._measure(
            target.engine.system, target.engine.version, target.gender, target.age_class, event_id
        )
        if measure == "distance":
            return Result(distance_meters=value, manual_timing=manual)
        return Result(time_seconds=value, manual_timing=manual)

    def _implements(self, target: Target, event_id: str) -> list[str]:
        return [
            e.implement
            for e in target.engine.list_events(target.gender, target.age_class)
            if e.event_id == event_id and e.implement is not None
        ]

    def calculate(self, req: CalculateRequest | BatchRow) -> dict[str, Any]:
        target = self._target(req.system, req.version, req.gender, req.age_class, req.age)
        assert req.result is not None
        result = self._result(target, req.event_id, req.result, req.manual_timing)
        try:
            score = target.engine.calculate(
                req.event_id, target.gender, target.age_class, result, implement=req.implement
            )
        except AmbiguousEventError as exc:
            raise ApiError(
                422,
                "ambiguous_implement",
                str(exc),
                {"implements": self._implements(target, req.event_id)},
            ) from exc
        out = serialize(score)
        if target.selection is not None:
            out["selection"] = target.selection
        return out

    def combined(self, req: CombinedRequest) -> dict[str, Any]:
        target = self._target(req.system, req.version, req.gender, req.age_class, req.age)
        calculate_combined = getattr(target.engine, "calculate_combined", None)
        if calculate_combined is None:
            raise InvalidCombinedEventError(
                f"{target.engine.system} har ikke mangekamp"
            )
        events = [
            CombinedEventInput(
                e.event_id, self._result(target, e.event_id, e.result, e.manual_timing), e.implement
            )
            for e in req.events
        ]
        combined = calculate_combined(target.gender, target.age_class, events)
        out: dict[str, Any] = {
            "total": combined.total,
            "scoring_system": combined.scoring_system,
            "version": combined.version,
            "gender": combined.gender.value,
            "age_class": combined.age_class,
            "events": [serialize(s) for s in combined.events],
        }
        if target.selection is not None:
            out["selection"] = target.selection
        return out

    def batch_row(self, row: BatchRow) -> dict[str, Any]:
        out: dict[str, Any] = {"row_id": row.row_id, "message": None, "error": None,
                               "calculation": None}
        if row.result is None:
            return {**out, "status": "no_result", "message": row.result_status}
        try:
            calculation = self.calculate(row)
        except ImplementMismatchError as exc:
            return {**out, "status": "implement_mismatch", "message": str(exc)}
        except ScoringError as exc:
            code = scoring_error_code(exc) or "internal_error"
            return {**out, "status": "invalid", "message": str(exc),
                    "error": error_body(code, str(exc))}
        except ApiError as exc:
            if exc.code == "ambiguous_implement":
                return {**out, "status": "ambiguous_implement", "message": exc.message}
            return {**out, "status": "invalid", "message": exc.message,
                    "error": error_body(exc.code, exc.message, exc.details)}
        return {**out, "status": "ok", "calculation": calculation}

    def batch(self, rows: list[BatchRow]) -> dict[str, Any]:
        results = [self.batch_row(row) for row in rows]
        statuses = [r["status"] for r in results]
        return {"summary": {s: statuses.count(s) for s in ROW_STATUSES}, "rows": results}


def _classes(engine: ScoringEngine, gender: Gender) -> list[str]:
    """Klassene i motorens rekkefølge, men aldre stigende."""
    classes = list(dict.fromkeys(e.age_class for e in engine.list_events(gender)))
    if all(c.isdigit() for c in classes):
        classes.sort(key=int)
    return classes


def serialize(score: ScoreResult) -> dict[str, Any]:
    """``ScoreResult`` som ``Calculation`` i kontrakten."""
    return {
        "points": score.points,
        "result_kind": "age_adjusted_result"
        if score.scoring_system == "wma_age_grading"
        else "points",
        "scoring_system": score.scoring_system,
        "version": score.version,
        "event_id": score.event_id,
        "event_name": score.event_name,
        "gender": score.gender.value,
        "age_class": score.age_class,
        "implement": score.implement,
        "result_used": score.result_used,
        "parameters": dict(score.parameters),
        "formula_type": score.formula_type,
        "calculation_detail": score.calculation_detail,
        "calculation_steps": [
            {"label": s.label, "value": s.value, "formula": s.formula, "ref": s.ref}
            for s in score.calculation_steps
        ],
        "within_plausible_range": score.within_plausible_range,
    }
