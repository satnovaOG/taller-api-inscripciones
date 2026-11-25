# API de Inscripciones Lab

Taller práctico de diseño de APIs REST — Ingeniería de Software II,
Universidad Nacional de Colombia.

Vas a diseñar y construir, en 6 pasos cortos, el contrato REST de un sistema
de inscripciones académicas que controla **cupos**, **prerrequisitos** y
**duplicados**. Cada paso tiene pruebas automáticas que te dicen si quedó bien,
y puedes ver y probar la API en el navegador a medida que avanzas.

## Instalación

Requiere Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Levanta la API (déjala corriendo en otra terminal; se recarga sola al guardar):

```bash
uvicorn app.main:app --reload
```

Y abre **http://127.0.0.1:8000/docs**.

## Estructura

```
docs/                   Enunciado del taller (PDF)
DISENO.md               Pasos 1, 2 y 3: tu diseño en papel (tablas para completar)
app/
  datos.py              "Base de datos" en memoria (completo, no lo modifiques)
  modelos.py            Paso 3: la forma de los JSON y los estados
  main.py               Pasos 2, 3 y 4: los 5 endpoints y sus reglas
  exportar_openapi.py   Paso 4: genera openapi.json (completo)
tests/
  test_paso2_endpoints.py
  test_paso3_modelo.py
  test_paso4_openapi.py
  test_paso5_mis_pruebas.py   Paso 5: aquí escribes TUS 3 pruebas
cliente-http/           Paso 6: lo exportado de Postman (u otra herramienta) y una captura
```

## Cómo trabajar cada paso

1. Busca los `TODO(Paso N)` del paso en el que vas.
2. Complétalos.
3. Corre las pruebas de ese paso:

   ```bash
   pytest tests/test_paso2_endpoints.py -v
   pytest tests/test_paso3_modelo.py -v
   pytest tests/test_paso4_openapi.py -v
   pytest tests/test_paso5_mis_pruebas.py -v
   ```

   O todas a la vez: `pytest -v`

## Los 6 pasos

| # | Paso | Dónde | Qué haces |
|---|------|-------|-----------|
| 1 | Identificar recursos | `DISENO.md` | Completar la tabla de recursos y sus URIs |
| 2 | Definir 5 endpoints | `DISENO.md`, `app/main.py` | Completar el contrato y ponerle el decorador a cada endpoint |
| 3 | Modelar JSON y estados | `app/modelos.py`, `app/main.py` | Modelos Pydantic, estados ACTIVA/CANCELADA y las 3 reglas |
| 4 | Documentar con OpenAPI | `app/main.py`, `app/modelos.py` | `summary`, `tags`, `responses`, ejemplos y exportar `openapi.json` |
| 5 | Crear 3 pruebas | `tests/test_paso5_mis_pruebas.py` | Probar duplicados, prerrequisitos y cupos |
| 6 | Probar con un cliente HTTP | `cliente-http/` | Ejecutar las peticiones desde Postman u otra herramienta y guardar lo exportado |

## Datos de partida

| Curso | Nombre | Cupos | Prerrequisitos |
|-------|--------|-------|----------------|
| IS1 | Ingeniería de Software I | 30 | — |
| IS2 | Ingeniería de Software II | **2** | IS1 |
| ARQ | Arquitectura de Software | 25 | IS2 |

Estudiantes: `e1`, `e2`, `e3` ya aprobaron IS1; `e4` no ha aprobado nada.

## Entrega

Un `.zip` del repositorio con `DISENO.md` completo, `openapi.json` exportado
y la carpeta `cliente-http/` con lo exportado de tu herramienta y una captura,
con `pytest -v` en verde.
