"""
Paso 5 - Escribe 3 pruebas para las reglas de negocio

El fixture `cliente` (en conftest.py) te da un cliente HTTP con los datos
reiniciados en cada prueba. Recuerda quién es quién (ver app/datos.py):
    e1, e2, e3 aprobaron IS1      e4 no ha aprobado nada
    IS2 tiene solo 2 cupos y requiere IS1

Sigue el patrón Arrange / Act / Assert del ejemplo.

    pytest tests/test_paso5_mis_pruebas.py -v
"""
def test_ejemplo_inscripcion_exitosa(cliente):
    # Arrange: e1 ya aprobó IS1, así que puede ver IS2
    cuerpo = {"estudiante_id": "e1", "curso_codigo": "IS2"}
    # Act
    r = cliente.post("/inscripciones", json=cuerpo)
    # Assert
    assert r.status_code == 201
    assert r.json()["estado"] == "ACTIVA"


def test_no_permite_inscripcion_duplicada(cliente):
    # Arrange: e1 ya esta inscrito en IS2
    cuerpo = {"estudiante_id": "e1", "curso_codigo": "IS2"}
    assert cliente.post("/inscripciones", json=cuerpo).status_code == 201
    # Act: intenta inscribirlo otra vez
    r = cliente.post("/inscripciones", json=cuerpo)
    # Assert
    assert r.status_code == 409
    assert r.json()["detail"] == "DUPLICADA"


def test_no_permite_inscribir_sin_prerrequisitos(cliente):
    # Arrange: e4 no ha aprobado IS1 (prerrequisito de IS2)
    cuerpo = {"estudiante_id": "e4", "curso_codigo": "IS2"}
    # Act
    r = cliente.post("/inscripciones", json=cuerpo)
    # Assert
    assert r.status_code == 409
    assert r.json()["detail"] == "PRERREQUISITOS_PENDIENTES"


def test_no_permite_inscribir_sin_cupo(cliente):
    # Arrange: se llenan los 2 cupos de IS2 con e1 y e2
    for estudiante in ("e1", "e2"):
        r = cliente.post("/inscripciones", json={"estudiante_id": estudiante, "curso_codigo": "IS2"})
        assert r.status_code == 201
    # Act: e3 intenta inscribirse en IS2
    r = cliente.post("/inscripciones", json={"estudiante_id": "e3", "curso_codigo": "IS2"})
    # Assert
    assert r.status_code == 409
    assert r.json()["detail"] == "SIN_CUPO"