# Makefile for TestLearn Application

.PHONY: help install run test build docker-up docker-down clean

# Default target
help:
	@echo "TestLearn Application - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     - Install dependencies"
	@echo "  run         - Run development server"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build    - Build Docker image"
	@echo "  docker-up       - Start with Docker Compose"
	@echo "  docker-down     - Stop Docker Compose"
	@echo "  docker-test     - Run tests in Docker"
	@echo "  docker-dev      - Start development container"
	@echo ""
	@echo "Database:"
	@echo "  migrate     - Run database migrations"
	@echo "  seed        - Seed database with initial data"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean       - Remove temporary files"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install pytest pytest-cov httpx

# Run development server
run:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
test:
	pytest tests/ -v --tb=short

# Run tests with coverage
test-coverage:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run linting (if you add a linter later)
lint:
	@echo "Linting not configured yet"

# Build Docker image
docker-build:
	docker build -t testlearn:latest .

# Start with Docker Compose (production)
docker-up:
	docker-compose up --build

# Start with Docker Compose (detached)
docker-up-detach:
	docker-compose up -d --build

# Stop Docker Compose
docker-down:
	docker-compose down

# Run tests in Docker
docker-test:
	docker-compose --profile test run test

# Start development container
docker-dev:
	docker-compose --profile dev up web-dev

# Build production image
docker-build-prod:
	docker build --target production -t testlearn:prod .

# Database migrations
migrate:
	alembic upgrade head

# Seed database
seed:
	python -c "from app.services import seed_initial_data; seed_initial_data()"

# Cleanup temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf build
	rm -rf dist

# Clean all (including database and logs)
clean-all: clean
	rm -rf data/
	rm -rf logs/
	rm -f *.db
	rm -f *.sqlite

# Create directories
dirs:
	mkdir -p data logs

# Start with environment setup
setup: dirs install
	@echo "Setup complete! Copy .env.example to .env and configure as needed."

# Production deployment
deploy: docker-build-prod
	@echo "Production image built. Deploy with: docker run -p 8000:8000 testlearn:prod"
