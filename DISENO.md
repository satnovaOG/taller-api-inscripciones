# Diseño de la API de Inscripciones

Grupo: ______________________________

## Paso 1 — Recursos

Un recurso es un **sustantivo** que la API expone con su propia URI.
La fila de *Curso* ya está hecha como ejemplo.

| Recurso     | URI de la colección | Atributos clave                        | Se relaciona con |
|-------------|---------------------|----------------------------------------|------------------|
| Curso       | `/cursos`           | codigo, nombre, cupos, prerrequisitos  | Inscripción      |
| Estudiante  | `/estudiantes`      | id, nombre, aprobados                  | Inscripción      |
| Inscripción | `/inscripciones`    | id, estudiante_id, curso_codigo, estado, creada_en | Estudiante, Curso |

**Pregunta:** "inscribir" es un verbo. ¿Por qué en REST lo modelamos como el
recurso *Inscripción* y no como una URI `/inscribir`?

> Respuesta: En REST las URI identifican **cosas** (sustantivos) y el verbo
> HTTP expresa la acción sobre ellas. "Inscribir" es en realidad el acto de
> **crear** un recurso nuevo que antes no existía: la *Inscripción*, que
> relaciona a un estudiante con un curso. Así `POST /inscripciones` crea la
> inscripción y el resultado tiene identidad propia: un `id`, un `estado`
> (ACTIVA/CANCELADA) y una fecha, por lo que luego se puede consultar
> (`GET /inscripciones/{id}`) o cancelar (`PATCH`). Una URI `/inscribir` sería
> una llamada a procedimiento (estilo RPC): no representa nada que se pueda
> consultar, listar o modificar después, y obligaría a inventar más verbos
> (`/cancelar`, `/consultar`...) en lugar de reutilizar los métodos HTTP.

## Paso 2 — Contrato: los 5 endpoints

Completa el código de éxito y los errores posibles de cada endpoint.
Pistas: crear → `201`; no existe → `404`; choca con una regla de negocio → `409`.

| # | Método | URI                                      | Cuerpo que recibe     | Éxito | Errores |
|---|--------|------------------------------------------|-----------------------|-------|---------|
| 1 | GET    | `/cursos`                                | —                     | 200   | —       |
| 2 | POST   | `/inscripciones`                         | `InscripcionCrear`    | 201   | 404 (estudiante o curso no existe); 409 (`DUPLICADA`, `PRERREQUISITOS_PENDIENTES`, `SIN_CUPO`) |
| 3 | GET    | `/inscripciones/{inscripcion_id}`        | —                     | 200   | 404 (inscripción no existe) |
| 4 | GET    | `/estudiantes/{estudiante_id}/inscripciones` | —                 | 200   | 404 (estudiante no existe) |
| 5 | PATCH  | `/inscripciones/{inscripcion_id}`        | `CambioEstado`        | 200   | 404 (inscripción no existe); 409 (`TRANSICION_INVALIDA`) |

## Paso 3 — Estados de una inscripción

```
   POST /inscripciones            PATCH {"estado": "CANCELADA"}
  ─────────────────────▶  ACTIVA  ──────────────────────────────▶  CANCELADA
```

**Pregunta:** ¿Qué debe responder la API si alguien intenta cancelar una
inscripción que ya está CANCELADA? ¿Por qué?

> Respuesta:
