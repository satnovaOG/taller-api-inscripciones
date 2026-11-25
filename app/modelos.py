"""
Paso 3 - Modelar el JSON y los estados de una inscripción

Cada clase de este archivo es la "forma" de un JSON que entra o sale de la API.
FastAPI usa estas clases para validar lo que llega y para documentar el contrato.

Curso y Error ya están resueltos: úsalos como ejemplo.

TU TAREA (busca los TODO(Paso 3)):
  1. EstadoInscripcion: los dos estados posibles, ACTIVA y CANCELADA.
  2. InscripcionCrear: lo que el cliente ENVÍA para inscribirse
       {"estudiante_id": "e1", "curso_codigo": "IS2"}
  3. Inscripcion: lo que la API DEVUELVE
       {"id": 1, "estudiante_id": "e1", "curso_codigo": "IS2",
        "estado": "ACTIVA", "creada_en": "2026-11-18T08:00:00"}
  4. CambioEstado: lo que se envía para cancelar
       {"estado": "CANCELADA"}

Comprueba:
    pytest tests/test_paso3_modelo.py -v
"""
from datetime import datetime  # noqa: F401  (lo necesitarás en Inscripcion)
from enum import Enum

from pydantic import BaseModel, Field


class Curso(BaseModel):
    """Ejemplo ya resuelto: así se ve un curso en JSON."""
    codigo: str = Field(examples=["IS2"])
    nombre: str = Field(examples=["Ingeniería de Software II"])
    cupos: int = Field(examples=[2])
    cupos_disponibles: int = Field(examples=[1])
    prerrequisitos: list[str] = Field(examples=[["IS1"]])


class EstadoInscripcion(str, Enum):
    # TODO(Paso 3): define los dos estados. Formato:  NOMBRE = "NOMBRE"
    pass


class InscripcionCrear(BaseModel):
    # TODO(Paso 3): dos campos de tipo str: estudiante_id y curso_codigo
    # (En el Paso 4 les agregarás un ejemplo con Field(examples=[...]))
    pass


class Inscripcion(BaseModel):
    id: int
    # TODO(Paso 3): agrega estudiante_id (str), curso_codigo (str),
    #               estado (EstadoInscripcion) y creada_en (datetime)


class CambioEstado(BaseModel):
    # TODO(Paso 3): un solo campo, estado, de tipo EstadoInscripcion
    pass


class Error(BaseModel):
    """Cuerpo de todas las respuestas de error (ya resuelto)."""
    detail: str = Field(examples=["SIN_CUPO"])
