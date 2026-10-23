# TaskFlow Infrastructure

Terraform for the TaskFlow multi-tenant SaaS platform. One root composition per
environment, driven by a tfvars file; all resources live in local modules.

Conventions here come from `.kiro/steering/infra-guidelines.md`. Architectural
decisions come from `.kiro/specs/301-terraform-foundation/design.md`
(DEC-101..103) and `.kiro/specs/101-authentication/design.md` (DEC-001..003).

## Directory structure

```
infra/
├── bootstrap/                  # State bucket + KMS key. Run once, local state.
└── terraform/
    ├── main.tf                 # Root composition — module blocks only
    ├── variables.tf            # Typed, described inputs
    ├── outputs.tf              # Values consumed by app config and other stacks
    ├── locals.tf               # name_prefix, common_tags
    ├── backend.tf              # S3 backend, native locking
    ├── versions.tf             # Version pins + provider config
    ├── .tflint.hcl             # Shared lint ruleset (root + modules)
    ├── environments/
    │   └── dev.tfvars          # Per-environment values
    └── modules/
        └── cognito/            # User pool, app client, hosted UI domain
```

Planned modules, each added by its own story: `vpc` (I2), `ecs` (I3),
`aurora` and `s3` (I4).

## Prerequisites

- Terraform >= 1.14 — native S3 state locking (DEC-101) requires it
- AWS credentials with permission to manage the resources in scope
- `tflint` and `pre-commit` for the local quality gates

## Usage

Bootstrap once per account, then initialize this configuration against the
bucket it created:

```bash
cd ../bootstrap && terraform init && terraform apply     # once per account
cd ../terraform
terraform init -backend-config="key=dev/terraform.tfstate"
```

Day to day:

```bash
terraform plan -var-file=environments/dev.tfvars -out=dev.plan
terraform apply dev.plan
terraform output
```

Adding a new environment means adding `environments/<env>.tfvars` and using a
distinct state key (`-backend-config="key=<env>/terraform.tfstate"`).

## Conventions

**Naming.** Every resource is `${var.name_prefix}-<resource-type>`, where
`name_prefix` is `<project>-<environment>` from `locals.tf` — for example
`taskflow-dev-users`. Modules never build the prefix themselves; they receive it.

**Tagging.** `local.common_tags` carries `Project`, `Environment`, and
`ManagedBy`, plus anything in `var.extra_tags`. Modules merge those with a
per-resource `Name` tag. Every taggable resource gets tags.

**Variables.** Type and description on all of them. Required variables have no
default. Optional variables have a sensible default. Use `validation` blocks
wherever the constraint is known.

**Outputs.** Description on all of them. Mark secrets `sensitive`.

**Secrets.** Never in `.tf` or `.tfvars`. Read them at apply time from Secrets
Manager or SSM through a data source.

**Multi-tenancy.** No tenant identifier is ever hardcoded. Per-tenant resources
use `for_each` over tenant configuration.

**Root composition.** `main.tf` declares module blocks only, no resources. That
keeps the blast radius of a change inside one module.

## Adding a module

1. Create `modules/<name>/` with `main.tf`, `variables.tf`, `outputs.tf`,
   `versions.tf`, and `README.md`. Nothing else is a module.
2. Put a header comment at the top of `main.tf` saying what the module is for
   and which story or decision record it implements.
3. Accept `name_prefix` and `tags` as inputs. Do not read `var.environment` for
   naming — it is already in the prefix. Reading it for behavior, such as
   enabling deletion protection only on `prod`, is fine.
4. Pin providers in `versions.tf`. Declare no `provider` block; the root
   configuration owns provider configuration.
5. Wire it into the root `main.tf`, passing `local.name_prefix` and
   `local.common_tags`.
6. Re-export anything other stacks need from the root `outputs.tf`, prefixed
   with the module name.
7. Document inputs and outputs as tables in the module README.
8. Run the gates below before opening a PR.

## Quality gates

Blocking in pre-commit and in CI:

```bash
terraform fmt -recursive
terraform init -backend=false && terraform validate
tflint --recursive --config "$(pwd)/.tflint.hcl"
```

`terraform validate` needs no credentials, which is why `-backend=false` is
used. `plan` is posted as a PR comment; `apply` runs on merge for dev and
requires manual approval for prod.
