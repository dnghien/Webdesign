from fastapi.testclient import TestClient

from app.models import Hero, Team

V = "/api/v1"


def test_create_team(client: TestClient):
    response = client.post(f"{V}/teams", json={"name": "X-Men", "headquarters": "Westchester"})
    assert response.status_code == 201
    assert response.json()["name"] == "X-Men"


def test_create_team_duplicate(client: TestClient, team: Team):
    response = client.post(f"{V}/teams", json={"name": team.name, "headquarters": "Somewhere"})
    assert response.status_code == 409
    assert response.json() == {"detail": "Team name already exists"}


def test_list_teams(client: TestClient, team: Team):
    response = client.get(f"{V}/teams")
    assert response.status_code == 200
    assert [t["name"] for t in response.json()] == ["Avengers"]


def test_team_heroes(client: TestClient, team: Team, hero: Hero):
    response = client.get(f"{V}/teams/{team.id}/heroes")
    assert response.status_code == 200
    assert [h["name"] for h in response.json()] == ["Tony"]


def test_team_heroes_not_found(client: TestClient):
    response = client.get(f"{V}/teams/999/heroes")
    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}
