from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import estudiantes as crud_estudiantes
from src.database.database import get_db
from src.schemas.estudiantes import (
    EstudianteCreate,
    EstudianteResponse,
    EstudianteUpdate,
)


router = APIRouter(
    prefix="/estudiantes",
    tags=["Estudiantes"],
)


@router.post(
    "/",
    response_model=EstudianteResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_estudiante(
    estudiante: EstudianteCreate,
    db: Session = Depends(get_db),
):
    return crud_estudiantes.create_estudiante(db, estudiante)


@router.get(
    "/",
    response_model=list[EstudianteResponse],
)
def listar_estudiantes(
    db: Session = Depends(get_db),
):
    return crud_estudiantes.get_estudiantes(db)


@router.get(
    "/{estudiante_id}",
    response_model=EstudianteResponse,
)
def obtener_estudiante(
    estudiante_id: UUID,
    db: Session = Depends(get_db),
):
    estudiante = crud_estudiantes.get_estudiante(db, estudiante_id)

    if estudiante is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    return estudiante


@router.put(
    "/{estudiante_id}",
    response_model=EstudianteResponse,
)
def actualizar_estudiante(
    estudiante_id: UUID,
    datos: EstudianteUpdate,
    db: Session = Depends(get_db),
):
    estudiante = crud_estudiantes.get_estudiante(db, estudiante_id)

    if estudiante is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    return crud_estudiantes.update_estudiante(
        db,
        estudiante,
        datos,
    )


@router.delete(
    "/{estudiante_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_estudiante(
    estudiante_id: UUID,
    db: Session = Depends(get_db),
):
    estudiante = crud_estudiantes.get_estudiante(db, estudiante_id)

    if estudiante is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    crud_estudiantes.delete_estudiante(db, estudiante)