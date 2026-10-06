"""Fill the database with sample data.  Run: python -m app.seed"""
from sqlmodel import Session, SQLModel, select

from app.database import engine
from app.models import Hero, Mission, Team


def seed() -> None:
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if session.exec(select(Team)).first() is not None:
            print("Database already seeded, nothing to do.")
            return

        avengers = Team(name="Avengers", headquarters="New York")
        xmen = Team(name="X-Men", headquarters="Westchester")

        sokovia = Mission(title="Battle of Sokovia")
        sentinels = Mission(title="Stop the Sentinels")

        heroes = [
            Hero(name="Tony", age=45, secret_name="Iron Man", power="armor", team=avengers, missions=[sokovia]),
            Hero(name="Natasha", age=35, secret_name="Black Widow", power="espionage", team=avengers, missions=[sokovia]),
            Hero(name="Steve", age=105, secret_name="Captain America", power="super soldier", team=avengers, missions=[sokovia]),
            Hero(name="Logan", age=150, secret_name="Wolverine", power="healing", team=xmen, missions=[sentinels]),
            Hero(name="Jean", age=30, secret_name="Phoenix", power="telekinesis", team=xmen, missions=[sentinels]),
            Hero(name="Peter", age=16, secret_name="Spider-Man", power="spider sense"),
            Hero(name="Mira", age=28, secret_name="Aurora", power="light projection", team=avengers, missions=[sokovia]),
            Hero(name="Kaito", age=32, secret_name="Northstar", power="enhanced navigation", team=xmen, missions=[sentinels]),
            Hero(name="Asha", age=24, secret_name="Pulse", power="sonic waves", team=avengers, missions=[sokovia]),
            Hero(name="Orion", age=41, secret_name="Wayfinder", power="short-range teleportation", team=xmen, missions=[sentinels]),
            Hero(name="Nadia", age=27, secret_name="Verdant", power="plant growth", team=avengers, missions=[sokovia]),
            Hero(name="Tomas", age=36, secret_name="Bulwark", power="protective shields", team=xmen, missions=[sentinels]),
            Hero(name="Iris", age=22, secret_name="Prism", power="light refraction", team=avengers, missions=[sokovia]),
            Hero(name="Ravi", age=30, secret_name="Tide", power="water shaping", team=xmen, missions=[sentinels]),
            Hero(name="Elena", age=34, secret_name="Tempest", power="weather sensing", team=avengers, missions=[sokovia]),
            Hero(name="Jules", age=26, secret_name="Recall", power="memory mapping", team=xmen, missions=[sentinels]),
            Hero(name="Samira", age=29, secret_name="Aegis", power="kinetic barriers", team=avengers, missions=[sokovia]),
            Hero(name="Noah", age=31, secret_name="Mosaic", power="material sensing", team=xmen, missions=[sentinels]),
            Hero(name="Leila", age=25, secret_name="Sparrow", power="gliding", team=avengers, missions=[sokovia]),
            Hero(name="Eli", age=38, secret_name="Anchor", power="gravity control", team=xmen, missions=[sentinels]),
        ]
        session.add_all(heroes)  # teams and missions are saved through the relationships
        session.commit()
        print(f"Seeded 2 teams, {len(heroes)} heroes, 2 missions.")


if __name__ == "__main__":
    seed()
