# Flight Data Analysis - Makefile
# ===============================

.PHONY: help install clean test lint format docs run-analysis run-viz run-dashboard all

# Default target
help:
	@echo "Flight Data Analysis - Available Commands"
	@echo "=========================================="
	@echo "install      - Install dependencies"
	@echo "clean        - Clean generated files"
	@echo "test         - Run tests"
	@echo "lint         - Run linting"
	@echo "format       - Format code"
	@echo "docs         - Generate documentation"
	@echo "run-analysis - Run data analysis"
	@echo "run-viz      - Generate visualizations"
	@echo "run-dashboard- Create dashboards"
	@echo "all          - Run analysis, viz, and dashboard"
	@echo "setup        - Complete project setup"

# Installation
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	pip install -e .

# Development installation
install-dev: install
	@echo "Installing development dependencies..."
	pip install -r requirements.txt
	pip install -e ".[dev,docs]"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf output/
	rm -rf logs/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Run linting
lint:
	@echo "Running linting..."
	flake8 src/ tests/ main.py
	mypy src/ main.py

# Format code
format:
	@echo "Formatting code..."
	black src/ tests/ main.py
	isort src/ tests/ main.py

# Generate documentation
docs:
	@echo "Generating documentation..."
	cd docs && make html

# Run data analysis
run-analysis:
	@echo "Running data analysis..."
	python main.py analyze

# Generate visualizations
run-viz:
	@echo "Generating visualizations..."
	python main.py visualize

# Create dashboards
run-dashboard:
	@echo "Creating dashboards..."
	python main.py dashboard

# Run everything
all: run-analysis run-viz run-dashboard

# Complete project setup
setup: install-dev
	@echo "Setting up project structure..."
	mkdir -p logs output reports
	@echo "Project setup complete!"

# Create distribution
dist: clean
	@echo "Creating distribution..."
	python setup.py sdist bdist_wheel

# Install in development mode
dev-install:
	@echo "Installing in development mode..."
	pip install -e .

# Run with specific data file
run-custom:
	@echo "Running with custom data..."
	python main.py all --data $(DATA_PATH)

# Quick start
quick-start: setup run-analysis run-viz run-dashboard
	@echo "Quick start complete! Check output/ directory for results." 