.PHONY: install lint format typecheck test coverage clean

install:
	uv sync

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

typecheck:
	mypy src/

test:
	pytest

coverage:
	pytest --cov=src --cov-report=term-missing --cov-report=html

clean:
	rm -rf .mypy_cache .ruff_cache htmlcov cache/
	rm -rf .venv/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.db" -delete
