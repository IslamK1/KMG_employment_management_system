data:
	python -m seeders.seed_data

seed:
	python -m seeders.seed

run:
	uvicorn app.main:app --reload

migrate:
	alembic upgrade head
	
format:
	ruff format .
	ruff check . --fix

format-check:
	ruff format . --check
	ruff check .