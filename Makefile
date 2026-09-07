# Cognitive Industries — Les Industries Cognitives
# Project: AI-IDP / AegisTrace
# Author and Intellectual Property Owner: Pierre-Edward Procyk
# Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
# File: Makefile

PYTHON ?= python3
PIP ?= pip

.PHONY: help install dev lint type test verify conformance security privacy permanence benchmarks paper clean demo

help:
	@echo "AegisTrace Makefile"
	@echo "  install     - Install package in editable mode"
	@echo "  dev         - Install dev dependencies"
	@echo "  lint        - Run ruff"
	@echo "  type        - Run mypy"
	@echo "  test        - Run pytest"
	@echo "  verify      - Run lint + type + tests + conformance"
	@echo "  conformance - Run conformance suite"
	@echo "  security    - Run security tests"
	@echo "  privacy     - Run privacy tests"
	@echo "  permanence  - Run permanence tests"
	@echo "  benchmarks  - Run benchmarks"
	@echo "  paper       - Compile arXiv paper"
	@echo "  demo        - Run the demo scenario"
	@echo "  clean       - Clean build artifacts"

install:
	$(PIP) install -e .

dev:
	$(PIP) install -e ".[dev]"

lint:
	$(PYTHON) -m ruff check src tests

type:
	$(PYTHON) -m mypy src/aegistrace

test:
	$(PYTHON) -m pytest tests/unit tests/integration -v

verify: lint type test conformance security privacy permanence

conformance:
	$(PYTHON) -m pytest tests/conformance -v

security:
	$(PYTHON) -m pytest tests/security -v

privacy:
	$(PYTHON) -m pytest tests/privacy -v

permanence:
	$(PYTHON) -m pytest tests/permanence -v

benchmarks:
	$(PYTHON) -m pytest benchmarks -v

paper:
	cd paper && tectonic main.tex

demo:
	$(PYTHON) -m aegistrace.cli admin demo --out .aitrace-demo

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
