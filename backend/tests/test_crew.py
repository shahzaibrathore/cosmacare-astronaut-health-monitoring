"""Tests for crew management API."""

def test_create_crew_success(client):
    response = client.post(
        "/crew/",
        json={"name": "Shahzaib", "role": "Mission Specialist"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Shahzaib"
    assert data["role"] == "Mission Specialist"
    assert "id" in data


def test_create_duplicate_crew_returns_409(client):
    payload = {"name": "Shahzaib", "role": "Mission Specialist"}

    first = client.post("/crew/", json=payload)
    second = client.post("/crew/", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_create_crew_rejects_whitespace_name(client):
    response = client.post(
        "/crew/",
        json={"name": "   ", "role": "Mission Specialist"},
    )

    assert response.status_code == 422


def test_create_crew_trims_name(client):
    response = client.post(
        "/crew/",
        json={"name": "  Shahzaib  ", "role": "Mission Specialist"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Shahzaib"


def test_list_crew(client):
    client.post("/crew/", json={"name": "Astronaut One"})
    client.post("/crew/", json={"name": "Astronaut Two"})

    response = client.get("/crew/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_existing_crew(client):
    created = client.post("/crew/", json={"name": "Astronaut One"})
    crew_id = created.json()["id"]

    response = client.get(f"/crew/{crew_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Astronaut One"


def test_get_missing_crew_returns_404(client):
    response = client.get("/crew/9999")

    assert response.status_code == 404
