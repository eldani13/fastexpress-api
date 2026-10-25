"""Pruebas E2E de la interfaz: casos UI-01 a UI-09 y reproducción de defectos.

Se ejecutan con:  pytest -m e2e --no-cov
Los defectos abiertos se marcan xfail(strict=True): la prueba describe el
comportamiento CORRECTO y hoy falla. Cuando el desarrollador corrige el
defecto, la prueba pasa, pytest la reporta como XPASS(strict) = fallo, y el
desarrollador debe quitar el marcador xfail en el mismo pull request.
"""

import pytest

pytestmark = pytest.mark.e2e


# ------------------------------------------------- Validaciones del cliente
def test_UI01_peso_vacio(formulario):
    formulario.cotizar(peso="", monto="50")
    assert formulario.error_peso().inner_text() == "Ingresa el peso."
    assert "aparecerá aquí" in formulario.guia().inner_text()


def test_UI02_peso_no_numerico(formulario):
    formulario.cotizar(peso="abc", monto="50")
    assert "Escribe solo números" in formulario.error_peso().inner_text()


def test_UI03_peso_con_tres_decimales(formulario):
    formulario.cotizar(peso="2,555", monto="50")
    assert formulario.error_peso().inner_text() == "Usa máximo 2 decimales."


def test_UI04_coma_decimal_aceptada(formulario):
    formulario.cotizar(peso="4,5", monto="80", cliente="VIP")
    assert formulario.total() == "$11.20"


# ------------------------------------------------------ Flujo con la API
def test_UI05_rechazo_por_peso(formulario, pagina):
    formulario.cotizar(peso="21", monto="50")
    sello = pagina.locator("[data-testid=sello-rechazo]")
    sello.wait_for(timeout=5000)
    assert sello.inner_text() == "Rechazado"
    assert "20 kg" in formulario.guia().inner_text()


def test_UI06_cotizacion_completa(formulario, pagina):
    formulario.cotizar(peso="10", monto="250", cliente="FRECUENTE", envio="EXPRESS")
    assert formulario.total() == "$55.63"
    assert pagina.locator("[data-testid=cinta-express]").is_visible()
    desglose = pagina.locator("[data-testid=desglose]").inner_text()
    assert "Seguro" in desglose and "+$5.00" in desglose


def test_UI07_regresion_DEF002_guia_se_retira(formulario):
    formulario.cotizar(peso="10", monto="250")
    formulario.total()
    formulario.cotizar(peso="abc", monto="250")
    assert "aparecerá aquí" in formulario.guia().inner_text()


def test_UI08_movil_sin_desplazamiento_horizontal(navegador, servidor):
    contexto = navegador.new_context(viewport={"width": 390, "height": 844})
    pag = contexto.new_page()
    pag.goto(servidor + "/")
    ancho = pag.evaluate("document.documentElement.scrollWidth")
    contexto.close()
    assert ancho <= 390


def test_UI09_rechazo_por_monto(formulario, pagina):
    formulario.cotizar(peso="2", monto="1500")
    pagina.locator("[data-testid=sello-rechazo]").wait_for(timeout=5000)
    assert "$1,000" in formulario.guia().inner_text()


# --------------------------------------------------- Defectos abiertos
@pytest.mark.xfail(strict=True, raises=AssertionError, reason="DEF-005 abierto: un error 500 se muestra como falta de conexión")
def test_DEF005_error_del_servidor_no_se_presenta_como_falta_de_conexion(formulario, pagina):
    # Se simula un 500 interceptando la petición; así la prueba no depende de DEF-004
    pagina.route(
        "**/api/v1/cotizaciones",
        lambda ruta: ruta.fulfill(status=500, body="Internal Server Error"),
    )
    formulario.cotizar(peso="2", monto="50")
    pagina.locator("[data-testid=mensaje-fallo]").wait_for(timeout=5000)
    mensaje = pagina.locator("[data-testid=mensaje-fallo]").inner_text()
    assert "conexión" not in mensaje
    assert "error" in mensaje.lower()


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="DEF-006 abierto: separador de miles produce un mensaje engañoso")
@pytest.mark.parametrize("monto", ["1,000", "1.500", "12,000"])
def test_DEF006_separador_de_miles_tiene_mensaje_claro(formulario, monto):
    formulario.cotizar(peso="2", monto=monto)
    assert "separador de miles" in formulario.error_monto().inner_text()
