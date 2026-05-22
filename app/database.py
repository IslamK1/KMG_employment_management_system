# Импортируем инструменты SQLAlchemy для работы с базой данных
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Путь к файлу базы данных SQLite
# sqlite:/// — тип базы, ./test.db — файл в корне проекта
# Когда запустишь проект — появится файл test.db в корне
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Создаём движок — он реально соединяется с БД и выполняет SQL запросы
# check_same_thread: False — нужно для SQLite, потому что FastAPI
# работает в нескольких потоках, а SQLite по умолчанию это не любит
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Фабрика сессий — создаёт новые сессии для каждого запроса
# Сессия — это временное соединение с БД для одной операции
# autocommit=False — изменения не сохраняются сами, нужен явный db.commit()
# autoflush=False  — данные не отправляются в БД до коммита
# bind=engine      — привязываем к нашему движку выше
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей
# Когда пишешь class Employee(Base) — SQLAlchemy понимает что это таблица в БД
Base = declarative_base()


# Генератор сессий — используется в каждом роуте через Depends(get_db)
# FastAPI сам вызывает эту функцию и передаёт сессию в роут
def get_db():
    db = SessionLocal()  # открываем новую сессию
    try:
        yield db  # отдаём сессию в роут, роут делает свою работу
    finally:
        db.close()  # закрываем соединение ВСЕГДА — даже если была ошибка