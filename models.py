from sqlmodel import Field, Relationship, SQLModel


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    laureates: list[Laureate] = Relationship(back_populates="category")


class Laureate(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    full_name: str
    contact_email: str
    year_awarded: int
    category_id: int | None = Field(default=None, foreign_key="category.id")

    category: Category | None = Relationship(back_populates="laureates")