# Guía práctica: Neon + ORM + FastAPI

Paso a paso para crear una base de datos en **Neon**, conectarla desde Python con **SQLAlchemy** (ORM), persistir datos y exponerlos con una **API REST** en FastAPI.

La teoría está en [`README.md`](README.md). Esta guía es el taller: qué pulsar, qué archivo crear y en qué orden.

---

## Qué vas a construir

```mermaid
flowchart LR
    Cliente["Cliente /docs"] --> Router["routers"]
    Router --> Repo["repositories"]
    Repo --> ORM["SQLAlchemy"]
    ORM --> Neon["Neon PostgreSQL"]
```

1. Proyecto y base de datos en Neon.
2. Cadena de conexión en `.env` (nunca en Git).
3. Modelos ORM = tablas.
4. Schemas Pydantic = JSON de entrada/salida.
5. Repositorio = leer y escribir con el ORM.
6. Router = GET / POST / PUT / DELETE.

Al final, `POST /estudiantes` guarda una fila real en Postgres y `GET /estudiantes` la vuelve a leer.

---

## Patrón de diseño: arquitectura por capas

No pondremos todo en un solo `main.py`. Cada carpeta tiene **una responsabilidad**. Así el curso puede crecer (más recursos, autenticación) sin reescribir la API.

| Capa | Carpeta | Pregunta que responde | ¿Habla con HTTP? | ¿Habla con la BD? |
| --- | --- | --- | --- | --- |
| Entrada | `app/main.py` | ¿Cómo se arranca la app? | Ensambla | No |
| Config | `app/core/` | ¿Dónde está Neon? ¿cómo abro sesión? | No | Crea el motor |
| Contrato | `app/schemas/` | ¿Qué JSON entra y sale? | Sí (Pydantic) | No |
| Persistencia | `app/models/` | ¿Cómo es la tabla? | No | Sí (ORM) |
| Acceso a datos | `app/repositories/` | ¿Cómo leo/escribo filas? | No | Sí |
| HTTP | `app/routers/` | ¿Qué ruta y qué verbo? | Sí | No (llama al repo) |

**Por qué este patrón (y no un solo archivo)**

- El router no conoce SQL: si cambias Neon por otro Postgres, el contrato HTTP no se toca.
- El modelo ORM no se mezcla con el JSON: puedes ocultar columnas internas.
- El repositorio concentra las consultas: más fácil de explicar y de probar.
- Es el mismo estilo *layered* que verán en empresas, recortado para un curso.

Más adelante, si hay reglas de negocio (validar cupos, enviar correo), se añade `app/services/` entre router y repositorio. Hoy no hace falta.

---

## Encarpetado que usaremos

```text
Aplicaciones-web-2026-2/
├── README.md                 # conceptos (API, REST, FastAPI)
├── GUIA-NEON-ORM.md          # esta guía
├── requirements.txt
├── .env.example              # plantilla sin secretos
├── .env                      # TU connection string (no se sube a Git)
└── app/
    ├── __init__.py
    ├── main.py               # FastAPI + include_router
    ├── core/
    │   ├── __init__.py
    │   ├── config.py         # lee DATABASE_URL
    │   └── database.py       # engine, Session, get_db
    ├── models/
    │   ├── __init__.py
    │   └── estudiante.py     # tabla estudiantes
    ├── schemas/
    │   ├── __init__.py
    │   └── estudiante.py     # body y respuesta JSON
    ├── repositories/
    │   ├── __init__.py
    │   └── estudiante.py     # listar, obtener, crear, actualizar, borrar
    └── routers/
        ├── __init__.py
        └── estudiantes.py    # GET POST PUT DELETE
```

`main.py` de la raíz puede quedar como el ejemplo en memoria del README conceptual. La API con Neon vive en el paquete `app/`.

Arranque:

```bash
uvicorn app.main:app --reload
```

---

## Requisitos

- Cuenta de correo o GitHub para [Neon](https://console.neon.tech/)
- Python 3.11 o superior
- Entorno virtual del curso

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Cuando llegues al paso de dependencias, el `requirements.txt` debe incluir algo como:

```text
fastapi==0.115.12
uvicorn[standard]==0.34.2
sqlalchemy>=2.0.36
psycopg[binary]>=3.2.0
python-dotenv>=1.0.1
pydantic-settings>=2.6.0
```

- **SQLAlchemy**: ORM.
- **psycopg**: driver de PostgreSQL (versión 3).
- **python-dotenv / pydantic-settings**: leer `.env`.

---

## Paso 1 — Crear la cuenta y el proyecto en Neon

1. Entra a [https://console.neon.tech](https://console.neon.tech) y regístrate (GitHub, Google o email).
2. Acepta el plan **Free** (alcanza para el curso).
3. Pulsa **New Project** / **Create project**.
4. Completa:
   - **Project name:** `itm-aplicaciones-web-2026-2` (o el de tu equipo).
   - **Postgres version:** la que venga por defecto (15 o 16).
   - **Region:** la más cercana (por ejemplo `São Paulo` o `US East`). Más cerca = menos latencia.
5. Pulsa **Create Project**.

Neon crea por ti:

- un **branch** `production`;
- una base llamada **`neondb`**;
- un rol (usuario) con contraseña;
- un compute que se duerme si nadie lo usa (en el plan gratis tarda unos segundos en despertar).

---

## Paso 2 — Crear (o usar) la base de datos

Para el curso basta **`neondb`**. Si quieres una base con nombre propio:

1. En el proyecto, menú **Project** → **Databases** (o **SQL Editor**).
2. **New database**.
3. Nombre: `itm_web`.
4. Owner: el rol que ya existe.
5. **Create**.

En el **SQL Editor** puedes comprobar que existe:

```sql
SELECT current_database();
```

Aún **no** crees la tabla `estudiantes` a mano. El ORM la creará en el paso 8. Si quieres verla después:

```sql
SELECT * FROM estudiantes;
```

---

## Paso 3 — Copiar la cadena de conexión

1. En el **Dashboard** del proyecto pulsa **Connect**.
2. Elige:
   - Branch: `production`
   - Database: `neondb` (o `itm_web`)
   - Role: el usuario que te creó Neon
3. Deja **Connection pooling** en **off** mientras desarrollas y creas tablas (conexión **directa**).
   - Directa: `ep-xxxx.us-east-2.aws.neon.tech`
   - Con pool (`-pooler` en el host): para muchas conexiones concurrentes; no la uses al crear esquema.
4. Copia la URI. Se ve así:

```text
postgresql://USUARIO:CONTRASEÑA@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require
```

Neon **exige SSL**. No quites `sslmode=require`.

Si la URI trae `channel_binding=require` y en Windows falla la conexión, déjala primero; si sigue fallando, quita solo ese parámetro y conserva `sslmode=require`.

---

## Paso 4 — Guardar la conexión en el proyecto (sin subirla)

En la raíz del repo:

**`.env.example`** (sí se sube a Git):

```env
DATABASE_URL=postgresql://USUARIO:CONTRASEÑA@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require
```

**`.env`** (no se sube; ya está en `.gitignore`):

```env
DATABASE_URL=postgresql://tu_usuario:tu_clave@ep-abc-123.us-east-2.aws.neon.tech/neondb?sslmode=require
```

Pega **tu** URI real solo en `.env`.

SQLAlchemy + psycopg 3 necesitan el esquema `postgresql+psycopg://`. En `config.py` lo convertimos para que puedas pegar la URI de Neon tal cual.

---

## Paso 5 — Capa `core`: configuración y motor ORM

### `app/__init__.py`

Vacío (marca el directorio como paquete).

### `app/core/__init__.py`

Vacío.

### `app/core/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str

    @property
    def sqlalchemy_url(self) -> str:
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


settings = Settings()
```

### `app/core/database.py`

```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.sqlalchemy_url,
    pool_pre_ping=True,  # Neon puede dormir el compute; verifica la conexión
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- `create_engine`: fábrica de conexiones.
- `SessionLocal`: una sesión = una unidad de trabajo (una petición HTTP).
- `Base`: clase padre de todos los modelos (tablas).
- `get_db`: FastAPI inyecta la sesión y la cierra al terminar.

---

## Paso 6 — Modelo ORM (la tabla)

### `app/models/__init__.py`

```python
from app.models.estudiante import Estudiante

__all__ = ["Estudiante"]
```

Importar aquí permite que `Base.metadata.create_all` “vea” todas las tablas.

### `app/models/estudiante.py`

```python
from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Estudiante(Base):
    __tablename__ = "estudiantes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(120))
    programa: Mapped[str] = mapped_column(String(120))
```

Esto **es** la tabla. El ORM traduce:

| Python | PostgreSQL |
| --- | --- |
| `Estudiante` | `estudiantes` |
| `id: UUID` | `id UUID PRIMARY KEY` |
| `nombre: str` | `nombre VARCHAR(120)` |

Todavía no hay filas. Solo el mapa objeto ↔ tabla.

---

## Paso 7 — Schemas Pydantic (el JSON)

El modelo ORM no se expone crudo en la API. El schema es el contrato REST.

### `app/schemas/estudiante.py`

```python
from uuid import UUID

from pydantic import BaseModel, Field


class EstudianteCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    programa: str = Field(min_length=1, max_length=120)


class EstudianteUpdate(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    programa: str = Field(min_length=1, max_length=120)


class EstudianteRead(BaseModel):
    id: UUID
    nombre: str
    programa: str

    model_config = {"from_attributes": True}
```

- `Create` / `Update`: lo que el cliente envía (sin `id`).
- `Read`: lo que devolvemos (con `id`).
- `from_attributes=True`: permite `EstudianteRead.model_validate(fila_orm)`.

---

## Paso 8 — Repositorio: leer y escribir con el ORM

Aquí está el “conectar y mover data”. El router no hace `db.execute`; llama a estas funciones.

### `app/repositories/estudiante.py`

```python
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.estudiante import Estudiante
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate


def listar(db: Session) -> list[Estudiante]:
    return list(db.scalars(select(Estudiante).order_by(Estudiante.nombre)))


def obtener_por_id(db: Session, estudiante_id: UUID) -> Estudiante | None:
    return db.get(Estudiante, estudiante_id)


def crear(db: Session, datos: EstudianteCreate) -> Estudiante:
    estudiante = Estudiante(nombre=datos.nombre, programa=datos.programa)
    db.add(estudiante)
    db.commit()
    db.refresh(estudiante)
    return estudiante


def actualizar(
    db: Session,
    estudiante: Estudiante,
    datos: EstudianteUpdate,
) -> Estudiante:
    estudiante.nombre = datos.nombre
    estudiante.programa = datos.programa
    db.commit()
    db.refresh(estudiante)
    return estudiante


def eliminar(db: Session, estudiante: Estudiante) -> None:
    db.delete(estudiante)
    db.commit()
```

Qué hace cada llamada ORM:

| Método | Efecto |
| --- | --- |
| `select(Estudiante)` | `SELECT * FROM estudiantes` |
| `db.get(...)` | busca por clave primaria |
| `db.add(...)` | marca la fila como nueva |
| `db.commit()` | **escribe de verdad** en Neon |
| `db.refresh(...)` | recarga el objeto (por ejemplo el `id` generado) |
| `db.delete(...)` | `DELETE FROM estudiantes WHERE id = ...` |

Sin `commit()`, Neon no guarda nada.

---

## Paso 9 — Router: la API REST

### `app/routers/estudiantes.py`

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories import estudiante as repo
from app.schemas.estudiante import EstudianteCreate, EstudianteRead, EstudianteUpdate

router = APIRouter(prefix="/estudiantes", tags=["estudiantes"])


@router.get("", response_model=list[EstudianteRead])
def listar_estudiantes(db: Session = Depends(get_db)):
    return repo.listar(db)


@router.get("/{estudiante_id}", response_model=EstudianteRead)
def obtener_estudiante(estudiante_id: UUID, db: Session = Depends(get_db)):
    estudiante = repo.obtener_por_id(db, estudiante_id)
    if estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante


@router.post("", response_model=EstudianteRead, status_code=status.HTTP_201_CREATED)
def crear_estudiante(datos: EstudianteCreate, db: Session = Depends(get_db)):
    return repo.crear(db, datos)


@router.put("/{estudiante_id}", response_model=EstudianteRead)
def actualizar_estudiante(
    estudiante_id: UUID,
    datos: EstudianteUpdate,
    db: Session = Depends(get_db),
):
    estudiante = repo.obtener_por_id(db, estudiante_id)
    if estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return repo.actualizar(db, estudiante, datos)


@router.delete("/{estudiante_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_estudiante(estudiante_id: UUID, db: Session = Depends(get_db)):
    estudiante = repo.obtener_por_id(db, estudiante_id)
    if estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    repo.eliminar(db, estudiante)
```

`Depends(get_db)` abre una sesión por petición y la cierra al responder. OPTIONS lo cubre FastAPI/CORS; no hace falta un `@router.options` a mano.

---

## Paso 10 — Ensamblar la app y crear las tablas

### `app/main.py`

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.models import estudiante as _estudiante_model  # noqa: F401
from app.routers import estudiantes


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API Estudiantes — ITM 2026-2",
    description="API REST con FastAPI, SQLAlchemy y Neon PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(estudiantes.router)


@app.get("/")
def inicio():
    return {"mensaje": "API con Neon", "docs": "/docs", "recurso": "/estudiantes"}
```

`create_all` en el arranque sirve para el curso. En producción se usan **migraciones** (Alembic). El import de `estudiante` registra el modelo en `Base.metadata`; si no lo importas, la tabla no se crea.

---

## Paso 11 — Levantar y probar el ciclo completo

```bash
uvicorn app.main:app --reload
```

La primera vez el compute de Neon puede tardar 5–15 s en despertar. Si ves un timeout, espera y reintenta.

Abre `http://127.0.0.1:8000/docs`.

### Crear (escribe en Neon)

`POST /estudiantes`

```json
{
  "nombre": "Ana Pérez",
  "programa": "Ingeniería de Sistemas"
}
```

Respuesta `201` con `id`. En el SQL Editor de Neon:

```sql
SELECT id, nombre, programa FROM estudiantes;
```

Debe aparecer la fila.

### Leer

- `GET /estudiantes` — todas las filas.
- `GET /estudiantes/{id}` — una; `404` si el UUID no existe.

### Reemplazar

`PUT /estudiantes/{id}`

```json
{
  "nombre": "Ana Pérez Gómez",
  "programa": "Ingeniería de Software"
}
```

### Borrar

`DELETE /estudiantes/{id}` → `204`. Un segundo `GET` de ese id debe dar `404`.

Si reinicias `uvicorn`, los datos **siguen ahí**: ya no viven en una lista de Python.

---

## Paso 12 — Comprobar la conexión a mano (opcional)

Si la API falla al arrancar, aísla Neon del router:

```python
from sqlalchemy import text
from app.core.database import engine

with engine.connect() as conn:
    print(conn.execute(text("SELECT version()")).scalar())
```

Si esto imprime la versión de PostgreSQL, la URI y el SSL están bien. El error entonces está en modelos o rutas.

---

## Errores frecuentes

| Síntoma | Causa habitual | Qué hacer |
| --- | --- | --- |
| `password authentication failed` | URI mal copiada o cortada | Copia de nuevo desde **Connect** |
| `SSL connection required` | Quitaste `sslmode=require` | Déjalo en la URI |
| Timeout al primer request | Compute dormido | Espera y reintenta; `pool_pre_ping=True` ya está |
| `could not translate host name` | Sin internet o host incompleto | Revisa el `.env` |
| Tabla no existe | No se importó el modelo | Importa `app.models.estudiante` antes de `create_all` |
| `.env` no se lee | Arrancas desde otra carpeta | Ejecuta `uvicorn` desde la raíz del repo |
| Subiste la contraseña a Git | Pegaste la URI en un `.py` | Rótala en Neon (**Reset password**) y usa solo `.env` |

---

## Cómo se lee esto en una petición real

Ejemplo: `GET /estudiantes`.

1. FastAPI entra a `routers/estudiantes.py`.
2. `Depends(get_db)` abre una `Session` contra Neon.
3. El router llama `repo.listar(db)`.
4. El repositorio ejecuta `select(Estudiante)` → SQL → Neon.
5. Neon devuelve filas; SQLAlchemy las convierte en objetos `Estudiante`.
6. FastAPI serializa con `EstudianteRead` a JSON.
7. `get_db` cierra la sesión.

Para `POST` el camino es el mismo hasta el repositorio; ahí `add` + `commit` insertan la fila.

---

## Qué no hacer (todavía)

- No pongas la URI en `main.py` ni en capturas de pantalla del repo.
- No uses la URI **pooled** (`-pooler`) para `create_all` / migraciones.
- No mezcles el modelo ORM y el schema en la misma clase al inicio del curso (más adelante pueden ver SQLModel).
- No abras una sola sesión global para toda la app: una sesión **por petición**.

---

## Lista de verificación del estudiante

- [ ] Proyecto creado en Neon
- [ ] Base `neondb` (o `itm_web`) visible en el dashboard
- [ ] URI copiada con `sslmode=require`
- [ ] `.env` local y `.env.example` sin secretos
- [ ] Carpetas `app/core`, `models`, `schemas`, `repositories`, `routers`
- [ ] `uvicorn app.main:app --reload` arranca
- [ ] `POST` crea fila visible en el SQL Editor de Neon
- [ ] `GET` la vuelve a leer
- [ ] `PUT` y `DELETE` funcionan
- [ ] Reiniciar el servidor **no** borra los estudiantes
