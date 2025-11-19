"""End-to-end tests that exercise the most important API flows.

Запуск: `pytest backend/tests/test_full_system.py -q`
"""
from __future__ import annotations

import sys
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
