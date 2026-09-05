from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities.estudiantes import Estudiante
from src.schemas.estudiantes import EstudianteCreate, EstudianteUpdate


def create_estudiante(db: Session, estudiante: EstudianteCreate) -> Estudiante:
    nuevo_estudiante = Estudiante(
        nombre=estudiante.nombre,
        apellido=estudiante.apellido,
        correo=estudiante.correo,
        edad=estudiante.edad,
    )

    db.add(nuevo_estudiante)
    db.commit()
    db.refresh(nuevo_estudiante)

    return nuevo_estudiante


def get_estudiantes(db: Session) -> list[Estudiante]:
    result = db.execute(select(Estudiante))
    return list(result.scalars().all())


def get_estudiante(db: Session, estudiante_id: UUID) -> Estudiante | None:
    return db.get(Estudiante, estudiante_id)


def update_estudiante(
    db: Session,
    estudiante: Estudiante,
    datos: EstudianteUpdate,
) -> Estudiante:
    if datos.nombre is not None:
        estudiante.nombre = datos.nombre

    if datos.apellido is not None:
        estudiante.apellido = datos.apellido

    if datos.correo is not None:
        estudiante.correo = datos.correo

    if datos.edad is not None:
        estudiante.edad = datos.edad

    db.commit()
    db.refresh(estudiante)

    return estudiante


def delete_estudiante(db: Session, estudiante: Estudiante) -> None:
    db.delete(estudiante)
    db.commit()
