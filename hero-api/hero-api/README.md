# Hero API — Week 9 (PostgreSQL + SQLModel + Alembic)

## Setup
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install "fastapi[standard]" sqlmodel "psycopg[binary]" alembic

# PostgreSQL (as administrator): CREATE USER app WITH PASSWORD 'secret'; CREATE DATABASE appdb OWNER app;
export DATABASE_URL="postgresql+psycopg://app:secret@localhost:5432/appdb"   # PowerShell: $env:DATABASE_URL = "..."

alembic upgrade head      # create / update the schema
python -m app.seed        # sample data (safe to run twice)
fastapi dev app/main.py   # http://127.0.0.1:8000/docs  and  /redoc
```

## Structure
- `app/database.py` — engine (`echo=True`), `get_session`, `SessionDep`
- `app/models.py` — Team, Hero, Mission, HeroMissionLink + Create / Public / Update schemas
- `app/main.py` — app setup: title, tag sections, routers mounted under `/api/v1`
- `app/routers/heroes.py` — heroes CRUD + filters (incl. `status`), missions many-to-many
- `app/routers/teams.py` — teams (409 on duplicate name), heroes of a team
- `app/seed.py` — 2 teams, 20 heroes and 2 missions using relationships
- `migrations/` — Alembic: `initial schema` → `add hero.power` → `add hero status and created_at` → `add string length limits`
- `frontend/index.html` — Lab 2 page (fetch + CORS)
- `tests/` + `pytest.ini` — Lab 3 tests
- `sql/warmup.sql` — Part 1 SQL
- `answers.md` — answers to Questions 1–20

## Lab 1 — RPC style → REST
| Before (RPC style) | REST (`/api/v1`) |
|---|---|
| GET /getHeroes | GET /heroes |
| GET /heroById?id=3 | GET /heroes/3 |
| POST /addTeam | POST /teams |
| POST /removeHero/3 | DELETE /heroes/3 |
| GET /heroesOfTeam?team=1 | GET /teams/1/heroes |
| POST /changeHeroTeam?hero=3&team=2 | PATCH /heroes/3 with body `{"team_id": 2}` |

Validation: `name` 2–50 chars, `age` 0–200, `power` ≤ 100, `secret_name` 2–50, `status` ∈ {active, retired};
team `name` 2–50 (unique), `headquarters` 2–100. Invalid input → 422.

## Lab 2 — CORS + Fetch
- `app/main.py` adds `CORSMiddleware` for the Live Server origins `http://127.0.0.1:5500` and `http://localhost:5500`.
- `frontend/index.html`: right-click → **Open with Live Server** (API must be running on port 8000).
  - Heroes table from `GET /api/v1/heroes`, built with `textContent` only (no `innerHTML`).
  - Form → `POST /api/v1/heroes`: 201 refreshes the table, 422 shows the error under each field (try age `-5`).
  - Team `<select>` filled from `GET /api/v1/teams`; choosing a team lists `GET /api/v1/teams/{id}/heroes`.
- CORS test: comment out your origin in `origins`, reload the page → the console shows
  *"blocked by CORS policy: No 'Access-Control-Allow-Origin' header"*; restore it and reload.

## Lab 3 — Testing
```bash
pip install pytest
python -m pytest -v        # 16 tests, all green
```
- `pytest.ini` — test settings (`testpaths = tests`)
- `tests/conftest.py` — fresh in-memory SQLite per test (`StaticPool`) + `TestClient` with
  `app.dependency_overrides[get_session]`, so the real `app.db` is never touched (checked: same SHA-256 before/after)
- `tests/test_heroes.py` — list 200, detail 200/404, create 201, invalid 422 (age -5, missing secret_name),
  unknown team_id 400, update, delete
- `tests/test_teams.py` — create 201, duplicate 409, list 200, nested heroes 200/404

An unknown `team_id` now returns **400** (the body is invalid), while a missing resource in the URL stays **404**.

## Endpoints (all under `/api/v1`)
| Method | Path | Status |
|---|---|---|
| POST | /heroes | 201, 400 unknown team, 422 |
| GET | /heroes?offset&limit&min_age&team_id&name&status | 200 (limit ≤ 100) |
| GET / PATCH / DELETE | /heroes/{id} | 200 / 200 / 204, 404 (PATCH: 400 unknown team) |
| POST / GET | /teams | 201 (409 duplicate name) / 200 |
| GET | /teams/{id}/heroes | 200, 404 |
| POST | /missions | 201 |
| POST | /heroes/{hero_id}/missions/{mission_id} | 204 (idempotent), 404 |
| GET | /heroes/{id}/missions | 200, 404 |
