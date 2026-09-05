from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class VehiculoCreate(BaseModel):
    placa: str = Field(min_length=1, max_length=10)
    marca: str = Field(min_length=1, max_length=50)
    modelo: str = Field(min_length=1, max_length=50)
    anio: int = Field(ge=1950, le=date.today().year + 1)
    disponible: bool = Field(default=True)


class VehiculoUpdate(BaseModel):
    placa: str = Field(min_length=1, max_length=10)
    marca: str = Field(min_length=1, max_length=50)
    modelo: str = Field(min_length=1, max_length=50)
    anio: int = Field(ge=1950, le=date.today().year + 1)
    disponible: bool = Field(default=True)


class VehiculoRead(BaseModel):
    id: UUID
    placa: str
    marca: str
    modelo: str
    anio: int
    disponible: bool

    model_config = {"from_attributes": True}
