.PHONY: install dev test lint format docker-up docker-down

install:
	python -m pip install -e ".[dev]"

dev:
	uvicorn zentory.app.main:create_app --factory --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check .

format:
	ruff format .
	ruff check . --fix

docker-up:
	docker compose up --build

docker-down:
	docker compose down
