"""WMA Age Grading 2023: aldersjustert resultat med ettårige aldersfaktorer (BV-040).

Resultatet ganges med faktoren for utøverens alder i hele år (30–110), og produktet rundes opp til
hundredeler for løp og ned til hel centimeter for hopp og kast (BV-042, som BV-031). Motoren gir
**ikke** prosent eller poeng, fordi kilden ikke har standarder å dele på (BV-041). ``points`` er
derfor alltid 0, og det aldersjusterte resultatet står i ``result_used``.

Faktorene leses fra ``data/wma_age_factors_2023.json``. Klassen er alderen som tekst, f.eks.
``"45"``.
Faktoren brukes slik den står: den kan være over eller under 1 for både løp og kast, fordi den også
tar hensyn til lettere redskap og lavere hekker. «Kort hekk» og «Lang hekk» er kolonnene «Short
Hurdles» og «Long Hurdles» i kilden, som ikke oppgir distansen per alder.
"""

from __future__ import annotations

import json
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from functools import cached_property
from importlib import resources
from typing import Any, ClassVar

from athletics_scoring.engine import ScoringEngine
from athletics_scoring.errors import (
    InvalidResultError,
    UnknownEventError,
    UnsupportedManualTimingError,
)
from athletics_scoring.models import (
    CalculationStep,
    EventInfo,
    Gender,
    InputSpec,
    Parameters,
    Result,
    ScoreResult,
)

DATA_FILE = "wma_age_factors_2023.json"
CENTIMETRE = Decimal("0.01")
FORMULA_TYPE = "age_factor"
# Rimelig område for resultatet (sekunder eller meter), fra toppnivå for 30-åringer til sakte
# resultater for de eldste. Brukerhjelp for inndatafeltet, ikke fra kilden, og påvirker ikke
# beregningen.
PLAUSIBLE_RANGE: dict[str, tuple[float, float]] = {
    "sprint_60m": (6.0, 30.0),
    "sprint_100m": (9.5, 45.0),
    "sprint_200m": (19.0, 90.0),
    "sprint_400m": (43.0, 240.0),
    "middle_800m": (100.0, 480.0),
    "middle_1000m": (130.0, 600.0),
    "middle_1500m": (205.0, 900.0),
    "middle_mile": (220.0, 960.0),
    "distance_3000m": (440.0, 1800.0),
    "distance_5000m": (750.0, 3000.0),
    "distance_10000m": (1560.0, 6000.0),
    "hurdles_60m": (7.0, 30.0),
    "hurdles_short": (12.0, 50.0),
    "hurdles_long": (22.0, 180.0),
    "steeplechase": (240.0, 1500.0),
    "high_jump": (0.5, 2.5),
    "pole_vault": (1.0, 6.5),
    "long_jump": (1.5, 9.0),
    "triple_jump": (4.0, 18.5),
    "shot_put": (2.0, 23.5),
    "discus": (5.0, 75.0),
    "hammer": (5.0, 87.0),
    "javelin": (5.0, 100.0),
    "weight_throw": (3.0, 26.0),
    "racewalk_3000m": (640.0, 2400.0),
    "racewalk_5000m": (1100.0, 3600.0),
    "racewalk_10000m": (2280.0, 7200.0),
    "racewalk_20000m": (4680.0, 14400.0),
    "half_marathon": (3450.0, 14400.0),
    "marathon": (7200.0, 28800.0),
}
# Øvelser der tiden naturlig oppgis i sekunder. Resten oppgis i minutter og sekunder.
SECONDS_ONLY = {"sprint_60m", "sprint_100m", "sprint_200m", "sprint_400m", "hurdles_60m",
                "hurdles_short", "hurdles_long"}  # fmt: skip


def _dec(value: float | int) -> Decimal:
    return Decimal(repr(value)) if isinstance(value, float) else Decimal(value)


def _fmt(value: Decimal) -> str:
    return format(value.normalize(), "f").replace(".", ",")


class WmaAgeGradingCalculator(ScoringEngine):
    system: ClassVar[str] = "wma_age_grading"
    version: ClassVar[str] = "2023"

    @cached_property
    def _data(self) -> dict[str, Any]:
        text = resources.files("athletics_scoring").joinpath("data", DATA_FILE).read_text("utf-8")
        data: dict[str, Any] = json.loads(text)
        return data

    @cached_property
    def _entries(self) -> dict[tuple[str, str], dict[str, Any]]:
        return {(e["gender"], e["event_id"]): e for e in self._data["entries"]}

    def sources(self) -> list[dict[str, Any]]:
        return [dict(doc) for doc in self._data["meta"]["source_documents"]]

    def ages(self) -> list[str]:
        """Aldrene motoren tar imot: ``"30"`` … ``"110"`` (BV-040)."""
        first, last = self._data["meta"]["ages"]
        return [str(age) for age in range(first, last + 1)]

    # --- oppslag -------------------------------------------------------------------------------

    def _find(
        self, event_id: str, gender: Gender, age_class: str
    ) -> tuple[dict[str, Any], Decimal]:
        entry = self._entries.get((gender.value, event_id))
        if entry is None:
            raise UnknownEventError(f"{event_id} finnes ikke for {gender.value} i WMA Age Grading")
        factor = entry["factors"].get(age_class)
        if factor is None:
            first, last = self._data["meta"]["ages"]
            raise UnknownEventError(
                f"WMA Age Grading har faktorer for alder {first}–{last} i hele år, "
                f"ikke {age_class!r} (BV-040)"
            )
        return entry, _dec(factor)

    @staticmethod
    def _check_implement(entry: dict[str, Any], implement: str | None) -> None:
        if implement is not None:
            raise UnknownEventError(
                f"{entry['name']}: faktorene i WMA Age Grading gjelder redskapet for alderen, "
                f"og tar ikke imot redskap ({implement!r})"
            )

    @staticmethod
    def _input_spec(entry: dict[str, Any]) -> InputSpec:
        lower, upper = PLAUSIBLE_RANGE[entry["event_id"]]
        is_time = entry["measure"] == "time"
        return InputSpec(
            entry["measure"],
            float(CENTIMETRE),
            uses_minutes=is_time and entry["event_id"] not in SECONDS_ONLY,
            manual_timing_allowed=False,
            plausible_min=lower,
            plausible_max=upper,
        )

    def list_events(
        self, gender: Gender | None = None, age_class: str | None = None
    ) -> list[EventInfo]:
        genders = [gender] if gender is not None else list(Gender)
        ages = self.ages() if age_class is None else [age_class]
        return [
            EventInfo(
                event_id=e["event_id"],
                event_name=e["name"],
                gender=g,
                age_class=age,
                formula_type=FORMULA_TYPE,
                input=self._input_spec(e),
            )
            for g in genders
            for age in ages
            for e in self._data["entries"]
            if e["gender"] == g.value and age in e["factors"]
        ]

    def get_parameters(
        self, event_id: str, gender: Gender, age_class: str, implement: str | None = None
    ) -> Parameters:
        entry, factor = self._find(event_id, gender, age_class)
        self._check_implement(entry, implement)
        return {"age_factor": float(factor)}

    # --- beregning -----------------------------------------------------------------------------

    @staticmethod
    def _value(entry: dict[str, Any], result: Result) -> Decimal:
        if result.manual_timing:
            raise UnsupportedManualTimingError(
                "WMA Age Grading har ingen regel for manuell tid. Oppgi tiden slik den skal brukes"
            )
        if entry["measure"] == "distance":
            if result.distance_meters is None or result.time_seconds is not None:
                raise InvalidResultError(f"{entry['event_id']} krever distanse (distance_meters)")
            value = _dec(result.distance_meters)
        else:
            if result.time_seconds is None or result.distance_meters is not None:
                raise InvalidResultError(f"{entry['event_id']} krever tid (time_seconds)")
            value = _dec(result.time_minutes or 0) * 60 + _dec(result.time_seconds)
        if value <= 0:
            raise InvalidResultError("Resultatet må være større enn 0")
        return value

    def calculate(
        self,
        event_id: str,
        gender: Gender,
        age_class: str,
        result: Result,
        implement: str | None = None,
    ) -> ScoreResult:
        """Aldersjustert resultat i ``result_used``. ``points`` er alltid 0 (BV-041)."""
        entry, factor = self._find(event_id, gender, age_class)
        self._check_implement(entry, implement)
        is_time = entry["measure"] == "time"
        value = self._value(entry, result)

        product = value * factor
        adjusted = product.quantize(CENTIMETRE, rounding=ROUND_CEILING if is_time else ROUND_FLOOR)
        expression = f"{_fmt(value)} × {_fmt(factor)} = {_fmt(product)}"
        steps = (
            CalculationStep(
                "input", float(value), "tid i sekunder" if is_time else "resultat i meter"
            ),
            CalculationStep(
                "age", float(age_class), "alder i hele år på konkurransedagen", ref="BV-040"
            ),
            CalculationStep(
                "age_factor",
                float(factor),
                f"ettårig aldersfaktor for {age_class} år, {entry['source']['location']}",
                ref=entry["source"]["ref"],
            ),
            CalculationStep(
                "age_adjusted",
                float(product),
                f"{expression}, aldersjustert resultat, ikke prosent",
                ref="BV-041",
            ),
            CalculationStep(
                "age_adjusted_rounded",
                float(adjusted),
                "rundet opp til hundredeler" if is_time else "rundet ned til hel centimeter",
                ref="BV-042",
            ),
        )
        lower, upper = PLAUSIBLE_RANGE[event_id]
        return ScoreResult(
            points=0,
            scoring_system=self.system,
            version=self.version,
            event_id=event_id,
            event_name=entry["name"],
            gender=gender,
            age_class=age_class,
            result_used=float(adjusted),
            parameters={"age_factor": float(factor)},
            formula_type=FORMULA_TYPE,
            calculation_detail=f"{expression} → {_fmt(adjusted)}",
            calculation_steps=steps,
            within_plausible_range=lower <= float(value) <= upper,
        )
