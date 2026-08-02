"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_project_metadata.py
Purpose: Verify release metadata and documented full-validation dependency profile
Classification: test
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _pyproject() -> dict:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


def test_project_release_metadata_is_canonical() -> None:
    data = _pyproject()
    project = data["project"]
    assert project["version"] == "2.0.0"
    assert project["requires-python"] == ">=3.12"


def test_test_full_extra_contains_complete_validation_stack() -> None:
    extras = _pyproject()["project"]["optional-dependencies"]
    assert "test-full" in extras
    requirements = {requirement.split(";", 1)[0].strip().lower() for requirement in extras["test-full"]}
    expected_prefixes = {
        "pytest>=",
        "pytest-cov>=",
        "ruff>=",
        "mypy>=",
        "psycopg2-binary>=",
        "opentelemetry-api>=",
        "opentelemetry-sdk>=",
        "opentelemetry-exporter-otlp>=",
    }
    for prefix in expected_prefixes:
        assert any(requirement.startswith(prefix) for requirement in requirements), prefix
