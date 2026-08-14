---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/SOURCE_GAP_REGISTER.md
Title: Source Gap Register
Version: 2.0.0
Last Material Revision: 2026-08-14
---

# Source Gap Register

Gaps in source coverage identified during research, with handling.

| Gap ID | Description | Handling |
|--------|-------------|----------|
| G-001 | Full-text archival storage of every cited Canadian primary source was not performed | Citation includes official title and publishing body; URL recorded in bibliography; absence of local archive noted |
| G-002 | No external peer review performed | Internal independent validation by A31–A34; external review remains a future independent-validation objective |
| G-003 | Real deployment benchmark data not available | Synthetic benchmark data used, clearly labelled |
| G-004 | Indigenous rights-holder engagement not performed | Public-framework analysis only. Engagement is required before deployments that materially affect Indigenous rights, community data, governance authority, or services; it is not a universal prerequisite for unrelated implementations |
| G-005 | Provincial AI legislative developments (e.g., Quebec AI regulatory developments) tracked at high level only | Federal-provincial jurisdiction analysis identifies the interaction pattern; provincial monitoring is a future work item |
| G-006 | Operational cost data from a deployed AI-IDP system not available | Cost-benefit analysis uses parametric models based on published audit-log storage costs and analogous regulatory regimes (e.g., financial audit, privacy impact assessment) |
| G-007 | Post-quantum signature migration not live-activated | Migration architecture and interfaces are implemented/tested in the reference corpus; live PQC signing requires the external runtime library and production configuration |
| G-008 | Live federation with an external registry not tested | Federation protocol specified; reference implementation includes in-process federation between two AegisTrace instances; live federation with an external jurisdiction is a future work item |
| G-009 | MCP adapter is not validated against a production MCP server | Adapter implements the protocol surface required for evidence collection; live integration with a production MCP server is a future work item |
| G-010 | French full-body translation not produced | Bilingual identity and key French deliverables exist; a full French edition remains future work |

## Capability-status convention

Where project documents describe high-assurance target capabilities that are implemented at the interface/module level but require an external service, credential, hardware device, or runtime library for live activation, those capabilities may be marked with an asterisk (`*`). The asterisk preserves the intended implementation standard while directing readers to the validation status and limitations for activation state.
