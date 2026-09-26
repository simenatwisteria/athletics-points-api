"""Tyrvingtabellen 2014 (NFIF), 10–19 år.

Parametrene leses fra ``data/tyrving_parameters_2014.json``. Regelteksten («Bruk av 2014-tabellen»):

- R1: manuell tid får tillegg før tabellen brukes: 100/110/200 m +0,24 s; 60/80/300 m +0,20 s;
  400 m +0,14 s. Tilleggene gjelder etter distanse, også for hekk. Løp over 500 m får ingen
  tillegg. 40 m har ingen regel og avvises.
- R2: til og med 500 m regnes i hundredeler; lengre løp i tideler, og hundredeler strykes.
- R3: alle desimaler beholdes; poengsummen rundes alltid ned. Negativ sum gir 0.
- R4: kast og stav bruker tre multiplikatorer: over 1000p-nivået, mellom 1000p og 80 %, og
  under 80 %.

All regning skjer med ``Decimal``, så resultatet er eksakt (beslutning 2026-09-26, AP-005).
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping
from decimal import ROUND_DOWN, Decimal
from functools import cached_property
from importlib import resources
from typing import Any, ClassVar

from athletics_scoring.engine import ScoringEngine
from athletics_scoring.errors import (
    AmbiguousEventError,
    InvalidResultError,
    UnknownEventError,
    UnsupportedManualTimingError,
)
from athletics_scoring.models import (
    CalculationStep,
    EventInfo,
    Gender,
    Parameters,
    Result,
    ScoreResult,
)

DATA_FILE = "tyrving_parameters_2014.json"

# R1: tillegg for manuell tid, etter distanse i meter (flatløp og hekk).
MANUAL_TIMING_ADDITION = {
    60: Decimal("0.20"),
    80: Decimal("0.20"),
    300: Decimal("0.20"),
    100: Decimal("0.24"),
    110: Decimal("0.24"),
    200: Decimal("0.24"),
    400: Decimal("0.14"),
}
EIGHTY_PERCENT = Decimal("0.8")


def _dec(value: float | int) -> Decimal:
    """Tall fra JSON eller input til Decimal via korteste desimalrepresentasjon (7.55 → '7.55')."""
    return Decimal(repr(value)) if isinstance(value, float) else Decimal(value)


def _fmt(value: Decimal) -> str:
    return format(value.normalize(), "f").replace(".", ",")


class TyrvingCalculator(ScoringEngine):
    system: ClassVar[str] = "tyrving"
    version: ClassVar[str] = "2014"

    @cached_property
    def _entries(self) -> list[dict[str, Any]]:
        text = resources.files("athletics_scoring").joinpath("data", DATA_FILE).read_text("utf-8")
        entries: list[dict[str, Any]] = json.loads(text)["entries"]
        return entries

    # --- oppslag -------------------------------------------------------------------------------

    def _find(
        self, event_id: str, gender: Gender, age_class: str, implement: str | None
    ) -> dict[str, Any]:
        try:
            age = int(age_class)
        except ValueError:
            raise UnknownEventError(
                f"Tyrving bruker alder 10–19 som klasse, ikke {age_class!r}"
            ) from None
        candidates = [
            e
            for e in self._entries
            if e["event_id"] == event_id and e["gender"] == gender.value and e["age"] == age
        ]
        if not candidates:
            raise UnknownEventError(
                f"{event_id} finnes ikke for {gender.value}{age} i Tyrving 2014"
            )
        if implement is not None:
            wanted = re.sub(r"\s+", "", implement)
            matching = [e for e in candidates if e["implement"] == wanted]
            if not matching:
                known = ", ".join(str(e["implement"]) for e in candidates)
                raise UnknownEventError(
                    f"{event_id} {gender.value}{age} finnes ikke med utstyr {implement!r} "
                    f"(kjente: {known})"
                )
            return matching[0]
        if len(candidates) > 1:
            known = ", ".join(str(e["implement"]) for e in candidates)
            raise AmbiguousEventError(
                f"{event_id} {gender.value}{age} finnes med flere utstyrsvarianter; "
                f"oppgi implement ({known})"
            )
        return candidates[0]

    def list_events(
        self, gender: Gender | None = None, age_class: str | None = None
    ) -> list[EventInfo]:
        return [
            EventInfo(
                event_id=e["event_id"],
                event_name=e["name"],
                gender=Gender(e["gender"]),
                age_class=str(e["age"]),
                formula_type=e["formula_type"],
                implement=e["implement"],
            )
            for e in self._entries
            if (gender is None or e["gender"] == gender.value)
            and (age_class is None or str(e["age"]) == age_class)
        ]

    def get_parameters(
        self, event_id: str, gender: Gender, age_class: str, implement: str | None = None
    ) -> Parameters:
        params: Mapping[str, float] = self._find(event_id, gender, age_class, implement)["params"]
        return dict(params)

    # --- beregning -----------------------------------------------------------------------------

    def _effective_result(
        self, entry: dict[str, Any], result: Result, steps: list[CalculationStep]
    ) -> Decimal:
        if entry["measure"] == "distance":
            if result.distance_meters is None or result.time_seconds is not None:
                raise InvalidResultError(f"{entry['event_id']} krever distanse (distance_meters)")
            value = _dec(result.distance_meters)
            if value <= 0:
                raise InvalidResultError("Resultatet må være større enn 0")
            if result.manual_timing:
                raise InvalidResultError("manual_timing gjelder bare løp")
            return value.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

        if result.time_seconds is None or result.distance_meters is not None:
            raise InvalidResultError(f"{entry['event_id']} krever tid (time_seconds)")
        value = _dec(result.time_minutes or 0) * 60 + _dec(result.time_seconds)
        if value <= 0:
            raise InvalidResultError("Resultatet må være større enn 0")

        if result.manual_timing and entry["scale"] == 100:
            distance = int(re.search(r"_(\d+)m$", entry["event_id"]).group(1))  # type: ignore[union-attr]
            if distance not in MANUAL_TIMING_ADDITION:
                raise UnsupportedManualTimingError(
                    f"Regelverket har ikke tillegg for manuell tid på {entry['name']}"
                )
            addition = MANUAL_TIMING_ADDITION[distance]
            value += addition
            steps.append(
                CalculationStep(
                    "manual_timing_addition", float(addition), "R1: tillegg for manuell tid"
                )
            )

        # R2: hundredeler til og med 500 m, tideler i lengre løp (hundredeler strykes).
        resolution = Decimal("0.01") if entry["scale"] == 100 else Decimal("0.1")
        return value.quantize(resolution, rounding=ROUND_DOWN)

    def calculate(
        self,
        event_id: str,
        gender: Gender,
        age_class: str,
        result: Result,
        implement: str | None = None,
    ) -> ScoreResult:
        entry = self._find(event_id, gender, age_class, implement)
        steps: list[CalculationStep] = []
        value = self._effective_result(entry, result, steps)
        params = {k: _dec(v) for k, v in entry["params"].items()}
        h1000 = params["h1000"]
        scale = Decimal(entry["scale"])

        if entry["formula_type"] == "three_interval":
            points_raw, detail = self._three_interval(value, h1000, params, scale, steps)
        else:
            difference = (h1000 - value) * scale
            sign = 1 if entry["measure"] == "time" else -1
            points_raw = 1000 + sign * difference * params["quotient"]
            op = "+" if sign == 1 else "−"
            detail = (
                f"1000 {op} ({_fmt(h1000 * scale)} − {_fmt(value * scale)}) × "
                f"{_fmt(params['quotient'])} = {_fmt(points_raw)}"
            )
            steps.append(
                CalculationStep(
                    "difference", float(difference), f"(h1000 − resultat) × {entry['scale']}"
                )
            )

        points = max(0, math.floor(points_raw))
        steps.append(CalculationStep("points_raw", float(points_raw), "før nedrunding"))
        steps.append(CalculationStep("points", float(points), "rundet ned, minst 0 (R3)"))
        return ScoreResult(
            points=points,
            scoring_system=self.system,
            version=self.version,
            event_id=entry["event_id"],
            event_name=entry["name"],
            gender=gender,
            age_class=str(entry["age"]),
            result_used=float(value),
            parameters=dict(entry["params"]),
            formula_type=entry["formula_type"],
            calculation_detail=f"{detail} → {points}",
            calculation_steps=tuple(steps),
            implement=entry["implement"],
        )

    @staticmethod
    def _three_interval(
        value: Decimal,
        h1000: Decimal,
        params: dict[str, Decimal],
        scale: Decimal,
        steps: list[CalculationStep],
    ) -> tuple[Decimal, str]:
        """R4: f1 over h1000, f2 mellom h1000 og 80 %, f3 under 80 %."""
        eighty = h1000 * EIGHTY_PERCENT
        steps.append(CalculationStep("eighty_percent", float(eighty), "0,8 × h1000"))
        f1, f2, f3 = params["f1"], params["f2"], params["f3"]
        if value >= h1000:
            points = 1000 + (value - h1000) * scale * f1
            detail = f"1000 + ({_fmt(value * scale)} − {_fmt(h1000 * scale)}) × {_fmt(f1)}"
        elif value >= eighty:
            points = 1000 - (h1000 - value) * scale * f2
            detail = f"1000 − ({_fmt(h1000 * scale)} − {_fmt(value * scale)}) × {_fmt(f2)}"
        else:
            points = 1000 - ((h1000 - eighty) * scale * f2 + (eighty - value) * scale * f3)
            detail = (
                f"1000 − (({_fmt(h1000 * scale)} − {_fmt(eighty * scale)}) × {_fmt(f2)} + "
                f"({_fmt(eighty * scale)} − {_fmt(value * scale)}) × {_fmt(f3)})"
            )
        return points, f"{detail} = {_fmt(points)}"
