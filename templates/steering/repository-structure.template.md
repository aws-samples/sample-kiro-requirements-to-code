---
inclusion: always
---

<!-- Context budget: keep this file under ~150 lines. It loads into EVERY conversation.
     Show the tree to one level of detail plus the boundary rules. Do not list every file. -->

# Repository Structure

## Layout

```
[REPO-NAME]/
├── .kiro/
│   ├── steering/            # Project rules Kiro loads (this file)
│   ├── specs/<feature>/     # requirements.md, design.md, tasks.md, stories/
│   ├── hooks/               # Automated quality gates
│   └── settings/mcp.json    # MCP server config
├── docs/
│   └── decisions/           # ADRs, one file per decision
├── infra/
│   └── terraform/           # modules/, environments/
├── src/
│   ├── [SHARED-MODULE]/     # [RESPONSIBILITY]
│   ├── [SERVICE-A]/         # [RESPONSIBILITY]
│   └── [SERVICE-B]/         # [RESPONSIBILITY]
├── tests/                   # unit/, integration/, e2e/
└── [CI-CONFIG-PATH]         # [CI-SYSTEM] pipeline definitions
```

## Where New Code Goes

| Adding | Location | Never |
|--------|----------|-------|
| Business rule | `src/[SERVICE]/services/` | Transport handlers |
| Cloud resource | `infra/terraform/modules/[MODULE]/` | Console or CLI by hand |
| Reusable helper | `src/[SHARED-MODULE]/` | Copied between services |
| Env-specific value | `infra/terraform/environments/[ENV].tfvars` | Hardcoded in module code |
| Architecture decision | `docs/decisions/[NNNN]-[SLUG].md` | Only in a PR comment |
| Generated artifact | `[BUILD-OUTPUT-DIR]` (gitignored) | Committed to the repo |

## Module Boundaries

- Dependency direction is one-way: `[TRANSPORT-DIR]` → `services` → `repositories`. A repository importing a service is a design error.
- `src/[SHARED-MODULE]/` imports nothing from services, so it stays deployable with any of them.
- Services never import each other. Cross-service calls go over [TRANSPORT-MECHANISM] against the published contract.
- Terraform modules take inputs and return outputs only. No cross-module `remote_state` reads, because that couples deploy order.

## Ownership

| Path | Owner |
|------|-------|
| `src/[SERVICE-A]/` | [TEAM-OR-ALIAS] |
| `infra/**` | [TEAM-OR-ALIAS] |
| `.kiro/steering/` | [TEAM-OR-ALIAS] |

Enforced in `[CODEOWNERS-PATH]`.

## Naming

- Spec folders: `[FEATURE-ID]-[FEATURE-SLUG]` (e.g. `101-authentication`), matching the tracker feature ID for traceability.
- Story files: `[REF]-[TRACKER-ID-OR-PENDING]-[SLUG].md` inside `.kiro/specs/<feature>/stories/`.
- Directories: [DIR-CASE-CONVENTION]. One concept per directory.
