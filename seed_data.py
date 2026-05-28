import random
from datetime import date, timedelta
from app.database import SessionLocal
from app.models import OilCompany, Well, Employee, DailyProduction
from faker import Faker 
import bcrypt

fake = Faker("ru_RU")
db = SessionLocal()

#Очищаем таблицы перед заполнением
db.query(DailyProduction).delete()
db.query(Well).delete()
db.query(Employee).delete()
db.query(OilCompany).delete()
db.commit()

#Создаём 22 компании
regions = [
    "Астана", "Алматы", "Актау", "Актобе", "Павлодар", "Атырау",
    "Кызылорда", "Костанай", "Шымкент", "Мангыстау", 
]



companies = []
for _ in range(22):
    company = OilCompany(
        name=f"{fake.company()} Мунай",
        region = random.choice(regions)
    )
    db.add(company)
    companies.append(company)

db.commit()
print(f"Создано компаний: {len(companies)}")


#Для каждой компании создаём от 2 до 5 сотрудников
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
            oil_company_id=company.id
        )
        db.add(employee)
        employee_count += 1

db.commit()
print(f"Создано сотрудников: {employee_count}")

#Для каждой компании создаём от 2 до 10 скважин 
well_types = ["нефтяная", "газовая", "разведочная", "нагнетательная"]

wells = []
for company in companies:
    num_wells = random.randint(2, 10)
    for _ in range(num_wells):
        well = Well(
            name=f"Скважина-{fake.bothify('##??').upper()}",
            type=random.choice(well_types),
            max_drilling_depth = random.randint(1000, 6000),
            oil_company_id = company.id
        )
        db.add(well)
        wells.append(well)

db.commit()
print(f"Создано скважин: {len(wells)}")

#Берём первые 3-5 компаний, для них первые 5 скважин 
num_companies_for_production = random.randint(3, 5)
target_companies = companies[:num_companies_for_production]

#Для каждой из этих компаний берём первые 5 скважин по ID
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

#Генерируем суточные показатели за 365 дней — Bulk Insert 
today = date.today()
bulk_records = []

for well in target_wells:
    for day_offset in range(365):
        production_date = today - timedelta(days=day_offset)
        bulk_records.append({
            "well_id": well.id,
            "date": production_date,
            "oil_volume": round(random.uniform(50.0, 500.0), 2)
        })

#Bulk insert — вставляем все записи одним запросом
db.bulk_insert_mappings(DailyProduction, bulk_records)
db.commit()

print(f"Создано суточных показателей: {len(bulk_records)}")
print(f"\n База данных успешно заполнена!")
db.close()