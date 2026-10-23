---
inclusion: always
---

<!-- Context budget: keep this file under ~150 lines. It loads into EVERY conversation.
     Keep it to blocking rules. Scanner tuning and incident runbooks belong in a manual file. -->

# Security Guidelines

These rules are blocking. If a story cannot meet one, raise it in design review and record an ADR — do not route around it in code.

## Secrets

- Secrets live in [SECRET-STORE] and are resolved at runtime by ARN or path. Rotation then needs no redeploy.
- Application config holds a *reference*, never a value: inject `[SECRET-REF-ENV-VAR]` (e.g. `APP_DB_SECRET_ARN`) and fetch at startup.
- Never commit a populated `.env`, `*.tfvars` with credentials, or a key file. `.env.example` carries key names with empty values only.
- The `secret-guard` hook in `.kiro/hooks/` blocks writes containing credential-shaped strings. If it fires, rotate the credential first and assume exposure.

## Identity and Access

- IAM policies name explicit actions and explicit resource ARNs. `Action: "*"` or `Resource: "*"` fails review, because a compromised [WORKLOAD-UNIT] must not be able to reach data it does not own.
- One role per [WORKLOAD-UNIT]. No shared roles across services, so blast radius stays local.
- Human access to [PROD-ENV-NAME] goes through [ACCESS-MECHANISM] with MFA and a time limit. No long-lived access keys for people.
- [TENANT-OR-SCOPE] isolation is enforced at [ENFORCEMENT-POINT] from the verified token claim, never from a caller-supplied identifier.

## Data Protection

| Concern | Rule |
|---------|------|
| At rest | Customer-managed KMS key `[CMK-ALIAS]` on [WHICH-STORES]. AWS-managed keys only for [APPROVED-EXCEPTIONS]. |
| In transit | TLS 1.2+ everywhere, internal hops included. |
| Backups | [RETENTION-PERIOD] retention, encrypted, restore tested [TEST-CADENCE]. |
| Residency | [SENSITIVE-DATA-CLASS] stays within [REGION-OR-BOUNDARY] for [COMPLIANCE-DRIVER]. |

## Input Validation

- Validate at every trust boundary ([BOUNDARY-LIST]) against a declared schema with [VALIDATION-LIBRARY]. Reject unknown fields rather than ignoring them.
- Parameterised queries only. Any string-concatenated query is a review blocker.
- Bound request body size and page size at [MAX-PAGE-SIZE] so one caller cannot exhaust [SHARED-RESOURCE].
- Encode output for its destination ([OUTPUT-SINKS]). Treat every stored value as untrusted on read.

## Logging

- No [SENSITIVE-DATA-CLASS], credentials, bearer values, or full request bodies in logs. Log identifiers such as [SAFE-ID-EXAMPLES] instead.
- Redaction happens in the shared logger in `src/[SHARED-MODULE]/`, not at call sites, because call-site discipline does not survive refactors.
- Audit [AUDITED-EVENTS] with actor, action, resource, and timestamp. Retain [AUDIT-RETENTION] for [COMPLIANCE-DRIVER].

## Dependencies

- Pin exact versions and commit `[LOCKFILE-NAME]`. Terraform providers pinned as `aws ~> [PROVIDER-VERSION]` in `versions.tf`.
- `[SCA-SCANNER]` runs in CI; findings at [SEVERITY-THRESHOLD] or above block merge.
- A new direct dependency needs a named owner and a license check against [ALLOWED-LICENSES].
