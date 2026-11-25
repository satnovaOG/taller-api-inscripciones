"""
Pruebas del Paso 2 - Los 5 endpoints existen con el método y la ruta correctos.

    pytest tests/test_paso2_endpoints.py -v
"""
import pytest
from fastapi.routing import APIRoute

from app.main import app

CONTRATO = [
    ("GET", "/cursos"),
    ("POST", "/inscripciones"),
    ("GET", "/inscripciones/{inscripcion_id}"),
    ("GET", "/estudiantes/{estudiante_id}/inscripciones"),
    ("PATCH", "/inscripciones/{inscripcion_id}"),
]


def _rutas():
    return {(m, r.path): r for r in app.routes if isinstance(r, APIRoute) for m in r.methods}


@pytest.mark.parametrize("metodo,ruta", CONTRATO)
def test_endpoint_existe(metodo, ruta):
    assert (metodo, ruta) in _rutas(), (
        f"Falta el endpoint {metodo} {ruta}. Agrega su decorador @app.{metodo.lower()}(...)"
    )


def test_hay_exactamente_5_endpoints():
    assert len(_rutas()) == 5, "La API debe tener exactamente los 5 endpoints del contrato."


def test_crear_inscripcion_responde_201():
    ruta = _rutas().get(("POST", "/inscripciones"))
    assert ruta is not None, "Primero crea POST /inscripciones."
    assert ruta.status_code == 201, (
        "Crear un recurso debe responder 201 Created: usa status_code=201 en el decorador."
    )


def test_listar_cursos_funciona(cliente):
    r = cliente.get("/cursos")
    assert r.status_code == 200
    assert {c["codigo"] for c in r.json()} == {"IS1", "IS2", "ARQ"}
