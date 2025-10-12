.PHONY: help install install-dev test test-coverage lint format clean build docs serve-docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install package dependencies"
	@echo "  install-dev  - Install package with development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  docs         - Build documentation"
	@echo "  serve-docs   - Serve documentation locally"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,test,docs]"
	pre-commit install

# Testing
test:
	pytest tests/

test-coverage:
	pytest --cov=src/Code4Ved_automation --cov-report=html --cov-report=term tests/

test-unit:
	pytest tests/unit/

test-integration:
	pytest tests/integration/

test-e2e:
	pytest tests/e2e/

# Code quality
lint:
	flake8 src/ tests/
	mypy src/
	black --check src/ tests/
	isort --check-only src/ tests/

format:
	black src/ tests/
	isort src/ tests/

check-security:
	bandit -r src/
	safety check

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Building
build: clean
	python -m build

# Documentation
docs:
	cd docs && make html

serve-docs:
	cd docs/build/html && python -m http.server 8000

# Development utilities
setup-env:
	python -m venv .venv
	@echo "Virtual environment created. Activate with:"
	@echo "source .venv/bin/activate  # On Linux/Mac"
	@echo ".venv\\Scripts\\activate     # On Windows"

run-examples:
	python examples/basic_usage.py

benchmark:
	python -m pytest benchmarks/ --benchmark-only