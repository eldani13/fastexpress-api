"""Contratos de entrada y salida de la API."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.reglas import TipoCliente, TipoEnvio


class CotizacionRequest(BaseModel):
    """Datos que envía el formulario.

    Los rangos de peso y monto no se validan aquí sino en el core, para que
    la regla viva en un solo lugar y responda con su código de negocio.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "peso": 10,
                "tipo_cliente": "FRECUENTE",
                "tipo_envio": "EXPRESS",
                "monto_declarado": 250,
            }
        }
    )

    peso: Decimal = Field(description="Peso del paquete en kg (0.01 – 20.00)")
    tipo_cliente: TipoCliente
    tipo_envio: TipoEnvio
    monto_declarado: Decimal = Field(
        description="Valor declarado del paquete en USD (0.01 – 1,000.00)"
    )


class CotizacionResponse(BaseModel):
    """Cotización con desglose. Los valores monetarios se devuelven como
    texto con 2 decimales para no perder precisión."""

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


class ErrorResponse(BaseModel):
    codigo: str
    mensaje: str
    detalles: list[str] = []
