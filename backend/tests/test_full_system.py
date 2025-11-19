"""End-to-end tests that exercise the most important API flows.

Запуск: `pytest backend/tests/test_full_system.py -q`
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Готовим PYTHONPATH, чтобы можно было импортировать backend.*
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.deps import get_db  # noqa: E402
from backend.app.db.base import Base  # noqa: E402
from backend.app.main import app  # noqa: E402

# Собственный in-memory движок, который не затрагивает реальную БД проекта.
test_engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def _reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_full_user_and_domain_flow(client: TestClient):
    tg_id = "tg-777"
    username = "tester"

    # 1. Регистрируем пользователя и убеждаемся, что повторный запрос возвращает ту же запись.
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

    # 2. Создаём домен и убеждаемся, что он попадает в общий список.
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

    # 3. Начисляем опыт и проверяем, что обновился уровень домена и глобальные показатели пользователя.
    xp_gain = 200
    updated = client.post(
        "/api/v1/domains/add-xp",
        params={"tg_id": tg_id, "domain_id": domain["id"], "xp": xp_gain},
    )
    assert updated.status_code == 200, updated.text
    upgraded = updated.json()
    assert upgraded["current_level"] == 2
    assert upgraded["current_xp"] == 100  # 200 XP => один уровень и остаток 100 XP
    assert upgraded["xp_to_next_level"] == 141  # calc_xp_to_next(2)

    refreshed_user = client.get(f"/api/v1/users/by-tg/{tg_id}")
    assert refreshed_user.status_code == 200
    user_after_xp = refreshed_user.json()
    assert user_after_xp["current_global_level"] == 2
    assert user_after_xp["global_xp"] == 200

    # 4. Проверяем, что список доменов отражает обновлённые значения.
    domains_after_xp = client.get("/api/v1/domains/", params={"tg_id": tg_id})
    assert domains_after_xp.status_code == 200
    domain_state = domains_after_xp.json()[0]
    assert domain_state["current_level"] == 2
    assert domain_state["current_xp"] == 100

    # 5. Создаём дневник дня, который добавляет XP и фиксирует реальный доход.
    log_payload = {
        "summary": "Тренировка и пара часов кода",
        "accomplishments": "Доделал модуль XP",
        "blockers": "Не хватило сна",
        "rating": 7,
        "xp_updates": [{"domain_id": domain["id"], "xp": 80}],
        "finances": [
            {
                "amount": 2500,
                "source": "Freelance",
                "description": "Мини-заказ",
            }
        ],
    }
    created_log = client.post("/api/v1/daily-logs/", params={"tg_id": tg_id}, json=log_payload)
    assert created_log.status_code == 200, created_log.text
    log_data = created_log.json()
    assert log_data["total_xp_awarded"] == 80
    assert log_data["xp_pulse"] is True
    assert len(log_data["xp_breakdown"]) == 1
    assert len(log_data["finances"]) == 1
    finance_from_log = log_data["finances"][0]
    assert finance_from_log["amount"] == 2500

    # 6. Убеждаемся, что XP из дневника применился к домену.
    domain_after_log = client.get("/api/v1/domains/", params={"tg_id": tg_id}).json()[0]
    assert domain_after_log["current_level"] == 3
    assert domain_after_log["current_xp"] == 39  # 141 XP ушло на апгрейд до 3 уровня

    # 7. Добавляем дополнительный доход уже после закрытия дневника.
    standalone_income = client.post(
        "/api/v1/finances/",
        params={"tg_id": tg_id},
        json={
            "amount": 5000,
            "source": "Salary",
            "description": "Аванс",
            "daily_log_id": log_data["id"],
        },
    )
    assert standalone_income.status_code == 200, standalone_income.text

    incomes = client.get("/api/v1/finances/", params={"tg_id": tg_id})
    assert incomes.status_code == 200
    assert len(incomes.json()) == 2

    # 8. Создаём серию дневников в пределах одной недели и запрашиваем сводку.
    base_week_start = date(2023, 5, 1)  # Понедельник
    xp_values = [10, 20, 0]
    ratings = [6, 8, 5]
    incomes_amounts = [100, 0, 250]

    for idx, xp in enumerate(xp_values):
        payload = {
            "log_date": str(base_week_start + timedelta(days=idx)),
            "summary": f"Log #{idx}",
            "accomplishments": "",
            "blockers": "",
            "rating": ratings[idx],
            "xp_updates": [{"domain_id": domain["id"], "xp": xp}] if xp else [],
            "finances": [],
        }
        if incomes_amounts[idx]:
            payload["finances"].append(
                {
                    "amount": incomes_amounts[idx],
                    "source": f"Bonus {idx}",
                    "description": "auto",
                }
            )

        created_log = client.post(
            "/api/v1/daily-logs/",
            params={"tg_id": tg_id},
            json=payload,
        )
        assert created_log.status_code == 200, created_log.text

    weekly = client.get("/api/v1/weekly-logs", params={"tg_id": tg_id})
    assert weekly.status_code == 200
    weekly_list = weekly.json()
    target_week = None
    expected_week_start = str(base_week_start)
    for entry in weekly_list:
        if entry["period_start"] == expected_week_start:
            target_week = entry
            break
    assert target_week, weekly_list
    assert target_week["log_count"] == len(xp_values)
    assert target_week["total_xp"] == sum(xp_values)
    assert target_week["average_rating"] == pytest.approx(sum(ratings) / len(ratings), rel=1e-3)
    assert target_week["xp_pulse_count"] == 2  # только два лога добавили XP
    assert target_week["total_income"] == sum(incomes_amounts)
