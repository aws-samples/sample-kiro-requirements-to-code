#
# Root composition for TaskFlow (story I1).
#
# This file wires modules together and passes shared naming and tagging in from
# locals.tf. It declares no resources directly — everything belongs to a module
# under modules/.
#
# Module inventory and sequencing: .kiro/specs/301-terraform-foundation/design.md
#

# ---------------------------------------------------------------------------
# Authentication — Cognito user pool, app client, hosted UI domain (story A1)
# ---------------------------------------------------------------------------

module "cognito" {
  source = "./modules/cognito"

  name_prefix = local.name_prefix
  environment = var.environment

  callback_urls = var.callback_urls
  logout_urls   = var.logout_urls

  password_min_length = var.password_min_length

  tags = local.common_tags
}

# ---------------------------------------------------------------------------
# Remaining PI 1 modules, added by their own stories:
#
#   module "vpc"    — I2, Sprint 1: VPC, subnets, NAT, flow logs
#   module "ecs"    — I3, Sprint 2: Fargate cluster, task execution role (DEC-102)
#   module "aurora" — I4, Sprint 2: Aurora Serverless v2 (DEC-103)
#   module "s3"     — I4, Sprint 2: attachment buckets + KMS
#
# Each follows the same pattern: name_prefix from locals, tags from
# local.common_tags, no hardcoded region or account IDs.
# ---------------------------------------------------------------------------
