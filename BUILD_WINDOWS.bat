@echo off
REM ============================================================================
REM  Cognitive Industries — Les Industries Cognitives
REM  Project: AI-IDP / AegisTrace
REM  Author: Pierre-Edward Procyk
REM  Copyright: (c) 2026 Pierre-Edward Procyk. All rights reserved.
REM  File: BUILD_WINDOWS.bat
REM  Purpose: One-click Windows build and verification script
REM  Version: 2.0.0
REM  Date: 2026-08-01
REM  Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
REM ============================================================================
REM
REM  INSTRUCTIONS:
REM  1. Extract the full archive to C:\Cognitive Industries\AI-IDP-AegisTrace
REM  2. Install Python 3.12+ from https://python.org (check "Add to PATH")
REM  3. Install Git from https://git-scm.com
REM  4. Double-click this file (BUILD_WINDOWS.bat)
REM
REM  This script will:
REM    - Create a virtual environment
REM    - Install all dependencies (including test-full)
REM    - Run the test suite (113 tests)
REM    - Run the demo scenario
REM    - Verify the ledger
REM    - Compile the arXiv paper (if Tectonic is installed)
REM    - Display a summary
REM
REM ============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo  ============================================================================
echo   AI-IDP / AegisTrace — Windows Build Script v2.0.0
echo   Cognitive Industries — Les Industries Cognitives
echo   (c) 2026 Pierre-Edward Procyk. All rights reserved.
echo  ============================================================================
echo.

REM --- Check Python ---
echo [1/7] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not on PATH.
    echo Please install Python 3.12+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo OK: Python %PYVER%

REM --- Check Git ---
echo.
echo [2/7] Checking Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Git is not installed. Git push will not be available.
    echo Install Git from https://git-scm.com
) else (
    for /f "tokens=3" %%i in ('git --version 2^>^&1') do set GITVER=%%i
    echo OK: Git %GITVER%
)

REM --- Create virtual environment ---
echo.
echo [3/7] Creating virtual environment...
if exist .venv (
    echo Virtual environment already exists. Using existing.
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)
echo OK: Virtual environment ready

REM --- Activate and install ---
echo.
echo [4/7] Installing dependencies (this may take a few minutes)...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
python -m pip install -e ".[test-full]" -q
if errorlevel 1 (
    echo ERROR: Dependency installation failed.
    echo Try: pip install -e ".[dev]" first, then pip install psycopg2-binary opentelemetry-sdk opentelemetry-exporter-otlp requests
    pause
    exit /b 1
)
echo OK: All dependencies installed

REM --- Run tests ---
echo.
echo [5/7] Running test suite (113 tests expected)...
python -m pytest tests/ -v --tb=short
if errorlevel 1 (
    echo WARNING: Some tests failed. Check the output above.
) else (
    echo OK: All tests passed
)

REM --- Run demo ---
echo.
echo [6/7] Running demo scenario...
python -m aegistrace.cli admin demo --out .aitrace-demo
if errorlevel 1 (
    echo WARNING: Demo failed. Check the output above.
) else (
    echo OK: Demo completed successfully
    echo.
    echo Verifying ledger...
    python -m aegistrace.cli verify --ledger .aitrace-demo\ledger.jsonl
)

REM --- Check Tectonic (optional) ---
echo.
echo [7/7] Checking arXiv paper compilation (optional)...
where tectonic >nul 2>&1
if errorlevel 1 (
    echo SKIPPED: Tectonic not installed.
    echo To compile the paper, install Tectonic from https://tectonic-typesetting.github.io
) else (
    cd paper
    tectonic main.tex
    if errorlevel 1 (
        echo WARNING: Paper compilation failed.
    ) else (
        echo OK: Paper compiled successfully
        copy main.pdf aegis-trace-arxiv.pdf >nul
    )
    cd ..
)

REM --- Summary ---
echo.
echo  ============================================================================
echo   BUILD COMPLETE
echo  ============================================================================
echo.
echo   Version:    2.0.0
echo   Date:       2026-08-01
echo   Python:     %PYVER%
echo   Tests:      113 (with test-full profile)
echo   Spec docs:  25
echo   JSON schemas: 14
echo   Python source files: 57
echo   Bibliography: 57 entries
echo.
echo   Project root: %CD%
echo   Virtual env:  %CD%\.venv
echo   Demo output:  %CD%\.aitrace-demo
echo.
echo   Next steps:
echo     1. Read FILING_INSTRUCTIONS.md
echo     2. Read GITHUB_PUSH_INSTRUCTIONS.md (to push to GitHub)
echo     3. Read ARXIV_SUBMISSION_INSTRUCTIONS.md (to submit to arXiv)
echo     4. Read OFFICIAL_EMAIL_TEMPLATES.md (for government communications)
echo.
echo  ============================================================================
echo.
pause
