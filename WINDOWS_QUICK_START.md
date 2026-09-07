# AI-IDP / AegisTrace — Windows Quick Start

Last Material Revision: 2026-08-01

**Version:** 2.1.0
**Date:** 2026-08-01  
**Author:** Pierre-Edward Procyk  
**Organization:** Cognitive Industries — Les Industries Cognitives

---

## Prerequisites

1. **Python 3.12+** — Download from https://python.org  
   During installation, check **"Add Python to PATH"**

2. **Git** — Download from https://git-scm.com  
   (Optional but recommended for GitHub push)

3. **Tectonic** (optional, for arXiv paper compilation) — Download from https://tectonic-typesetting.github.io

---

## Quick Start

1. **Extract** the archive to `C:\Cognitive Industries\AI-IDP-AegisTrace`

2. **Double-click** `BUILD_WINDOWS.bat`

That's it. The script will:
- Create a Python virtual environment
- Install all dependencies (including test-full profile)
- Run all 113 tests
- Run the demo scenario
- Verify the ledger
- Compile the arXiv paper (if Tectonic is installed)
- Display a summary

---

## Manual Setup (if BUILD_WINDOWS.bat fails)

Open PowerShell or Command Prompt:

```cmd
cd "C:\Cognitive Industries\AI-IDP-AegisTrace"

REM Create virtual environment
python -m venv .venv

REM Activate
.venv\Scripts\activate

REM Install
pip install -e ".[test-full]"

REM Run tests
pytest tests/ -v

REM Run demo
python -m aegistrace.cli admin demo --out .aitrace-demo

REM Verify ledger
python -m aegistrace.cli verify --ledger .aitrace-demo\ledger.jsonl
```

---

## What's in this project

| Item | Count | Location |
|------|-------|----------|
| Specification documents | 25 | `spec/` |
| JSON Schemas | 14 | `schemas/` |
| Python source files | 57 | `src/aegistrace/` + `tests/` |
| Tests | 113 | `tests/` |
| Bibliography references | 58 | `paper/references.bib` |
| arXiv paper | 1 (13 pages) | `paper/main.tex` + `paper/main.pdf` |
| Official PDFs | 2 (EN + FR) | Project root |


| Documentation guides | 14 | `docs/` |
| Brand assets | 3 (originals preserved) | `brand/originals/` |

---

## Key Documents

| Document | Purpose |
|----------|---------|
| `PROJECT_ROADMAP.pdf` | Complete project roadmap (phases, steps, targets) |
| `OFFICIAL_PROJECT_DOCUMENT_EN.pdf` | Official English document for government |
| `DOCUMENT_OFFICIEL_PROJET_FR.pdf` | Official French document for Quebec government |
| `FILING_INSTRUCTIONS.md` | What goes where, to who, why |

---

## Honest Project Status

AI-IDP is a proposed Canadian framework for AI agent identity, delegation, and traceability. AegisTrace is its functional and verifiable reference implementation. The project seeks technical, legal, academic, and institutional evaluation; it does not yet claim to be a law, an adopted standard, a certification, or a production product.

---

## Contact

Pierre-Edward Procyk  
Founder / CEO  
Cognitive Industries — Les Industries Cognitives  
Saguenay, Québec, Canada  
p.procyk.media@gmail.com  
  

© 2026 Pierre-Edward Procyk. Cognitive Industries — Les Industries Cognitives. All rights reserved.

# AI-IDP / AegisTrace — Windows Quick Start
