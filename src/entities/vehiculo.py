from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    placa: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    marca: Mapped[str] = mapped_column(String(50), nullable=False)
    modelo: Mapped[str] = mapped_column(String(50), nullable=False)
    anio: Mapped[int] = mapped_column(nullable=False)
    disponible: Mapped[bool] = mapped_column(default=True)
