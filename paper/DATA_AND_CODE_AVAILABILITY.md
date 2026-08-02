# Data and Code Availability

Last Material Revision: 2026-08-01

## Code Availability

The AegisTrace reference implementation is available in the project repository. The repository is local-only during the autonomous execution; external release requires separate written authorization from Pierre-Edward Procyk. The repository contains:

- `src/aegistrace/` — the Python reference implementation (45 Python modules)
- `tests/` — 13 Python test/support files exercising 113 passing tests with the test-full profile
- `spec/` — the formal specification (25 specification documents)
- `schemas/` — the JSON schemas (14 schemas)
- `threat-model/` — the threat model
- `paper/` — this arXiv paper source
- `docs/` — developer, auditor, regulator documentation
- `examples/` — worked examples
- `science/` — the scientific method, hypotheses, reported synthetic evaluation, results, and limitations

## Data Availability

All non-test evaluation data reported in this paper is synthetic or illustrative and is not represented as an external empirical observation. Test fixtures are deterministic. Real deployment data is not available; this is documented as a limitation (Section~\ref{sec:limitations} of the paper).

## Reproducibility

The AegisTrace reference implementation is reproducible:

- All dependencies are pinned in `pyproject.toml`.
- All tests are deterministic (Ed25519 signatures are deterministic; no random seeds).
- The demo scenario (`aegistrace admin demo`) produces a verifiable ledger from scratch.
- The reported synthetic evaluation and its limitations are documented in `science/RESULTS_REPORT.md` and `science/SCIENTIFIC_METHOD.md`.
- A clean rerun of the test suite produces the same results.

## External Release

External release of the code or data requires separate written authorization from Pierre-Edward Procyk. See the project's PUBLICATION_METADATA_STATUS.md and LICENSING_STATUS.md for details.

# Data and Code Availability
