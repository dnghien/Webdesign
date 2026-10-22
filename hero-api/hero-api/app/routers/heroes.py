from fastapi import APIRouter, HTTPException, Query, Response
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Hero, HeroCreate, HeroPublic, HeroStatus, HeroUpdate,
    Mission, MissionCreate, MissionPublic, Team,
)

router = APIRouter(tags=["heroes"])


def error(status_code: int, detail: str) -> dict:
    """OpenAPI description of an error response, shown in /docs and /redoc."""
    return {status_code: {"description": detail,
                          "content": {"application/json": {"example": {"detail": detail}}}}}


def not_found(detail: str) -> dict:
    return error(404, detail)


UNKNOWN_TEAM = error(400, "Team not found")


# ---------- helpers ----------
def get_hero_or_404(session: SessionDep, hero_id: int) -> Hero:
    hero = session.get(Hero, hero_id)
    if hero is None:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


def ensure_team_exists(session: SessionDep, team_id: int | None) -> None:
    # 400, not 404: the URL is fine, the team_id inside the body is invalid
    if team_id is not None and session.get(Team, team_id) is None:
        raise HTTPException(status_code=400, detail="Team not found")


# ---------- Heroes ----------
@router.post("/heroes", response_model=HeroPublic, status_code=201,
             summary="Create a hero", responses=UNKNOWN_TEAM)
def create_hero(hero_in: HeroCreate, session: SessionDep):
    """Create a hero. `team_id` is optional but must point to an existing team."""
    ensure_team_exists(session, hero_in.team_id)
    hero = Hero.model_validate(hero_in)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.get("/heroes", response_model=list[HeroPublic], summary="List heroes")
def list_heroes(
    session: SessionDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    min_age: int | None = Query(default=None, ge=0),
    team_id: int | None = None,
    name: str | None = Query(default=None, description="Case-insensitive substring of the name"),
    status: HeroStatus | None = None,
):
    """List heroes ordered by id, with paging (`limit` ≤ 100) and optional filters."""
    statement = select(Hero)
    if min_age is not None:
        statement = statement.where(Hero.age >= min_age)
    if team_id is not None:
        statement = statement.where(Hero.team_id == team_id)
    if name is not None:
        statement = statement.where(Hero.name.ilike(f"%{name}%"))
    if status is not None:
        statement = statement.where(Hero.status == status)
    statement = statement.order_by(Hero.id).offset(offset).limit(limit)
    return session.exec(statement).all()


@router.get("/heroes/{hero_id}", response_model=HeroPublic,
            summary="Get one hero", responses=not_found("Hero not found"))
def read_hero(hero_id: int, session: SessionDep):
    """Return the hero with this id (the secret name is never exposed)."""
    return get_hero_or_404(session, hero_id)


@router.patch("/heroes/{hero_id}", response_model=HeroPublic,
              summary="Update a hero", responses={**not_found("Hero not found"), **UNKNOWN_TEAM})
def update_hero(hero_id: int, hero_in: HeroUpdate, session: SessionDep):
    """Partial update: only the fields sent are changed. Send `team_id` to move the hero to another team."""
    hero = get_hero_or_404(session, hero_id)
    data = hero_in.model_dump(exclude_unset=True)  # only the fields the client sent
    if "team_id" in data:
        ensure_team_exists(session, data["team_id"])
    hero.sqlmodel_update(data)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.delete("/heroes/{hero_id}", status_code=204,
               summary="Delete a hero", responses=not_found("Hero not found"))
def delete_hero(hero_id: int, session: SessionDep):
    """Delete the hero. Returns 204 with an empty body."""
    hero = get_hero_or_404(session, hero_id)
    session.delete(hero)
    session.commit()
    return Response(status_code=204)


# ---------- Missions (hero sub-resource) ----------
@router.post("/missions", response_model=MissionPublic, status_code=201,
             summary="Create a mission")
def create_mission(mission_in: MissionCreate, session: SessionDep):
    """Create a mission that heroes can then be assigned to."""
    mission = Mission.model_validate(mission_in)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


@router.post("/heroes/{hero_id}/missions/{mission_id}", status_code=204,
             summary="Assign a mission to a hero",
             responses=not_found("Hero not found / Mission not found"))
def assign_mission(hero_id: int, mission_id: int, session: SessionDep):
    """Link a hero to a mission. Idempotent: assigning twice changes nothing."""
    hero = get_hero_or_404(session, hero_id)
    mission = session.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission not in hero.missions:  # already assigned -> do nothing
        hero.missions.append(mission)
        session.add(hero)
        session.commit()
    return Response(status_code=204)


@router.get("/heroes/{hero_id}/missions", response_model=list[MissionPublic],
            summary="List the missions of a hero", responses=not_found("Hero not found"))
def list_hero_missions(hero_id: int, session: SessionDep):
    """Return the missions this hero is assigned to."""
    return get_hero_or_404(session, hero_id).missions
