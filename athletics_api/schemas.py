"""Forespørslene i kontrakten. Svarene bygges som dicts i ``service.py``."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SystemSelector = Literal["auto", "tyrving", "wa_combined_events", "masters_combined_events",
                         "wma_age_grading"]
GenderCode = Literal["M", "F"]

MAX_BATCH_ROWS = 2000


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CalculateRequest(_Strict):
    system: SystemSelector
    version: str | None = None
    event_id: str
    gender: GenderCode
    age_class: str | None = None
    age: int | None = Field(default=None, ge=10, le=110)
    implement: str | None = None
    result: float = Field(strict=True)
    manual_timing: bool = False


class CombinedEventRequest(_Strict):
    event_id: str
    implement: str | None = None
    result: float = Field(strict=True)
    manual_timing: bool = False


class CombinedRequest(_Strict):
    system: SystemSelector
    version: str | None = None
    gender: GenderCode
    age_class: str | None = None
    age: int | None = Field(default=None, ge=10, le=110)
    events: list[CombinedEventRequest] = Field(min_length=1, max_length=20)


class BatchRow(_Strict):
    row_id: str | None = None
    system: SystemSelector
    version: str | None = None
    event_id: str
    gender: GenderCode
    age_class: str | None = None
    age: int | None = Field(default=None, ge=10, le=110)
    implement: str | None = None
    result: float | None = Field(strict=True)
    result_status: str | None = None
    manual_timing: bool = False


class BatchRequest(_Strict):
    rows: list[BatchRow] = Field(min_length=1, max_length=MAX_BATCH_ROWS)
