# Registro de decisiones técnicas (backend)

Responsable: Desarrollador Backend

Cada decisión sigue el formato ADR (Architecture Decision Record): contexto, decisión,
consecuencias. Una decisión no se borra; si cambia, se agrega una nueva que la reemplaza.

---

## ADR-001: usar `Decimal` en todo el cálculo

- **Fecha:** 2026-10-12 · **Estado:** aceptada
- **Contexto:** con `float`, `round(40.5 * 0.25, 2)` da `10.12` en lugar de `10.13` (caso R4 de la tabla de decisión). Un error de un centavo en dinero es un defecto.
- **Decisión:** todos los valores monetarios y pesos son `decimal.Decimal`. La conversión desde la entrada se hace con `Decimal(str(valor))`, nunca desde `float` binario. Redondeo `ROUND_HALF_UP` al centavo por componente.
- **Consecuencias:** resultados exactos y verificables al centavo. La API devuelve los números como texto para no perder precisión en JSON.

## ADR-002: separar validación y cálculo en dos funciones

- **Fecha:** 2026-10-12 · **Estado:** aceptada
- **Contexto:** una sola función tendría V(G) = 12, por encima del umbral recomendado de 10, y un grafo de flujo difícil de leer.
- **Decisión:** `validar_cotizacion()` (V(G) = 7) valida entradas; `calcular_tarifa()` (V(G) = 6) aplica las reglas.
- **Consecuencias:** cada función se prueba con su propio conjunto básico de caminos (V1–V7 y C1–C6).

## ADR-003: las reglas de negocio viven solo en el backend

- **Fecha:** 2026-10-12 · **Estado:** aceptada
- **Contexto:** si el frontend también validara 20 kg o $1,000, un cambio de regla obligaría a modificar dos lugares.
- **Decisión:** el frontend valida solo formato. Los límites y tarifas están únicamente en `app/core/reglas.py`.
- **Consecuencias:** cambiar una tarifa es editar una constante. El frontend muestra el rechazo que decide el backend.

## ADR-004: errores de negocio con código y estado 422

- **Fecha:** 2026-10-12 · **Estado:** aceptada
- **Contexto:** el frontend necesita distinguir "peso excedido" de "monto inválido" sin interpretar mensajes de texto.
- **Decisión:** cada error tiene un código estable (`LIMITE_PESO_EXCEDIDO`, etc.) y se responde con 422 y el formato `{codigo, mensaje, detalles}`. Los errores de formato de FastAPI se convierten al mismo formato (`ENTRADA_INVALIDA`).
- **Consecuencias:** contrato uniforme, probado en `tests/api/test_api.py`.

## ADR-005: servir el frontend en `/app/` (corrige DEF-001)

- **Fecha:** 2026-10-12 · **Estado:** aceptada
- **Contexto:** montar los archivos estáticos en `/` capturaba peticiones a la API con método no permitido (404 en vez de 405).
- **Decisión:** el frontend se monta en `/app/` y `/` redirige ahí.
- **Consecuencias:** la API conserva sus códigos HTTP correctos. Prueba de regresión: `test_frontend_servido_sin_ocultar_la_api`.

## ADR-006: regla BR-05 para el campo `Monto`

- **Fecha:** 2026-10-12 · **Estado:** aceptada
- **Contexto:** el enunciado pide pruebas para `Monto` sin definirlo. El docente indicó que el equipo podía proponerlo.
- **Decisión:** `Monto` es el valor declarado del paquete: 0.01–100.00 sin seguro, 100.01–1,000.00 con seguro del 2 %, más de 1,000.00 se rechaza.
- **Consecuencias:** el campo tiene particiones y valores límite con sentido de negocio.

## ADR-007: versiones fijas de dependencias

- **Fecha:** 2026-10-13 · **Estado:** aceptada
- **Contexto:** con versiones sin fijar, una instalación limpia del 13 de octubre descargó Starlette 1.8, que ya muestra una advertencia de obsolescencia en el cliente de pruebas, y una versión de Playwright distinta de la verificada. Cada integrante podía terminar probando un sistema diferente.
- **Decisión:** `requirements*.txt` fijan la versión exacta (`==`) de cada dependencia, incluida Starlette, que llega como dependencia de FastAPI. Se agrega `httpx2`, el cliente que espera el TestClient de Starlette 1.6, con lo que desaparece la advertencia.
- **Consecuencias:** los cuatro computadores y GitHub Actions ejecutan exactamente lo mismo. Actualizar una dependencia es un cambio deliberado: issue, rama y pull request con la suite en verde.

## ADR-008: validar decimales sin aritmética (corrige DEF-004)

- **Fecha:** 2026-10-24 · **Estado:** aceptada
- **Contexto:** `_tiene_mas_de_dos_decimales` usaba `quantize`, que trabaja con la precisión del contexto decimal (28 dígitos). Con números de 29 dígitos o más lanzaba `InvalidOperation` y la API respondía 500 (DEF-004, issue #1).
- **Decisión:** revisar los decimales con `Decimal.as_tuple()`: si el exponente es −2 o mayor, el número tiene como máximo 2 decimales; si es menor, se revisa que los dígitos sobrantes sean cero. No se hace ninguna operación aritmética.
- **Consecuencias:** la validación funciona con números de cualquier tamaño; un peso o monto enorme llega a la regla de negocio y se rechaza con 422. `5.000` sigue siendo válido y `5.005` no. La prueba `test_DEF004_numeros_enormes_se_rechazan_sin_error_500` queda como regresión (PR #2).