"""Pruebas de la API REST (integración HTTP con TestClient)."""

from pathlib import Path

import pytest

pytestmark = pytest.mark.api

URL = "/api/v1/cotizaciones"
FRONTEND_PRESENTE = (Path(__file__).resolve().parents[3] / "frontend" / "index.html").is_file()


def solicitud(**cambios):
    datos = {
        "peso": 10,
        "tipo_cliente": "FRECUENTE",
        "tipo_envio": "EXPRESS",
        "monto_declarado": 250,
    }
    datos.update(cambios)
    return datos


def test_health(cliente_api):
    respuesta = cliente_api.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}


def test_cotizacion_exitosa_con_desglose(cliente_api):
    respuesta = cliente_api.post(URL, json=solicitud())
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["subtotal"] == "45.00"
    assert cuerpo["descuento"] == "4.50"
    assert cuerpo["recargo"] == "10.13"
    assert cuerpo["seguro"] == "5.00"
    assert cuerpo["total"] == "55.63"
    assert cuerpo["monto_declarado"] == "250.00"


def test_acepta_numeros_como_texto(cliente_api):
    respuesta = cliente_api.post(URL, json=solicitud(peso="5.01", monto_declarado="50"))
    assert respuesta.status_code == 200
    assert respuesta.json()["tarifa_kg"] == "4.00"


@pytest.mark.parametrize(
    "cambios, codigo",
    [
        pytest.param({"peso": 0}, "PESO_INVALIDO", id="peso-cero"),
        pytest.param({"peso": 20.01}, "LIMITE_PESO_EXCEDIDO", id="peso-excedido"),
        pytest.param({"peso": 5.005}, "PESO_INVALIDO", id="peso-3-decimales"),
        pytest.param({"monto_declarado": 0}, "MONTO_INVALIDO", id="monto-cero"),
        pytest.param({"monto_declarado": 1000.01}, "LIMITE_MONTO_EXCEDIDO", id="monto-excedido"),
    ],
)
def test_errores_de_negocio(cliente_api, cambios, codigo):
    respuesta = cliente_api.post(URL, json=solicitud(**cambios))
    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo["codigo"] == codigo
    assert cuerpo["mensaje"]


@pytest.mark.parametrize(
    "datos",
    [
        pytest.param(solicitud(peso="abc"), id="peso-no-numerico"),
        pytest.param(solicitud(tipo_cliente="ORO"), id="cliente-desconocido"),
        pytest.param(solicitud(tipo_envio="AEREO"), id="envio-desconocido"),
        pytest.param({"peso": 3}, id="campos-faltantes"),
        pytest.param({}, id="cuerpo-vacio"),
    ],
)
def test_entrada_mal_formada(cliente_api, datos):
    respuesta = cliente_api.post(URL, json=datos)
    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo["codigo"] == "ENTRADA_INVALIDA"
    assert cuerpo["detalles"]



@pytest.mark.parametrize(
    "cambios, codigo",
    [
        pytest.param({"peso": "9" * 29}, "LIMITE_PESO_EXCEDIDO", id="peso-29-digitos"),
        pytest.param({"peso": 1e308}, "LIMITE_PESO_EXCEDIDO", id="peso-1e308"),
        pytest.param({"monto_declarado": "9" * 29}, "LIMITE_MONTO_EXCEDIDO", id="monto-29-digitos"),
    ],
)
def test_DEF004_numeros_enormes_se_rechazan_sin_error_500(cambios, codigo):
    from fastapi.testclient import TestClient

    from app.main import app

    cliente = TestClient(app, raise_server_exceptions=False)
    respuesta = cliente.post(URL, json=solicitud(**cambios))
    assert respuesta.status_code == 422
    assert respuesta.json()["codigo"] == codigo


def test_metodo_no_permitido(cliente_api):
    assert cliente_api.get(URL).status_code == 405


@pytest.mark.skipif(not FRONTEND_PRESENTE, reason="repositorio sin carpeta frontend")
def test_frontend_servido_sin_ocultar_la_api(cliente_api):
    """Regresión DEF-001: el frontend no debe capturar rutas de la API."""
    pagina = cliente_api.get("/")
    assert pagina.status_code == 200
    assert str(pagina.url).endswith("/app/")
    assert "Cotiza tu envío" in pagina.text
    assert cliente_api.get(URL).status_code == 405


def test_documentacion_openapi_disponible(cliente_api):
    esquema = cliente_api.get("/openapi.json").json()
    assert URL in esquema["paths"]
