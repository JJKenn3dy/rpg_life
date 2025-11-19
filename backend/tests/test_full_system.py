"""End-to-end tests that exercise the most important API flows.

Запуск: `pytest backend/tests/test_full_system.py -q`
"""
from fastapi.testclient import TestClient


def _expected_self_rating(payload: dict) -> int:
    normalized_score = max(0, min(payload["day_score"], 100))
    base = (normalized_score + 5) // 10
    bonus = int(payload.get("xp_pulse_sent", False)) + int(
        payload.get("xp_pulse_received", False)
    )
    if payload.get("xp_pulse"):
        bonus += 1
    return max(1, min(10, base + bonus))


def test_full_user_and_domain_flow(client: TestClient):
    tg_id = "tg-777"
    username = "tester"

    created = client.post("/api/v1/users/register", json={"tg_id": tg_id, "username": username})
    assert created.status_code == 200, created.text
    user = created.json()
    assert user["tg_id"] == tg_id
    assert user["username"] == username
    assert user["current_global_level"] == 1
    assert user["global_xp"] == 0

    duplicate = client.post("/api/v1/users/register", json={"tg_id": tg_id, "username": username})
    assert duplicate.status_code == 200
    assert duplicate.json()["id"] == user["id"]

    fetched = client.get(f"/api/v1/users/by-tg/{tg_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == user["id"]

    domain_name = "Python"
    created_domain = client.post(
        "/api/v1/domains/",
        params={"tg_id": tg_id},
        json={"name": domain_name},
    )
    assert created_domain.status_code == 200, created_domain.text
    domain = created_domain.json()
    assert domain["name"] == domain_name
    assert domain["current_level"] == 1
    assert domain["current_xp"] == 0
    assert domain["xp_to_next_level"] == 100

    listed = client.get("/api/v1/domains/", params={"tg_id": tg_id})
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    xp_gain = 200
    updated = client.post(
        "/api/v1/domains/add-xp",
        params={"tg_id": tg_id, "domain_id": domain["id"], "xp": xp_gain},
    )
    assert updated.status_code == 200, updated.text
    upgraded = updated.json()
    assert upgraded["current_level"] == 2
    assert upgraded["current_xp"] == 100
    assert upgraded["xp_to_next_level"] == 141

    refreshed_user = client.get(f"/api/v1/users/by-tg/{tg_id}")
    assert refreshed_user.status_code == 200
    user_after_xp = refreshed_user.json()
    assert user_after_xp["current_global_level"] == 2
    assert user_after_xp["global_xp"] == 200

    domains_after_xp = client.get("/api/v1/domains/", params={"tg_id": tg_id})
    assert domains_after_xp.status_code == 200
    domain_state = domains_after_xp.json()[0]
    assert domain_state["current_level"] == 2
    assert domain_state["current_xp"] == 100

    log_payload = {
        "day_score": 73,
        "notes": "Выполнил все тренировки",
        "summary": "Успешный день",
        "xp_pulse_sent": True,
        "xp_pulse_received": False,
        "xp_pulse": True,
    }
    expected_rating = _expected_self_rating(log_payload)

    created_log = client.post(
        "/api/v1/daily-logs/",
        params={"tg_id": tg_id},
        json=log_payload,
    )
    assert created_log.status_code == 200, created_log.text
    log = created_log.json()
    assert log["self_rating"] == expected_rating

    latest_log = client.get("/api/v1/daily-logs/latest", params={"tg_id": tg_id})
    assert latest_log.status_code == 200
    latest_data = latest_log.json()
    assert latest_data["self_rating"] == expected_rating
    assert latest_data["summary"] == log_payload["summary"]
