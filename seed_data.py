import random
from datetime import date, timedelta
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.database import SessionLocal
from app.models import OilCompany, Well, Employee, DailyProduction

import bcrypt
from faker import Faker 
from faker.providers import BaseProvider


#Класс провайдера для генерации фейковых скважин 
class OilProvider(BaseProvider):
    
    well_types = ["нефтяная", "газовая", "разведочная", "нагнетальная"]

    def well_type(self) -> str:
        return self.random_element(self.well_types)
    

fake = Faker("ru_RU") #Инициализация Faker с русской локализацией
fake.add_provider(OilProvider) #Добавление кастомного провайдера для генерации типов скважин

db = SessionLocal() #Создание сессии для работы с базой данных

#Очищение таблиц перед заполнением
db.query(DailyProduction).delete()
db.query(Well).delete()
db.query(Employee).delete()
db.query(OilCompany).delete()
db.commit()


#Создание 22 компаний с уникальными названиями и регионами
companies = []
for _ in range(22):
    company = OilCompany(
        name=f"{fake.company()} Мунай",
        region = fake.region()
    )
    db.add(company)
    companies.append(company)


db.commit()
print(f"Создано компаний: {len(companies)}")


#Для каждой компании создается от 2 до 5 сотрудников 
#с одинаковым паролем "12345" (хэшируется с помощью bcrypt)
hashed_password = bcrypt.hashpw("12345".encode(), bcrypt.gensalt()).decode()

employee_count = 0
for company in companies:
    num_employees = random.randint(2, 5)
    for _ in range(num_employees):
        employee = Employee(
            name = fake.name(),
            email = fake.unique.email(),
            position = fake.job(),
            password = hashed_password,
            oil_company_id = company.id
        )
        db.add(employee)
        employee_count += 1

db.commit()
print(f"Создано сотрудников: {employee_count}")


#Для каждой компании создается от 2 до 10 скважин
wells = []
for company in companies:
    num_wells = random.randint(2, 10)
    for _ in range(num_wells):
        well = Well(
            name = f"Скважина-{fake.bothify('##??').upper()}",
            type = fake.well_type(),
            max_drilling_depth = random.randint(1000, 6000),
            oil_company_id = company.id
        )
        db.add(well)
        wells.append(well)

db.commit()
print(f"Создано скважин: {len(wells)}")


#Берутся первые 3-5 компаний, для них первые 5 скважин 
num_companies_for_production = random.randint(3, 5)
target_companies = companies[:num_companies_for_production]


#Для каждой из этих компаний берутся первые 5 скважин по ID
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


#Генерация суточных показателей за 365 дней — Bulk Insert 
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


#Bulk insert — все записи вставляются одним запросом
bulk_insert = pg_insert(DailyProduction).values(bulk_records).on_conflict_do_nothing()
db.execute(bulk_insert)
db.commit()


print(f"Создано суточных показателей: {len(bulk_records)}")
print(f"\n База данных успешно заполнена!")
db.close()