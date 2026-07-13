.PHONY: dev backend frontend db-migrate db-seed install setup stop help

# Default target
help: ## Show this help
	@echo ""
	@echo "VeloxShip — Development Commands"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ─── Setup ──────────────────────────────────────────

setup: ## First-time setup: create venv, install all dependencies
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -e ".[dev]"
	cd frontend && npm install

install-backend: ## Install backend dependencies
	cd backend && . venv/bin/activate && pip install -e ".[dev]"

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

# ─── Database ───────────────────────────────────────

db-migrate: ## Run database migrations
	cd backend && . venv/bin/activate && alembic upgrade head

db-seed: ## Seed admin user and service tiers
	cd backend && . venv/bin/activate && python -m app.scripts.seed

db-reset: ## Drop and recreate database, then migrate and seed
	sudo -u postgres dropdb --if-exists veloxship
	sudo -u postgres createdb -O velox_user veloxship
	sudo -u postgres psql -d veloxship -c "CREATE EXTENSION IF NOT EXISTS unaccent;"
	sudo -u postgres psql -d veloxship -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
	$(MAKE) db-migrate db-seed

db-psql: ## Open psql shell to veloxship database
	psql -U velox_user -d veloxship -h localhost

# ─── Run Services ──────────────────────────────────

dev: ## Start backend + frontend (main command)
	@echo "\n\033[36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
	@echo "\033[36m  VeloxShip — Starting Development Servers\033[0m"
	@echo "\033[36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n"
	$(MAKE) db-migrate db-seed
	@echo "\n\033[32m  ✓ Backend:  http://localhost:8000\033[0m"
	@echo "\033[32m  ✓ Frontend: http://localhost:5173\033[0m"
	@echo "\033[32m  ✓ API Docs: http://localhost:8000/docs\033[0m"
	@echo "\033[33m  Login: admin / admin123\033[0m"
	@echo "\033[33m  Press Ctrl+C to stop\033[0m\n"
	@trap 'kill 0' SIGINT; \
		cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000 & \
		cd frontend && npm run dev & \
		wait

backend: ## Start backend only
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000

frontend: ## Start frontend only
	cd frontend && npm run dev

# ─── Testing ────────────────────────────────────────

test-backend: ## Run backend tests
	cd backend && . venv/bin/activate && pytest

test-frontend: ## Run frontend tests
	cd frontend && npm test

test: test-backend test-frontend ## Run all tests

# ─── Docker ─────────────────────────────────────────

docker-db: ## Start PostgreSQL via Docker (alternative to local psql)
	sudo docker-compose -f docker-compose.db.yml up -d

docker-dev: ## Start full app via Docker
	sudo docker-compose -f docker-compose.local.yml up --build

docker-down: ## Stop all Docker containers
	sudo docker-compose -f docker-compose.local.yml down
	sudo docker-compose -f docker-compose.db.yml down 2>/dev/null || true
