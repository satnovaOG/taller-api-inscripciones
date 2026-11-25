"""
Pruebas del Paso 4 - El contrato queda documentado en OpenAPI.

    python -m app.exportar_openapi      # genera openapi.json
    pytest tests/test_paso4_openapi.py -v
"""
import json
from pathlib import Path

import pytest

from app.main import app

RAIZ = Path(__file__).resolve().parent.parent

OPERACIONES = [
    ("get", "/cursos"),
    ("post", "/inscripciones"),
    ("get", "/inscripciones/{inscripcion_id}"),
    ("get", "/estudiantes/{estudiante_id}/inscripciones"),
    ("patch", "/inscripciones/{inscripcion_id}"),
]


def _op(metodo, ruta):
    return app.openapi()["paths"].get(ruta, {}).get(metodo, {})


@pytest.mark.parametrize("metodo,ruta", OPERACIONES)
def test_cada_endpoint_tiene_summary_y_tag(metodo, ruta):
    op = _op(metodo, ruta)
    assert op.get("summary"), f"{metodo.upper()} {ruta}: agrega summary='...' al decorador."
    assert op.get("tags"), f"{metodo.upper()} {ruta}: agrega tags=[...] al decorador."


def test_crear_documenta_sus_errores():
    respuestas = _op("post", "/inscripciones").get("responses", {})
    assert "404" in respuestas and "409" in respuestas, (
        "POST /inscripciones debe documentar 404 y 409 con responses={...}."
    )


def test_cancelar_documenta_sus_errores():
    respuestas = _op("patch", "/inscripciones/{inscripcion_id}").get("responses", {})
    assert "404" in respuestas and "409" in respuestas


def test_consultar_documenta_404():
    assert "404" in _op("get", "/inscripciones/{inscripcion_id}").get("responses", {})


def test_inscripcion_crear_tiene_ejemplos():
    esquema = app.openapi()["components"]["schemas"]["InscripcionCrear"]["properties"]
    for campo in ("estudiante_id", "curso_codigo"):
        assert esquema[campo].get("examples"), (
            f"InscripcionCrear.{campo}: agrega Field(examples=[...]) para que /docs muestre un ejemplo."
        )


def test_openapi_json_exportado():
    archivo = RAIZ / "openapi.json"
    assert archivo.exists(), "Corre `python -m app.exportar_openapi` para generar openapi.json."
    contrato = json.loads(archivo.read_text(encoding="utf-8"))
    assert set(contrato["paths"]) == set(app.openapi()["paths"]), (
        "openapi.json está desactualizado: vuelve a exportarlo."
    )
