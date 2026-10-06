# Hero API — Week 9 (PostgreSQL + SQLModel + Alembic)

## Setup
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install "fastapi[standard]" sqlmodel "psycopg[binary]" alembic

# PostgreSQL (as administrator): CREATE USER app WITH PASSWORD 'secret'; CREATE DATABASE appdb OWNER app;
export DATABASE_URL="postgresql+psycopg://app:secret@localhost:5432/appdb"   # PowerShell: $env:DATABASE_URL = "..."

alembic upgrade head      # create / update the schema
python -m app.seed        # sample data (safe to run twice)
fastapi dev app/main.py   # http://127.0.0.1:8000/docs
```

## Structure
- `app/database.py` — engine (`echo=True`), `get_session`, `SessionDep`
- `app/models.py` — Team, Hero, Mission, HeroMissionLink + Create / Public / Update schemas
- `app/main.py` — endpoints (heroes CRUD + filters, teams with 409, missions many-to-many)
- `app/seed.py` — 2 teams, 20 heroes and 2 missions using relationships
- `migrations/` — Alembic: `initial schema` → `add hero.power`
- `sql/warmup.sql` — Part 1 SQL
- `answers.md` — answers to Questions 1–20

## Endpoints
| Method | Path | Status |
|---|---|---|
| POST | /heroes | 201, 404 unknown team |
| GET | /heroes?offset&limit&min_age&team_id&name | 200 (limit ≤ 100) |
| GET / PATCH / DELETE | /heroes/{id} | 200 / 200 / 204, 404 |
| POST / GET | /teams | 201 (409 duplicate name) / 200 |
| GET | /teams/{id}/heroes | 200, 404 |
| POST | /missions | 201 |
| POST | /heroes/{hero_id}/missions/{mission_id} | 204 (idempotent), 404 |
| GET | /heroes/{id}/missions | 200, 404 |
