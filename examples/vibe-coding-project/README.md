# Vibe-Coding Project Example

Last Material Revision: 2026-08-01

## Scenario

A small developer uses a vibe-coding tool to rapidly prototype a web application. The agent operates at conformance level L1.

## Participants

- **Controller:** Small developer (registered as `aitrace://ca/controller/developer-001`)
- **Principal:** Same as controller
- **Agent:** Vibe-coding tool (`aitrace://ca/agent/vibe-coder#v2.0`)
- **Agent instance:** Specific session (`aitrace://ca/agent-instance/vibe-coder#session-001`)
- **Provider:** AI provider (`aitrace://ca/provider/provider-002`)
- **Model:** AI model (`aitrace://ca/model/llm#v1.5`)
- **Deployment:** Local deployment (`aitrace://ca/deployment/local-001`)

## Workflow

1. Developer authorizes the vibe-coder to generate a web app.
2. Vibe-coder generates files (CREATE events with after digests).
3. Vibe-coder runs the app (RUN event).
4. Vibe-coder modifies files based on feedback (MODIFY events with before/after digests).
5. Vibe-coder tests the app (TEST event).
6. All events are recorded in the developer's local AegisTrace ledger.

## L1 Conformance

At L1, the developer:
- Uses the open-source AegisTrace reference implementation (no fee).
- Maintains a local append-only ledger.
- Records events with Ed25519 signatures.
- Does not require external audit.

## Non-Production-Deployment Policy

The developer's vibe-coding project explicitly avoids production deployment at L1. Production deployment requires L3 or higher conformance, with sectoral certification.

## Quality Evidence

At L1, the developer records:
- Test results (pass/fail)
- Code review (self-review)
- Build record

## Public Records

At L1, the developer may optionally publish Merkle anchors to a public verification repository. This is recommended but not required.

# Vibe-Coding Project Example
