import random
from datetime import date, timedelta

import bcrypt
from faker import Faker
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import SessionLocal
from app.models import DailyProduction, Employee, OilCompany, Well
from providers.oil_provider import OilProvider

fake = Faker("ru_RU")
fake.add_provider(OilProvider)

db = SessionLocal()

db.query(DailyProduction).delete()
db.query(Well).delete()
db.query(Employee).delete()
db.query(OilCompany).delete()
db.commit()


companies = []
for _ in range(22):
    company = OilCompany(name=f"{fake.company()} Мунай", region=fake.region())
    db.add(company)
    companies.append(company)


db.commit()
print(f"Создано компаний: {len(companies)}")


hashed_password = bcrypt.hashpw("12345".encode(), bcrypt.gensalt()).decode()

employee_count = 0
for company in companies:
    num_employees = random.randint(2, 5)
    for _ in range(num_employees):
        employee = Employee(
            name=fake.name(),
            email=fake.unique.email(),
            position=fake.job(),
            password=hashed_password,
            oil_company_id=company.id,
        )
        db.add(employee)
        employee_count += 1

db.commit()
print(f"Создано сотрудников: {employee_count}")


wells = []
for company in companies:
    num_wells = random.randint(2, 10)
    for _ in range(num_wells):
        well = Well(
            name=f"Скважина-{fake.bothify('##??').upper()}",
            type=fake.well_type(),
            max_drilling_depth=random.randint(1000, 6000),
            oil_company_id=company.id,
        )
        db.add(well)
        wells.append(well)

db.commit()
print(f"Создано скважин: {len(wells)}")


num_companies_for_production = random.randint(3, 5)
target_companies = companies[:num_companies_for_production]


target_wells = []
for company in target_companies:
    company_wells = (
        db.query(Well)
        .filter(Well.oil_company_id == company.id)
        .order_by(Well.id)
        .limit(5)
        .all()
    )
    target_wells.extend(company_wells)

print(f"Скважин для генерации показателей: {len(target_wells)}")


today = date.today()

bulk_records = []
for well in target_wells:
    for day_offset in range(365):
        production_date = today - timedelta(days=day_offset)
        bulk_records.append({
            "well_id": well.id,
            "date": production_date,
            "working_hours": round(random.uniform(1.0, 24.0), 1),
            "liquid_volume": round(random.uniform(50.0, 500.0), 2),
            "water_cut": round(random.uniform(0.0, 80.0), 1),
            "density": round(random.uniform(0.82, 0.92), 3),
        })


bulk_insert = pg_insert(DailyProduction).values(bulk_records).on_conflict_do_nothing()
db.execute(bulk_insert)
db.commit()


print(f"Создано суточных показателей: {len(bulk_records)}")
print("\n База данных успешно заполнена!")
db.close()
