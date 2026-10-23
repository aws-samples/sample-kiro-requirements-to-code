# Stories — REST API Ingestion (Feature 101)

## Conventions

- One file per story
- File name: `<ref>-<trackerId>-<slug>.md` — `pending` is the tracker ID placeholder until the story is synced to GitHub Issues, then the file is renamed with the issue number
- Ref prefix: `E` (for Event ingestion)
- States: `New | Active | Done | Closed | Removed` (front-matter `state`)
- Front-matter drives tracker sync; body splits at `## Acceptance Criteria` for field mapping

## Stories in This Feature

| Ref | Title | Sprint | Owner | Effort | Status |
|-----|-------|--------|-------|--------|--------|
| E1 | API Gateway + Ingestion Lambda | S1 | dana | 3 PD | Done |
| E4 | Terraform Ingestion Module | S1 | eric | 2 PD | Done |
| E2 | Schema Validation + DLQ | S2 | dana | 4 PD | New |
| E3 | Kinesis Persistence + Correlation | S2 | eric | 3 PD | New |

## Dependency Graph

```
E1 (Lambda handler)     E4 (Terraform module)     [deliberately parallel in S1]
        \                     /
         ├── E2 (Schema validation + DLQ)
         └── E3 (Kinesis persistence)
```

E1 and E4 have no story dependencies (`dependsOn: []`): E4 packages whatever is in
the source directories, so it plans and validates before E1's handler lands. E2 and
E3 both require E1 and E4.

## GitHub Issues Mapping (Lightweight Sync)

This example syncs to GitHub Issues rather than Azure DevOps — same story files,
lighter field mapping:

| Front-matter | GitHub Issues |
|--------------|---------------|
| `owner: dana` / `eric` | Assignee (`@dana` / `@eric` — replace with real handles) |
| `sprint: S1` / `S2` | Milestone `PI-1 Sprint 1` / `PI-1 Sprint 2` |
| `state: New` / `Active` | open (+ `in-progress` label when Active) |
| `state: Done` / `Closed` | closed |
| `effort`, `priority` | Labels `effort:3`, `priority:1` |

Example 1 (`example-1-saas-platform`) shows the full enterprise sync playbook; this
feature keeps the protocol identical and the mapping table smaller.
