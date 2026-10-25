"""Constantes de las reglas de negocio de FastExpress.

Todas las cifras del enunciado viven aquí, para que un cambio en una regla
se haga en un solo lugar y no quede repartido por el código.
"""

from decimal import Decimal
from enum import Enum


class TipoCliente(str, Enum):
    NUEVO = "NUEVO"
    FRECUENTE = "FRECUENTE"
    VIP = "VIP"


class TipoEnvio(str, Enum):
    ESTANDAR = "ESTANDAR"
    EXPRESS = "EXPRESS"


# BR-01: tarifa base de toda orden (USD)
TARIFA_BASE = Decimal("5.00")

# BR-02: cálculo por peso (kg). Todo el peso se cobra a la tarifa de su rango.
PESO_MINIMO = Decimal("0.01")
LIMITE_TRAMO_1 = Decimal("5.00")      # 0.01 – 5.00 kg
PESO_MAXIMO = Decimal("20.00")        # 5.01 – 20.00 kg; más de 20 se rechaza
TARIFA_KG_TRAMO_1 = Decimal("2.00")
TARIFA_KG_TRAMO_2 = Decimal("4.00")

# BR-03: descuentos por tipo de cliente
DESCUENTO_NUEVO = Decimal("0.00")
DESCUENTO_FRECUENTE = Decimal("0.10")
DESCUENTO_VIP = Decimal("0.20")

# BR-04: recargo por tipo de envío (sobre el subtotal ya descontado)
RECARGO_ESTANDAR = Decimal("0.00")
RECARGO_EXPRESS = Decimal("0.25")

# BR-05 (propuesta del equipo): seguro por monto declarado (USD)
MONTO_MINIMO = Decimal("0.01")
UMBRAL_SEGURO = Decimal("100.00")     # hasta 100.00 no se cobra seguro
MONTO_MAXIMO = Decimal("1000.00")     # más de 1,000.00 se rechaza
TASA_SEGURO = Decimal("0.02")

# Precisión: pesos y montos con máximo 2 decimales; dinero redondeado al centavo
DECIMALES_PERMITIDOS = 2
CENTAVO = Decimal("0.01")
