---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Contact: p.procyk.media@gmail.com
File: paper/README_SUBMISSION.md
Title: arXiv Submission README
Purpose: Describe the arXiv submission package and submission process
Version: 2.0.0
Status: Submission-ready (not submitted)
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# arXiv Submission README

## Package Contents

This package contains the submission-ready arXiv source for the paper:

> **Identity Before Autonomy: A Universal Framework for Persistent AI Actor Identity, Permanent Traceability, Delegation, Quality Assurance, and Accountable AI Operation**
>
> Pierre-Edward Procyk
> Cognitive Industries — Les Industries Cognitives
> Saguenay, Québec, Canada
> p.procyk.media@gmail.com

Files:

- `main.tex` — the LaTeX source
- `references.bib` — the bibliography
- `main.pdf` — the compiled PDF (also `aegis-trace-arxiv.pdf`)
- `README_SUBMISSION.md` — this file
- `arxiv_metadata.md` — arXiv submission metadata
- `author_metadata.md` — author metadata
- `AI_ASSISTANCE_DISCLOSURE.md` — AI-assistance disclosure
- `AUTHOR_CONTRIBUTIONS.md` — author-contributions statement
- `COMPETING_INTERESTS.md` — competing-interest statement
- `DATA_AND_CODE_AVAILABILITY.md` — data and code availability statement
- `REPRODUCIBILITY_STATEMENT.md` — reproducibility statement

## Compilation

The paper compiles from a clean environment using Tectonic:

```bash
cd paper/
tectonic main.tex
```

The compilation produces `main.pdf` (≈13 pages, ≈87 KiB). The compilation requires no proprietary font dependency; the paper uses Latin Modern (LModern) fonts, which are open-source and bundled with Tectonic.

## Submission Status

**Not submitted.** No arXiv submission has been performed. The Master Execution Prompt forbids external submission without separate written authorization from Pierre-Edward Procyk. The package is in submission-ready state and may be submitted when authorization is granted.

## Submission Process (When Authorized)

1. Verify current official arXiv requirements at https://arxiv.org/help/submit
2. Verify category selection (recommended: cs.CY Computers and Society, with cs.CR Cryptography and Security as cross-listing)
3. Verify supported LaTeX (Tectonic output is arXiv-compatible)
4. Compile from a clean directory: `cd paper/ && tectonic main.tex`
5. Validate all references (natbib + bibtex; references.bib is complete)
6. Validate every figure (the paper has no figures; tables use booktabs)
7. Validate every table (the paper has no tables in the body; booktabs is loaded for supplementary tables)
8. Validate every citation (every \citep has a corresponding .bib entry)
9. Inspect the rendered PDF
10. Verify no missing files
11. Verify no proprietary font dependency (LModern is open-source)
12. Verify no unsupported result
13. Verify no fabricated source (all .bib entries are real public references)
14. Create a submission archive: `zip -r aegis-trace-arxiv-v1.zip main.tex references.bib`
15. Create checksums: `sha256sum aegis-trace-arxiv-v1.zip > aegis-trace-arxiv-v1.zip.sha256`
16. Upload to arXiv

## Compilation Notes

The paper uses standard open-source LaTeX packages: `article` class, `inputenc`, `fontenc`, `lmodern`, `geometry`, `microtype`, `booktabs`, `longtable`, `array`, `amsmath`, `amssymb`, `enumitem`, `xcolor`, `titlesec`, `abstract`, `natbib`, `url`, `hyperref`, `cleveref`. All packages are available in standard TeX distributions and in Tectonic's auto-download bundle.

## Author Block

The arXiv title page uses the restrained academic block:

```
Pierre-Edward Procyk
Cognitive Industries — Les Industries Cognitives
Saguenay, Québec, Canada

Correspondence:
p.procyk.media@gmail.com
```

The telephone number and secondary email are NOT included on the arXiv title page per Master Prompt §H (academic block).

## Categorization

Recommended arXiv categories:
- Primary: cs.CY (Computers and Society) — the paper addresses AI governance, accountability, and societal implications.
- Cross-listing: cs.CR (Cryptography and Security) — the paper presents a cryptographic framework (Ed25519, hash chains, Merkle trees).
- Optional cross-listing: cs.AI (Artificial Intelligence) — the paper addresses AI agent governance.

## License

No public licence is applied. The paper's copyright is held by Pierre-Edward Procyk. arXiv submission requires selecting a licence; the licence selection will be made by Pierre-Edward Procyk at submission time and will be documented in this file.

## AI-Assistance Disclosure

This paper was produced with AI assistance under the Autonomous Master Execution Prompt issued by Pierre-Edward Procyk to Kimi Desktop. AI assistance was used for research synthesis, code implementation, document drafting, and validation support. AI assistance does not constitute authorship. All original concepts, frameworks, architectures, and IP remain the sole property of Pierre-Edward Procyk. The author reviewed and approved all content. The author is accountable for the paper's accuracy, completeness, and integrity. See `AI_ASSISTANCE_DISCLOSURE.md` for the full disclosure.
