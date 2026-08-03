---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: brand/DOCUMENT_IDENTITY_RULES.md
Title: Document Identity Rules
Version: 2.0.0
Last Material Revision: 2026-08-01
---

# Document Identity Rules

This file defines how every authored file in the AI-IDP / AegisTrace project carries its identity metadata.

## Format-Appropriate Header

Every original authored file must begin with a format-appropriate metadata header containing the required fields defined in Master Prompt §K.

### Markdown header (YAML front matter)

```
---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Contact: p.procyk.media@gmail.com
Secondary Contact: p.1o9.cognitive@outlook.com
Telephone: 
Location: Saguenay, Québec, Canada
File: <repository-relative path>
Title: <artifact title>
Purpose: <precise responsibility of the file>
Audience: <intended reader or operator>
Document Classification: Public | Internal | Confidential | Restricted | Research | Draft | Submission-ready
Classification: Domain | Application | Policy | Adapter | Infrastructure | Test | Research | Documentation | Legal | Administrative | Scientific | Impact | Release
Version: <semantic version>
Status: Draft | In research | Implemented | Validated | Submission-ready | Released
Last Material Revision: <ISO 8601 date>
Dependencies: <direct sources, modules, or artifacts>
Source Basis: <verified sources, project specifications, executed data, or approved author instructions>
Invariants: <conditions that must remain true>
Failure Behaviour: <expected behaviour when requirements are not met>
Trace Policy: <applicable AegisTrace record requirements>
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
---
```

### Python header (module docstring)

```python
"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: <repository-relative path>
Purpose: <precise responsibility of the file>
Classification: <domain | application | policy | adapter | infrastructure | test>
Security Classification: <public | internal | confidential | restricted>
Version: <semantic version>
Last Material Revision: <ISO 8601 date>
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
```

### LaTeX header (comment block)

```latex
% Cognitive Industries — Les Industries Cognitives
% Project: AI-IDP / AegisTrace
% Author and Intellectual Property Owner: Pierre-Edward Procyk
% Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
% File: <repository-relative path>
% Purpose: <precise responsibility of the file>
% Version: <semantic version>
% Last Material Revision: <ISO 8601 date>
% Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
```

### JSON header ($schema + _metadata)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "_metadata": {
    "organization": "Cognitive Industries — Les Industries Cognitives",
    "project": "AI-IDP / AegisTrace",
    "author": "Pierre-Edward Procyk",
    "copyright": "© 2026 Pierre-Edward Procyk. All rights reserved.",
    "file": "<repository-relative path>",
    "version": "<semantic version>",
    "last_material_revision": "<ISO 8601 date>",
    "licence_status": "No licence selected unless approved in writing by Pierre-Edward Procyk."
  },
  ...
}
```

## Third-Party File Rule

Do not add headers to third-party source files where doing so would violate their licence, integrity, or provenance. Preserve third-party notices in `NOTICE.md`.

## Front Matter per Document Type

### Government / Policy PDFs
1. Branded cover
2. Full title
3. Subtitle
4. `Pierre-Edward Procyk`
5. `Founder / CEO`
6. `Cognitive Industries — Les Industries Cognitives`
7. `Saguenay, Québec, Canada`
8. Version
9. Publication or preparation date
10. Document classification
11. Copyright notice
12. Contact block
13. Document-control table
14. Executive summary
15. Table of contents
16. List of figures
17. List of tables
18. Acronym list where required

### University report PDF
1. Neutral academic cover
2. Title
3. `Pierre-Edward Procyk`
4. `Cognitive Industries — Les Industries Cognitives`
5. `Saguenay, Québec, Canada`
6. No invented university information
7. Version and date
8. Abstract
9. Keywords
10. Table of contents
11. List of figures
12. List of tables
13. Research-integrity declaration
14. AI-assistance disclosure

### Technical specification PDF
1. Controlled-document cover
2. Specification title
3. Specification identifier
4. Version
5. Status
6. Editor or author
7. Organization
8. Copyright
9. Contact
10. Normative-language statement
11. Conformance statement
12. Revision history
13. Table of contents

### arXiv paper title page
1. Academic title
2. `Pierre-Edward Procyk`
3. `Cognitive Industries — Les Industries Cognitives`
4. `Saguenay, Québec, Canada`
5. Correspondence email where appropriate
6. Abstract
7. Keywords
8. Restrained branding only
9. No promotional cover
10. No invented academic affiliation
