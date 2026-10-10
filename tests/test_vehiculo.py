from uuid import uuid4

VEHICULO = {
    "placa": "ABC123",
    "marca": "Toyota",
    "modelo": "Corolla",
    "anio": 2022,
    "disponible": True,
}


def crear_vehiculo(client, **cambios):
    respuesta = client.post("/vehiculos", json={**VEHICULO, **cambios})
    assert respuesta.status_code == 201
    return respuesta.json()


# GET lista
def test_listar_vehiculos_ok(client):
    crear_vehiculo(client)
    respuesta = client.get("/vehiculos")
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1
    assert respuesta.json()[0]["placa"] == "ABC123"


def test_listar_vehiculos_metodo_no_permitido(client):
    respuesta = client.patch("/vehiculos")
    assert respuesta.status_code == 405
    assert respuesta.json() == {"detail": "Method Not Allowed"}


# GET por id
def test_obtener_vehiculo_ok(client):
    creado = crear_vehiculo(client)
    respuesta = client.get(f"/vehiculos/{creado['id']}")
    assert respuesta.status_code == 200
    assert respuesta.json() == creado


def test_obtener_vehiculo_inexistente(client):
    respuesta = client.get(f"/vehiculos/{uuid4()}")
    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Vehículo no encontrado"}


# POST
def test_crear_vehiculo_ok(client):
    respuesta = client.post("/vehiculos", json=VEHICULO)
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert "id" in cuerpo
    assert cuerpo["marca"] == "Toyota"
    assert cuerpo["disponible"] is True


def test_crear_vehiculo_datos_invalidos(client):
    respuesta = client.post(
        "/vehiculos", json={"marca": "Mazda", "anio": 1900}
    )
    assert respuesta.status_code == 422
    campos_con_error = {e["loc"][-1] for e in respuesta.json()["detail"]}
    assert {"placa", "modelo", "anio"} <= campos_con_error


# PUT
def test_actualizar_vehiculo_ok(client):
    creado = crear_vehiculo(client)
    nuevo = {**VEHICULO, "marca": "Mazda", "modelo": "CX-5"}
    respuesta = client.put(f"/vehiculos/{creado['id']}", json=nuevo)
    assert respuesta.status_code == 200
    assert respuesta.json()["marca"] == "Mazda"
    assert respuesta.json()["id"] == creado["id"]


def test_actualizar_vehiculo_inexistente(client):
    respuesta = client.put(f"/vehiculos/{uuid4()}", json=VEHICULO)
    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Vehículo no encontrado"}


# DELETE
def test_eliminar_vehiculo_ok(client):
    creado = crear_vehiculo(client)
    respuesta = client.delete(f"/vehiculos/{creado['id']}")
    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert client.get(f"/vehiculos/{creado['id']}").status_code == 404


def test_eliminar_vehiculo_inexistente(client):
    respuesta = client.delete(f"/vehiculos/{uuid4()}")
    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Vehículo no encontrado"}
