---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/PROTOCOL_DEVIATIONS.md
Title: Protocol Deviations
Version: 2.0.0
Last Material Revision: 2026-08-01
---

# Protocol Deviations

Deviations from the research protocol documented per Master Prompt §14 (protocol-deviation rules).

| Deviation ID | Deviation | Justification | Effect |
|---------------|-----------|---------------|--------|
| PD-001 | Citation chaining was performed to depth 1–2 for primary Canadian sources, not exhaustive forward-and-backward chaining to saturation | Resource constraint; saturation-based chaining of every primary source is a multi-week task | Bibliography covers foundational sources; secondary chains abbreviated; gap recorded |
| PD-002 | Stopping criteria applied after two successive iterations revealed no new major legal, technical, or governance category | Per Master Prompt §14 stopping rule | Documentation of stopping rationale in research/protocol/STOPPING_RATIONALE.md |
| PD-003 | arXiv paper compiled with Tectonic rather than vanilla TeX Live | Tectonic is the available engine; output is arXiv-compatible | No effect on submission readiness; arXiv accepts Tectonic-compiled PDFs |
| PD-004 | DOCX generation performed via python-docx (not docx-js) | python-docx is the mature Python-native option available in the environment | Equivalent output; DOCX opens correctly in Word/LibreOffice |
| PD-005 | Live GitHub remote integration not exercised | Master Prompt forbids external publication | Adapter is functional against local Git; ready-to-push payloads produced |
| PD-006 | OpenTelemetry adapter specified but not implemented as runtime exporter | Adapter scope limited to evidence-collection interface | OTLP export is a documented future work item |
