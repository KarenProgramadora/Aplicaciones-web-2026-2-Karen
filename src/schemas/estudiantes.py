from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EstudianteBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    apellido: str = Field(..., min_length=2, max_length=50)
    correo: EmailStr
    edad: int = Field(..., ge=16, le=100)


class EstudianteCreate(EstudianteBase):
    pass


class EstudianteUpdate(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )
    apellido: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )
    correo: EmailStr | None = None
    edad: int | None = Field(
        default=None,
        ge=16,
        le=100,
    )


class EstudianteResponse(EstudianteBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)