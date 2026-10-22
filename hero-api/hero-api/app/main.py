from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app import models  # noqa: F401 (importing the models registers them in SQLModel.metadata)
from app.database import engine
from app.routers import heroes, teams


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)  # creates only the tables that do not exist yet
    yield


tags_metadata = [
    {"name": "heroes", "description": "Create, list, filter, update and delete heroes; assign missions."},
    {"name": "teams", "description": "Teams (unique names) and the heroes that belong to them."},
]

app = FastAPI(
    title="Hero API",
    description="REST API for heroes, teams and missions (FastAPI + SQLModel + Alembic).",
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

# Lab 2: allow the frontend served by VS Code Live Server to call the API from the browser
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(heroes.router, prefix="/api/v1")
app.include_router(teams.router, prefix="/api/v1")
