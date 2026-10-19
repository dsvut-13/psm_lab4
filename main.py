from typing import Protocol

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from database import engine
from models import Laureate

app = FastAPI(title="Nobel Laureates REST API")


# DTO з валідацією email за допомогою regex
class LaureateCreate(BaseModel):
    full_name: str
    contact_email: str = Field(
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    )
    year_awarded: int
    category_id: int


# Абстрактний інтерфейс репозиторію (Принцип OCP)[cite: 22]
class AbstractRepository(Protocol):
    def get_all(self) -> list[Laureate]: ...
    def get_by_id(self, id: int) -> Laureate | None: ...
    def create(self, data: LaureateCreate) -> Laureate: ...
    def update(self, id: int, data: LaureateCreate) -> Laureate | None: ...
    def delete(self, id: int) -> bool: ...


# Конкретна реалізація репозиторію для PostgreSQL[cite: 18, 21]
class PostgresRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Laureate]:
        return list(self.session.exec(select(Laureate)).all())

    def get_by_id(self, id: int) -> Laureate | None:
        return self.session.get(Laureate, id)

    def create(self, data: LaureateCreate) -> Laureate:
        db_laureate = Laureate(**data.model_dump())
        self.session.add(db_laureate)
        self.session.commit()
        self.session.refresh(db_laureate)
        return db_laureate

    def update(self, id: int, data: LaureateCreate) -> Laureate | None:
        db_laureate = self.session.get(Laureate, id)
        if db_laureate:
            for key, value in data.model_dump().items():
                setattr(db_laureate, key, value)
            self.session.add(db_laureate)
            self.session.commit()
            self.session.refresh(db_laureate)
        return db_laureate

    def delete(self, id: int) -> bool:
        db_laureate = self.session.get(Laureate, id)
        if db_laureate:
            self.session.delete(db_laureate)
            self.session.commit()
            return True
        return False


def get_repository():
    with Session(engine) as session:
        yield PostgresRepository(session)


# Ендпоінти REST API[cite: 19, 21]
@app.get("/laureates/")
def read_laureates(repo: AbstractRepository = Depends(get_repository)):
    return repo.get_all()


@app.get("/laureates/{laureate_id}")
def read_laureate(
    laureate_id: int, repo: AbstractRepository = Depends(get_repository)
):
    laureate = repo.get_by_id(laureate_id)
    if not laureate:
        raise HTTPException(
            status_code=404, detail="Лауреата з таким ID не знайдено"
        )
    return laureate


@app.post("/laureates/")
def create_laureate(
    laureate: LaureateCreate,
    repo: AbstractRepository = Depends(get_repository),
):
    return repo.create(laureate)


@app.put("/laureates/{laureate_id}")
def update_laureate(
    laureate_id: int,
    laureate: LaureateCreate,
    repo: AbstractRepository = Depends(get_repository),
):
    updated = repo.update(laureate_id, laureate)
    if not updated:
        raise HTTPException(
            status_code=404, detail="Лауреата з таким ID не знайдено"
        )
    return updated


@app.delete("/laureates/{laureate_id}")
def delete_laureate(
    laureate_id: int, repo: AbstractRepository = Depends(get_repository)
):
    if not repo.delete(laureate_id):
        raise HTTPException(
            status_code=404, detail="Лауреата з таким ID не знайдено"
        )
    return {"message": "Лауреата успішно видалено"}