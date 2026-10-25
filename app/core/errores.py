"""Errores de negocio de la cotización.

Cada error lleva un código estable que usan la API, el frontend y las pruebas.
"""


class CotizacionError(ValueError):
    """Error base: la cotización no se puede calcular."""

    codigo = "COTIZACION_INVALIDA"

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class PesoInvalidoError(CotizacionError):
    codigo = "PESO_INVALIDO"


class LimitePesoExcedidoError(CotizacionError):
    """BR-02: un peso mayor a 20.00 kg se rechaza."""

    codigo = "LIMITE_PESO_EXCEDIDO"


class MontoInvalidoError(CotizacionError):
    codigo = "MONTO_INVALIDO"


class LimiteMontoExcedidoError(CotizacionError):
    """BR-05: un monto declarado mayor a 1,000.00 se rechaza."""

    codigo = "LIMITE_MONTO_EXCEDIDO"
