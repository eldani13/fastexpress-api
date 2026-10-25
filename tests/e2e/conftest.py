"""Infraestructura de las pruebas de extremo a extremo (E2E).

Levanta la aplicación real (uvicorn) en un puerto propio y abre Chromium con
Playwright. Requiere: pip install -r requirements-e2e.txt
                      python -m playwright install chromium
"""

import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # las pruebas E2E se omiten si Playwright no está instalado
    sync_playwright = None

PUERTO = 8765
URL_BASE = f"http://127.0.0.1:{PUERTO}"
CARPETA_BACKEND = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def servidor():
    proceso = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(PUERTO)],
        cwd=CARPETA_BACKEND,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        limite = time.time() + 20
        while time.time() < limite:
            try:
                if httpx.get(f"{URL_BASE}/health", timeout=1, trust_env=False).status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.3)
        else:
            pytest.fail("El servidor no respondió en 20 segundos")
        yield URL_BASE
    finally:
        proceso.terminate()
        proceso.wait(timeout=10)


@pytest.fixture(scope="session")
def navegador():
    if sync_playwright is None:
        pytest.skip("Instala requirements-e2e.txt para las pruebas E2E")
    with sync_playwright() as p:
        nav = p.chromium.launch()
        yield nav
        nav.close()


@pytest.fixture
def pagina(navegador, servidor):
    contexto = navegador.new_context(viewport={"width": 1280, "height": 900})
    pag = contexto.new_page()
    pag.goto(servidor + "/")
    yield pag
    contexto.close()


class Formulario:
    """Acciones del usuario sobre el cotizador (patrón Page Object)."""

    def __init__(self, pag):
        self.pag = pag

    def cotizar(self, peso="", monto="", cliente="NUEVO", envio="ESTANDAR"):
        self.pag.fill("[data-testid=input-peso]", peso)
        self.pag.fill("[data-testid=input-monto]", monto)
        self.pag.check(f"input[name=tipo_cliente][value={cliente}]")
        self.pag.check(f"input[name=tipo_envio][value={envio}]")
        self.pag.click("[data-testid=boton-cotizar]")

    def total(self):
        return self.pag.locator("[data-testid=total]").inner_text(timeout=5000)

    def error_peso(self):
        return self.pag.locator("[data-testid=error-peso]")

    def error_monto(self):
        return self.pag.locator("[data-testid=error-monto]")

    def guia(self):
        return self.pag.locator("[data-testid=guia]")


@pytest.fixture
def formulario(pagina):
    return Formulario(pagina)
