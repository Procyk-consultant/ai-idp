@echo off
REM ============================================================================
REM  AI-IDP / AegisTrace — Placeholder Replacement Script
REM  Version: 2.0.0
REM  Date: 2026-08-01
REM
REM  This script replaces [INSERT ARXIV LINK], [INSERT GITHUB LINK],
REM  [ARXIV LINK], and [GITHUB LINK] with the actual URLs obtained
REM  after arXiv submission and GitHub push.
REM
REM  USAGE:
REM    1. After arXiv submission, save your arXiv ID to project-control\ARXIV_ID.txt
REM       (e.g., arXiv:2608.12345)
REM    2. After GitHub push, save your GitHub URL to project-control\GITHUB_URL.txt
REM       (e.g., https://github.com/Procyk-consultant/ai-idp)
REM    3. Run this script: REPLACE_PLACEHOLDERS.bat
REM    4. The script will update all files, commit, and push.
REM ============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo  ============================================================================
echo   AI-IDP Placeholder Replacement Script v2.0.0
echo  ============================================================================
echo.

REM --- Read ARXIV_ID ---
if not exist project-control\ARXIV_ID.txt (
    echo ERROR: project-control\ARXIV_ID.txt not found.
    echo Create it with your arXiv ID (e.g., arXiv:2608.12345)
    pause
    exit /b 1
)
set /p ARXIV_ID=<project-control\ARXIV_ID.txt
set ARXIV_URL=https://arxiv.org/abs/%ARXIV_ID:arXiv:=%
echo arXiv ID: %ARXIV_ID%
echo arXiv URL: %ARXIV_URL%
echo.

REM --- Read GITHUB_URL ---
if not exist project-control\GITHUB_URL.txt (
    echo ERROR: project-control\GITHUB_URL.txt not found.
    echo Create it with your GitHub URL (e.g., https://github.com/Procyk-consultant/ai-idp)
    pause
    exit /b 1
)
set /p GITHUB_URL=<project-control\GITHUB_URL.txt
echo GitHub URL: %GITHUB_URL%
echo.

REM --- Confirm ---
echo About to replace:
echo   [INSERT ARXIV LINK] and [ARXIV LINK] with: %ARXIV_URL%
echo   [INSERT GITHUB LINK] and [GITHUB LINK] with: %GITHUB_URL%
echo.
echo Files to update:
echo   - PUBLISHING_CONTENT.md
echo   - LINKEDIN_CONTENT_TEMPLATES.md
echo   - README.md
echo   - HERMES_HANDOFF_PROMPT.md
echo.
set /p CONFIRM=Proceed? (yes/no): 
if /i not "%CONFIRM%"=="yes" (
    echo Aborted.
    pause
    exit /b 0
)

REM --- Replace in PUBLISHING_CONTENT.md ---
echo Updating PUBLISHING_CONTENT.md...
powershell -Command "(Get-Content PUBLISHING_CONTENT.md -Raw) -replace '\[INSERT ARXIV LINK\]', '%ARXIV_URL%' -replace '\[INSERT GITHUB LINK\]', '%GITHUB_URL%' | Set-Content PUBLISHING_CONTENT.md -NoNewline"

REM --- Replace in LINKEDIN_CONTENT_TEMPLATES.md ---
echo Updating LINKEDIN_CONTENT_TEMPLATES.md...
powershell -Command "(Get-Content LINKEDIN_CONTENT_TEMPLATES.md -Raw) -replace '\[INSERT ARXIV LINK\]', '%ARXIV_URL%' -replace '\[INSERT GITHUB LINK\]', '%GITHUB_URL%' -replace '\[ARXIV LINK\]', '%ARXIV_URL%' -replace '\[GITHUB LINK\]', '%GITHUB_URL%' | Set-Content LINKEDIN_CONTENT_TEMPLATES.md -NoNewline"

REM --- Replace in README.md ---
echo Updating README.md...
powershell -Command "(Get-Content README.md -Raw) -replace '\[INSERT ARXIV LINK\]', '%ARXIV_URL%' -replace '\[INSERT GITHUB LINK\]', '%GITHUB_URL%' -replace '\[ARXIV LINK\]', '%ARXIV_URL%' -replace '\[GITHUB LINK\]', '%GITHUB_URL%' | Set-Content README.md -NoNewline"

REM --- Replace in HERMES_HANDOFF_PROMPT.md ---
echo Updating HERMES_HANDOFF_PROMPT.md...
powershell -Command "(Get-Content HERMES_HANDOFF_PROMPT.md -Raw) -replace '\[INSERT ARXIV LINK\]', '%ARXIV_URL%' -replace '\[INSERT GITHUB LINK\]', '%GITHUB_URL%' -replace '\[ARXIV LINK\]', '%ARXIV_URL%' -replace '\[GITHUB LINK\]', '%GITHUB_URL%' | Set-Content HERMES_HANDOFF_PROMPT.md -NoNewline"

echo.
echo All placeholders replaced.
echo.

REM --- Commit and push ---
echo Committing to Git...
git add PUBLISHING_CONTENT.md LINKEDIN_CONTENT_TEMPLATES.md README.md HERMES_HANDOFF_PROMPT.md
git commit -m "Replace placeholders with actual arXiv and GitHub URLs"
git push

echo.
echo  ============================================================================
echo   DONE — Placeholders replaced and pushed to GitHub
echo  ============================================================================
echo.
pause
