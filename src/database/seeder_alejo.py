from datetime import date

from src.database.database import SessionLocal
from src.database.seeder import _insertar_si_falta, crear_tablas
from src.entities import Mascota

MASCOTAS_SEMILLA = [
    {
        "nombre": "Firulais",
        "especie": "Perro",
        "edad_meses": 8,
        "esterilizado": False,
        "fecha_ingreso": date(2026, 9, 1),
    },
    {
        "nombre": "Michi",
        "especie": "Gato",
        "edad_meses": 14,
        "esterilizado": True,
        "fecha_ingreso": date(2026, 8, 15),
    },
    {
        "nombre": "Rocky",
        "especie": "Perro",
        "edad_meses": 24,
        "esterilizado": True,
        "fecha_ingreso": date(2026, 7, 20),
    },
]


def main() -> None:
    crear_tablas()

    db = SessionLocal()
    try:
        mascotas = _insertar_si_falta(
            db, Mascota, "nombre", MASCOTAS_SEMILLA
        )
    finally:
        db.close()

    print(f"Seeder de Alejo terminado. Filas nuevas: {mascotas}")


if __name__ == "__main__":
    main()
