.PHONY: help install install-dev lint format check test clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt
	playwright install

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	playwright install
	pre-commit install

format: ## Format code with black and isort
	black .
	isort .

lint: ## Run all linting tools
	black --check .
	isort --check-only .
	flake8 .
	mypy src/

check: format lint ## Format and lint code

test: ## Run tests
	python -m pytest

test-verbose: ## Run tests with verbose output
	python -m pytest -v

test-coverage: ## Run tests with coverage
	python -m pytest --cov=src

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

fix: ## Auto-fix linting issues
	black .
	isort .
	pre-commit run --all-files

setup: install-dev ## Complete setup for development
	@echo "Setup complete! You can now run:"
	@echo "  make check    # Check code quality"
	@echo "  make format   # Format code"
	@echo "  make test     # Run tests" 