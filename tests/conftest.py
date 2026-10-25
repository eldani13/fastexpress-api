import pytest
from fastapi.testclient import TestClient

from app.core import calcular_tarifa
from app.main import app


@pytest.fixture
def cotizar():
    """Atajo para calcular con valores por defecto neutros:
    cliente NUEVO, envío ESTANDAR y monto $50.00 (sin seguro)."""

    def _cotizar(peso="1.00", cliente="NUEVO", envio="ESTANDAR", monto="50.00"):
        return calcular_tarifa(peso, cliente, envio, monto)

    return _cotizar


@pytest.fixture
def cliente_api():
    return TestClient(app)
