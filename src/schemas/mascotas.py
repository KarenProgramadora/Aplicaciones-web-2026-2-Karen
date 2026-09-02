from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class MascotaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    especie: str = Field(min_length=1, max_length=50)
    edad_meses: int = Field(ge=0)
    esterilizado: bool = Field(default=False)
    fecha_ingreso: date


class MascotaUpdate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    especie: str = Field(min_length=1, max_length=50)
    edad_meses: int = Field(ge=0)
    esterilizado: bool = Field(default=False)
    fecha_ingreso: date


class MascotaRead(BaseModel):
    id: UUID
    nombre: str
    especie: str
    edad_meses: int
    esterilizado: bool
    fecha_ingreso: date

    model_config = {"from_attributes": True}
