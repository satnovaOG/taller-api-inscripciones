"""
API de Inscripciones -- Pasos 2, 3 y 4

Levántala con:
    uvicorn app.main:app --reload
y abre http://127.0.0.1:8000/docs  (ahí ves y pruebas todo lo que vayas haciendo)

El endpoint 1 (GET /cursos) ya está resuelto: úsalo de modelo para los demás.
Las funciones 2 a 5 ya existen, pero todavía NO son endpoints: les falta el decorador.

  Paso 2  ->  TODO(Paso 2): ponle a cada función su decorador @app.<método>("<ruta>", ...)
  Paso 3  ->  TODO(Paso 3): completa las reglas de cupos, prerrequisitos, duplicados y estados
  Paso 4  ->  TODO(Paso 4): documenta cada endpoint (tags, summary y responses)

Errores: siempre  raise HTTPException(status_code=..., detail="CODIGO")
Ejemplo de errores documentados para el Paso 4:
    responses={404: {"model": Error, "description": "NO_ENCONTRADO"}}
"""
from fastapi import FastAPI, HTTPException

from app import datos
from app.modelos import CambioEstado, Curso, Error, EstadoInscripcion, Inscripcion, InscripcionCrear  # noqa: F401

app = FastAPI(
    title="API de Inscripciones",
    version="1.0.0",
    description="Inscripciones académicas con control de cupos, prerrequisitos y duplicados.",
)


def _curso_json(c: dict) -> dict:
    return {**c, "cupos_disponibles": c["cupos"] - len(datos.activas_del_curso(c["codigo"]))}


# 1 --- GET /cursos  (EJEMPLO RESUELTO) ----------------------------------------
@app.get(
    "/cursos",
    response_model=list[Curso],
    tags=["Cursos"],
    summary="Listar cursos con sus cupos disponibles",
)
def listar_cursos():
    return [_curso_json(c) for c in datos.CURSOS.values()]


# 2 --- POST /inscripciones ----------------------------------------------------
# TODO(Paso 2): decorador para  POST /inscripciones
#               con response_model=Inscripcion y status_code=201 (se crea un recurso)
# TODO(Paso 4): agrégale tags=["Inscripciones"], un summary y responses para 404 y 409
def crear_inscripcion(cuerpo: InscripcionCrear):
    estudiante = datos.ESTUDIANTES.get(cuerpo.estudiante_id)
    curso = datos.CURSOS.get(cuerpo.curso_codigo)
    if estudiante is None or curso is None:
        raise HTTPException(status_code=404, detail="NO_ENCONTRADO")

    # TODO(Paso 3) Regla 1 - DUPLICADA
    #   Si datos.buscar_activa(estudiante_id, curso_codigo) encuentra algo -> 409 "DUPLICADA"

    # TODO(Paso 3) Regla 2 - PRERREQUISITOS_PENDIENTES
    #   Si algún código de curso["prerrequisitos"] NO está en estudiante["aprobados"] -> 409

    # TODO(Paso 3) Regla 3 - SIN_CUPO
    #   Si len(datos.activas_del_curso(codigo)) >= curso["cupos"] -> 409 "SIN_CUPO"

    return datos.guardar_inscripcion(cuerpo.estudiante_id, cuerpo.curso_codigo,
                                     EstadoInscripcion.ACTIVA.value)


# 3 --- GET /inscripciones/{inscripcion_id} ------------------------------------
# TODO(Paso 2): decorador para  GET /inscripciones/{inscripcion_id}
#               con response_model=Inscripcion
# TODO(Paso 4): tags, summary y responses para 404
def obtener_inscripcion(inscripcion_id: int):
    inscripcion = datos.INSCRIPCIONES.get(inscripcion_id)
    if inscripcion is None:
        raise HTTPException(status_code=404, detail="NO_ENCONTRADO")
    return inscripcion


# 4 --- GET /estudiantes/{estudiante_id}/inscripciones -------------------------
# TODO(Paso 2): decorador para  GET /estudiantes/{estudiante_id}/inscripciones
#               con response_model=list[Inscripcion]
# TODO(Paso 4): tags=["Estudiantes"] y un summary
def inscripciones_de_estudiante(estudiante_id: str):
    if estudiante_id not in datos.ESTUDIANTES:
        raise HTTPException(status_code=404, detail="NO_ENCONTRADO")
    return datos.del_estudiante(estudiante_id)


# 5 --- PATCH /inscripciones/{inscripcion_id} ----------------------------------
# TODO(Paso 2): decorador para  PATCH /inscripciones/{inscripcion_id}
#               con response_model=Inscripcion
# TODO(Paso 4): tags, summary y responses para 404 y 409
def cambiar_estado(inscripcion_id: int, cuerpo: CambioEstado):
    inscripcion = datos.INSCRIPCIONES.get(inscripcion_id)
    if inscripcion is None:
        raise HTTPException(status_code=404, detail="NO_ENCONTRADO")

    # TODO(Paso 3) Única transición válida:  ACTIVA --> CANCELADA
    #   Si la inscripción NO está "ACTIVA" o cuerpo.estado NO es CANCELADA
    #     -> 409 "TRANSICION_INVALIDA"
    #   Si es válida: cambia inscripcion["estado"] a "CANCELADA" y devuélvela.
    raise NotImplementedError("Completa el Paso 3")
