# Импортируем типы колонок для описания таблицы
from sqlalchemy import Column, Integer, String

# Импортируем Base — от него наследуются все модели
from app.database import Base


# Модель Employee описывает таблицу "employees" в базе данных
# SQLAlchemy смотрит на этот класс и создаёт таблицу при старте
class Employee(Base):
    # Имя таблицы в базе данных
    __tablename__ = "employees"

    # Уникальный идентификатор каждого сотрудника
    # primary_key=True — главный ключ, автоматически увеличивается (1, 2, 3...)
    # index=True — создаёт индекс для быстрого поиска по id
    id = Column(Integer, primary_key=True, index=True)

    # Имя сотрудника — обязательное поле (nullable=False)
    name = Column(String, nullable=False)

    # Email сотрудника — обязательное и уникальное поле
    # unique=True — два сотрудника не могут иметь одинаковый email
    email = Column(String, unique=True, nullable=False)

    # Должность — необязательное поле (nullable=True)
    # Если не указать — будет None (NULL в базе)
    position = Column(String, nullable=True)

    # Хэш пароля — обязательное поле
    # Храним не сам пароль, а его хэш — так безопаснее
    # Даже если взломают БД — пароли не узнают
    password = Column(String, nullable=False)