from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import vehiculo as repo
from src.database.database import get_db
from src.schemas.vehiculo import VehiculoCreate, VehiculoRead, VehiculoUpdate

router = APIRouter(prefix="/vehiculos", tags=["vehiculos"])


@router.get("", response_model=list[VehiculoRead])
def listar_vehiculos(db: Session = Depends(get_db)):
    return repo.listar(db)


@router.get("/{vehiculo_id}", response_model=VehiculoRead)
def obtener_vehiculo(vehiculo_id: UUID, db: Session = Depends(get_db)):
    vehiculo = repo.obtener_por_id(db, vehiculo_id)
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo


@router.post(
    "",
    response_model=VehiculoRead,
    status_code=status.HTTP_201_CREATED,
)
def crear_vehiculo(datos: VehiculoCreate, db: Session = Depends(get_db)):
    return repo.crear(db, datos)


@router.put("/{vehiculo_id}", response_model=VehiculoRead)
def actualizar_vehiculo(
    vehiculo_id: UUID,
    datos: VehiculoUpdate,
    db: Session = Depends(get_db),
):
    vehiculo = repo.obtener_por_id(db, vehiculo_id)
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return repo.actualizar(db, vehiculo, datos)


@router.delete("/{vehiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_vehiculo(vehiculo_id: UUID, db: Session = Depends(get_db)):
    vehiculo = repo.obtener_por_id(db, vehiculo_id)
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    repo.eliminar(db, vehiculo)
