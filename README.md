# API de Inscripciones

API REST desarrollada con **FastAPI** para la gestión de inscripciones académicas con control de **cupos**, **prerrequisitos**, **duplicados** y **transiciones de estado**.

> **Curso:** Ingeniería de Software II — Universidad Nacional de Colombia (2026-2)  
> **Docente:** Liliana Marcela Olarte Mesa  
> **Autor:** Santiago Montealegre Romero

---

## Descripción general

La API modela tres recursos principales (`Curso`, `Estudiante` e `Inscripción`) y expone un contrato REST de 5 endpoints documentado con **OpenAPI 3.1**. El almacenamiento es en memoria (`app/datos.py`) para facilitar pruebas reproducibles y demostraciones locales.

### Reglas de negocio implementadas

- **Existencia (`404 NO_ENCONTRADO`):** tanto el estudiante como el curso (o la inscripción consultada/modificada) deben existir.
- **Sin duplicados (`409 DUPLICADA`):** un estudiante no puede tener más de una inscripción `ACTIVA` en el mismo curso.
- **Prerrequisitos (`409 PRERREQUISITOS_PENDIENTES`):** el estudiante debe haber aprobado todos los prerrequisitos definidos por el curso.
- **Control de cupos (`409 SIN_CUPO`):** solo las inscripciones en estado `ACTIVA` ocupan cupo.
- **Ciclo de vida controlado (`409 TRANSICION_INVALIDA`):** toda inscripción inicia en `ACTIVA` y únicamente puede pasar a `CANCELADA` (estado final que libera el cupo).

El detalle completo de recursos, contrato, esquemas JSON y decisiones de diseño se encuentra en [`DISENO.md`](DISENO.md).

---

## Contrato REST

| # | Método | Ruta | Descripción | Éxito | Errores |
|---|---|---|---|---|---|
| 1 | `GET` | `/cursos` | Listar cursos con sus cupos disponibles | `200` | — |
| 2 | `POST` | `/inscripciones` | Inscribir a un estudiante en un curso | `201` | `404` (`NO_ENCONTRADO`), `409` (`DUPLICADA`, `PRERREQUISITOS_PENDIENTES`, `SIN_CUPO`), `422` |
| 3 | `GET` | `/inscripciones/{inscripcion_id}` | Consultar una inscripción por su `id` | `200` | `404` (`NO_ENCONTRADO`), `422` |
| 4 | `GET` | `/estudiantes/{estudiante_id}/inscripciones` | Listar las inscripciones de un estudiante | `200` | `404` (`NO_ENCONTRADO`) |
| 5 | `PATCH` | `/inscripciones/{inscripcion_id}` | Cancelar una inscripción (`ACTIVA` → `CANCELADA`) | `200` | `404` (`NO_ENCONTRADO`), `409` (`TRANSICION_INVALIDA`), `422` |

La especificación completa del contrato está exportada en [`openapi.json`](openapi.json).

---

## Requisitos e instalación

- **Python 3.10+**

```bash
python3 -m venv .venv
source .venv/bin/activate        # En Windows (PowerShell): .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Ejecución de la API

Levanta el servidor local con recarga automática:

```bash
uvicorn app.main:app --reload
```

Una vez iniciado, quedan disponibles:

- **Swagger UI (pruebas interactivas):** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
- **Esquema OpenAPI en vivo:** `http://127.0.0.1:8000/openapi.json`

Para regenerar el archivo estático [`openapi.json`](openapi.json) desde la aplicación:

```bash
python -m app.exportar_openapi
```

---

## Datos iniciales en memoria

Cada vez que se inicia la API (o antes de cada caso en `pytest`), los datos se reinician con el siguiente estado base (`app/datos.py`):

### Cursos

| Código | Nombre | Cupos | Prerrequisitos |
|---|---|---:|---|
| `IS1` | Ingeniería de Software I | 30 | — |
| `IS2` | Ingeniería de Software II | **2** | `IS1` |
| `ARQ` | Arquitectura de Software | 25 | `IS2` |

### Estudiantes

| ID | Nombre | Cursos aprobados |
|---|---|---|
| `e1` | Ana Gómez | `IS1` |
| `e2` | Bruno Díaz | `IS1` |
| `e3` | Carla Ruiz | `IS1` |
| `e4` | Diego Pardo | *(ninguno)* |

---

## Pruebas automatizadas (`pytest`)

Ejecuta toda la suite de pruebas:

```bash
pytest -v
```

También puedes ejecutar cada suite por separado:

| Archivo | Qué verifica | Comando |
|---|---|---|
| `tests/test_paso2_endpoints.py` | Existencia exacta de los 5 endpoints, métodos y `201 Created` | `pytest tests/test_paso2_endpoints.py -v` |
| `tests/test_paso3_modelo.py` | Modelos Pydantic, estados `ACTIVA`/`CANCELADA`, liberación de cupos y rechazo de transiciones/estados inválidos | `pytest tests/test_paso3_modelo.py -v` |
| `tests/test_paso4_openapi.py` | Metadatos OpenAPI (`tags`, `summary`, `responses`, ejemplos) y vigencia de `openapi.json` | `pytest tests/test_paso4_openapi.py -v` |
| `tests/test_paso5_mis_pruebas.py` | Reglas de negocio: `DUPLICADA`, `PRERREQUISITOS_PENDIENTES` y `SIN_CUPO` | `pytest tests/test_paso5_mis_pruebas.py -v` |

---

## Pruebas desde cliente HTTP (Paso 6)

La carpeta [`cliente-http/`](cliente-http/) incluye dos alternativas para validar el flujo completo de 9 peticiones contra la API corriendo en `http://127.0.0.1:8000` (con datos recién inicializados):

1. **Colección de Postman:** importa [`cliente-http/inscripciones_postman_collection.json`](cliente-http/inscripciones_postman_collection.json) en Postman Desktop y ejecútala con el *Collection Runner*. Utiliza las variables de colección `base_url` e `inscripcion_id`.
2. **Script en PowerShell:**
   ```powershell
   .\cliente-http\probar_api.ps1
   ```

### Secuencia verificada

| # | Petición | Resultado esperado |
|---|---|---|
| 1 | `POST /inscripciones` (`e1` en `IS2`) | `201` (`ACTIVA`, guarda `inscripcion_id`) |
| 2 | `POST /inscripciones` (`e1` en `IS2` de nuevo) | `409 DUPLICADA` |
| 3 | `POST /inscripciones` (`e4` en `IS2`) | `409 PRERREQUISITOS_PENDIENTES` |
| 4 | `POST /inscripciones` (`e2` en `IS2`) | `201` (`ACTIVA`) |
| 5 | `POST /inscripciones` (`e3` en `IS2`) | `409 SIN_CUPO` |
| 6 | `GET /inscripciones/{inscripcion_id}` | `200` |
| 7 | `GET /estudiantes/e1/inscripciones` | `200` |
| 8 | `PATCH /inscripciones/{inscripcion_id}` (`{"estado": "CANCELADA"}`) | `200` (`CANCELADA`) |
| 9 | `GET /cursos` | `200` (`IS2` con `cupos_disponibles: 1`) |

---

## Estructura del repositorio

```text
.
├── DISENO.md                                     # Diseño REST: recursos, contrato, estados y decisiones
├── README.md                                     # Documentación general del proyecto
├── openapi.json                                  # Especificación OpenAPI 3.1 exportada
├── pytest.ini                                    # Configuración de pytest
├── requirements.txt                              # Dependencias Python
├── app/
│   ├── datos.py                                  # Almacenamiento en memoria y datos iniciales
│   ├── modelos.py                                # Esquemas Pydantic y enum EstadoInscripcion
│   ├── main.py                                   # Endpoints FastAPI y reglas de negocio
│   └── exportar_openapi.py                       # Script para exportar openapi.json
├── tests/
│   ├── conftest.py                               # Fixture de cliente HTTP con datos reiniciados
│   ├── test_paso2_endpoints.py                   # Pruebas de rutas y códigos HTTP
│   ├── test_paso3_modelo.py                      # Pruebas de modelos y máquina de estados
│   ├── test_paso4_openapi.py                     # Pruebas del contrato OpenAPI
│   └── test_paso5_mis_pruebas.py                 # Pruebas de reglas de negocio (409)
├── cliente-http/
│   ├── LEEME.md                                  # Guía del cliente HTTP
│   ├── inscripciones_postman_collection.json     # Colección exportada de Postman (9 peticiones)
│   ├── probar_api.ps1                            # Script automatizado de verificación HTTP
│   └── resultados.txt                            # Registro de salida de pruebas HTTP
└── docs/
    └── Taller-API-Inscripciones-Enunciado.pdf    # Enunciado original del taller
```

---

## Resumen de pasos completados

- [x] **Paso 1:** Identificación de recursos y URIs en [`DISENO.md`](DISENO.md).
- [x] **Paso 2:** Definición de los 5 endpoints y códigos HTTP en [`DISENO.md`](DISENO.md) y [`app/main.py`](app/main.py).
- [x] **Paso 3:** Modelado de esquemas Pydantic, estados `ACTIVA`/`CANCELADA` y reglas de negocio en [`app/modelos.py`](app/modelos.py) y [`app/main.py`](app/main.py).
- [x] **Paso 4:** Documentación OpenAPI (`tags`, `summary`, `responses`, ejemplos) y exportación de [`openapi.json`](openapi.json).
- [x] **Paso 5:** Pruebas de reglas de negocio (`DUPLICADA`, `PRERREQUISITOS_PENDIENTES`, `SIN_CUPO`) en [`tests/test_paso5_mis_pruebas.py`](tests/test_paso5_mis_pruebas.py).
- [x] **Paso 6:** Colección de Postman y script de verificación HTTP en [`cliente-http/`](cliente-http/).
