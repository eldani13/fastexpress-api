"""Caja negra – Tabla de decisión Tipo de Cliente x Tipo de Envío (BR-03, BR-04).

Condiciones fijas: peso 10 kg (subtotal $45.00) y monto $50.00 (sin seguro).
El recargo EXPRESS se aplica sobre el subtotal ya descontado.
"""

from decimal import Decimal

import pytest

pytestmark = pytest.mark.caja_negra


@pytest.mark.parametrize(
    "cliente, envio, descuento, recargo, total",
    [
        pytest.param("NUEVO", "ESTANDAR", "0.00", "0.00", "45.00", id="R1-NUEVO-ESTANDAR"),
        pytest.param("NUEVO", "EXPRESS", "0.00", "11.25", "56.25", id="R2-NUEVO-EXPRESS"),
        pytest.param("FRECUENTE", "ESTANDAR", "4.50", "0.00", "40.50", id="R3-FRECUENTE-ESTANDAR"),
        # 40.50 x 0.25 = 10.125 -> redondeo HALF_UP a 10.13
        pytest.param("FRECUENTE", "EXPRESS", "4.50", "10.13", "50.63", id="R4-FRECUENTE-EXPRESS"),
        pytest.param("VIP", "ESTANDAR", "9.00", "0.00", "36.00", id="R5-VIP-ESTANDAR"),
        pytest.param("VIP", "EXPRESS", "9.00", "9.00", "45.00", id="R6-VIP-EXPRESS"),
    ],
)
def test_tabla_decision(cotizar, cliente, envio, descuento, recargo, total):
    cotizacion = cotizar(peso="10", cliente=cliente, envio=envio)
    assert cotizacion.subtotal == Decimal("45.00")
    assert cotizacion.descuento == Decimal(descuento)
    assert cotizacion.recargo == Decimal(recargo)
    assert cotizacion.total == Decimal(total)
