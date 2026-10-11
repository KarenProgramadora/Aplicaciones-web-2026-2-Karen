from uuid import uuid4

URL = "/mascotas"


def _crear(client, datos):
    return client.post(URL, json=datos)


# ---------- GET lista ----------
def test_listar_mascotas_normal(client, mascota_valida):
    _crear(client, mascota_valida)

    respuesta = client.get(URL)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["nombre"] == "Firulais"


def test_listar_mascotas_error_metodo_no_permitido(client):
    respuesta = client.patch(URL)

    assert respuesta.status_code == 405
    assert respuesta.json() == {"detail": "Method Not Allowed"}


# ---------- GET por ID ----------
def test_obtener_mascota_normal(client, mascota_valida):
    creada = _crear(client, mascota_valida).json()

    respuesta = client.get(f"{URL}/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_obtener_mascota_error_id_inexistente(client):
    respuesta = client.get(f"{URL}/{uuid4()}")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Mascota no encontrada"}


# ---------- POST ----------
def test_crear_mascota_normal(client, mascota_valida):
    respuesta = _crear(client, mascota_valida)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert "id" in cuerpo
    assert cuerpo["nombre"] == "Firulais"
    assert cuerpo["edad_meses"] == 8
    assert cuerpo["esterilizado"] is False


def test_crear_mascota_error_edad_negativa(client, mascota_valida):
    mascota_valida["edad_meses"] = -1

    respuesta = _crear(client, mascota_valida)

    assert respuesta.status_code == 422
    error = respuesta.json()["detail"][0]
    assert error["loc"] == ["body", "edad_meses"]
    assert error["type"] == "greater_than_equal"


# ---------- PUT ----------
def test_actualizar_mascota_normal(client, mascota_valida):
    creada = _crear(client, mascota_valida).json()
    mascota_valida["edad_meses"] = 9
    mascota_valida["esterilizado"] = True

    respuesta = client.put(f"{URL}/{creada['id']}", json=mascota_valida)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["id"] == creada["id"]
    assert cuerpo["edad_meses"] == 9
    assert cuerpo["esterilizado"] is True


def test_actualizar_mascota_error_id_inexistente(client, mascota_valida):
    respuesta = client.put(f"{URL}/{uuid4()}", json=mascota_valida)

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Mascota no encontrada"}


# ---------- DELETE ----------
def test_eliminar_mascota_normal(client, mascota_valida):
    creada = _crear(client, mascota_valida).json()

    respuesta = client.delete(f"{URL}/{creada['id']}")

    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert client.get(f"{URL}/{creada['id']}").status_code == 404


def test_eliminar_mascota_error_id_inexistente(client):
    respuesta = client.delete(f"{URL}/{uuid4()}")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Mascota no encontrada"}
