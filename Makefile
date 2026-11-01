.PHONY: install run lint test

install:
	uv sync

run:
	uv run database

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run python tests/test_database.py
