"""
Общие фикстуры для тестов.

Поднимает изолированную in-memory SQLite базу (отдельную от рабочего PostgreSQL),
переопределяет зависимости get_db и require_auth, и предоставляет TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.dependencies import require_auth
from app.main import app
from app.models import OilCompany, Well

# In-memory SQLite. StaticPool + check_same_thread=False держат одно
# соединение, поэтому схема и данные общие для тестовой сессии и приложения.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Чистая БД на каждый тест: создание таблиц, удаление таблиц."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """
    TestClient с подменёнными зависимостями.

    get_db отдаёт тестовую сессию, require_auth всегда пропускает —
    чтобы не логиниться в каждом HTTP-тесте.
    """

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_auth] = lambda: "test@test.com"

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_well(db_session):
    """Создаёт компанию и скважину — нужны для рапортов (внешний ключ well_id)."""
    company = OilCompany(name="Тест Компания", region="Тест Регион")
    db_session.add(company)
    db_session.commit()

    well = Well(
        name="Скважина-Т1",
        type="нефтяная",
        max_drilling_depth=3000,
        oil_company_id=company.id,
    )
    db_session.add(well)
    db_session.commit()
    return well
