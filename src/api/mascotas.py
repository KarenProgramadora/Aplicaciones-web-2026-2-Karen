from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import mascotas as repo
from src.database.database import get_db
from src.schemas.mascotas import MascotaCreate, MascotaRead, MascotaUpdate

router = APIRouter(prefix="/mascotas", tags=["mascota"])


@router.get("", response_model=list[MascotaRead])
def list_mascota(db: Session = Depends(get_db)):
    return repo.list_mascota(db)


@router.get("/{mascota_id}", response_model=MascotaRead)
def get_mascota(mascota_id: UUID, db: Session = Depends(get_db)):
    mascota = repo.get_mascota_by_id(db, mascota_id)
    if mascota is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return mascota


@router.post(
    "",
    response_model=MascotaRead,
    status_code=status.HTTP_201_CREATED,
)
def create_mascota(data: MascotaCreate, db: Session = Depends(get_db)):
    return repo.create_mascota(db, data)


@router.put("/{mascota_id}", response_model=MascotaRead)
def update_mascota(
    mascota_id: UUID, data: MascotaUpdate, db: Session = Depends(get_db)
):
    mascota = repo.get_mascota_by_id(db, mascota_id)
    if mascota is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return repo.update_mascota(db, mascota, data)


@router.delete("/{mascota_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mascota(mascota_id: UUID, db: Session = Depends(get_db)):
    mascota = repo.get_mascota_by_id(db, mascota_id)
    if mascota is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    repo.delete_mascota(db, mascota)
