"""Medición de robustez y tiempo de respuesta (indicadores ISO 9126).

Envía 1,000 peticiones con datos aleatorios (válidos e inválidos) a la API
en ejecución y reporta:
  - cuántas respondieron 200, 422 y 500 (tolerancia a fallos)
  - tiempo medio, percentil 95 y máximo (comportamiento temporal)

Uso, con el servidor encendido (uvicorn app.main:app):
    python scripts/medir_robustez.py
"""

import random
import statistics
import time

import httpx

URL_BASE = "http://127.0.0.1:8000"
PETICIONES = 1000

random.seed(1)  # misma secuencia en cada ejecución, para poder repetir la medición

tiempos_ms = []
por_estado = {}

with httpx.Client(base_url=URL_BASE, trust_env=False) as cliente:
    for _ in range(PETICIONES):
        cuerpo = {
            "peso": round(random.uniform(-2, 25), 2),
            "tipo_cliente": random.choice(["NUEVO", "FRECUENTE", "VIP", "ORO"]),
            "tipo_envio": random.choice(["ESTANDAR", "EXPRESS"]),
            "monto_declarado": round(random.uniform(-50, 1200), 2),
        }
        inicio = time.perf_counter()
        respuesta = cliente.post("/api/v1/cotizaciones", json=cuerpo)
        tiempos_ms.append((time.perf_counter() - inicio) * 1000)
        por_estado[respuesta.status_code] = por_estado.get(respuesta.status_code, 0) + 1

tiempos_ms.sort()
p95 = tiempos_ms[int(len(tiempos_ms) * 0.95) - 1]

print(f"Peticiones enviadas: {PETICIONES}")
print(f"Respuestas por código HTTP: {dict(sorted(por_estado.items()))}")
print(f"Errores 500: {por_estado.get(500, 0)}")
print(f"Tiempo medio: {statistics.mean(tiempos_ms):.2f} ms")
print(f"Percentil 95: {p95:.2f} ms")
print(f"Máximo: {tiempos_ms[-1]:.2f} ms")
