"""Algoritmo de cotización de envíos FastExpress.

El cálculo se divide en dos funciones para que cada grafo de flujo de control
sea legible en el informe de caja blanca:

* ``validar_cotizacion``: verifica peso y monto (BR-02 y BR-05). V(G) = 7.
* ``calcular_tarifa``: aplica las reglas BR-01 a BR-05. V(G) = 6.

Los comentarios ``# Dn`` marcan los nodos de decisión de cada grafo.

Fórmula (supuestos documentados en el README):
    subtotal  = tarifa base + peso x tarifa por kg
    descuento = subtotal x % descuento
    recargo   = (subtotal - descuento) x % recargo
    seguro    = monto declarado x 2 %   (solo si el monto supera 100.00)
    total     = subtotal - descuento + recargo + seguro

Cada componente se redondea al centavo (ROUND_HALF_UP), así el desglose
siempre suma exactamente el total.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from app.core import reglas
from app.core.errores import (
    CotizacionError,
    LimiteMontoExcedidoError,
    LimitePesoExcedidoError,
    MontoInvalidoError,
    PesoInvalidoError,
)
from app.core.reglas import TipoCliente, TipoEnvio


@dataclass(frozen=True)
class Cotizacion:
    peso: Decimal
    tipo_cliente: TipoCliente
    tipo_envio: TipoEnvio
    monto_declarado: Decimal
    tarifa_base: Decimal
    tarifa_kg: Decimal
    cargo_peso: Decimal
    subtotal: Decimal
    porcentaje_descuento: Decimal
    descuento: Decimal
    porcentaje_recargo: Decimal
    recargo: Decimal
    seguro: Decimal
    total: Decimal


def _redondear(valor: Decimal) -> Decimal:
    return valor.quantize(reglas.CENTAVO, rounding=ROUND_HALF_UP)


def _a_decimal(valor, error: type[CotizacionError], campo: str) -> Decimal:
    """Convierte la entrada a Decimal sin pasar por float binario."""
    if isinstance(valor, bool):
        raise error(f"El {campo} debe ser un número.")
    try:
        numero = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError, TypeError):
        raise error(f"El {campo} debe ser un número.") from None
    if not numero.is_finite():
        raise error(f"El {campo} debe ser un número finito.")
    return numero


def _tiene_mas_de_dos_decimales(numero: Decimal) -> bool:
    return numero != numero.quantize(reglas.CENTAVO)


def validar_cotizacion(peso, monto_declarado) -> tuple[Decimal, Decimal]:
    """Valida peso (BR-02) y monto declarado (BR-05).

    Devuelve ambos valores como Decimal o lanza un ``CotizacionError``.
    """
    peso = _a_decimal(peso, PesoInvalidoError, "peso")
    monto = _a_decimal(monto_declarado, MontoInvalidoError, "monto declarado")

    if _tiene_mas_de_dos_decimales(peso):                      # D1
        raise PesoInvalidoError("El peso admite máximo 2 decimales.")
    if peso < reglas.PESO_MINIMO:                              # D2
        raise PesoInvalidoError("El peso mínimo es 0.01 kg.")
    if peso > reglas.PESO_MAXIMO:                              # D3
        raise LimitePesoExcedidoError(
            "Envío rechazado: el peso supera el límite de 20.00 kg."
        )

    if _tiene_mas_de_dos_decimales(monto):                     # D4
        raise MontoInvalidoError("El monto declarado admite máximo 2 decimales.")
    if monto < reglas.MONTO_MINIMO:                            # D5
        raise MontoInvalidoError("El monto declarado mínimo es $0.01.")
    if monto > reglas.MONTO_MAXIMO:                            # D6
        raise LimiteMontoExcedidoError(
            "Envío rechazado: el monto declarado supera el máximo asegurable de $1,000.00."
        )

    return peso.quantize(reglas.CENTAVO), monto.quantize(reglas.CENTAVO)


def calcular_tarifa(peso, tipo_cliente, tipo_envio, monto_declarado) -> Cotizacion:
    """Algoritmo principal de cálculo de la tarifa (BR-01 a BR-05)."""
    peso, monto = validar_cotizacion(peso, monto_declarado)
    tipo_cliente = TipoCliente(tipo_cliente)
    tipo_envio = TipoEnvio(tipo_envio)

    # BR-02: tarifa por kg según el rango de peso
    if peso <= reglas.LIMITE_TRAMO_1:                          # D1
        tarifa_kg = reglas.TARIFA_KG_TRAMO_1
    else:
        tarifa_kg = reglas.TARIFA_KG_TRAMO_2

    # BR-01 + BR-02: subtotal
    cargo_peso = _redondear(peso * tarifa_kg)
    subtotal = reglas.TARIFA_BASE + cargo_peso

    # BR-03: descuento por tipo de cliente
    if tipo_cliente == TipoCliente.FRECUENTE:                  # D2
        porcentaje_descuento = reglas.DESCUENTO_FRECUENTE
    elif tipo_cliente == TipoCliente.VIP:                      # D3
        porcentaje_descuento = reglas.DESCUENTO_VIP
    else:
        porcentaje_descuento = reglas.DESCUENTO_NUEVO
    descuento = _redondear(subtotal * porcentaje_descuento)

    # BR-04: recargo por tipo de envío, sobre el subtotal ya descontado
    if tipo_envio == TipoEnvio.EXPRESS:                        # D4
        porcentaje_recargo = reglas.RECARGO_EXPRESS
    else:
        porcentaje_recargo = reglas.RECARGO_ESTANDAR
    recargo = _redondear((subtotal - descuento) * porcentaje_recargo)

    # BR-05: seguro por monto declarado
    if monto > reglas.UMBRAL_SEGURO:                           # D5
        seguro = _redondear(monto * reglas.TASA_SEGURO)
    else:
        seguro = Decimal("0.00")

    total = subtotal - descuento + recargo + seguro

    return Cotizacion(
        peso=peso,
        tipo_cliente=tipo_cliente,
        tipo_envio=tipo_envio,
        monto_declarado=monto,
        tarifa_base=reglas.TARIFA_BASE,
        tarifa_kg=tarifa_kg,
        cargo_peso=cargo_peso,
        subtotal=subtotal,
        porcentaje_descuento=porcentaje_descuento,
        descuento=descuento,
        porcentaje_recargo=porcentaje_recargo,
        recargo=recargo,
        seguro=seguro,
        total=total,
    )
