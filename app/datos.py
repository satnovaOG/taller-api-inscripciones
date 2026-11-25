"""
Datos en memoria del taller (COMPLETO -- no lo modifiques).

Simula la base de datos de la universidad con un diccionario por recurso.
`reiniciar()` deja todo como al inicio; las pruebas lo llaman antes de cada caso.

Datos de partida:
  Cursos
    IS1  Ingeniería de Software I    30 cupos  sin prerrequisitos
    IS2  Ingeniería de Software II    2 cupos  requiere IS1
    ARQ  Arquitectura de Software    25 cupos  requiere IS2
  Estudiantes
    e1 Ana, e2 Bruno, e3 Carla  -> ya aprobaron IS1
    e4 Diego                    -> no ha aprobado nada
"""
from datetime import datetime

CURSOS: dict[str, dict] = {}
ESTUDIANTES: dict[str, dict] = {}
INSCRIPCIONES: dict[int, dict] = {}
_siguiente_id = 1


def reiniciar() -> None:
    global _siguiente_id
    CURSOS.clear()
    ESTUDIANTES.clear()
    INSCRIPCIONES.clear()
    _siguiente_id = 1
    CURSOS.update({
        "IS1": {"codigo": "IS1", "nombre": "Ingeniería de Software I", "cupos": 30, "prerrequisitos": []},
        "IS2": {"codigo": "IS2", "nombre": "Ingeniería de Software II", "cupos": 2, "prerrequisitos": ["IS1"]},
        "ARQ": {"codigo": "ARQ", "nombre": "Arquitectura de Software", "cupos": 25, "prerrequisitos": ["IS2"]},
    })
    ESTUDIANTES.update({
        "e1": {"id": "e1", "nombre": "Ana Gómez", "aprobados": ["IS1"]},
        "e2": {"id": "e2", "nombre": "Bruno Díaz", "aprobados": ["IS1"]},
        "e3": {"id": "e3", "nombre": "Carla Ruiz", "aprobados": ["IS1"]},
        "e4": {"id": "e4", "nombre": "Diego Pardo", "aprobados": []},
    })


def guardar_inscripcion(estudiante_id: str, curso_codigo: str, estado: str) -> dict:
    """Crea y guarda una inscripción nueva. Devuelve el diccionario guardado."""
    global _siguiente_id
    inscripcion = {
        "id": _siguiente_id,
        "estudiante_id": estudiante_id,
        "curso_codigo": curso_codigo,
        "estado": estado,
        "creada_en": datetime.now(),
    }
    INSCRIPCIONES[_siguiente_id] = inscripcion
    _siguiente_id += 1
    return inscripcion


def activas_del_curso(curso_codigo: str) -> list[dict]:
    """Inscripciones ACTIVAS de un curso (las que ocupan cupo)."""
    return [i for i in INSCRIPCIONES.values()
            if i["curso_codigo"] == curso_codigo and i["estado"] == "ACTIVA"]


def buscar_activa(estudiante_id: str, curso_codigo: str) -> dict | None:
    """La inscripción ACTIVA de ese estudiante en ese curso, o None."""
    for i in activas_del_curso(curso_codigo):
        if i["estudiante_id"] == estudiante_id:
            return i
    return None


def del_estudiante(estudiante_id: str) -> list[dict]:
    """Todas las inscripciones (activas o canceladas) de un estudiante."""
    return [i for i in INSCRIPCIONES.values() if i["estudiante_id"] == estudiante_id]


reiniciar()
