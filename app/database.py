"""
Модуль подключения к базе данных.
Настраивает движок SQLAlchemy, сессии и базовый класс моделей.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Генератор сессий базы данных.

    Создаёт новую сессию для каждого запроса и закрывает её после завершения.
    Используется через FastAPI Depends для внедрения зависимостей.

    Yields:
        Session: Сессия SQLAlchemy для работы с базой данных.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
