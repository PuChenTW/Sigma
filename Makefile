API_HOST ?= 127.0.0.1
API_PORT ?= 8000

.PHONY: help sync sync-asr api test test-api test-source-tools lint format check smoke-api

help:
	@echo "Development commands:"
	@echo "  make sync              Install development dependencies"
	@echo "  make sync-asr          Install development dependencies with ASR extras"
	@echo "  make api               Run the FastAPI development server"
	@echo "  make test              Run all Python tests"
	@echo "  make test-api          Run API/schema/domain tests"
	@echo "  make test-source-tools Run source_tools tests"
	@echo "  make lint              Run Ruff checks"
	@echo "  make format            Format Python code with Ruff"
	@echo "  make check             Run tests and lint"
	@echo "  make smoke-api         Run a one-shot API health smoke test"

sync:
	uv sync --group dev

sync-asr:
	uv sync --group dev --extra asr

api:
	uv run uvicorn studio_api.main:app --reload --app-dir src --host $(API_HOST) --port $(API_PORT)

test:
	uv run pytest packages/source-tools/tests apps/api/tests packages/schemas/tests packages/domain/tests -q

test-api:
	uv run pytest apps/api/tests packages/schemas/tests packages/domain/tests -q

test-source-tools:
	uv run pytest packages/source-tools/tests -q

lint:
	uv run ruff check .

format:
	uv run ruff format .

check: test lint

smoke-api:
	uv run pytest apps/api/tests/test_api_scaffold.py -q
