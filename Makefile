# SmartMeet Development Makefile
.PHONY: help setup env-setup install-deps dev-db db-status start-api start-web start-addin dev stop clean migrate db-reset db-seed test console

# Default help command
help:
	@echo "🚀 SmartMeet Development Commands:"
	@echo ""
	@echo "📋 Quick Start:"
	@echo "  make first-setup    - Complete first-time setup (env + deps + db + seed)"
	@echo "  make dev            - Start all services for development"
	@echo "  make stop           - Stop all services"
	@echo ""
	@echo "🛠️  Setup Commands:"
	@echo "  make setup          - Full project setup (deps + db setup)"
	@echo "  make env-setup      - Create environment files"
	@echo "  make install-deps   - Install all dependencies"
	@echo "  make dev-db         - Start PostgreSQL database"
	@echo "  make db-status      - Check database connection status"
	@echo ""
	@echo "🏃 Development Commands:"
	@echo "  make start-api      - Start FastAPI backend only"
	@echo "  make start-web      - Start Next.js web portal only"
	@echo "  make start-addin    - Start Outlook add-in only"
	@echo ""
	@echo "🗄️  Database Commands:"
	@echo "  make migrate        - Run database migrations"
	@echo "  make migration:status - Show migration status"
	@echo "  make db-reset       - Reset database (⚠️  DELETES ALL DATA)"
	@echo "  make db-seed        - Seed database with test data"
	@echo "  make db-console     - Database interactive console"
	@echo ""
	@echo "🔧 Utility Commands:"
	@echo "  make console        - Start interactive Python console"
	@echo "  make test           - Run all tests"
	@echo "  make lint           - Run linting"
	@echo "  make clean          - Clean up containers and temp files"
	@echo "  make logs           - Show database logs"
	@echo ""
	@echo "🌐 Access Points:"
	@echo "  • API Backend:      http://localhost:8000"
	@echo "  • API Docs:         http://localhost:8000/docs"
	@echo "  • Web Portal:       http://localhost:3000"
	@echo "  • Outlook Add-in:   http://localhost:3001"
	@echo "  • Database Admin:   http://localhost:8080 (adminer)"
	@echo "  • Database:         postgresql://smartmeet:password@localhost:5432/smartmeet_dev"

# Complete first-time setup
first-setup: env-setup install-deps dev-db db-wait migrate db-seed
	@echo ""
	@echo "🎉 SmartMeet development environment is ready!"
	@echo ""
	@echo "📋 Next steps:"
	@echo "  1. Edit .env.local with your OAuth credentials"
	@echo "  2. Run 'make start-api' to start the API server"
	@echo "  3. Visit http://localhost:8000/docs to see the API"
	@echo ""

# Environment setup
env-setup:
	@echo "📝 Setting up environment files..."
	@if [ ! -f .env.local ]; then \
		cp env.local.example .env.local; \
		echo "✅ Created .env.local - please configure your OAuth credentials"; \
	else \
		echo "📄 .env.local already exists"; \
	fi
	@if [ ! -f apps/api-backend/.env ]; then \
		cp env.local.example apps/api-backend/.env; \
		echo "✅ Created apps/api-backend/.env"; \
	else \
		echo "📄 apps/api-backend/.env already exists"; \
	fi

# Install all dependencies
install-deps:
	@echo "📦 Installing dependencies..."
	@echo "📦 Installing API backend dependencies..."
	cd apps/api-backend && pip install -r requirements.txt
	@echo "📦 Installing database package dependencies..."
	pip install -r packages/database/requirements.txt
	@echo "📦 Installing web portal dependencies..."
	cd apps/web-portal && npm install
	@echo "📦 Installing Outlook add-in dependencies..."
	cd apps/outlook-addin && npm install
	@echo "✅ All dependencies installed"

# Combined setup command
setup: env-setup install-deps
	@echo "✅ Project setup complete!"

# Start PostgreSQL database with health check
dev-db:
	@echo "🗄️  Starting PostgreSQL database..."
	@mkdir -p docker/postgres-init
	docker-compose -f docker/docker-compose.dev.yml up -d postgres redis adminer
	@echo "⏳ Waiting for PostgreSQL to be ready..."
	@timeout 30s bash -c 'until docker-compose -f docker/docker-compose.dev.yml exec -T postgres pg_isready -U smartmeet -d smartmeet_dev; do sleep 1; done' || (echo "❌ Database failed to start" && exit 1)
	@echo "✅ PostgreSQL is ready!"
	@echo "🌐 Database Admin: http://localhost:8080 (adminer)"
	@echo "📊 Connection: postgresql://smartmeet:password@localhost:5432/smartmeet_dev"

# Wait for database to be ready (internal command)
db-wait:
	@echo "⏳ Waiting for database to be ready..."
	@timeout 30s bash -c 'until docker-compose -f docker/docker-compose.dev.yml exec -T postgres pg_isready -U smartmeet -d smartmeet_dev > /dev/null 2>&1; do sleep 1; done' || (echo "❌ Database not ready" && exit 1)

# Check database status
db-status:
	@echo "🔍 Checking database status..."
	@if docker-compose -f docker/docker-compose.dev.yml ps postgres | grep -q "Up"; then \
		echo "✅ PostgreSQL container is running"; \
		if docker-compose -f docker/docker-compose.dev.yml exec -T postgres pg_isready -U smartmeet -d smartmeet_dev > /dev/null 2>&1; then \
			echo "✅ Database is accepting connections"; \
			python tools/database/manage.py migration:status; \
		else \
			echo "❌ Database is not ready"; \
		fi \
	else \
		echo "❌ PostgreSQL container is not running"; \
		echo "💡 Run 'make dev-db' to start the database"; \
	fi

# Development - Start all services
dev:
	@echo "🚀 Starting all SmartMeet services..."
	@make dev-db
	@echo ""
	@echo "✅ All services started:"
	@echo "   🗄️  Database:       postgresql://localhost:5432/smartmeet_dev"
	@echo "   🌐 Database Admin:  http://localhost:8080"
	@echo "   📊 Redis:           redis://localhost:6379"
	@echo ""
	@echo "🏃 To start the applications:"
	@echo "   make start-api      # Start API backend"
	@echo "   make start-web      # Start web portal"
	@echo "   make start-addin    # Start Outlook add-in"

# Individual service starts
start-api:
	@echo "🔧 Starting FastAPI backend..."
	@make db-status
	cd apps/api-backend && python run.py

start-web:
	@echo "🌐 Starting Next.js web portal..."
	cd apps/web-portal && npm run dev

start-addin:
	@echo "📧 Starting Outlook add-in..."
	cd apps/outlook-addin && npm run dev -- --port 3001

# Database migration commands
migrate:
	@echo "🗄️  Running database migrations..."
	python tools/database/manage.py migrate

migration\:status:
	@echo "🔍 Checking migration status..."
	python tools/database/manage.py migration:status

# Database operations
db-reset:
	@echo "⚠️  DANGER: This will DELETE ALL DATA!"
	@read -p "Are you sure? Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ] || (echo "Cancelled" && exit 1)
	@echo "🗄️  Resetting database..."
	python tools/database/manage.py db:reset --yes

db-seed:
	@echo "🌱 Seeding database with test data..."
	python tools/database/manage.py db:seed

# Interactive consoles
console:
	@echo "🐍 Starting SmartMeet Python console..."
	python tools/database/manage.py console

db-console:
	@echo "🗄️  Starting PostgreSQL console..."
	docker-compose -f docker/docker-compose.dev.yml exec postgres psql -U smartmeet -d smartmeet_dev

# Utility commands
logs:
	@echo "📋 Showing database logs..."
	docker-compose -f docker/docker-compose.dev.yml logs -f postgres

stop:
	@echo "🛑 Stopping all services..."
	docker-compose -f docker/docker-compose.dev.yml down

clean:
	@echo "🧹 Cleaning up..."
	docker-compose -f docker/docker-compose.dev.yml down -v
	docker system prune -f
	@echo "✅ Cleanup complete"

# Testing and quality
test:
	@echo "🧪 Running tests..."
	cd apps/api-backend && python -m pytest tests/ || echo "⚠️  Configure tests for API Backend"
	cd apps/web-portal && npm run test || echo "⚠️  Configure tests for Web Portal"
	cd apps/outlook-addin && npm run test || echo "⚠️  Configure tests for Add-in"

lint:
	@echo "🔍 Running linting..."
	cd apps/api-backend && python -m flake8 . || echo "⚠️  Install flake8 for Python linting"
	cd apps/web-portal && npm run lint || echo "⚠️  Configure ESLint for Web Portal"
	cd apps/outlook-addin && npm run lint || echo "⚠️  Configure ESLint for Add-in" 