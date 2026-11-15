"""Telemetry ingestion + Pydantic boundary tests."""
import pytest

VALID = {
    "crew_id": 1,
    "heart_rate": 75,
    "spo2": 98.0,
    "body_temp": 37.0,
    "systolic_bp": 120,
    "diastolic_bp": 80,
}


def _p(**overrides):
    data = dict(VALID)
    data.update(overrides)
    return data


# ---------- Happy path ----------

@pytest.mark.parametrize("hr", [30, 45, 60, 75, 100, 150, 200, 220])
def test_hr_in_range_accepts(client, hr):
    assert client.post("/telemetry/", json=_p(heart_rate=hr)).status_code == 201


@pytest.mark.parametrize("spo2", [50.0, 75.0, 89.9, 90.0, 95.0, 98.5, 100.0])
def test_spo2_in_range_accepts(client, spo2):
    assert client.post("/telemetry/", json=_p(spo2=spo2)).status_code == 201


@pytest.mark.parametrize("temp", [30.0, 35.0, 36.5, 37.5, 39.0, 43.0])
def test_temp_in_range_accepts(client, temp):
    assert client.post("/telemetry/", json=_p(body_temp=temp)).status_code == 201


@pytest.mark.parametrize("sys_", [60, 90, 120, 160, 250])
def test_systolic_in_range_accepts(client, sys_):
    assert client.post("/telemetry/", json=_p(systolic_bp=sys_)).status_code == 201


@pytest.mark.parametrize("dia", [40, 60, 80, 100, 150])
def test_diastolic_in_range_accepts(client, dia):
    assert client.post("/telemetry/", json=_p(diastolic_bp=dia)).status_code == 201


# ---------- Boundary rejections (422) ----------

@pytest.mark.parametrize("hr", [29, 0, -1, 221, 300, 1000])
def test_hr_out_of_range_rejects(client, hr):
    assert client.post("/telemetry/", json=_p(heart_rate=hr)).status_code == 422


@pytest.mark.parametrize("spo2", [49.9, 49.0, 0.0, -5.0, 100.1, 150.0])
def test_spo2_out_of_range_rejects(client, spo2):
    assert client.post("/telemetry/", json=_p(spo2=spo2)).status_code == 422


@pytest.mark.parametrize("temp", [29.9, 20.0, 0.0, -10.0, 43.1, 50.0])
def test_temp_out_of_range_rejects(client, temp):
    assert client.post("/telemetry/", json=_p(body_temp=temp)).status_code == 422


@pytest.mark.parametrize("sys_", [59, 0, -1, 251, 500])
def test_systolic_out_of_range_rejects(client, sys_):
    assert client.post("/telemetry/", json=_p(systolic_bp=sys_)).status_code == 422


@pytest.mark.parametrize("dia", [39, 0, -1, 151, 500])
def test_diastolic_out_of_range_rejects(client, dia):
    assert client.post("/telemetry/", json=_p(diastolic_bp=dia)).status_code == 422


# ---------- Null / missing / wrong-type ----------

@pytest.mark.parametrize(
    "field",
    ["heart_rate", "spo2", "body_temp", "systolic_bp", "diastolic_bp", "crew_id"],
)
def test_null_fields_rejected(client, field):
    assert client.post("/telemetry/", json=_p(**{field: None})).status_code == 422


@pytest.mark.parametrize(
    "field",
    ["heart_rate", "spo2", "body_temp", "systolic_bp", "diastolic_bp", "crew_id"],
)
def test_missing_fields_rejected(client, field):
    data = dict(VALID)
    data.pop(field)
    assert client.post("/telemetry/", json=data).status_code == 422


@pytest.mark.parametrize(
    "field,bad",
    [
        ("heart_rate", "not-a-number"),
        ("spo2", "abc"),
        ("body_temp", []),
        ("systolic_bp", {}),
        ("diastolic_bp", "x"),
    ],
)
def test_invalid_types_rejected(client, field, bad):
    assert client.post("/telemetry/", json=_p(**{field: bad})).status_code == 422


# ---------- Float precision ----------

@pytest.mark.parametrize("spo2", [98.15, 98.25, 97.99])
def test_spo2_float_precision_accepted(client, spo2):
    assert client.post("/telemetry/", json=_p(spo2=spo2)).status_code == 201


@pytest.mark.parametrize("temp", [36.55, 36.99, 37.01, 37.49])
def test_temp_float_precision_accepted(client, temp):
    assert client.post("/telemetry/", json=_p(body_temp=temp)).status_code == 201


# ---------- Response shape ----------

def test_response_shape(client):
    body = client.post("/telemetry/", json=_p()).json()

    for key in (
        "id", "crew_id", "heart_rate", "spo2", "body_temp",
        "systolic_bp", "diastolic_bp", "timestamp",
    ):
        assert key in body


def test_response_echo_values(client):
    body = client.post(
        "/telemetry/", json=_p(heart_rate=88, spo2=97.5)
    ).json()

    assert body["heart_rate"] == 88
    assert body["spo2"] == 97.5


# ---------- Historical query ----------

def test_get_telemetry_empty(client):
    r = client.get("/telemetry/999")
    assert r.status_code == 200
    assert r.json() == []


def test_get_telemetry_returns_records(client):
    for _ in range(3):
        client.post("/telemetry/", json=_p())

    assert len(client.get("/telemetry/1").json()) == 3


@pytest.mark.parametrize("limit", [1, 2, 5, 10, 50])
def test_get_telemetry_limit(client, limit):
    for _ in range(10):
        client.post("/telemetry/", json=_p())

    r = client.get(f"/telemetry/1?limit={limit}")
    assert len(r.json()) == min(limit, 10)


@pytest.mark.parametrize("limit", [0, -1, 501, 10000])
def test_get_telemetry_invalid_limit(client, limit):
    r = client.get(f"/telemetry/1?limit={limit}")
    assert r.status_code == 422


def test_ordering_descending(client):
    for hr in (60, 70, 80):
        client.post("/telemetry/", json=_p(heart_rate=hr))

    r = client.get("/telemetry/1")
    hrs = [row["heart_rate"] for row in r.json()]

    assert hrs[0] == 80


# ---------- Auto-seed ----------

def test_auto_seed_crew(client):
    r = client.post("/telemetry/", json=_p(crew_id=42))
    assert r.status_code == 201

    r2 = client.get("/crew/42")
    assert r2.status_code == 200
    assert r2.json()["id"] == 42

# ---------- Atomic transaction rollback ----------

def test_telemetry_transaction_rolls_back_on_alert_failure(client, monkeypatch):
    from app.routers import telemetry as telemetry_router

    def simulate_alert_failure(data, db):
        raise RuntimeError("Simulated alert generation failure")

    monkeypatch.setattr(
        telemetry_router,
        "evaluate_telemetry",
        simulate_alert_failure,
    )

    with pytest.raises(RuntimeError, match="Simulated alert generation failure"):
        client.post(
            "/telemetry/",
            json=_p(crew_id=999),
        )

    # Auto-created crew must also be rolled back.
    assert client.get("/crew/999").status_code == 404

    # No telemetry should remain.
    assert client.get("/telemetry/999").json() == []

    # No alerts should remain.
    alerts = client.get("/alerts/", params={"crew_id": 999})
    assert alerts.status_code == 200
    assert alerts.json() == []
def test_get_telemetry_rejects_invalid_crew_id(client):
    response = client.get("/telemetry/0")
    assert response.status_code == 422


def test_get_telemetry_maximum_limit(client):
    response = client.get("/telemetry/1?limit=500")
    assert response.status_code == 200


def test_get_telemetry_rejects_limit_above_500(client):
    response = client.get("/telemetry/1?limit=501")
    assert response.status_code == 422