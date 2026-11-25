"""
Pruebas del Paso 3 - Modelos JSON y estados de una inscripción.

(Las reglas de cupos, prerrequisitos y duplicados NO se prueban aquí:
 esas pruebas las escribes tú en el Paso 5.)

    pytest tests/test_paso3_modelo.py -v
"""
from app import modelos


def test_estados_de_inscripcion():
    assert {e.value for e in modelos.EstadoInscripcion} == {"ACTIVA", "CANCELADA"}, (
        "EstadoInscripcion debe tener exactamente ACTIVA y CANCELADA."
    )


def test_campos_de_inscripcion_crear():
    assert set(modelos.InscripcionCrear.model_fields) == {"estudiante_id", "curso_codigo"}, (
        "Para crear una inscripción solo se envían estudiante_id y curso_codigo."
    )


def test_campos_de_inscripcion():
    esperados = {"id", "estudiante_id", "curso_codigo", "estado", "creada_en"}
    assert set(modelos.Inscripcion.model_fields) == esperados


def test_campos_de_cambio_estado():
    assert set(modelos.CambioEstado.model_fields) == {"estado"}


def test_inscripcion_nueva_queda_activa(cliente):
    r = cliente.post("/inscripciones", json={"estudiante_id": "e1", "curso_codigo": "IS1"})
    assert r.status_code == 201, r.text
    cuerpo = r.json()
    assert cuerpo["estado"] == "ACTIVA"
    assert cuerpo["id"] == 1
    assert cuerpo["estudiante_id"] == "e1" and cuerpo["curso_codigo"] == "IS1"


def test_inscripcion_ocupa_un_cupo(cliente):
    cliente.post("/inscripciones", json={"estudiante_id": "e1", "curso_codigo": "IS2"})
    is2 = next(c for c in cliente.get("/cursos").json() if c["codigo"] == "IS2")
    assert is2["cupos_disponibles"] == 1


def test_consultar_inscripcion(cliente):
    cliente.post("/inscripciones", json={"estudiante_id": "e1", "curso_codigo": "IS1"})
    assert cliente.get("/inscripciones/1").status_code == 200
    assert cliente.get("/inscripciones/99").status_code == 404


def test_inscripciones_de_estudiante(cliente):
    cliente.post("/inscripciones", json={"estudiante_id": "e1", "curso_codigo": "IS1"})
    r = cliente.get("/estudiantes/e1/inscripciones")
    assert r.status_code == 200 and len(r.json()) == 1
    assert cliente.get("/estudiantes/nadie/inscripciones").status_code == 404


def test_cancelar_cambia_estado_y_libera_cupo(cliente):
    cliente.post("/inscripciones", json={"estudiante_id": "e1", "curso_codigo": "IS2"})
    r = cliente.patch("/inscripciones/1", json={"estado": "CANCELADA"})
    assert r.status_code == 200, r.text
    assert r.json()["estado"] == "CANCELADA"
    is2 = next(c for c in cliente.get("/cursos").json() if c["codigo"] == "IS2")
    assert is2["cupos_disponibles"] == 2, "Una inscripción cancelada no debe ocupar cupo."


def test_no_se_cancela_dos_veces(cliente):
    cliente.post("/inscripciones", json={"estudiante_id": "e1", "curso_codigo": "IS1"})
    cliente.patch("/inscripciones/1", json={"estado": "CANCELADA"})
    r = cliente.patch("/inscripciones/1", json={"estado": "CANCELADA"})
    assert r.status_code == 409
    assert r.json()["detail"] == "TRANSICION_INVALIDA"


def test_estado_desconocido_es_rechazado(cliente):
    cliente.post("/inscripciones", json={"estudiante_id": "e1", "curso_codigo": "IS1"})
    r = cliente.patch("/inscripciones/1", json={"estado": "PERDIDA"})
    assert r.status_code == 422, "Pydantic debe rechazar estados que no existen en el Enum."
