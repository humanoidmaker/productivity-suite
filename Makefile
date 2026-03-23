.PHONY: up down backend-test frontend-test lint seed clean

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

backend-test:
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing

backend-lint:
	cd backend && ruff check app/ tests/

frontend-app-test:
	cd frontend-app && npm test

frontend-admin-test:
	cd frontend-admin && npm test

seed:
	cd backend && python -m scripts.seed_admin
	cd backend && python -m scripts.init_minio_buckets
	cd backend && python -m scripts.seed_templates

clean:
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

migrate:
	cd backend && alembic upgrade head

migration:
	cd backend && alembic revision --autogenerate -m "$(msg)"
