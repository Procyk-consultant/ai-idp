---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Contact: p.procyk.media@gmail.com
File: project-control/MISSING_AUTHOR_DATA.md
Title: Missing Author Data Register
Purpose: Record fields that are genuinely absent so they are never fabricated
Version: 2.0.0
Status: Verified
Last Material Revision: 2026-08-01
---

# Missing Author Data Register

This file enumerates author/organization/contact fields that are **genuinely absent** from the verified data supplied by Pierre-Edward Procyk. These fields must be:

1. **Omitted** from public-facing drafts wherever possible.
2. **Never fabricated** with plausible substitutes.
3. **Never filled** with placeholder strings such as "TBD", "placeholder", "N/A", or invented values.

When a particular form requires one of these fields, the rendering agent must leave the field absent (not blank-as-string) and record the omission here.

## Missing Fields

| Field | Reason | Handling |
|------|--------|----------|
| Official website | Not supplied | Omit from all public-facing metadata |
| Street address | Not supplied | Use only "Saguenay, Québec, Canada" |
| Postal code | Not supplied | Omit |
| ORCID | Not supplied | Omit from arXiv metadata; do not generate |
| University affiliation | Not supplied | Use neutral academic format; do not invent institution |
| Faculty | Not supplied | Omit |
| Department | Not supplied | Omit |
| Government contact | Not supplied | Do not name any official; do not invent departmental contact |
| Academic degree | Not supplied | Omit |
| Professional licence | Not supplied | Omit |
| Fax number | Not supplied | Omit |
| Additional telephone numbers | Not supplied | Use only the single verified number |
| Additional email addresses | Not supplied | Use only the two verified emails |
| GitHub username | Not supplied | Repository references use the project path, not a personal handle |
| Legal company-registration number | Not supplied | Omit |
| Tax number | Not supplied | Omit |
| Project sponsor | Not supplied | Omit; do not invent endorsement |
| arXiv identifier | Not assigned (no external submission) | Omit; do not pre-fill |
| DOI | Not assigned | Omit; do not pre-fill |
| QR code | Not requested | Do not generate unless explicitly instructed |

## Handling Rule

If a future revision of the master prompt or a separate written instruction from Pierre-Edward Procyk supplies any of the above fields, this register MUST be updated synchronously with `VERIFIED_AUTHOR_DATA.md` and `VERIFIED_CONTACT_DATA.json`. The three files form a single source of truth and must never diverge.

## Authoritative Sources

- `project-control/VERIFIED_AUTHOR_DATA.md`
- `project-control/VERIFIED_CONTACT_DATA.json`
- This file (`project-control/MISSING_AUTHOR_DATA.md`)

If any artifact in the repository contains author/contact data that is not present in these three files, that artifact is defective and must be corrected.
