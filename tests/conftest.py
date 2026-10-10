import os

os.environ.setdefault(
    "DATABASE_URL", "postgresql://usuario:clave@localhost:5432/pruebas"
)

# pylint: disable=wrong-import-position
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from src.database.database import Base, get_db


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    sesion_prueba = sessionmaker(
        bind=engine, autoflush=False, autocommit=False
    )

    def get_db_prueba():
        db = sesion_prueba()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_prueba
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()
