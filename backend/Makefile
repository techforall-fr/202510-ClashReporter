.PHONY: install dev test lint format clean run

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov mypy black ruff

test:
	pytest tests/ -v --cov=app --cov-report=html

lint:
	ruff check app/
	mypy app/ --ignore-missing-imports

format:
	black app/ tests/
	ruff check --fix app/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov/

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-mock:
	USE_MOCK=true uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
