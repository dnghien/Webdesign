from fastapi.testclient import TestClient

from app.models import Hero, Team

V = "/api/v1"


def test_list_heroes(client: TestClient, hero: Hero):
    response = client.get(f"{V}/heroes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Tony"
    assert "secret_name" not in data[0]  # never leaves the server


def test_list_heroes_empty(client: TestClient):
    response = client.get(f"{V}/heroes")
    assert response.status_code == 200
    assert response.json() == []


def test_read_hero(client: TestClient, hero: Hero):
    response = client.get(f"{V}/heroes/{hero.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == hero.id
    assert data["status"] == "active"
    assert data["created_at"] is not None


def test_read_hero_not_found(client: TestClient):
    response = client.get(f"{V}/heroes/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Hero not found"}


def test_create_hero(client: TestClient, team: Team):
    payload = {"name": "Natasha", "secret_name": "Black Widow", "age": 35, "team_id": team.id}
    response = client.post(f"{V}/heroes", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "Natasha"
    assert data["team_id"] == team.id
    assert data["status"] == "active"  # default
    # the new hero is really stored
    assert client.get(f"{V}/heroes/{data['id']}").status_code == 200


def test_create_hero_invalid_age(client: TestClient):
    response = client.post(f"{V}/heroes", json={"name": "Bad", "secret_name": "Bad", "age": -5})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "age"]


def test_create_hero_missing_secret_name(client: TestClient):
    response = client.post(f"{V}/heroes", json={"name": "Nobody"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "secret_name"]


def test_create_hero_unknown_team(client: TestClient):
    payload = {"name": "Lost", "secret_name": "Lost One", "team_id": 999}
    response = client.post(f"{V}/heroes", json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "Team not found"}


def test_update_hero_unknown_team(client: TestClient, hero: Hero):
    response = client.patch(f"{V}/heroes/{hero.id}", json={"team_id": 999})
    assert response.status_code == 400


def test_update_hero(client: TestClient, hero: Hero):
    response = client.patch(f"{V}/heroes/{hero.id}", json={"status": "retired"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "retired"
    assert data["name"] == "Tony"  # untouched fields stay the same


def test_delete_hero(client: TestClient, hero: Hero):
    assert client.delete(f"{V}/heroes/{hero.id}").status_code == 204
    assert client.get(f"{V}/heroes/{hero.id}").status_code == 404
