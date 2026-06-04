import bcrypt

from app.database import Base, SessionLocal, engine
from app.models import Employee

Base.metadata.create_all(bind=engine)

db = SessionLocal()

existing = db.query(Employee).filter(Employee.email == "admin@mail.ru").first()

if not existing:
    hashed = bcrypt.hashpw("12345".encode(), bcrypt.gensalt()).decode()
    user = Employee(
        name="Admin", email="admin@mail.ru", position="Administrator", password=hashed
    )
    db.add(user)
    db.commit()
    print("Пользователь создан: admin@mail.ru / 12345")
else:
    print("Пользователь уже существует")

db.close()
