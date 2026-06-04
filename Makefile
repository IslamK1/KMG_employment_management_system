data:
	python seed_data.py

seed:
	python seed.py

run:
	uvicorn app.main:app --reload

migrate:
	alembic upgrade head