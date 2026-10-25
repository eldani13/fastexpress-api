# Especificación de la API REST

Responsable: Desarrollador Backend · Versión de la API: 1.0.0

La documentación interactiva generada por FastAPI está en `http://127.0.0.1:8000/docs`
con el servidor encendido. Este documento es la referencia escrita y manda si hay diferencias.

## Endpoints

| Método | Ruta | Descripción | Respuestas |
|---|---|---|---|
| GET | `/health` | Estado del servicio | 200 |
| POST | `/api/v1/cotizaciones` | Calcula una cotización | 200, 422 |
| GET | `/` | Redirige a la interfaz en `/app/` | 307 |

## POST /api/v1/cotizaciones

### Solicitud

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `peso` | número o texto numérico | Sí | 0.01 a 20.00 kg, máximo 2 decimales (BR-02) |
| `tipo_cliente` | texto | Sí | `NUEVO`, `FRECUENTE` o `VIP`, en mayúsculas (BR-03) |
| `tipo_envio` | texto | Sí | `ESTANDAR` o `EXPRESS`, en mayúsculas (BR-04) |
| `monto_declarado` | número o texto numérico | Sí | 0.01 a 1,000.00 USD, máximo 2 decimales (BR-05) |

```json
{ "peso": 10, "tipo_cliente": "FRECUENTE", "tipo_envio": "EXPRESS", "monto_declarado": 250 }
```

### Respuesta 200

Todos los valores numéricos se devuelven como **texto con 2 decimales** para no perder precisión.

| Campo | Significado | Ejemplo |
|---|---|---|
| `peso`, `monto_declarado` | Entrada normalizada | `"10.00"`, `"250.00"` |
| `tipo_cliente`, `tipo_envio` | Entrada | `"FRECUENTE"`, `"EXPRESS"` |
| `tarifa_base` | BR-01 | `"5.00"` |
| `tarifa_kg` | Tarifa del rango de peso (BR-02) | `"4.00"` |
| `cargo_peso` | peso × tarifa_kg | `"40.00"` |
| `subtotal` | tarifa_base + cargo_peso | `"45.00"` |
| `porcentaje_descuento`, `descuento` | BR-03 | `"0.10"`, `"4.50"` |
| `porcentaje_recargo`, `recargo` | BR-04, sobre subtotal − descuento | `"0.25"`, `"10.13"` |
| `seguro` | BR-05 | `"5.00"` |
| `total` | subtotal − descuento + recargo + seguro | `"55.63"` |

### Respuesta 422 (error)

```json
{ "codigo": "LIMITE_PESO_EXCEDIDO", "mensaje": "Envío rechazado: el peso supera el límite de 20.00 kg.", "detalles": [] }
```

| Código | Causa | Regla |
|---|---|---|
| `ENTRADA_INVALIDA` | Campo faltante, valor no numérico o tipo desconocido. `detalles` lista cada problema | Contrato |
| `PESO_INVALIDO` | Peso menor a 0.01 o con más de 2 decimales | BR-02 |
| `LIMITE_PESO_EXCEDIDO` | Peso mayor a 20.00 kg | BR-02 |
| `MONTO_INVALIDO` | Monto menor a 0.01 o con más de 2 decimales | BR-05 |
| `LIMITE_MONTO_EXCEDIDO` | Monto mayor a 1,000.00 | BR-05 |

Un error **500 nunca es una respuesta válida** de esta API; si aparece, es un defecto.

## Ejemplos de uso

Linux / macOS / Git Bash:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/cotizaciones \
  -H "Content-Type: application/json" \
  -d '{"peso":10,"tipo_cliente":"FRECUENTE","tipo_envio":"EXPRESS","monto_declarado":250}'
```

Windows PowerShell:

```powershell
$cuerpo = @{ peso = 10; tipo_cliente = "FRECUENTE"; tipo_envio = "EXPRESS"; monto_declarado = 250 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/cotizaciones -ContentType "application/json" -Body $cuerpo
```

## Historial de cambios

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-12 | Primera versión: BR-01 a BR-05, errores con código |
| 1.0.1 | 2026-10-24 | DEF-004: pesos y montos con más de 28 dígitos responden 422 en lugar de 500 |