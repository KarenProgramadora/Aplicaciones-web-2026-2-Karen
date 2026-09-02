from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities.mascotas import Mascota
from src.schemas.mascotas import MascotaCreate, MascotaUpdate


def list_mascota(db: Session) -> list[Mascota]:
    return list(db.scalars(select(Mascota).order_by(Mascota.nombre)))


def get_mascota_by_id(db: Session, mascota_id: UUID) -> Mascota | None:
    return db.get(Mascota, mascota_id)


def create_mascota(db: Session, data: MascotaCreate) -> Mascota:
    mascota = Mascota(
        nombre=data.nombre,
        especie=data.especie,
        edad_meses=data.edad_meses,
        esterilizado=data.esterilizado,
        fecha_ingreso=data.fecha_ingreso,
    )
    db.add(mascota)
    db.commit()
    db.refresh(mascota)
    return mascota


def update_mascota(
    db: Session, mascota: Mascota, data: MascotaUpdate
) -> Mascota:
    mascota.nombre = data.nombre
    mascota.especie = data.especie
    mascota.edad_meses = data.edad_meses
    mascota.esterilizado = data.esterilizado
    mascota.fecha_ingreso = data.fecha_ingreso
    db.commit()
    db.refresh(mascota)
    return mascota


def delete_mascota(db: Session, mascota: Mascota) -> None:
    db.delete(mascota)
    db.commit()
