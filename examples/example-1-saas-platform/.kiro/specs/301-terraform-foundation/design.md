# Design — Terraform Foundation (Feature 301)

## Summary

PI 1 infrastructure delivers a production-ready AWS environment: VPC, ECS, Aurora, S3, with pre-commit quality gates. The CI/CD pipeline that manages it is Feature 302. Multi-region and advanced networking features are deferred.

## Architectural Decisions

### DEC-101 — S3 + Native Locking for Terraform State

- **Context:** Need reliable remote state that supports team collaboration.
- **Decision:** S3 backend with `use_lockfile = true` (Terraform 1.14+ native locking). No DynamoDB lock table.
- **Alternatives considered:**
  - S3 + DynamoDB — legacy approach, extra resource to manage
  - Terraform Cloud — additional cost, vendor dependency
  - Local state — not viable for team collaboration
- **Consequences:** Simpler infrastructure (no DynamoDB table). Requires Terraform 1.14+.
- **Rollback path:** Add DynamoDB table if native locking proves unreliable.

### DEC-102 — ECS Fargate over EKS

- **Context:** Need container orchestration for Python API services.
- **Decision:** ECS Fargate — serverless containers, no node management.
- **Alternatives considered:**
  - EKS — more powerful but significant operational overhead for 2-person team
  - Lambda — cold starts problematic for API latency requirements
  - App Runner — limited networking and VPC integration options
- **Consequences:** Less flexibility than EKS (no DaemonSets, limited service mesh). Acceptable for API workload.
- **Rollback path:** Migrate to EKS when team grows or needs exceed Fargate capabilities.

### DEC-103 — Aurora Serverless v2

- **Context:** Need PostgreSQL with auto-scaling and multi-AZ without capacity planning.
- **Decision:** Aurora PostgreSQL Serverless v2 — scales from 0.5 ACU to 16 ACU.
- **Alternatives considered:**
  - Aurora Provisioned — requires capacity planning, over-provisions at low load
  - RDS PostgreSQL — no serverless option, manual failover
  - DynamoDB — schema-per-tenant model needs relational
- **Consequences:** Higher per-ACU cost but matches actual usage. Min 0.5 ACU cost even at idle.
- **Rollback path:** Switch to provisioned Aurora if cost pattern favors fixed capacity.

## Module Inventory

```
infra/
├── bootstrap/              # State bucket + KMS key (run once, local state)
└── terraform/
    ├── modules/
    │   ├── vpc/            # VPC, subnets, NAT, flow logs
    │   ├── ecs/            # ECS cluster, task execution role
    │   ├── aurora/         # Aurora Serverless v2 cluster
    │   ├── s3/             # Attachment buckets + KMS
    │   └── cognito/        # (from Feature 101)
    ├── environments/
    │   └── dev.tfvars
    ├── main.tf             # Root composition
    ├── variables.tf
    ├── outputs.tf
    ├── locals.tf
    ├── backend.tf
    └── versions.tf
```

## Sequencing

| Sprint | Stories | Rationale |
|--------|---------|-----------|
| S1 | I1 (Terraform foundation) | Must exist first |
| S1 | I2 (VPC) | Networking before compute |
| S2 | I3 (ECS) | Needs VPC subnets |
| S2 | I4 (Aurora + S3) | Needs VPC private subnets |

## Open Questions / Risks

1. **NAT Gateway cost** — Single NAT for dev, multi-AZ NAT for prod. Cost impact ~$32/month/AZ.
2. **Aurora min ACU** — 0.5 ACU minimum means ~$43/month even at zero load. Acceptable for dev.
3. **VPC Endpoints** — Deferred to the next PI (recorded in `work-item-map.yaml`). Until then, ECS tasks reach AWS APIs through the NAT gateway; revisit sooner if NAT data-processing charges grow. The `infra-guidelines.md` baseline names interface endpoints as the target state.
