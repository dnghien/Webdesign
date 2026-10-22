"""Shared fixtures: every test gets a fresh in-memory SQLite DB, so the real app.db is never touched."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models import Hero, Team


@pytest.fixture(name="session")
def session_fixture():
    # StaticPool keeps ONE connection, so every session sees the same in-memory DB
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    # No "with TestClient(...)": the lifespan (create_all on the real engine) does not run
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="team")
def team_fixture(session: Session) -> Team:
    team = Team(name="Avengers", headquarters="New York")
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@pytest.fixture(name="hero")
def hero_fixture(session: Session, team: Team) -> Hero:
    hero = Hero(name="Tony", secret_name="Iron Man", age=45, power="armor", team_id=team.id)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero
