# Environment Report — AI-IDP / AegisTrace 2.1.0

**Observed:** 2026-09-07, America/Toronto

**Operating system:** Windows

**Python used:** 3.12.10

**Tectonic:** 0.16.9

**Git source repository:** `C:\Cognitive Industries\AI-IDP-AegisTrace`

**Isolated verification worktree:** `C:\Users\Agenc\Documents\Codex\2026-09-06\referenced-chatgpt-conversation-this-is-an\work\ai-idp-reconcile-audit-20260907`

**Evidence archive inspected:** `D:\cognitive_industries_official_V.20260812`

## Dependency environment

An isolated Python virtual environment was created for the reconciliation audit. The branch was installed with its declared `test-full` dependencies, then reinstalled without dependency changes after the 2.1.0 metadata correction. `pip check` passed before the repair run.

`liboqs-python` was present in the initial full-test environment. Importing it while no native liboqs installation existed unexpectedly launched a network clone and native compile. The diagnostic test was interrupted. Task-created processes were stopped, and both generated trees were moved intact to:

- `C:\Users\Agenc\Documents\Codex\2026-09-06\referenced-chatgpt-conversation-this-is-an\work\quarantine\liboqs-autobuild-temp-tmp9y3shvqp`
- `C:\Users\Agenc\Documents\Codex\2026-09-06\referenced-chatgpt-conversation-this-is-an\work\quarantine\liboqs-autobuild-install-_oqs`

The original task-created paths no longer exist. Nothing was deleted. The test contract was changed so native liboqs tests require `AEGISTRACE_RUN_LIBOQS_TESTS=1`, and `liboqs-python` was removed from the standard `test-full` extra while remaining in the explicit `pqc` extra.

## Available/unavailable execution targets

- Local Python execution: available and verified.
- Package/wheel build: available and verified.
- Tectonic paper build: available and verified.
- Git and credential-free public remote inspection: available and verified.
- Docker CLI: available.
- Docker Desktop Linux engine: unavailable at the named-pipe endpoint; no container build/run claim is made.
- Authenticated email mailbox evidence: not available through the inspected files/tools.
- Authenticated GitHub billing/support account evidence: not available through the public API.
