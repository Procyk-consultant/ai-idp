# Cognitive Industries — Les Industries Cognitives
# Project: AI-IDP / AegisTrace
# Author and Intellectual Property Owner: Pierre-Edward Procyk
# Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
# File: Dockerfile
#
# Container image for the AegisTrace reference implementation.
# This Dockerfile is provided for reproducibility; it is not used for
# external deployment during the autonomous run.

FROM python:3.12-slim AS base

LABEL org.opencontainers.image.title="AegisTrace"
LABEL org.opencontainers.image.description="Reference implementation of the AI-IDP standard"
LABEL org.opencontainers.image.author="Pierre-Edward Procyk"
LABEL org.opencontainers.image.vendor="Cognitive Industries — Les Industries Cognitives"
LABEL org.opencontainers.image.version="2.1.0"
LABEL org.opencontainers.image.licenses="No licence selected unless approved in writing by Pierre-Edward Procyk. All rights reserved."

WORKDIR /app

COPY pyproject.toml Makefile ./
COPY src/ ./src/
COPY tests/ ./tests/
COPY schemas/ ./schemas/
COPY spec/ ./spec/
COPY README.md ./README.md

RUN pip install --no-cache-dir -e ".[dev]"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python", "-m", "pytest", "tests/", "-v"]
