API_HOST ?= 127.0.0.1
API_PORT ?= 8000

.PHONY: help sync sync-asr api web web-sync web-typecheck web-build test test-api test-source-tools test-e2e lint format check smoke-api

help:
	@echo "Development commands:"
	@echo "  make sync              Install development dependencies"
	@echo "  make sync-asr          Install development dependencies with ASR extras"
	@echo "  make web-sync          Install frontend dependencies"
	@echo "  make api               Run the FastAPI development server"
	@echo "  make web               Run the Next.js development server"
	@echo "  make test              Run all Python tests"
	@echo "  make test-api          Run API/schema/domain tests"
	@echo "  make test-source-tools Run source_tools tests"
	@echo "  make test-e2e          Run Playwright workflow test"
	@echo "  make lint              Run Ruff checks"
	@echo "  make web-typecheck     Run frontend TypeScript checks"
	@echo "  make web-build         Build the frontend"
	@echo "  make format            Format Python code with Ruff"
	@echo "  make check             Run Python tests, Ruff, and frontend typecheck"
	@echo "  make smoke-api         Run a one-shot API health smoke test"

sync:
	uv sync --group dev

sync-asr:
	uv sync --group dev --extra asr

api:
	uv run uvicorn studio_api.main:app --reload --app-dir src --host $(API_HOST) --port $(API_PORT)

web-sync:
	cd frontend && npm install

web:
	cd frontend && NEXT_PUBLIC_API_BASE_URL=http://$(API_HOST):$(API_PORT) npm run dev

test:
	uv run pytest tests -q

test-api:
	uv run pytest tests/studio_api tests/studio_schemas tests/studio_domain tests/studio_workflows -q

test-source-tools:
	uv run pytest tests/source_tools -q

test-e2e:
	cd frontend && npm run test:e2e

lint:
	uv run ruff check .

web-typecheck:
	cd frontend && npm run typecheck

web-build:
	cd frontend && npm run build

format:
	uv run ruff format .

check: test lint web-typecheck

smoke-api:
	uv run pytest tests/studio_api/test_api_scaffold.py -q
