"""Endepunktene under ``/api/v1``. Hver rute oversetter og kaller ``Service``, ingenting mer."""

from typing import Annotated, Any

from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import JSONResponse

from athletics_api.errors import error_response
from athletics_api.schemas import BatchRequest, CalculateRequest, CombinedRequest, GenderCode
from athletics_api.service import Service

CACHE_IMMUTABLE = "public, max-age=31536000, immutable"
CACHE_NONE = "no-cache"

router = APIRouter(prefix="/api/v1")


def _service(request: Request) -> Service:
    service: Service = request.app.state.service
    return service


def _cache(response: Response, versioned: bool) -> None:
    """B-7: svar med oppgitt versjon endres aldri."""
    response.headers["Cache-Control"] = CACHE_IMMUTABLE if versioned else CACHE_NONE


@router.get("/health", tags=["drift"])
def health(request: Request) -> dict[str, Any]:
    return _service(request).health()


@router.get("/systems", tags=["katalog"])
def systems(request: Request) -> list[dict[str, Any]]:
    return _service(request).systems()


@router.get("/events", tags=["katalog"])
def events(
    request: Request,
    system: Annotated[str, Query()],
    version: Annotated[str | None, Query()] = None,
    gender: Annotated[GenderCode | None, Query()] = None,
    age_class: Annotated[str | None, Query()] = None,
) -> list[dict[str, Any]]:
    return _service(request).events(system, version, gender, age_class)


@router.post("/calculate", tags=["beregning"])
def calculate(body: CalculateRequest, request: Request, response: Response) -> dict[str, Any]:
    out = _service(request).calculate(body)
    _cache(response, body.version is not None)
    return out


@router.post("/combined", tags=["beregning"])
def combined(body: CombinedRequest, request: Request, response: Response) -> dict[str, Any]:
    out = _service(request).combined(body)
    _cache(response, body.version is not None)
    return out


@router.post("/batch", tags=["beregning"])
def batch(body: BatchRequest, request: Request, response: Response) -> dict[str, Any]:
    out = _service(request).batch(body.rows)
    _cache(response, all(row.version is not None for row in body.rows))
    return out


@router.post("/interpret", tags=["tolkning"])
def interpret() -> JSONResponse:
    """Planlagt (B-27). Svarer 501 i v1."""
    return error_response(
        501, "not_implemented", "Tolkning av resultatlister er planlagt, men ikke bygget ennå."
    )
