"""Daily log API tests."""
from fastapi.testclient import TestClient


def test_create_and_read_daily_logs(client: TestClient):
    tg_id = "daily-1"
    payload = {
        "day_score": 8,
        "notes": "Great progress today",
        "xp_pulse_sent": True,
        "xp_pulse_received": False,
        "xp_pulse": True,
        "log_date": "2024-03-01",
    }

    created_user = client.post("/api/v1/users/register", json={"tg_id": tg_id, "username": "hero"})
    assert created_user.status_code == 200, created_user.text

    created_log = client.post("/api/v1/daily-logs/", params={"tg_id": tg_id}, json=payload)
    assert created_log.status_code == 200, created_log.text
    log = created_log.json()
    assert log["day_score"] == payload["day_score"]
    assert log["notes"] == payload["notes"]
    assert log["xp_pulse_sent"] is True
    assert log["xp_pulse_received"] is False
    assert log["xp_pulse"] is True
    assert log["log_date"] == payload["log_date"]
    assert log["streak_length"] == 1

    listed = client.get("/api/v1/daily-logs/", params={"tg_id": tg_id})
    assert listed.status_code == 200
    logs = listed.json()
    assert len(logs) == 1
    assert logs[0]["id"] == log["id"]

    latest = client.get("/api/v1/daily-logs/latest", params={"tg_id": tg_id})
    assert latest.status_code == 200
    assert latest.json()["id"] == log["id"]
