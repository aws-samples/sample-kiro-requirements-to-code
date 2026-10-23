---
inclusion: always
---

# [YOUR PRODUCT NAME] — Product Overview

## Vision

[One paragraph: what your product does, who it serves, and what makes it valuable]

## Architecture Layers

1. **Infrastructure** — [Cloud services and platform foundation]
2. **Platform Services** — [Cross-cutting: auth, observability, secrets]
3. **Domain Services** — [Business logic and APIs]
4. **Application Layer** — [User-facing applications and integrations]

## Epics

| Epic | Description | PI |
|------|-------------|-----|
| 1. [Epic Name] | [Brief description] | PI [N] |
| 2. [Epic Name] | [Brief description] | PI [N] |
| 3. [Epic Name] | [Brief description] | PI [N] |

## Key Terminology

| Term | Definition |
|------|-----------|
| [Term 1] | [What it means in this project] |
| [Term 2] | [What it means in this project] |
| [Term 3] | [What it means in this project] |

## Non-Functional Requirements (Key)

- **Security:** [Key security requirement]
- **Scalability:** [Key scalability target]
- **Availability:** [SLA target]
- **Compliance:** [Regulatory framework if applicable]

## Multi-Tenancy Model (if applicable)

- **Data isolation:** [Strategy: schema-per-tenant, RLS, database-per-tenant]
- **Request context:** [How tenant is identified: JWT, header, subdomain]
- **Resource isolation:** [S3 prefix, IAM boundary, etc.]
