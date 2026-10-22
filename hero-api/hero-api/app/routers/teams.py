from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.database import SessionDep
from app.models import HeroPublic, Team, TeamCreate, TeamPublic

router = APIRouter(prefix="/teams", tags=["teams"])


def error(status_code: int, detail: str) -> dict:
    """OpenAPI description of an error response, shown in /docs and /redoc."""
    return {status_code: {"description": detail,
                          "content": {"application/json": {"example": {"detail": detail}}}}}


@router.post("", response_model=TeamPublic, status_code=201,
             summary="Create a team", responses=error(409, "Team name already exists"))
def create_team(team_in: TeamCreate, session: SessionDep):
    """Create a team. Team names are unique: a duplicate returns 409 Conflict."""
    team = Team.model_validate(team_in)
    session.add(team)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Team name already exists")
    session.refresh(team)
    return team


@router.get("", response_model=list[TeamPublic], summary="List teams")
def list_teams(session: SessionDep):
    """List all teams ordered by id."""
    return session.exec(select(Team).order_by(Team.id)).all()


@router.get("/{team_id}/heroes", response_model=list[HeroPublic],
            summary="List the heroes of a team", responses=error(404, "Team not found"))
def list_team_heroes(team_id: int, session: SessionDep):
    """Return the heroes that belong to this team."""
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.heroes  # relationship: SQLAlchemy runs the SELECT for us
