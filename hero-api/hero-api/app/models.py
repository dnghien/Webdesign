from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


# ---------- Team ----------
class TeamBase(SQLModel):
    name: str = Field(index=True, unique=True, min_length=2, max_length=50,
                      schema_extra={"examples": ["Avengers"]})
    headquarters: str = Field(min_length=2, max_length=100,
                              schema_extra={"examples": ["New York"]})


class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    heroes: list["Hero"] = Relationship(back_populates="team")


class TeamCreate(TeamBase):
    pass


class TeamPublic(TeamBase):
    id: int


# ---------- Hero <-> Mission link (many-to-many) ----------
class HeroMissionLink(SQLModel, table=True):
    hero_id: int | None = Field(default=None, foreign_key="hero.id", primary_key=True)
    mission_id: int | None = Field(default=None, foreign_key="mission.id", primary_key=True)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ---------- Hero ----------
class HeroStatus(str, Enum):
    active = "active"
    retired = "retired"


class HeroBase(SQLModel):
    name: str = Field(index=True, min_length=2, max_length=50,
                      schema_extra={"examples": ["Tony"]})
    age: int | None = Field(default=None, ge=0, le=200,
                            schema_extra={"examples": [45]})
    power: str | None = Field(default=None, max_length=100,  # Part 9: added with an Alembic migration
                              schema_extra={"examples": ["armor"]})
    team_id: int | None = Field(default=None, foreign_key="team.id",
                                schema_extra={"examples": [1]})
    status: HeroStatus = Field(default=HeroStatus.active,  # Enum -> drop-down in /docs
                               schema_extra={"examples": ["active"]})


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str = Field(max_length=50)
    created_at: datetime = Field(default_factory=utc_now)

    team: Team | None = Relationship(back_populates="heroes")
    missions: list["Mission"] = Relationship(back_populates="heroes",
                                             link_model=HeroMissionLink)


class HeroCreate(HeroBase):
    secret_name: str = Field(min_length=2, max_length=50,
                             schema_extra={"examples": ["Iron Man"]})


class HeroPublic(HeroBase):
    id: int
    created_at: datetime


class HeroUpdate(SQLModel):
    """Every field is optional: PATCH changes only what the client sends."""
    name: str | None = Field(default=None, min_length=2, max_length=50,
                             schema_extra={"examples": ["Tony"]})
    age: int | None = Field(default=None, ge=0, le=200,
                            schema_extra={"examples": [46]})
    power: str | None = Field(default=None, max_length=100,
                              schema_extra={"examples": ["nano armor"]})
    team_id: int | None = Field(default=None, schema_extra={"examples": [2]})
    secret_name: str | None = Field(default=None, min_length=2, max_length=50,
                                    schema_extra={"examples": ["Iron Man"]})
    status: HeroStatus | None = Field(default=None, schema_extra={"examples": ["retired"]})


# ---------- Mission ----------
class MissionBase(SQLModel):
    title: str = Field(min_length=2, max_length=100,
                       schema_extra={"examples": ["Battle of Sokovia"]})


class Mission(MissionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    heroes: list[Hero] = Relationship(back_populates="missions",
                                      link_model=HeroMissionLink)


class MissionCreate(MissionBase):
    pass


class MissionPublic(MissionBase):
    id: int
