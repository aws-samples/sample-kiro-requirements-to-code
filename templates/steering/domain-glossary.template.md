---
inclusion: always
---

<!-- Context budget: keep this file under ~150 lines. It loads into EVERY conversation.
     Include terms that appear in code or specs. Drop anything nobody has to look up. -->

# Domain Glossary

One name per concept, used identically in specs, code, database columns, and API fields. Ambiguous vocabulary is the cheapest way to get inconsistent code: if "account" means a billing entity in one story and a login in another, Kiro will model both and neither will be right. Fix the word here first, then implement.

## Terms

| Term | Definition | Notes |
|------|-----------|-------|
| [TERM] | [ONE-SENTENCE-DEFINITION] | Code: `[IDENTIFIER]`. [SCOPE-OR-CAVEAT] |
| [TERM] | [ONE-SENTENCE-DEFINITION] | Owned by [SERVICE-OR-TEAM] |
| [TERM] | [ONE-SENTENCE-DEFINITION] | Not the same as [SIMILAR-TERM] |
| [TERM] | [ONE-SENTENCE-DEFINITION] | Persisted in `[TABLE-OR-STORE]` |
| [TERM] | [ONE-SENTENCE-DEFINITION] | External name in [EXTERNAL-SYSTEM] is [EXTERNAL-TERM] |

## Banned and Preferred

Use the preferred term everywhere, including variable names and commit messages.

| Do not use | Use instead | Why |
|-----------|-------------|-----|
| [AMBIGUOUS-TERM] | [PREFERRED-TERM] | [WHAT-IT-GETS-CONFUSED-WITH] |
| [LEGACY-TERM] | [PREFERRED-TERM] | Renamed in [ADR-REFERENCE]; legacy name survives only in [LEGACY-SURFACE] |
| [VENDOR-TERM] | [PREFERRED-TERM] | Vendor wording leaks an implementation detail into the domain |

## Identifiers

| Identifier | Format | Example | Stability |
|-----------|--------|---------|-----------|
| [ENTITY]Id | [FORMAT] | `[EXAMPLE-VALUE]` | Immutable |
| [ENTITY]Id | [FORMAT] | `[EXAMPLE-VALUE]` | [STABILITY-RULE] |

Identifiers are opaque to clients. Never parse meaning out of one, because [FORMAT-CHANGE-RISK].

## Status Values

Enumerations belong here so the same set is used in code, API, and tracker.

| Enum | Allowed values | Transitions |
|------|---------------|-------------|
| [ENUM-NAME] | [VALUE-1], [VALUE-2], [VALUE-3] | [ALLOWED-TRANSITIONS] |

## Maintenance

Add a term the first time it causes a clarifying question. Review at each [REVIEW-BOUNDARY]. When a term changes meaning, update this file in the same PR as the code — a stale glossary is worse than none, since it is trusted by default.
