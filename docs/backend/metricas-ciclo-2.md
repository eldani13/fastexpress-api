# Métricas del backend: ciclo 2

Responsable: Desarrollador Backend (Julián Robles) · Fecha de medición: 25 de octubre de 2026

Mediciones de los indicadores ISO 9126 que corresponden al backend (fiabilidad, eficiencia y
mantenibilidad), tomadas sobre `main` después de corregir DEF-004 (PR #2). QA las consolida en la
tabla general de métricas.

**Entorno:** Windows, Python 3.12.1, servidor local uvicorn, dependencias de `requirements-dev.txt`.

## Resultados

| Característica | Indicador | Fórmula | Meta | Ciclo 1 | Ciclo 2 | Nivel |
|---|---|---|---|---|---|---|
| Fiabilidad | Robustez ante entradas aleatorias | Peticiones sin error 500 / enviadas | 100 % | 1,000/1,000 = 100 % | 1,000/1,000 = 100 % | 3 |
| Fiabilidad | Robustez ante valores extremos | Entradas extremas sin error 500 / probadas | 100 % | 1/5 = 20 % | **5/5 = 100 %** | **3** |
| Eficiencia | Tiempo de respuesta p95 | Percentil 95 de 1,000 peticiones | ≤ 500 ms | 2.1 ms | 1.24 ms | 3 |
| Mantenibilidad | Complejidad ciclomática máxima | Mayor V(G) | ≤ 10 | 7 | 7 | 3 |
| Mantenibilidad | Centralización de reglas | Valores de negocio en `reglas.py` / total | 100 % | 14/14 | 14/14 | 3 |
| Mantenibilidad | Cobertura de líneas | Líneas ejecutadas / totales | ≥ 85 % | 179/179 = 100 % | 178/182 = 97.8 % | 3 |
| Mantenibilidad | Cobertura de ramas | Ramas ejecutadas / totales | ≥ 85 % | 27/28 = 96 % | 29/30 = 96.7 % | 3 |

## Detalle de las mediciones

**Pruebas (`pytest`):** 292 aprobadas, 1 omitida, 0 xfailed. Las 3 pruebas de DEF-004 que en el
ciclo 1 estaban marcadas como falla esperada ahora pasan como pruebas de regresión.

**Robustez ante valores extremos:** las 5 entradas de la sesión exploratoria 1, ahora todas con 422.

| Campo | Entrada | Ciclo 1 | Ciclo 2 |
|---|---|---|---|
| peso | 29 nueves | 500 | 422 |
| peso | `1e1000000` | 500 | 422 |
| peso | `1e308` | 500 | 422 |
| peso | `1E2` | 422 | 422 |
| monto_declarado | 29 nueves | 500 | 422 |

**Robustez y tiempo de respuesta (`python scripts/medir_robustez.py`):** 1,000 peticiones con datos
aleatorios válidos e inválidos; 455 respondieron 200, 545 respondieron 422, ninguna 500.
Tiempo medio 1.02 ms, percentil 95 1.24 ms, máximo 26.69 ms.

**Complejidad (`radon cc app -s -a`):** máximo 7 (`validar_cotizacion`), promedio 1.86.
`_tiene_mas_de_dos_decimales` pasó de V(G) 1 a 2 por la corrección de DEF-004.

**Índice de mantenibilidad (`radon mi app -s`):** todos los módulos en grado A;
`cotizador.py` 63.53 (ciclo 1: 64.25) y `main.py` 70.38.

## Observaciones

1. **La cobertura de líneas bajó de 100 % a 97.8 %** porque las líneas 76–80 de `app/main.py`, que
   sirven el frontend, no se ejecutan: el frontend vive en el repositorio `fastexpress-frontend`.
   No falta ninguna prueba de lógica de negocio: `cotizador.py` sigue con 100 % de líneas y ramas.
2. **El tiempo de respuesta** se midió en un computador distinto al del ciclo 1, así que la mejora
   no se atribuye al código.
3. **El único indicador del backend que estaba en nivel 1** (robustez ante valores extremos, por DEF-004)
   pasó a nivel 3.