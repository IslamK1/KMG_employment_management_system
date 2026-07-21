"""
Тесты мобильного API (/api/v1): токен-аутентификация и приём рапортов.
"""

import bcrypt
import pytest

from app.models import Employee, OilCompany, Well


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


@pytest.fixture
def operator(db_session, sample_well):
    """Оператор, привязанный к компании тестовой скважины."""
    emp = Employee(
        name="Оператор",
        email="op@test.com",
        position="Оператор",
        password=_hash("12345"),
        role="operator",
        oil_company_id=sample_well.oil_company_id,
    )
    db_session.add(emp)
    db_session.commit()
    return emp


@pytest.fixture
def foreign_well(db_session):
    """Скважина другой компании — оператор не должен иметь к ней доступ."""
    other = OilCompany(name="Чужая Компания", region="Другой Регион")
    db_session.add(other)
    db_session.commit()
    well = Well(
        name="Чужая-Скважина",
        type="нефтяная",
        max_drilling_depth=2500,
        oil_company_id=other.id,
    )
    db_session.add(well)
    db_session.commit()
    return well


def _login(client, email="op@test.com", password="12345"):
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    return resp


def _auth_header(client, **kwargs):
    token = _login(client, **kwargs).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------- Аутентификация ----------


def test_login_returns_token(client, operator):
    resp = _login(client)
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password(client, operator):
    resp = _login(client, password="wrong")
    assert resp.status_code == 401


def test_me_returns_profile(client, operator):
    resp = client.get("/api/v1/auth/me", headers=_auth_header(client))
    assert resp.status_code == 200
    assert resp.json()["email"] == "op@test.com"
    assert resp.json()["role"] == "operator"


# ---------- Создание рапорта ----------


def _payload(well_id):
    return {
        "well_id": well_id,
        "date": "2026-01-15",
        "working_hours": 12,
        "liquid_volume": 100,
        "water_cut": 20,
        "density": 0.86,
    }


def test_create_report_success(client, operator, sample_well):
    resp = client.post(
        "/api/v1/reports",
        json=_payload(sample_well.id),
        headers=_auth_header(client),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    # нефть = 100 * (1 - 20/100) * 0.86 = 68.8
    assert body["oil_volume"] == 68.8
    assert body["well_id"] == sample_well.id


def test_create_report_requires_token(client, operator, sample_well):
    resp = client.post("/api/v1/reports", json=_payload(sample_well.id))
    assert resp.status_code == 401


def test_create_report_duplicate(client, operator, sample_well):
    header = _auth_header(client)
    first = client.post(
        "/api/v1/reports", json=_payload(sample_well.id), headers=header
    )
    assert first.status_code == 201
    second = client.post(
        "/api/v1/reports", json=_payload(sample_well.id), headers=header
    )
    assert second.status_code == 409


def test_create_report_validation_error(client, operator, sample_well):
    bad = _payload(sample_well.id)
    bad["working_hours"] = 25  # > 24 — недопустимо
    resp = client.post("/api/v1/reports", json=bad, headers=_auth_header(client))
    assert resp.status_code == 422


def test_create_report_foreign_well_forbidden(client, operator, foreign_well):
    resp = client.post(
        "/api/v1/reports",
        json=_payload(foreign_well.id),
        headers=_auth_header(client),
    )
    assert resp.status_code == 403
