from sqlmodel import Session, SQLModel, create_engine

from models import Category, Laureate

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/nobel_db"
engine = create_engine(DATABASE_URL)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        if session.query(Category).first():
            return

        physics = Category(name="Physics")
        literature = Category(name="Literature")
        session.add_all([physics, literature])
        session.commit()

        laureates = []
        for i in range(1, 60):
            cat_id = physics.id if i % 2 == 0 else literature.id
            laureates.append(
                Laureate(
                    full_name=f"Laureate Name {i}",
                    contact_email=f"laureate{i}@nobelprize.org",
                    year_awarded=1900 + i,
                    category_id=cat_id,
                )
            )

        session.add_all(laureates)
        session.commit()
        print("Базу даних успішно ініціалізовано (створено 50+ записів).")


if __name__ == "__main__":
    init_db()