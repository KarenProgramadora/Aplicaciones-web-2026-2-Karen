from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from main import app
import src.api.estudiantes as estudiantes_api


client = TestClient(app, raise_server_exceptions=False)


def estudiante_falso():
    """Crea un objeto falso con los atributos esperados por la API."""
    class EstudianteFalso:
        id = uuid4()
        nombre = "Karen"
        apellido = "Programadora"
        correo = "karen@test.com"
        edad = 22

    return EstudianteFalso()


# ============================================================
# 1. GET /estudiantes/ - PRUEBA EXITOSA
# ============================================================

def test_obtener_estudiantes_exitoso(monkeypatch):
    estudiante = estudiante_falso()

    def obtener_estudiantes(_db):
        return [estudiante]

    monkeypatch.setattr(
        estudiantes_api.crud_estudiantes,
        "get_estudiantes",
        obtener_estudiantes,
    )

    response = client.get("/estudiantes/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["nombre"] == "Karen"
    assert response.json()[0]["apellido"] == "Programadora"


# ============================================================
# 2. GET /estudiantes/ - PRUEBA DE ERROR
# ============================================================

def test_obtener_estudiantes_error_base_datos(monkeypatch):
    def obtener_estudiantes(_db):
        raise SQLAlchemyError("Error de conexión con la base de datos")

    monkeypatch.setattr(
        estudiantes_api.crud_estudiantes,
        "get_estudiantes",
        obtener_estudiantes,
    )

    response = client.get("/estudiantes/")

    assert response.status_code == 500


# ============================================================
# 3. GET /estudiantes/{id} - PRUEBA EXITOSA
# ============================================================

def test_obtener_estudiante_por_id_exitoso(monkeypatch):
    estudiante = estudiante_falso()
    estudiante_id = estudiante.id

    def obtener_estudiante(_db, _estudiante_id):
        return estudiante

    monkeypatch.setattr(
        estudiantes_api.crud_estudiantes,
        "get_estudiante",
        obtener_estudiante,
    )

    response = client.get(f"/estudiantes/{estudiante_id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(estudiante_id)
    assert response.json()["nombre"] == "Karen"


# ============================================================
# 4. GET /estudiantes/{id} - PRUEBA DE ERROR 404
# ============================================================

def test_obtener_estudiante_por_id_no_encontrado(monkeypatch):
    def obtener_estudiante(_db, _estudiante_id):
        return None

    monkeypatch.setattr(
        estudiantes_api.crud_estudiantes,
        "get_estudiante",
        obtener_estudiante,
    )

    estudiante_id = uuid4()

    response = client.get(f"/estudiantes/{estudiante_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Estudiante no encontrado"


# ============================================================
# 5. POST /estudiantes/ - PRUEBA EXITOSA
# ============================================================

def test_crear_estudiante_exitoso(monkeypatch):
    estudiante = estudiante_falso()

    def crear_estudiante(_db, datos):
        assert datos.nombre == "Laura"
        assert datos.apellido == "Gomez"
        return estudiante

    monkeypatch.setattr(
        estudiantes_api.crud_estudiantes,
        "create_estudiante",
        crear_estudiante,
    )

    datos = {
        "nombre": "Laura",
        "apellido": "Gomez",
        "correo": "laura@test.com",
        "edad": 21,
    }

    response = client.post("/estudiantes/", json=datos)

    assert response.status_code == 201
    assert response.json()["nombre"] == "Karen"
    assert "id" in response.json()


# ============================================================
# 6. POST /estudiantes/ - PRUEBA DE ERROR 422
# ============================================================

def test_crear_estudiante_datos_invalidos():
    datos = {
        "nombre": "A",
        "apellido": "B",
        "correo": "correo-no-valido",
        "edad": 10,
    }

    response = client.post("/estudiantes/", json=datos)

    assert response.status_code == 422
    assert "detail" in response.json()


# ============================================================
# 7. PUT /estudiantes/{id} - PRUEBA EXITOSA
# ============================================================

def test_actualizar_estudiante_exitoso(monkeypatch):
    estudiante = estudiante_falso()
    estudiante_id = estudiante.id

    def obtener_estudiante(_db, _estudiante_id):
        return estudiante

    def actualizar_estudiante(_db, _estudiante_id, datos):
        estudiante.nombre = datos.nombre
        estudiante.apellido = datos.apellido
        return estudiante

    monkeypatch.setattr(
        estudiantes_api.crud_estudiantes,
        "get_estudiante",
        obtener_estudiante,
    )

    monkeypatch.setattr(
        estudiantes_api.crud_estudiantes,
        "update_estudiante",
        actualizar_estudiante,
    )

    datos = {
        "nombre": "Maria",
        "apellido": "Lopez",
    }

    response = client.put(
        f"/estudiantes/{estudiante_id}",
        json=datos,
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "Maria"
    assert response.json()["apellido"] == "Lopez"


# ============================================================
# 8. PUT /estudiantes/{id} - PRUEBA DE ERROR 404
# ============================================================

def test_actualizar_estudiante_no_encontrado(monkeypatch):
    def obtener_estudiante(_db, _estudiante_id):
        return None

    monkeypatch.setattr(
        estudiantes_api.crud_estudiantes,
        "get_estudiante",
        obtener_estudiante,
    )

    estudiante_id = uuid4()

    datos = {
        "nombre": "Maria",
        "apellido": "Lopez",
    }

    response = client.put(
        f"/estudiantes/{estudiante_id}",
        json=datos,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Estudiante no encontrado"


# ============================================================
# 9. DELETE /estudiantes/{id} - PRUEBA EXITOSA
# ============================================================

def test_eliminar_estudiante_exitoso(monkeypatch):
    estudiante = estudiante_falso()
    estudiante_id = estudiante.id

    def obtener_estudiante(_db, _estudiante_id):
        return estudiante

    eliminado = {"valor": False}

    def eliminar_estudiante(_db, _estudiante_id):
        eliminado["valor"] = True

    monkeypatch.setattr(
        estudiantes_api.crud_estudiantes,
        "get_estudiante",
        obtener_estudiante,
    )

    monkeypatch.setattr(
        estudiantes_api.crud_estudiantes,
        "delete_estudiante",
        eliminar_estudiante,
    )

    response = client.delete(f"/estudiantes/{estudiante_id}")

    assert response.status_code == 204
    assert response.content == b""
    assert eliminado["valor"] is True


# ============================================================
# 10. DELETE /estudiantes/{id} - PRUEBA DE ERROR 404
# ============================================================

def test_eliminar_estudiante_no_encontrado(monkeypatch):
    def obtener_estudiante(_db, _estudiante_id):
        return None

    monkeypatch.setattr(
        estudiantes_api.crud_estudiantes,
        "get_estudiante",
        obtener_estudiante,
    )

    estudiante_id = uuid4()

    response = client.delete(f"/estudiantes/{estudiante_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Estudiante no encontrado"