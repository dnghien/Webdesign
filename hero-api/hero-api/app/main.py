from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Response
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, select

from app.database import SessionDep, engine
from app.models import (  # importing the models registers them in SQLModel.metadata
    Hero, HeroCreate, HeroPublic, HeroUpdate,
    Mission, MissionCreate, MissionPublic,
    Team, TeamCreate, TeamPublic,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)  # creates only the tables that do not exist yet
    yield


app = FastAPI(title="Hero API", lifespan=lifespan)


# ---------- helpers ----------
def get_hero_or_404(session: SessionDep, hero_id: int) -> Hero:
    hero = session.get(Hero, hero_id)
    if hero is None:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


def ensure_team_exists(session: SessionDep, team_id: int | None) -> None:
    if team_id is not None and session.get(Team, team_id) is None:
        raise HTTPException(status_code=404, detail="Team not found")


# ---------- Heroes ----------
@app.post("/heroes", response_model=HeroPublic, status_code=201)
def create_hero(hero_in: HeroCreate, session: SessionDep):
    ensure_team_exists(session, hero_in.team_id)
    hero = Hero.model_validate(hero_in)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.get("/heroes", response_model=list[HeroPublic])
def list_heroes(
    session: SessionDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, le=100),
    min_age: int | None = None,
    team_id: int | None = None,
    name: str | None = None,
):
    statement = select(Hero)
    if min_age is not None:
        statement = statement.where(Hero.age >= min_age)
    if team_id is not None:
        statement = statement.where(Hero.team_id == team_id)
    if name is not None:
        statement = statement.where(Hero.name.ilike(f"%{name}%"))
    statement = statement.order_by(Hero.id).offset(offset).limit(limit)
    return session.exec(statement).all()


@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    return get_hero_or_404(session, hero_id)


@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero_in: HeroUpdate, session: SessionDep):
    hero = get_hero_or_404(session, hero_id)
    data = hero_in.model_dump(exclude_unset=True)  # only the fields the client sent
    if "team_id" in data:
        ensure_team_exists(session, data["team_id"])
    hero.sqlmodel_update(data)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.delete("/heroes/{hero_id}", status_code=204)
def delete_hero(hero_id: int, session: SessionDep):
    hero = get_hero_or_404(session, hero_id)
    session.delete(hero)
    session.commit()
    return Response(status_code=204)


# ---------- Teams ----------
@app.post("/teams", response_model=TeamPublic, status_code=201)
def create_team(team_in: TeamCreate, session: SessionDep):
    team = Team.model_validate(team_in)
    session.add(team)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Team name already exists")
    session.refresh(team)
    return team


@app.get("/teams", response_model=list[TeamPublic])
def list_teams(session: SessionDep):
    return session.exec(select(Team).order_by(Team.id)).all()


@app.get("/teams/{team_id}/heroes", response_model=list[HeroPublic])
def list_team_heroes(team_id: int, session: SessionDep):
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.heroes  # relationship: SQLAlchemy runs the SELECT for us


# ---------- Missions ----------
@app.post("/missions", response_model=MissionPublic, status_code=201)
def create_mission(mission_in: MissionCreate, session: SessionDep):
    mission = Mission.model_validate(mission_in)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


@app.post("/heroes/{hero_id}/missions/{mission_id}", status_code=204)
def assign_mission(hero_id: int, mission_id: int, session: SessionDep):
    hero = get_hero_or_404(session, hero_id)
    mission = session.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission not in hero.missions:  # already assigned -> do nothing
        hero.missions.append(mission)
        session.add(hero)
        session.commit()
    return Response(status_code=204)


@app.get("/heroes/{hero_id}/missions", response_model=list[MissionPublic])
def list_hero_missions(hero_id: int, session: SessionDep):
    return get_hero_or_404(session, hero_id).missions
