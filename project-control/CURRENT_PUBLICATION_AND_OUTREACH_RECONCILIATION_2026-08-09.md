---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
File: project-control/CURRENT_PUBLICATION_AND_OUTREACH_RECONCILIATION_2026-08-09.md
Title: Current Publication and Outreach Reconciliation
Purpose: Establish a source-grounded current-state baseline before repository, outreach, or official-directory changes.
Version: 2.0.0
Status: Read-only audit record; implementation pending Pierre-Edward Procyk approval.
Date: 2026-08-09
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Licence Status: No public licence is granted.
---

# Current Publication and Outreach Reconciliation

## Scope and method

This record consolidates read-only checks performed on 2026-08-09 against the live public GitHub and Zenodo APIs, the published LinkedIn article URL, the current Google Docs outreach draft, and the current local project folders. It does not assert that any unverified claim in a local deliverable is current.

No public post, email, submission, push, Google Doc, NotebookLM notebook, brand original, or existing project document was modified during this audit.

## Authoritative public facts

| Fact | Verified value | Source of truth | Required treatment |
|---|---|---|---|
| GitHub repository | https://github.com/Procyk-consultant/ai-idp | GitHub public API, 2026-08-09 | Use as the public code and specification link. |
| GitHub public branch | `main`, public head `6a1007b` | GitHub public API, 2026-08-09 | Do not describe local unpushed work as public. |
| Zenodo record | https://zenodo.org/records/21769036 | Zenodo public API, 2026-08-09 | Use as the citable public research archive. |
| DOI | https://doi.org/10.5281/zenodo.21769036 | Zenodo record `21769036` | Use in scholarly and policy material; do not substitute arXiv. |
| Zenodo publication | Title: *Identity Before Autonomy: A Universal Framework for Persistent AI Actor Identity, Permanent Traceability, Delegation, Quality Assurance, and Accountable AI Operation*; version `2.0.0`; publication date 2026-08-02 | Zenodo public API | State exactly; avoid unsupported descriptions of review or endorsement. |
| LinkedIn profile | https://www.linkedin.com/in/pierre-edward-procyk-223b75305 | Operator-supplied URL | Use only where a professional profile link is needed. |
| Published LinkedIn article | https://www.linkedin.com/pulse/lia-sans-identit%25C3%25A9-nest-pas-de-linnovation-cest-un-risque-procyk-bhz5c/ | Current Google Docs outreach draft; public LinkedIn page reachable 2026-08-09 | Record as the existing launch article; obtain platform analytics or the post permalink only if needed for reporting. |
| arXiv | Deferred; no identifier is assigned | Project direction and local records | Remove from current outreach links, attachments, and calls to action. |
| Rights | All Rights Reserved; no public licence granted | Repository `LICENSE` and `LICENSING_STATUS.md` | Never describe the code or reference implementation as open source. |

## Current-state conflicts requiring reconciliation

| Conflict | Evidence | Correct handling |
|---|---|---|
| Stale publication controls | The August 8 FINAL package still says DOI not assigned and external publication not performed. | Preserve FINAL as a dated derivative. Update the canonical control record only after review; do not retroactively rewrite historical snapshots. |
| Canonical current report is untracked | `PROJECT_REPORT_v2.0.0.md` records GitHub and Zenodo as complete but is not in the public branch. | Review its factual statements, then intentionally commit only approved verified content. |
| Local worktree is not a release candidate | Local `main` is one commit ahead; eight tracked modifications and fifteen untracked items exist. | Categorize every item as approved source, test, generated artifact, temporary automation, or excluded local material before any commit/push. |
| Remote configuration contains an authentication component | Read-only inspection confirms an authentication-bearing remote URL. Its age and validity were not tested. | On approval, change only the remote URL to a credential-free form and use a credential manager, GitHub CLI, or SSH for authentication. |
| Communication history is incomplete | Canonical project-control lacks an actual communications log and the published LinkedIn article URL is not recorded there. | Create an evidence-only communications log after approval; do not invent past sends, posts, or agent actions. |

## Current outreach-draft assessment

The live Google Doc, *Stratégies d'outreach pour la gouvernance de l'identité de l'IA*, was created and revised by Pierre-Edward Procyk on 2026-08-09. It contains a usable target list and the correct Zenodo, GitHub, LinkedIn profile, and LinkedIn article URLs. It is not ready to send.

### Preserve

- The core problem: operational AI needs attributable identity, authority chains, and traceability.
- AegisTrace as a functional research reference implementation and proof of concept.
- Zenodo as the citable research archive and GitHub as the public technical repository.
- A respectful, recipient-specific Canadian English or Québec French approach.
- A request for dialogue, technical review, or a short exploratory briefing rather than a demand for immediate adoption.

### Remove or qualify before any use

- Any description of AI-IDP, AegisTrace, or its L1 profile as "open source". The project is All Rights Reserved.
- The figures "70% to 90%" cost reduction and "less than 18 months" payback unless each message explicitly identifies them as model-based internal estimates and supplies the exact evidence basis. They should not appear in initial outreach.
- Statements that Canada is in a "complete regulatory vacuum", that a framework "ensures" Charter/PIPEDA/Law 25 compliance, or that it "proves" legal conclusions. Use proposed, designed to support, or warrants independent review.
- Unverified references to recent incidents, cyber-deception exploits, alignment-faking events, new guidance, policy announcements, or current officeholders.
- arXiv references, placeholders, and any claim that the paper is publicly available on arXiv.
- Overlong one-hour requests, sales framing, and invented operational details about a recipient's mandate.

### Recipient verification finding

The Québec cyber and digital portfolio is currently held by France-Élaine Duranceau, not Éric Caire. Every named recipient, office, and address must be checked against a primary official source on the day a message is prepared.

## Phased repair plan

### Phase 1 — Establish the canonical public-state record

1. Review this reconciliation with Pierre-Edward Procyk.
2. Define the canonical records that will carry live GitHub, Zenodo, LinkedIn, and arXiv-deferred facts.
3. Update those canonical records only; preserve dated FINAL, NotebookLM, forensic, audit, and handoff derivatives as historical evidence.
4. Add only evidenced historical actions to a communications log.

### Phase 2 — Complete GitHub safely

1. Classify the 23 worktree entries and identify the exact approved release set.
2. Re-run appropriate tests and artifact checks for that set.
3. Replace the remote URL with a credential-free URL after approval.
4. Present the exact commit, diff, and push target; obtain confirmation before pushing.

### Phase 3 — Rebuild the communications architecture

1. Replace the current broad target list with separate tracks: federal policy consultation, federal operational/government digital, Québec digital/cybersecurity, privacy, standards, academic review, and regional innovation.
2. Set one modest, recipient-appropriate ask per message: referral, written feedback, eligibility guidance, or a 20-minute introductory conversation.
3. Use one primary attachment and, at most, one supporting attachment. Link Zenodo and GitHub rather than attaching an entire corpus.
4. Verify recipient names, office mandates, addresses, and current legal references immediately before drafting each final message.

### Phase 4 — Draft, review, and send

1. Produce a clean master message library in Canadian English and Québec French, with source notes for every external claim.
2. Present each recipient-specific email, attachment set, and claim ledger to Pierre-Edward Procyk.
3. Obtain explicit confirmation before every send.
4. Record the actual recipient, date, subject, attachment set, and resulting message URL or sent-mail identifier after each action.

### Phase 5 — Maintain publication coherence

1. Update the LinkedIn campaign to point to Zenodo and GitHub, not arXiv.
2. Keep each social post distinct from government or academic correspondence.
3. Record only actual post URLs and real engagement; do not manufacture reach, replies, or outcomes.

## Next approval gate

Approval is needed to begin Phase 1 canonical-record reconciliation and Phase 3 master-message drafting. No external communication, publication, remote push, submission, or overwrite of the Google Doc is authorized by this record.
