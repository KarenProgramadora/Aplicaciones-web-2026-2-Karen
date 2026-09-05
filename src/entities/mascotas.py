from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


class Mascota(Base):
    __tablename__ = "mascotas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    especie: Mapped[str] = mapped_column(String(50), nullable=False)
    edad_meses: Mapped[int] = mapped_column(nullable=False)
    esterilizado: Mapped[bool] = mapped_column(default=False)
    fecha_ingreso: Mapped[date] = mapped_column(Date, nullable=False)
