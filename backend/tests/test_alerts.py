"""Tests for alert listing and acknowledgement API."""

def create_test_alert(client):
    crew_response = client.post(
        "/crew/",
        json={"name": "Test Astronaut"},
    )
    assert crew_response.status_code == 201

    telemetry_response = client.post(
        "/telemetry/",
        json={
            "crew_id": crew_response.json()["id"],
            "heart_rate": 180,
            "spo2": 98,
            "body_temp": 37,
            "systolic_bp": 120,
            "diastolic_bp": 80,
        },
    )
    assert telemetry_response.status_code == 201

    alerts_response = client.get("/alerts/")
    assert alerts_response.status_code == 200
    assert len(alerts_response.json()) > 0

    return alerts_response.json()[0]["id"]


def test_list_alerts(client):
    create_test_alert(client)

    response = client.get("/alerts/")

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_filter_alerts_by_crew_id(client):
    alert_id = create_test_alert(client)

    response = client.get("/alerts/", params={"crew_id": 1})

    assert response.status_code == 200
    assert any(alert["id"] == alert_id for alert in response.json())


def test_filter_unacknowledged_alerts(client):
    create_test_alert(client)

    response = client.get("/alerts/", params={"acknowledged": False})

    assert response.status_code == 200
    assert all(alert["acknowledged"] is False for alert in response.json())


def test_acknowledge_alert(client):
    alert_id = create_test_alert(client)

    response = client.post(f"/alerts/{alert_id}/acknowledge")

    assert response.status_code == 200
    assert response.json()["acknowledged"] is True


def test_acknowledge_missing_alert_returns_404(client):
    response = client.post("/alerts/9999/acknowledge")

    assert response.status_code == 404


def test_alert_limit_validation(client):
    response = client.get("/alerts/", params={"limit": 0})

    assert response.status_code == 422
