"""Caja blanca – caminos independientes (conjunto básico de McCabe).

calcular_tarifa:      5 decisiones -> V(G) = 6 -> caminos C1..C6
validar_cotizacion:   6 decisiones -> V(G) = 7 -> caminos V1..V7

Cada camino cambia una sola decisión respecto al camino base, que es la
forma clásica de construir el conjunto básico.
"""

from decimal import Decimal

import pytest

from app.core import calcular_tarifa, validar_cotizacion
from app.core.errores import (
    LimiteMontoExcedidoError,
    LimitePesoExcedidoError,
    MontoInvalidoError,
    PesoInvalidoError,
)

pytestmark = pytest.mark.caja_blanca


# ------------------------------------------------- calcular_tarifa, V(G) = 6
# D1: peso <= 5.00 | D2: FRECUENTE | D3: VIP | D4: EXPRESS | D5: monto > 100
@pytest.mark.parametrize(
    "peso, cliente, envio, monto, total",
    [
        # Camino base: D1=V, D2=F, D3=F, D4=F, D5=F
        pytest.param("3", "NUEVO", "ESTANDAR", "50", "11.00", id="C1-base"),
        # D1=F: tramo 2 de peso
        pytest.param("12", "NUEVO", "ESTANDAR", "50", "53.00", id="C2-D1-falso"),
        # D2=V: descuento FRECUENTE 10 %
        pytest.param("3", "FRECUENTE", "ESTANDAR", "50", "9.90", id="C3-D2-verdadero"),
        # D2=F, D3=V: descuento VIP 20 %
        pytest.param("3", "VIP", "ESTANDAR", "50", "8.80", id="C4-D3-verdadero"),
        # D4=V: recargo EXPRESS 25 %
        pytest.param("3", "NUEVO", "EXPRESS", "50", "13.75", id="C5-D4-verdadero"),
        # D5=V: seguro 2 % del monto declarado
        pytest.param("3", "NUEVO", "ESTANDAR", "500", "21.00", id="C6-D5-verdadero"),
    ],
)
def test_caminos_calcular_tarifa(peso, cliente, envio, monto, total):
    assert calcular_tarifa(peso, cliente, envio, monto).total == Decimal(total)


# ---------------------------------------------- validar_cotizacion, V(G) = 7
def test_V1_camino_valido():
    assert validar_cotizacion("3", "50") == (Decimal("3.00"), Decimal("50.00"))


@pytest.mark.parametrize(
    "peso, monto, error",
    [
        pytest.param("3.001", "50", PesoInvalidoError, id="V2-D1-peso-decimales"),
        pytest.param("0", "50", PesoInvalidoError, id="V3-D2-peso-bajo-minimo"),
        pytest.param("20.01", "50", LimitePesoExcedidoError, id="V4-D3-peso-sobre-maximo"),
        pytest.param("3", "50.001", MontoInvalidoError, id="V5-D4-monto-decimales"),
        pytest.param("3", "0", MontoInvalidoError, id="V6-D5-monto-bajo-minimo"),
        pytest.param("3", "1000.01", LimiteMontoExcedidoError, id="V7-D6-monto-sobre-maximo"),
    ],
)
def test_caminos_validar_cotizacion(peso, monto, error):
    with pytest.raises(error):
        validar_cotizacion(peso, monto)
