"""IAAF/WA Scoring Tables for Combined Events (2001, opptrykk 2016), senior og ungdom fra 15 år.

Parametrene leses fra ``data/wa_combined_events_2001.json``. Formlene (WMA Appendix B s. 2):

- løp: ``a · (b − T)^c``, T i sekunder
- hopp: ``a · (M − b)^c``, M i centimeter
- kast: ``a · (D − b)^c``, D i meter

Poengene avkortes til heltall, og er differansen 0 eller negativ, blir poengene 0 (BV-003).
Manuell tid får tillegg før tabellen brukes (BV-024), og input rundes til tabellens oppløsning
(BV-025). Fra 15 år gjelder tabellen også ungdom (BV-021), og NFIF har fire tilleggsøvelser for
noen ungdomsklasser (BV-023).

All regning skjer med ``Decimal`` (BV-004). Potensen regnes som ``exp(c · ln(x))`` med 40 sifre.
"""

from __future__ import annotations

import json
import math
import re
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal, localcontext
from functools import cached_property
from importlib import resources
from typing import Any, ClassVar

from athletics_scoring.engine import ScoringEngine
from athletics_scoring.errors import (
    InvalidCombinedEventError,
    InvalidResultError,
    UnknownEventError,
)
from athletics_scoring.models import (
    CalculationStep,
    CombinedEventInput,
    CombinedScoreResult,
    EventInfo,
    Gender,
    InputSpec,
    Parameters,
    Result,
    ScoreResult,
)

DATA_FILE = "wa_combined_events_2001.json"
SENIOR = "senior"
# BV-024: tillegg for manuell tid etter distanse. Til og med 300 m +0,24 s, 400 m +0,14 s,
# lengre løp ingen tillegg.
MANUAL_TIMING_SHORT = Decimal("0.24")
MANUAL_TIMING_400M = Decimal("0.14")
CENTIMETRE = Decimal("0.01")
PRECISION = 40
# Rimelig område som andel av resultatet for 1000 poeng, som Tyrving (BV-014). Brukerhjelp.
PLAUSIBLE_RANGE = {
    "time": (Decimal("0.6"), Decimal("3.0")),
    "distance": (Decimal("0.2"), Decimal("1.6")),
}


def _dec(value: float | int) -> Decimal:
    """Tall fra JSON eller input til Decimal via korteste desimalrepresentasjon (7.55 → '7.55')."""
    return Decimal(repr(value)) if isinstance(value, float) else Decimal(value)


def _fmt(value: Decimal) -> str:
    return format(value.normalize(), "f").replace(".", ",")


def _distance(event_id: str) -> int | None:
    match = re.search(r"_(\d+)m$", event_id)
    return int(match.group(1)) if match else None


def _manual_timing_addition(event_id: str) -> Decimal:
    distance = _distance(event_id)
    if distance is None or distance > 400:
        return Decimal(0)
    return MANUAL_TIMING_400M if distance == 400 else MANUAL_TIMING_SHORT


def _power(base: Decimal, exponent: Decimal) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PRECISION
        return (base.ln() * exponent).exp()


def _formula(a: Decimal, difference: Decimal, c: Decimal) -> Decimal:
    """``a · difference^c``, eller 0 når differansen er 0 eller negativ (BV-003)."""
    if difference <= 0:
        return Decimal(0)
    with localcontext() as ctx:
        ctx.prec = PRECISION
        return a * _power(difference, c)


def _unit_factor(entry: dict[str, Any]) -> Decimal:
    """Hopp regnes i centimeter, alt annet i enheten resultatet oppgis i."""
    return Decimal(100) if entry["unit"] == "cm" else Decimal(1)


def _result_for_1000(entry: dict[str, Any]) -> Decimal:
    """Resultatet (sekunder eller meter) som gir nøyaktig 1000 poeng, for det rimelige området."""
    a, b, c = (_dec(entry["params"][k]) for k in ("a", "b", "c"))
    with localcontext() as ctx:
        ctx.prec = PRECISION
        span = _power(Decimal(1000) / a, 1 / c)
        value = b - span if entry["measure"] == "time" else b + span
        return value / _unit_factor(entry)


def _plausible_range(entry: dict[str, Any]) -> tuple[Decimal, Decimal]:
    low, high = PLAUSIBLE_RANGE[entry["measure"]]
    level = _result_for_1000(entry)
    lower = (level * low / CENTIMETRE).to_integral_value(rounding=ROUND_CEILING) * CENTIMETRE
    upper = (level * high / CENTIMETRE).to_integral_value(rounding=ROUND_FLOOR) * CENTIMETRE
    return lower, upper


def _input_spec(entry: dict[str, Any]) -> InputSpec:
    lower, upper = _plausible_range(entry)
    is_time = entry["measure"] == "time"
    distance = _distance(entry["event_id"]) or 0
    return InputSpec(
        entry["measure"],
        float(CENTIMETRE),
        uses_minutes=is_time and distance >= 600,
        manual_timing_allowed=is_time and distance <= 400,
        plausible_min=float(lower),
        plausible_max=float(upper),
    )


def effective_result(
    entry: dict[str, Any], result: Result, steps: list[CalculationStep]
) -> Decimal:
    """Resultatet slik tabellen bruker det: kontrollert, rundet (BV-025) og med tillegg for
    manuell tid (BV-024). ``entry`` trenger ``event_id`` og ``measure``. Stegene legges i ``steps``.
    """
    if entry["measure"] == "distance":
        if result.distance_meters is None or result.time_seconds is not None:
            raise InvalidResultError(f"{entry['event_id']} krever distanse (distance_meters)")
        if result.manual_timing:
            raise InvalidResultError("manual_timing gjelder bare løp")
        value = _dec(result.distance_meters)
        if value <= 0:
            raise InvalidResultError("Resultatet må være større enn 0")
        steps.append(CalculationStep("input", float(value), "resultat i meter"))
        rounded = value.quantize(CENTIMETRE, rounding=ROUND_FLOOR)
        if rounded != value:
            steps.append(
                CalculationStep(
                    "rounded", float(rounded), "rundet ned til hel centimeter", ref="BV-025"
                )
            )
        return rounded

    if result.time_seconds is None or result.distance_meters is not None:
        raise InvalidResultError(f"{entry['event_id']} krever tid (time_seconds)")
    value = _dec(result.time_minutes or 0) * 60 + _dec(result.time_seconds)
    if value <= 0:
        raise InvalidResultError("Resultatet må være større enn 0")
    steps.append(CalculationStep("input", float(value), "tid i sekunder"))
    rounded = value.quantize(CENTIMETRE, rounding=ROUND_CEILING)
    if rounded != value:
        steps.append(
            CalculationStep("rounded", float(rounded), "rundet opp til hundredeler", ref="BV-025")
        )
    if result.manual_timing:
        addition = _manual_timing_addition(entry["event_id"])
        rounded += addition
        steps.append(
            CalculationStep(
                "manual_timing_addition",
                float(addition),
                "tillegg for manuell tid"
                if addition
                else "manuell tid over 400 m får ikke tillegg",
                ref="BV-024",
            )
        )
    return rounded


class CombinedEventsCalculator(ScoringEngine):
    system: ClassVar[str] = "wa_combined_events"
    version: ClassVar[str] = "2001"

    @cached_property
    def _data(self) -> dict[str, Any]:
        text = resources.files("athletics_scoring").joinpath("data", DATA_FILE).read_text("utf-8")
        data: dict[str, Any] = json.loads(text)
        return data

    @property
    def _entries(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = self._data["entries"]
        return entries

    def sources(self) -> list[dict[str, Any]]:
        return [dict(doc) for doc in self._data["meta"]["source_documents"]]

    def age_classes(self, gender: Gender) -> list[str]:
        """Klassene motoren tar imot: ``"senior"`` og ungdomsklassene fra 15 år (BV-021)."""
        return [SENIOR, *self._data["meta"]["youth_classes"][gender.value]]

    # --- oppslag -------------------------------------------------------------------------------

    @staticmethod
    def _applies(entry: dict[str, Any], age_class: str) -> bool:
        return entry["classes"] is None or age_class in entry["classes"]

    def _find(self, event_id: str, gender: Gender, age_class: str) -> dict[str, Any]:
        classes = self.age_classes(gender)
        if age_class not in classes:
            raise UnknownEventError(
                f"Mangekamptabellen tar imot klassene {', '.join(classes)} for {gender.value}, "
                f"ikke {age_class!r}"
            )
        for entry in self._entries:
            if entry["event_id"] == event_id and entry["gender"] == gender.value:
                if not self._applies(entry, age_class):
                    raise UnknownEventError(
                        f"{entry['name']} regnes med mangekamptabellen bare for "
                        f"{', '.join(entry['classes'])}, ikke {age_class}"
                    )
                return entry
        raise UnknownEventError(f"{event_id} finnes ikke for {gender.value} i mangekamptabellen")

    def list_events(
        self, gender: Gender | None = None, age_class: str | None = None
    ) -> list[EventInfo]:
        genders = [gender] if gender is not None else list(Gender)
        return [
            EventInfo(
                event_id=e["event_id"],
                event_name=e["name"],
                gender=g,
                age_class=cls,
                formula_type=e["formula_type"],
                input=_input_spec(e),
            )
            for g in genders
            for cls in self.age_classes(g)
            if age_class is None or cls == age_class
            for e in self._entries
            if e["gender"] == g.value and self._applies(e, cls)
        ]

    def get_parameters(
        self, event_id: str, gender: Gender, age_class: str, implement: str | None = None
    ) -> Parameters:
        return dict(self._find(event_id, gender, age_class)["params"])

    # --- beregning -----------------------------------------------------------------------------

    def calculate(
        self,
        event_id: str,
        gender: Gender,
        age_class: str,
        result: Result,
        implement: str | None = None,
    ) -> ScoreResult:
        """Poeng for ``result``. ``implement`` brukes ikke: tabellen er lik uansett redskap."""
        entry = self._find(event_id, gender, age_class)
        steps: list[CalculationStep] = []
        value = effective_result(entry, result, steps)
        a, b, c = (_dec(entry["params"][k]) for k in ("a", "b", "c"))
        unit = entry["unit"]
        measured = value * _unit_factor(entry)
        difference = b - measured if entry["measure"] == "time" else measured - b
        if entry["measure"] == "time":
            expression = f"{_fmt(a)} × ({_fmt(b)} − {_fmt(measured)})^{_fmt(c)}"
        else:
            expression = f"{_fmt(a)} × ({_fmt(measured)} − {_fmt(b)})^{_fmt(c)}"
        steps.append(
            CalculationStep(
                "difference",
                float(difference),
                f"{'b − T' if entry['measure'] == 'time' else 'X − b'} i {unit}",
            )
        )

        points_raw = _formula(a, difference, c)
        points = max(0, math.floor(points_raw))
        shown = _fmt(points_raw.quantize(Decimal("0.0001"), rounding=ROUND_FLOOR))
        steps.append(
            CalculationStep(
                "points_raw",
                float(points_raw),
                f"{expression} = {shown}",
                ref=entry["source"]["ref"],
            )
        )
        steps.append(
            CalculationStep("points", float(points), "avkortet til heltall, minst 0", ref="BV-003")
        )
        lower, upper = _plausible_range(entry)
        return ScoreResult(
            points=points,
            scoring_system=self.system,
            version=self.version,
            event_id=entry["event_id"],
            event_name=entry["name"],
            gender=gender,
            age_class=age_class,
            result_used=float(value),
            parameters=dict(entry["params"]),
            formula_type=entry["formula_type"],
            calculation_detail=f"{expression} = {shown} → {points}",
            calculation_steps=tuple(steps),
            within_plausible_range=lower <= value <= upper,
        )

    def calculate_combined(
        self, gender: Gender, age_class: str, events: list[CombinedEventInput]
    ) -> CombinedScoreResult:
        """Mangekamp: summen av poengene for fritt valgte øvelser. Faste program kommer senere."""
        if not events:
            raise InvalidCombinedEventError("Mangekampen må ha minst én øvelse")
        ids = [e.event_id for e in events]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise InvalidCombinedEventError(f"Samme øvelse flere ganger: {', '.join(duplicates)}")
        scores = tuple(self.calculate(e.event_id, gender, age_class, e.result) for e in events)
        return CombinedScoreResult(
            total=sum(s.points for s in scores),
            scoring_system=self.system,
            version=self.version,
            gender=gender,
            age_class=age_class,
            events=scores,
        )
