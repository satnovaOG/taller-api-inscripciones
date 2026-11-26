# Diseño de la API de Inscripciones

**Curso:** Ingeniería de Software II — Universidad Nacional de Colombia (2026-2)  
**Grupo:** Santiago Montealegre Romero

---

## Paso 1 — Recursos

En REST, un recurso es un **sustantivo** que representa una entidad del dominio y se expone mediante su propia URI.

| Recurso | URI de la colección | Atributos clave | Se relaciona con |
|---|---|---|---|
| Curso | `/cursos` | `codigo`, `nombre`, `cupos`, `cupos_disponibles` *(derivado)*, `prerrequisitos` | Inscripción |
| Estudiante | `/estudiantes` | `id`, `nombre`, `aprobados` | Inscripción |
| Inscripción | `/inscripciones` | `id`, `estudiante_id`, `curso_codigo`, `estado`, `creada_en` | Estudiante, Curso |

> **Notas del modelo de dominio:**
> - **Inscripción** actúa como el recurso asociativo que vincula a un `Estudiante` con un `Curso`.
> - Los **cupos totales** (`cupos`) pertenecen al recurso `Curso`, mientras que `cupos_disponibles` se calcula dinámicamente restando las inscripciones en estado `ACTIVA` del curso.
> - Los **cursos aprobados** (`aprobados`) pertenecen al recurso `Estudiante` y se consultan al validar los `prerrequisitos` del curso.

**Pregunta:** "inscribir" es un verbo. ¿Por qué en REST lo modelamos como el recurso *Inscripción* y no como una URI `/inscribir`?

> **Respuesta:** En REST las URIs identifican **recursos** (sustantivos) y los métodos HTTP expresan la acción sobre ellos (`GET`, `POST`, `PATCH`, `DELETE`). "Inscribir" es en realidad la acción de **crear** un recurso nuevo que antes no existía: una *Inscripción*, que materializa la relación entre un estudiante y un curso.
>
> Al usar `POST /inscripciones`, el resultado tiene identidad y ciclo de vida propios (`id`, `estado` y `creada_en`), lo que permite reutilizar la misma URI y la semántica estándar de HTTP para consultarlo (`GET /inscripciones/{inscripcion_id}`), listarlo por estudiante (`GET /estudiantes/{estudiante_id}/inscripciones`) o cancelarlo (`PATCH /inscripciones/{inscripcion_id}`).
>
> En cambio, una URI `/inscribir` sigue un estilo RPC (llamada a procedimiento): no expone una entidad direccionable y obliga a multiplicar endpoints basados en verbos (`/cancelar`, `/consultar`, `/listar-inscripciones`), rompiendo la uniformidad de la interfaz REST.

---

## Paso 2 — Contrato: los 5 endpoints

Contrato REST definido e implementado en [`app/main.py`](app/main.py) y exportado en [`openapi.json`](openapi.json):

| # | Método | URI | Cuerpo que recibe | Éxito | Errores posibles |
|---|---|---|---|---|---|
| 1 | `GET` | `/cursos` | — | `200 OK` (`list[Curso]`) | — |
| 2 | `POST` | `/inscripciones` | `InscripcionCrear` | `201 Created` (`Inscripcion`) | `404` (`NO_ENCONTRADO`: estudiante o curso no existe); `409` (`DUPLICADA`, `PRERREQUISITOS_PENDIENTES`, `SIN_CUPO`); `422` (esquema JSON inválido) |
| 3 | `GET` | `/inscripciones/{inscripcion_id}` | — | `200 OK` (`Inscripcion`) | `404` (`NO_ENCONTRADO`: la inscripción no existe); `422` (`inscripcion_id` no entero) |
| 4 | `GET` | `/estudiantes/{estudiante_id}/inscripciones` | — | `200 OK` (`list[Inscripcion]`) | `404` (`NO_ENCONTRADO`: el estudiante no existe) |
| 5 | `PATCH` | `/inscripciones/{inscripcion_id}` | `CambioEstado` | `200 OK` (`Inscripcion`) | `404` (`NO_ENCONTRADO`: la inscripción no existe); `409` (`TRANSICION_INVALIDA`); `422` (estado fuera del enum `EstadoInscripcion`) |

### Orden de validación de reglas en `POST /inscripciones`

Para garantizar respuestas deterministas cuando confluyen varias condiciones, las validaciones se evalúan en orden estricto:

1. **Existencia (`404 NO_ENCONTRADO`):** verificar que tanto `estudiante_id` como `curso_codigo` existan.
2. **Duplicado (`409 DUPLICADA`):** el estudiante ya tiene una inscripción `ACTIVA` en ese curso.
3. **Prerrequisitos (`409 PRERREQUISITOS_PENDIENTES`):** al menos un prerrequisito del curso no figura en `estudiante.aprobados`.
4. **Cupos (`409 SIN_CUPO`):** el número de inscripciones `ACTIVA` del curso alcanzó su límite `cupos`.

### ¿Por qué cancelar con `PATCH` y no con `DELETE`?

- `PATCH /inscripciones/{inscripcion_id}` realiza una **modificación parcial** del atributo `estado` (`ACTIVA` → `CANCELADA`), preservando el registro histórico.
- Usar `DELETE` eliminaría el recurso y se perdería trazabilidad académica y de auditoría (saber que un estudiante se inscribió y canceló, y cuándo lo hizo).
- Aunque la inscripción sigue existiendo, al pasar a `CANCELADA` deja de contarse entre las activas y **libera inmediatamente el cupo** en `GET /cursos`.

---

## Paso 3 — Estados de una inscripción y modelos JSON

### Máquina de estados

```text
   POST /inscripciones            PATCH {"estado": "CANCELADA"}
  ─────────────────────▶  ACTIVA  ──────────────────────────────▶  CANCELADA
                       (ocupa cupo)                            (estado final,
                                                                no ocupa cupo)
```

- **Estado inicial:** toda inscripción creada con `POST /inscripciones` nace en estado `ACTIVA`.
- **Única transición válida:** `ACTIVA` → `CANCELADA`.
- **Estado final:** `CANCELADA` no admite transiciones salientes (ni volver a `CANCELADA` ni reactivarse a `ACTIVA`).

### Esquemas JSON principales (`app/modelos.py`)

- **`InscripcionCrear`** *(entrada de `POST /inscripciones`)*:
  ```json
  {
    "estudiante_id": "e1",
    "curso_codigo": "IS2"
  }
  ```
- **`Inscripcion`** *(respuesta de creación, consulta y cancelación)*:
  ```json
  {
    "id": 1,
    "estudiante_id": "e1",
    "curso_codigo": "IS2",
    "estado": "ACTIVA",
    "creada_en": "2026-11-25T15:14:34"
  }
  ```
- **`CambioEstado`** *(entrada de `PATCH /inscripciones/{inscripcion_id}`)*:
  ```json
  {
    "estado": "CANCELADA"
  }
  ```
- **`Error`** *(respuesta estándar de errores `404` y `409`)*:
  ```json
  {
    "detail": "SIN_CUPO"
  }
  ```

**Pregunta:** ¿Qué debe responder la API si alguien intenta cancelar una inscripción que ya está `CANCELADA`? ¿Por qué?

> **Respuesta:** Debe responder **`409 Conflict`** con el cuerpo `{"detail": "TRANSICION_INVALIDA"}`.
>
> - No corresponde `400 Bad Request` ni `422 Unprocessable Entity`, porque la petición está bien formada sintácticamente y `"CANCELADA"` es un valor válido del enum `EstadoInscripcion`.
> - No corresponde `404 Not Found`, porque la inscripción existe.
> - El conflicto ocurre contra el **estado actual del recurso y una regla de negocio**: la única transición permitida es `ACTIVA` → `CANCELADA`, y `CANCELADA` es un estado final. Rechazarlo explícitamente con `409` evita ocultar errores lógicos del cliente y garantiza invariantes del dominio (por ejemplo, impedir que una reactivación vulnere el control de cupos).

---

## Decisiones de diseño adicionales

- **`409 Conflict` frente a `400/422` en reglas de negocio:** los errores `DUPLICADA`, `PRERREQUISITOS_PENDIENTES`, `SIN_CUPO` y `TRANSICION_INVALIDA` no provienen de un JSON mal formado, sino de un conflicto entre la operación solicitada y el estado vigente del sistema. Reservar `422` para validación de tipos/esquemas (Pydantic) y `409` para reglas de dominio hace el contrato más predecible para los clientes.
- **Contrato OpenAPI (`openapi.json`):** documenta rutas, parámetros, esquemas, ejemplos y códigos de error (`404`, `409`), lo que permite a otro equipo generar clientes o colecciones automáticamente; aun así, las **reglas de precedencia de errores** y la **máquina de estados** se complementan en este documento para evitar ambigüedades.
- **Pruebas unitarias (`pytest`) vs. cliente HTTP:** `pytest` valida rápidamente las reglas de negocio en memoria durante el desarrollo, mientras que un cliente HTTP externo (Postman / script HTTP) verifica el comportamiento real sobre la red (serialización, cabeceras `Content-Type`, códigos HTTP y flujos encadenados entre endpoints), sirviendo además como documentación ejecutable para QA y frontend.
