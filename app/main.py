"""API REST del Módulo de Cotización de Envíos y Descuentos FastExpress."""

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core import CotizacionError, calcular_tarifa
from app.schemas import CotizacionRequest, CotizacionResponse, ErrorResponse

app = FastAPI(
    title="FastExpress – Cotizador de envíos",
    version="1.0.0",
    description="Cálculo de tarifas de envío según las reglas BR-01 a BR-05.",
)

# El frontend puede abrirse desde otro origen durante el desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(CotizacionError)
async def manejar_error_negocio(_: Request, exc: CotizacionError) -> JSONResponse:
    cuerpo = ErrorResponse(codigo=exc.codigo, mensaje=exc.mensaje)
    return JSONResponse(status_code=422, content=cuerpo.model_dump())


@app.exception_handler(RequestValidationError)
async def manejar_error_entrada(_: Request, exc: RequestValidationError) -> JSONResponse:
    detalles = [
        f"{'.'.join(str(p) for p in e['loc'] if p != 'body')}: {e['msg']}"
        for e in exc.errors()
    ]
    cuerpo = ErrorResponse(
        codigo="ENTRADA_INVALIDA",
        mensaje="Los datos enviados no tienen el formato esperado.",
        detalles=detalles,
    )
    return JSONResponse(status_code=422, content=cuerpo.model_dump())


@app.get("/health", tags=["Sistema"])
def health() -> dict:
    return {"estado": "ok"}


@app.post(
    "/api/v1/cotizaciones",
    response_model=CotizacionResponse,
    responses={422: {"model": ErrorResponse}},
    tags=["Cotizaciones"],
)
def cotizar(solicitud: CotizacionRequest) -> CotizacionResponse:
    cotizacion = calcular_tarifa(
        peso=solicitud.peso,
        tipo_cliente=solicitud.tipo_cliente,
        tipo_envio=solicitud.tipo_envio,
        monto_declarado=solicitud.monto_declarado,
    )
    return CotizacionResponse(**asdict(cotizacion))


# Sirve el frontend en "/app" si la carpeta existe (repositorio completo).
# DEF-001: montarlo en "/" hacía que el servidor de estáticos capturara rutas
# de la API con método no permitido (GET /api/v1/cotizaciones -> 404 en vez de 405).
_FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
if (_FRONTEND / "index.html").is_file():
    app.mount("/app", StaticFiles(directory=_FRONTEND, html=True), name="frontend")

    @app.get("/", include_in_schema=False)
    def raiz() -> RedirectResponse:
        return RedirectResponse(url="/app/")
