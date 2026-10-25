"""Robustez y consistencia: entradas atípicas y propiedades del desglose."""

from decimal import Decimal

import pytest

from app.core import TipoCliente, TipoEnvio, calcular_tarifa
from app.core.errores import CotizacionError, MontoInvalidoError, PesoInvalidoError

pytestmark = pytest.mark.robustez


@pytest.mark.parametrize(
    "peso",
    [
        pytest.param(None, id="nulo"),
        pytest.param("", id="vacio"),
        pytest.param(True, id="booleano"),
        pytest.param("NaN", id="nan"),
        pytest.param("Infinity", id="infinito"),
        pytest.param([5], id="lista"),
    ],
)
def test_peso_no_numerico_es_rechazado(peso):
    with pytest.raises(PesoInvalidoError):
        calcular_tarifa(peso, "NUEVO", "ESTANDAR", "50")


def test_monto_nulo_es_rechazado():
    with pytest.raises(MontoInvalidoError):
        calcular_tarifa("3", "NUEVO", "ESTANDAR", None)


def test_errores_de_negocio_tienen_codigo_y_mensaje():
    with pytest.raises(CotizacionError) as info:
        calcular_tarifa("25", "NUEVO", "ESTANDAR", "50")
    assert info.value.codigo == "LIMITE_PESO_EXCEDIDO"
    assert "20.00 kg" in info.value.mensaje


@pytest.mark.parametrize(
    "cliente, envio",
    [
        pytest.param("ORO", "ESTANDAR", id="cliente-desconocido"),
        pytest.param("NUEVO", "AEREO", id="envio-desconocido"),
        pytest.param("vip", "ESTANDAR", id="cliente-en-minusculas"),
    ],
)
def test_tipos_desconocidos_son_rechazados(cliente, envio):
    with pytest.raises(ValueError):
        calcular_tarifa("3", cliente, envio, "50")


def test_acepta_enums_y_numeros_nativos():
    cotizacion = calcular_tarifa(5.01, TipoCliente.VIP, TipoEnvio.EXPRESS, 100)
    # float 5.01 no debe convertirse en 5.0099999... (se usa str, no float binario)
    assert cotizacion.peso == Decimal("5.01")
    assert cotizacion.total == Decimal("25.04")  # 25.04 x 0.80 x 1.25


def test_espacios_alrededor_del_numero_se_toleran():
    assert calcular_tarifa(" 3 ", "NUEVO", "ESTANDAR", " 50 ").total == Decimal("11.00")


@pytest.mark.parametrize("peso", ["0.01", "4.99", "5.00", "5.01", "10", "19.99", "20"])
@pytest.mark.parametrize("cliente", ["NUEVO", "FRECUENTE", "VIP"])
@pytest.mark.parametrize("envio", ["ESTANDAR", "EXPRESS"])
@pytest.mark.parametrize("monto", ["0.01", "100.00", "100.01", "777.77", "1000"])
def test_desglose_suma_exactamente_el_total(peso, cliente, envio, monto):
    """Propiedad: para 210 combinaciones el desglose cuadra al centavo."""
    c = calcular_tarifa(peso, cliente, envio, monto)
    assert c.subtotal == c.tarifa_base + c.cargo_peso
    assert c.total == c.subtotal - c.descuento + c.recargo + c.seguro
    assert c.total == c.total.quantize(Decimal("0.01"))
    assert c.total > 0
