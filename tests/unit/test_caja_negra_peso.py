"""Caja negra – campo Peso (BR-02).

Particiones de equivalencia (CE) y análisis de valores límite (BVA).
Condiciones fijas: cliente NUEVO, envío ESTANDAR, monto $50.00 (sin seguro),
de modo que el total depende solo del peso.
"""

from decimal import Decimal

import pytest

from app.core.errores import LimitePesoExcedidoError, PesoInvalidoError

pytestmark = pytest.mark.caja_negra


# ---------------------------------------------------------------- Particiones
@pytest.mark.parametrize(
    "peso, total_esperado",
    [
        pytest.param("3", "11.00", id="CE2-tramo1-valida"),
        pytest.param("12", "53.00", id="CE3-tramo2-valida"),
    ],
)
def test_particiones_validas_peso(cotizar, peso, total_esperado):
    assert cotizar(peso=peso).total == Decimal(total_esperado)


@pytest.mark.parametrize(
    "peso, error",
    [
        pytest.param("-1", PesoInvalidoError, id="CE1-negativo-invalida"),
        pytest.param("25", LimitePesoExcedidoError, id="CE4-mayor-20-invalida"),
        pytest.param("abc", PesoInvalidoError, id="CE5-no-numerico-invalida"),
        pytest.param("5.005", PesoInvalidoError, id="CE6-mas-de-2-decimales-invalida"),
    ],
)
def test_particiones_invalidas_peso(cotizar, peso, error):
    with pytest.raises(error):
        cotizar(peso=peso)


# ------------------------------------------------------------ Valores límite
@pytest.mark.parametrize(
    "peso, tarifa_kg, total_esperado",
    [
        pytest.param("0.01", "2.00", "5.02", id="BVA-02-minimo"),
        pytest.param("0.02", "2.00", "5.04", id="BVA-03-minimo+1"),
        pytest.param("4.99", "2.00", "14.98", id="BVA-04-limite-tramo1-1"),
        pytest.param("5.00", "2.00", "15.00", id="BVA-05-limite-tramo1"),
        pytest.param("5.01", "4.00", "25.04", id="BVA-06-inicio-tramo2"),
        pytest.param("5.02", "4.00", "25.08", id="BVA-07-inicio-tramo2+1"),
        pytest.param("19.99", "4.00", "84.96", id="BVA-08-maximo-1"),
        pytest.param("20.00", "4.00", "85.00", id="BVA-09-maximo"),
    ],
)
def test_valores_limite_validos_peso(cotizar, peso, tarifa_kg, total_esperado):
    cotizacion = cotizar(peso=peso)
    assert cotizacion.tarifa_kg == Decimal(tarifa_kg)
    assert cotizacion.total == Decimal(total_esperado)


@pytest.mark.parametrize(
    "peso, error",
    [
        pytest.param("0.00", PesoInvalidoError, id="BVA-01-cero"),
        pytest.param("20.01", LimitePesoExcedidoError, id="BVA-10-maximo+1"),
    ],
)
def test_valores_limite_invalidos_peso(cotizar, peso, error):
    with pytest.raises(error):
        cotizar(peso=peso)
