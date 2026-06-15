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

css:
	npm run css:build

css-watch:
	npm run css:watch

js:
	cp node_modules/chart.js/dist/chart.umd.js static/js/chart.umd.js