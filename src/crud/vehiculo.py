from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities.vehiculo import Vehiculo
from src.schemas.vehiculo import VehiculoCreate, VehiculoUpdate


def listar(db: Session) -> list[Vehiculo]:
    return list(db.scalars(select(Vehiculo).order_by(Vehiculo.marca)))


def obtener_por_id(db: Session, vehiculo_id: UUID) -> Vehiculo | None:
    return db.get(Vehiculo, vehiculo_id)


def crear(db: Session, datos: VehiculoCreate) -> Vehiculo:
    vehiculo = Vehiculo(
        placa=datos.placa,
        marca=datos.marca,
        modelo=datos.modelo,
        anio=datos.anio,
        disponible=datos.disponible,
    )
    db.add(vehiculo)
    db.commit()
    db.refresh(vehiculo)
    return vehiculo


def actualizar(
    db: Session, vehiculo: Vehiculo, datos: VehiculoUpdate
) -> Vehiculo:
    vehiculo.placa = datos.placa
    vehiculo.marca = datos.marca
    vehiculo.modelo = datos.modelo
    vehiculo.anio = datos.anio
    vehiculo.disponible = datos.disponible
    db.commit()
    db.refresh(vehiculo)
    return vehiculo


def eliminar(db: Session, vehiculo: Vehiculo) -> None:
    db.delete(vehiculo)
    db.commit()
