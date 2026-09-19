from src.database.database import SessionLocal
from src.database.seeder import _insertar_si_falta, crear_tablas
from src.entities import Vehiculo

VEHICULOS_SEMILLA = [
    {
        "placa": "ABC123",
        "marca": "Toyota",
        "modelo": "Corolla",
        "anio": 2022,
        "disponible": True,
    },
    {
        "placa": "DEF456",
        "marca": "Mazda",
        "modelo": "CX-5",
        "anio": 2021,
        "disponible": True,
    },
    {
        "placa": "GHI789",
        "marca": "Chevrolet",
        "modelo": "Spark",
        "anio": 2023,
        "disponible": False,
    },
]


def main() -> None:
    crear_tablas()

    db = SessionLocal()
    try:
        vehiculos = _insertar_si_falta(
            db, Vehiculo, "placa", VEHICULOS_SEMILLA
        )
    finally:
        db.close()

    print(f"Seeder de Jose terminado. Filas nuevas: {vehiculos}")


if __name__ == "__main__":
    main()
