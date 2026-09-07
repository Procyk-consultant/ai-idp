# GIFT-X++ Action Tickets — GitHub Main Consumer Publication

```yaml
action_ticket:
  id: AT-20260907-05
  plan_node: P0-publication-boundary
  description: Confirm exact GitHub main ancestry, authorization, exclusions, and recoverable non-force publication path.
  preconditions:
    - role_is_single: true
    - deps_declared: true
    - tests_written: false
  acceptance_tests:
    unit: git merge-base --is-ancestor origin/main publish/2.1.0-consumer-main
    integration: fresh fetch and exact remote-head readback
    container: not applicable to Git ref governance
  risks:
    - R-public-scope: Exclude untracked workspace, outreach, transcript, and recovery material.
    - R-history-loss: Require fast-forward ancestry and prohibit force-push.
  outputs: [IP_HEADER_BLOCK, CODE, TEST, RATIONALE]
  owner: Codex
  due: 2026-09-07
  status: done
```

```yaml
action_ticket:
  id: AT-20260907-06
  plan_node: P4-consumer-presentation
  description: Present AI-IDP and AegisTrace in plain English and Canadian French without expanding legal, deployment, or certification claims.
  preconditions:
    - role_is_single: true
    - deps_declared: true
    - tests_written: true
  acceptance_tests:
    unit: local Markdown link and image-target validation
    integration: README and consumer-guide evidence cross-check against project status
    container: not applicable to Markdown presentation
  risks:
    - R-overclaim: Preserve proposed-framework, reference-implementation, and external-activation boundaries.
  outputs: [IP_HEADER_BLOCK, CODE, TEST, RATIONALE]
  owner: Codex
  due: 2026-09-07
  status: done
```

```yaml
action_ticket:
  id: AT-20260907-07
  plan_node: P4-brand-media
  description: Include official project marks and selected existing article/post visuals with byte preservation, public gallery, and checksum provenance.
  preconditions:
    - role_is_single: true
    - deps_declared: true
    - tests_written: true
  acceptance_tests:
    unit: SHA-256 checksum manifests match every included binary
    integration: README/gallery image targets resolve and every manifest row names an included file
    container: not applicable to static media
  risks:
    - R-brand-mutation: Copy assets byte-for-byte and never overwrite originals.
    - R-synthetic-confusion: Exclude the fictional payment visual and document selection limits.
  outputs: [IP_HEADER_BLOCK, CODE, TEST, RATIONALE]
  owner: Codex
  due: 2026-09-07
  status: done
```

```yaml
action_ticket:
  id: AT-20260907-08
  plan_node: P5-publication-verification
  description: Re-run engineering, document, media, secret, and Git-history gates before publishing main and verify the exact remote result afterward.
  preconditions:
    - role_is_single: true
    - deps_declared: true
    - tests_written: true
  acceptance_tests:
    unit: ruff, mypy, pytest, metadata, media checksums, Markdown targets
    integration: governed demo, ledger verification, wheel, paper, and git push/readback
    container: blocked because Docker Desktop Linux engine is unavailable
  risks:
    - R-ci-account-lock: Local gates remain controlling if GitHub does not start a runner; disclose exact remote annotation.
    - R-publication-mismatch: Compare origin/main with the committed local publication hash.
  outputs: [IP_HEADER_BLOCK, CODE, TEST, RATIONALE]
  owner: Codex
  due: 2026-09-07
  status: done
```
