# Workflow Templates

GitHub Actions workflows that enforce spec-driven development mechanically.

Spec discipline holds by hand for two developers reviewing each other's work.
It does not hold for twenty-five. The failure modes are boring and repeatable:
stories marked `Done` with no files behind them, work-item-map entries pointing
at stories nobody wrote, empty `dependsOn` fields contradicting the prose in
the same document. Every one of those is mechanically detectable — which is the
whole argument for these workflows. Prose conventions decay; a required check
does not.

Copy a template to `.github/workflows/`, drop the `.template` from the name,
and replace every `[PLACEHOLDER]`.

```bash
cp templates/workflows/spec-integrity.template.yml \
   .github/workflows/spec-integrity.yml
grep -n '\[PLACEHOLDER\]' .github/workflows/spec-integrity.yml
```

## The six workflows

| Workflow | Trigger | Enforces | Required check |
|---|---|---|---|
| `spec-integrity` | PR touching `.kiro/specs/**` or `.kiro/hooks/**`; push to `main` | `check-spec-integrity.py --strict` (E1–E8 errors, W1–W3 promoted to errors) and `check-hook-schema.py` | **Yes** |
| `work-item-link-check` | All PRs | PR names a story ref that resolves to a real story file, and carries that story's tracker ID | **Yes** |
| `code-quality` | PR touching source paths | ruff check, ruff format --check, mypy, pytest with a coverage floor | **Yes** |
| `terraform-plan` | PR touching `infra/**` | terraform fmt, validate, tflint, checkov (all blocking); plan posted as a PR comment | **Yes** |
| `terraform-apply` | Push to `main` touching `infra/**`; `workflow_dispatch` | dev auto-applies, prod waits on environment approval; serialised against state locks | No (post-merge deploy) |
| `pr-completeness-review` | PR on `story/*` branches | Nothing. Posts a completeness checklist derived from the story file | No (advisory) |

A required check is a two-part setting: the workflow reports a status, and
branch protection refuses the merge without it. Only the second part blocks
anything. Settings → Branches → add a rule for `main` → require status checks,
then select the check by **job name** (`spec-integrity`, `work-item-link-check`,
`python (3.12)`, `terraform-plan`). Renaming a job silently turns its gate into
a missing check rather than a failing one.

**The paths-filter trap.** Three of the four required-check candidates are
`paths:`-filtered (`spec-integrity` on `.kiro/**`, `code-quality` on source
paths, `terraform-plan` on `infra/**`). A required check that never runs stays
**Expected** forever — so requiring one of these as-is makes every PR that does
*not* touch those paths unmergeable. Only `work-item-link-check` runs on every
PR and is safe to require unmodified. For the other three, pick one of the two
standard fixes before flipping the branch-protection switch:

1. **No-op twin** — add a second workflow with the *same name and job name*,
   triggered on the inverse paths (`paths-ignore:` with the same list), whose
   only job succeeds immediately. GitHub treats matching job names as the same
   check, so one of the pair always reports.
2. **Drop the filter** — remove `paths:` and add a first step that detects
   whether relevant files changed (e.g. `dorny/paths-filter` or a `git diff
   --name-only` check) and short-circuits the job with success when none did.

The no-op twin costs one extra file per workflow and no run time; the
short-circuit keeps everything in one file at the cost of a checkout on every
PR. Either is fine — requiring a paths-filtered check without one of them is
not.

## Which to adopt first

**Start with `spec-integrity` alone.** It needs no secrets, no cloud account,
no repository variables, and no package installs — both checkers are
standard-library Python by design, so the CI gate runs the same code as the
local `PostFileSave` hook. It is also the workflow that catches the failures
that actually happen. Turn it on, fix what it finds, then make it required.

Copy both scripts from `templates/hooks/scripts/` into
`.kiro/hooks/scripts/` first. Repositories that already run the spec hook tend
to have `check-spec-integrity.py` and not `check-hook-schema.py`, and the
workflow's first step fails loudly rather than skipping the missing one.

Then, in order of payoff:

1. **`work-item-link-check`** — same zero-config story, and it closes the
   traceability hole that lets a merged PR belong to no story at all.
2. **`code-quality`** — needs a dev dependency group but no cloud access.
3. **`terraform-plan`** — first workflow that needs AWS. Do the OIDC setup
   below once and both Terraform workflows work.
4. **`terraform-apply`** — only after plan has been trustworthy for a while.
5. **`pr-completeness-review`** — advisory, so adopt it whenever. It is most
   useful once stories consistently carry implementation tasks.

Resist making everything required on day one. A repository with existing drift
will fail every check at once, and the reflex is to disable the checks rather
than fix the specs. Expect the first `--strict` run to fail: on this
repository's own `example-1-saas-platform`, `--strict` exits 1 today on three
W2 warnings (stories marked `Done` whose `trackerId` is still `pending`). That
is the check working.

## One-time OIDC setup

Only `terraform-plan` and `terraform-apply` need this. Neither ever uses a
long-lived IAM user key: those do not expire, every workflow in the repository
can read them, and they outlive whoever created them. GitHub's OIDC provider
issues a token per run, scoped to this repository, that expires with the job.

**1. Register GitHub as an OIDC identity provider in the AWS account** (once
per account). Provider URL `https://token.actions.githubusercontent.com`,
audience `sts.amazonaws.com`.

**2. Create two roles per environment** and scope the trust policy to this
repository. `111122223333` below is the AWS documentation placeholder account
ID — replace it.

- a **read-only plan role**, needing read access to the resources being planned
  plus read/write on the state object and its lock
- an **apply role** with the permissions the composition actually needs

Trust policy for the apply role, restricted to the `prod` environment so a
workflow running anywhere else cannot assume it:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::111122223333:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
        "token.actions.githubusercontent.com:sub": "repo:[PLACEHOLDER_ORG]/[PLACEHOLDER_REPO]:environment:prod"
      }
    }
  }]
}
```

The `sub` condition is the part that matters. A wildcard such as
`repo:org/*:*` hands every branch of every repository in the org the ability to
assume the role, including a branch someone pushes with a workflow of their
own. Scope it to an environment (`:environment:prod`) or a specific ref
(`:ref:refs/heads/main`), never to `*`. Do the same for the plan role, scoped
to `pull_request`.

**3. Create the GitHub Environments** `dev` and `prod` (Settings →
Environments). Add required reviewers to `prod`. This is the only thing making
prod applies manual — nothing in the workflow file enforces it, and nothing in
the workflow file can bypass it.

**4. Set the secrets and variables.**

| Scope | Name | Value |
|---|---|---|
| Repository secret | `AWS_PLAN_ROLE_ARN` | read-only plan role ARN |
| Environment secret (`dev`, `prod`) | `AWS_APPLY_ROLE_ARN` | apply role ARN for that environment |
| Repository variable | `AWS_REGION` | `[PLACEHOLDER]` |
| Repository variable | `TF_STATE_BUCKET` | remote state bucket |
| Repository variable | `TF_STATE_KEY` | state object key for plans, e.g. `dev/terraform.tfstate` (used by `terraform-plan`; `terraform-apply` derives `<env>/terraform.tfstate` itself — keep them consistent) |
| Repository variable | `TF_PLAN_ENVIRONMENT` | environment PRs plan against, e.g. `dev` |
| Repository variable | `TERRAFORM_VERSION` | must match `required_version` in `versions.tf` |
| Repository variable | `TFLINT_VERSION` | pin the linter, e.g. `v0.52.0` |

A role ARN is not really a secret, and repository variables work equally well;
storing it as a secret just keeps the account ID out of public run logs.

## Action pinning

Every `uses:` in these templates names a 40-character commit SHA, with the
release it resolves to as a trailing comment:

```yaml
- uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5.1.0
```

**Why.** A tag such as `v5` is a mutable pointer. Anyone who compromises the
action's repository or a maintainer account can repoint it at new code, and
every workflow that references `@v5` runs that code on its next trigger, with
the workflow's token and any OIDC role it can assume. This is how the
`tj-actions/changed-files` incident in March 2025 leaked CI secrets from
thousands of repositories. A commit SHA is content-addressed and cannot be
repointed; the worst an attacker can do is publish a new commit that nobody
references.

**Keeping pins fresh.** A SHA pin is only as good as the process that bumps
it. Dependabot reads the `# vX.Y.Z` comment, opens a PR when a newer release
exists, and rewrites both the SHA and the comment. Drop this into
`.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    groups:
      github-actions:
        patterns: ["*"]
```

Without Dependabot, `pinact run` (https://github.com/suzuki-shunsuke/pinact)
or `ratchet upgrade .github/workflows/*.yml`
(https://github.com/sethvargo/ratchet) rewrites the pins in place and is
suitable for a pre-commit hook or a scheduled job. Either tool also converts
any `@vN` reference a contributor adds back to a SHA.

The pins in this repository were resolved on the date of the commit that
introduced them; check the comment against the action's releases page before
copying a template that has sat unmodified for a long time.

## Conventions used throughout

**Actions are pinned to full commit SHAs** with the release as a trailing
comment (`actions/checkout@fbc6f399…6c09 # v5.1.0`), never `@main`, `@latest`
or a bare major tag. See [Action pinning](#action-pinning) below.

**`permissions:` is declared in every workflow** and starts at
`contents: read`. Scopes are added per job, only where used:
`pull-requests: write` to comment, `id-token: write` to mint the OIDC token.
An omitted `permissions:` block inherits the repository default, which may be
write-all.

**No secrets, account IDs, or regions are hardcoded.** Values come from
`${{ secrets.* }}`, `${{ vars.* }}`, or a literal `[PLACEHOLDER]`. Comments
that need an account ID use `111122223333`.

**PR-controlled text never reaches a script through `${{ }}`.** A PR title is
attacker-controlled — anyone who can open a PR sets it — and interpolating it
into a shell or Python body is script injection. The workflows pass it via
`env:` instead.

**Fork PRs are handled explicitly, not accidentally.** GitHub gives a forked
PR a read-only token and no OIDC token, so commenting and role assumption both
fail. The affected steps are guarded on
`github.event.pull_request.head.repo.full_name == github.repository` rather
than left to error. `spec-integrity`, `work-item-link-check` and
`code-quality` need neither, so they behave identically on forks.

## Relationship to the plan document

Section 7.4 of the reference plan lists these six as `spec-pr-review`,
`implementation-pr-review` and `kiro-completeness-check`. The names here differ
because the shape settled differently: `spec-integrity` replaces
`spec-pr-review` with a real script instead of a review prompt,
`pr-completeness-review` merges `implementation-pr-review` and
`kiro-completeness-check` (they were the same comment), and `code-quality`
covers the language gates that had no template at all.
