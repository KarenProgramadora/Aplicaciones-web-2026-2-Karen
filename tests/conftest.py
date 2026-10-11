import os

os.environ["DATABASE_URL"] = "sqlite://"

# pylint: disable=wrong-import-position
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from src.database.database import Base, get_db


@pytest.fixture(name="client")
def client_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(
        bind=engine, autoflush=False, autocommit=False
    )

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(name="mascota_valida")
def mascota_valida_fixture():
    return {
        "nombre": "Firulais",
        "especie": "Perro",
        "edad_meses": 8,
        "esterilizado": False,
        "fecha_ingreso": "2026-09-01",
    }
