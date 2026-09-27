"""Masters mangekamp etter WMA Appendix B (2023), med NFIFs masters-tabeller som fasit (BV-035).

Metoden (BV-030, Appendix B s. 1):

1. manuell tid får tillegg først (BV-024)
2. resultatet ganges med aldersfaktoren for 5-årsklassen (BV-032)
3. det aldersjusterte resultatet rundes opp til 0,01 s for løp og ned til hel cm for hopp og kast
   (BV-031)
4. poengene slås opp i IAAF/WA Combined Events-tabellen for senior, som avkorter til heltall

Parametrene leses fra ``data/masters_combined_events_2023.json``. Klassen oppgis direkte, f.eks.
``"M50"`` eller ``"W65"`` (BV-033). Redskap og hekkehøyde er gitt av klassen (BV-034). Masters-hekk
under senior-distansen slås opp i tabellen for 110 m hekk (menn) eller 100 m hekk (kvinner).
"""

from __future__ import annotations

import json
import re
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from functools import cached_property
from importlib import resources
from typing import Any, ClassVar

from athletics_scoring.engine import ScoringEngine
from athletics_scoring.errors import InvalidCombinedEventError, UnknownEventError
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
from athletics_scoring.wa_combined_events import (
    SENIOR,
    CombinedEventsCalculator,
    effective_result,
)

DATA_FILE = "masters_combined_events_2023.json"
CENTIMETRE = Decimal("0.01")
IMPLEMENT_RE = re.compile(r"^(\d+(?:[.,]\d+)?)(kg|g|cm)$")


def _dec(value: float) -> Decimal:
    return Decimal(repr(value))


def _fmt(value: Decimal) -> str:
    return format(value.normalize(), "f").replace(".", ",")


def _distance(event_id: str) -> int:
    match = re.search(r"_(\d+)m$", event_id)
    return int(match.group(1)) if match else 0


def _implement_value(text: str) -> tuple[Decimal, str] | None:
    """'7,26 kg' → (7.26, 'kg'), '800g' → (0.8, 'kg'), '84cm' → (84, 'cm')."""
    match = IMPLEMENT_RE.match(re.sub(r"\s+", "", text).lower())
    if match is None:
        return None
    value, unit = Decimal(match.group(1).replace(",", ".")), match.group(2)
    return (value / 1000, "kg") if unit == "g" else (value, unit)


class MastersCombinedCalculator(ScoringEngine):
    system: ClassVar[str] = "masters_combined_events"
    version: ClassVar[str] = "2023"

    def __init__(self, table: CombinedEventsCalculator | None = None) -> None:
        self._table = table or CombinedEventsCalculator()

    @cached_property
    def _data(self) -> dict[str, Any]:
        text = resources.files("athletics_scoring").joinpath("data", DATA_FILE).read_text("utf-8")
        data: dict[str, Any] = json.loads(text)
        return data

    @property
    def _entries(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = self._data["entries"]
        return entries

    @cached_property
    def _table_events(self) -> dict[tuple[str, str], EventInfo]:
        """Senior-tabellens øvelser per (kjønn, øvelse): formeltype, måltype og rimelig område."""
        return {(e.gender.value, e.event_id): e for e in self._table.list_events(age_class=SENIOR)}

    def sources(self) -> list[dict[str, Any]]:
        return [dict(doc) for doc in self._data["meta"]["source_documents"]]

    def age_classes(self, gender: Gender) -> list[str]:
        """Klassene motoren tar imot, f.eks. ``"M35"`` … ``"M100"`` (BV-032, BV-033)."""
        classes: list[str] = self._data["meta"]["age_classes"][gender.value]
        return list(classes)

    # --- oppslag -------------------------------------------------------------------------------

    def _find(
        self, event_id: str, gender: Gender, age_class: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        classes = self.age_classes(gender)
        if age_class not in classes:
            raise UnknownEventError(
                f"Masters mangekamp tar imot klassene {', '.join(classes)} for {gender.value}, "
                f"ikke {age_class!r}"
            )
        for entry in self._entries:
            if entry["event_id"] == event_id and entry["gender"] == gender.value:
                info = entry["classes"].get(age_class)
                if info is None:
                    raise UnknownEventError(
                        f"{entry['name']} finnes i masters mangekamp bare for "
                        f"{', '.join(entry['classes'])}, ikke {age_class}"
                    )
                return entry, info
        raise UnknownEventError(f"{event_id} finnes ikke for {gender.value} i masters mangekamp")

    @staticmethod
    def _check_implement(
        entry: dict[str, Any], info: dict[str, Any], age_class: str, implement: str | None
    ) -> None:
        """Redskapet er gitt av klassen. Et annet redskap avvises (BV-034)."""
        if implement is None:
            return
        own = info["implement"]
        if own is None:
            raise UnknownEventError(
                f"{entry['name']} har ikke redskap eller hekkehøyde, fikk {implement!r}"
            )
        given = _implement_value(implement)
        if given is None or given != _implement_value(own):
            raise UnknownEventError(
                f"{age_class} bruker {own} i {entry['name'].lower()}, ikke {implement!r}. "
                "Aldersfaktoren gjelder bare klassens redskap (BV-034)"
            )

    def _input_spec(self, entry: dict[str, Any], factor: Decimal) -> InputSpec:
        """Senior-tabellens rimelige område delt på aldersfaktoren."""
        table = self._table_events[(entry["gender"], entry["table_event_id"])].input
        distance = _distance(entry["event_id"])
        is_time = table.measure == "time"
        lower = (_dec(table.plausible_min) / factor / CENTIMETRE).to_integral_value(ROUND_CEILING)
        upper = (_dec(table.plausible_max) / factor / CENTIMETRE).to_integral_value(ROUND_FLOOR)
        return InputSpec(
            table.measure,
            table.resolution,
            uses_minutes=is_time and distance >= 600,
            manual_timing_allowed=is_time and distance <= 400,
            plausible_min=float(lower * CENTIMETRE),
            plausible_max=float(upper * CENTIMETRE),
        )

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
                formula_type=self._table_events[(g.value, e["table_event_id"])].formula_type,
                input=self._input_spec(e, _dec(e["classes"][cls]["factor"])),
                implement=e["classes"][cls]["implement"],
            )
            for g in genders
            for cls in self.age_classes(g)
            if age_class is None or cls == age_class
            for e in self._entries
            if e["gender"] == g.value and cls in e["classes"]
        ]

    def get_parameters(
        self, event_id: str, gender: Gender, age_class: str, implement: str | None = None
    ) -> Parameters:
        entry, info = self._find(event_id, gender, age_class)
        self._check_implement(entry, info, age_class, implement)
        params = self._table.get_parameters(entry["table_event_id"], gender, SENIOR)
        return {**params, "age_factor": info["factor"]}

    # --- beregning -----------------------------------------------------------------------------

    def calculate(
        self,
        event_id: str,
        gender: Gender,
        age_class: str,
        result: Result,
        implement: str | None = None,
    ) -> ScoreResult:
        """Poeng for ``result``. ``implement`` kan utelates; oppgis det, må det være klassens."""
        entry, info = self._find(event_id, gender, age_class)
        self._check_implement(entry, info, age_class, implement)
        measure = self._table_events[(gender.value, entry["table_event_id"])].input.measure
        is_time = measure == "time"

        steps: list[CalculationStep] = []
        value = effective_result({"event_id": event_id, "measure": measure}, result, steps)
        factor = _dec(info["factor"])
        steps.append(
            CalculationStep(
                "age_factor",
                float(factor),
                f"aldersfaktor for {age_class}, «{entry['factor_column']}» "
                f"({entry['source']['location']}), BV-030/BV-032",
                ref=entry["source"]["ref"],
            )
        )
        product = value * factor
        steps.append(
            CalculationStep(
                "age_adjusted",
                float(product),
                f"{_fmt(value)} × {_fmt(factor)} = {_fmt(product)}",
                ref="BV-030",
            )
        )
        adjusted = product.quantize(CENTIMETRE, rounding=ROUND_CEILING if is_time else ROUND_FLOOR)
        steps.append(
            CalculationStep(
                "age_adjusted_rounded",
                float(adjusted),
                "rundet opp til hundredeler" if is_time else "rundet ned til hel centimeter",
                ref="BV-031",
            )
        )

        table_result = Result(
            time_seconds=float(adjusted) if is_time else None,
            distance_meters=None if is_time else float(adjusted),
        )
        score = self._table.calculate(entry["table_event_id"], gender, SENIOR, table_result)
        steps += [s for s in score.calculation_steps if s.label != "input"]
        return ScoreResult(
            points=score.points,
            scoring_system=self.system,
            version=self.version,
            event_id=event_id,
            event_name=entry["name"],
            gender=gender,
            age_class=age_class,
            result_used=float(adjusted),
            parameters={**score.parameters, "age_factor": info["factor"]},
            formula_type=score.formula_type,
            calculation_detail=(
                f"{_fmt(value)} × {_fmt(factor)} = {_fmt(product)} → {_fmt(adjusted)}; "
                f"{score.calculation_detail}"
            ),
            calculation_steps=tuple(steps),
            implement=info["implement"],
            within_plausible_range=score.within_plausible_range,
        )

    def calculate_combined(
        self, gender: Gender, age_class: str, events: list[CombinedEventInput]
    ) -> CombinedScoreResult:
        """Mangekamp: summen av poengene for fritt valgte øvelser, som i AP-012."""
        if not events:
            raise InvalidCombinedEventError("Mangekampen må ha minst én øvelse")
        ids = [e.event_id for e in events]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise InvalidCombinedEventError(f"Samme øvelse flere ganger: {', '.join(duplicates)}")
        scores = tuple(
            self.calculate(e.event_id, gender, age_class, e.result, implement=e.implement)
            for e in events
        )
        return CombinedScoreResult(
            total=sum(s.points for s in scores),
            scoring_system=self.system,
            version=self.version,
            gender=gender,
            age_class=age_class,
            events=scores,
        )
