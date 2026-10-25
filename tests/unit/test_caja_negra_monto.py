"""Caja negra – campo Monto declarado (BR-05, regla propuesta por el equipo).

Condiciones fijas: peso 1 kg, cliente NUEVO, envío ESTANDAR (subtotal $7.00),
de modo que el total depende solo del seguro.
"""

from decimal import Decimal

import pytest

from app.core.errores import LimiteMontoExcedidoError, MontoInvalidoError

pytestmark = pytest.mark.caja_negra


# ---------------------------------------------------------------- Particiones
@pytest.mark.parametrize(
    "monto, seguro_esperado, total_esperado",
    [
        pytest.param("50", "0.00", "7.00", id="CE-M2-sin-seguro-valida"),
        pytest.param("500", "10.00", "17.00", id="CE-M3-con-seguro-valida"),
    ],
)
def test_particiones_validas_monto(cotizar, monto, seguro_esperado, total_esperado):
    cotizacion = cotizar(monto=monto)
    assert cotizacion.seguro == Decimal(seguro_esperado)
    assert cotizacion.total == Decimal(total_esperado)


@pytest.mark.parametrize(
    "monto, error",
    [
        pytest.param("-10", MontoInvalidoError, id="CE-M1-negativo-invalida"),
        pytest.param("1500", LimiteMontoExcedidoError, id="CE-M4-mayor-1000-invalida"),
        pytest.param("abc", MontoInvalidoError, id="CE-M5-no-numerico-invalida"),
        pytest.param("50.005", MontoInvalidoError, id="CE-M6-mas-de-2-decimales-invalida"),
    ],
)
def test_particiones_invalidas_monto(cotizar, monto, error):
    with pytest.raises(error):
        cotizar(monto=monto)


# ------------------------------------------------------------ Valores límite
@pytest.mark.parametrize(
    "monto, seguro_esperado, total_esperado",
    [
        pytest.param("0.01", "0.00", "7.00", id="BVA-M02-minimo"),
        pytest.param("0.02", "0.00", "7.00", id="BVA-M03-minimo+1"),
        pytest.param("99.99", "0.00", "7.00", id="BVA-M04-umbral-1"),
        pytest.param("100.00", "0.00", "7.00", id="BVA-M05-umbral"),
        pytest.param("100.01", "2.00", "9.00", id="BVA-M06-umbral+1"),
        pytest.param("100.02", "2.00", "9.00", id="BVA-M07-umbral+2"),
        pytest.param("999.99", "20.00", "27.00", id="BVA-M08-maximo-1"),
        pytest.param("1000.00", "20.00", "27.00", id="BVA-M09-maximo"),
    ],
)
def test_valores_limite_validos_monto(cotizar, monto, seguro_esperado, total_esperado):
    cotizacion = cotizar(monto=monto)
    assert cotizacion.seguro == Decimal(seguro_esperado)
    assert cotizacion.total == Decimal(total_esperado)


@pytest.mark.parametrize(
    "monto, error",
    [
        pytest.param("0.00", MontoInvalidoError, id="BVA-M01-cero"),
        pytest.param("1000.01", LimiteMontoExcedidoError, id="BVA-M10-maximo+1"),
    ],
)
def test_valores_limite_invalidos_monto(cotizar, monto, error):
    with pytest.raises(error):
        cotizar(monto=monto)
