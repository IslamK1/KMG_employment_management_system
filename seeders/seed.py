"""
Сидер учётных записей с ролями.

Создаёт трёх пользователей для проверки ролевой модели:
  admin@mail.ru    / 12345  — Администратор
  manager@mail.ru  / 12345  — Руководитель ДЗО (привязан к первой компании)
  operator@mail.ru / 12345  — Мастер (привязан к первой компании)
"""

import bcrypt

from app.database import Base, SessionLocal, engine
from app.models import Employee, OilCompany

Base.metadata.create_all(bind=engine)

db = SessionLocal()


def _hash(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


# первая компания для привязки manager/operator (если есть)
first_company = db.query(OilCompany).first()
company_id = first_company.id if first_company else None

accounts = [
    ("Admin", "admin@mail.ru", "Administrator", "admin", None),
    ("Manager", "manager@mail.ru", "Руководитель ДЗО", "manager", company_id),
    ("Operator", "operator@mail.ru", "Мастер", "operator", company_id),
]

for name, email, position, role, comp_id in accounts:
    existing = db.query(Employee).filter(Employee.email == email).first()
    if existing:
        # обновим роль на случай если аккаунт создан до ролей
        existing.role = role
        if comp_id and not existing.oil_company_id:
            existing.oil_company_id = comp_id
        print(f"Обновлён: {email} (роль {role})")
    else:
        db.add(
            Employee(
                name=name,
                email=email,
                position=position,
                password=_hash("12345"),
                role=role,
                oil_company_id=comp_id,
            )
        )
        print(f"Создан: {email} / 12345 (роль {role})")

db.commit()
db.close()
