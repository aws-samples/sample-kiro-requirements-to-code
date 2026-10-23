---
trackerId: ADO-12312
ref: I2
parent: 301
title: "VPC networking — subnets, NAT, security groups, flow logs"
state: New
sprint: S1
owner: bob
effort: 3
priority: 1
tags: [infra, terraform, networking, PI1]
dependsOn: [I1]
lastSync: 2026-07-18T09:42:00Z
---

## Context

Second infrastructure story in Feature 301, covering requirement R2. Builds the network layer that ECS (I3) and Aurora (I4) are placed into. Nothing else in PI 1 can be deployed into AWS until private subnets exist.

## Goal

As a platform engineer, I want a reusable VPC module so that compute and data services land in private subnets with controlled egress and auditable network traffic.

## Scope

- New Terraform module at `infra/terraform/modules/vpc/` following the module conventions (`main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, `README.md`)
- VPC with a configurable CIDR block and DNS support/hostnames enabled
- Public and private subnets across 2 availability zones (4 subnets total), sized from the VPC CIDR
- Internet gateway for public subnet egress
- NAT gateways with Elastic IPs for private subnet egress — count driven by a `single_nat_gateway` variable (one for dev, one per AZ for prod)
- Route tables: one public route table, one private route table per AZ, with associations
- Baseline security groups: ALB (ingress 443 from the internet), ECS tasks (ingress from the ALB security group only), Aurora (ingress 5432 from the ECS task security group only)
- VPC flow logs delivered to a CloudWatch log group with retention and a scoped IAM role
- Outputs consumed by I3 and I4: `vpc_id`, subnet ID lists, security group IDs, CIDR block
- Wire the module into the root composition and `environments/dev.tfvars`

## Out of Scope

- VPC interface endpoints for S3, Secrets Manager, ECR and CloudWatch — deferred to the next PI per `work-item-map.yaml`
- Transit Gateway, VPC peering and any cross-account networking
- Network Firewall and WAF rules (PI 2)
- IPv6 addressing
- Production tfvars — dev only for now

## Dependencies

- Requires: I1 (Terraform foundation provides the root composition, remote state, and quality gates)
- Blocks: I3 (ECS cluster needs private subnets and the task security group), I4 (Aurora needs private subnets and the database security group)

## Acceptance Criteria

- **Given** the module at `infra/terraform/modules/vpc/`, **When** I run `terraform validate` and `terraform plan -var-file=environments/dev.tfvars`, **Then** the plan succeeds and shows a VPC, 2 public subnets, 2 private subnets, an internet gateway, NAT gateway(s), route tables and associations.
- **Given** the subnets are created, **When** I inspect their availability zones, **Then** the public and private subnets are spread across exactly 2 distinct AZs.
- **Given** `single_nat_gateway = true` in `dev.tfvars`, **When** the plan is generated, **Then** one NAT gateway and one Elastic IP are created and both private route tables point their default route at it.
- **Given** `single_nat_gateway = false`, **When** the plan is generated, **Then** one NAT gateway per AZ is created and each private route table routes through the NAT gateway in its own AZ.
- **Given** an instance in a private subnet, **When** it makes an outbound HTTPS call, **Then** traffic egresses via the NAT gateway and there is no route from the internet inbound.
- **Given** the baseline security groups, **When** I inspect their rules, **Then** the ALB group allows 443 from `0.0.0.0/0`, the ECS task group allows traffic only from the ALB group, and the Aurora group allows 5432 only from the ECS task group — no rule uses a wildcard source other than the ALB ingress.
- **Given** VPC flow logs are enabled, **When** traffic flows in the VPC, **Then** flow log records appear in the CloudWatch log group `/aws/vpc/taskflow-dev-flow-logs` and the delivery role grants only `logs:CreateLogStream` and `logs:PutLogEvents` on that log group.
- **Given** the module outputs, **When** consumed by the root composition, **Then** `vpc_id`, `vpc_cidr_block`, `public_subnet_ids`, `private_subnet_ids`, `alb_security_group_id`, `ecs_tasks_security_group_id` and `database_security_group_id` are available.
- **Given** every resource in the module, **When** I inspect its tags, **Then** `var.tags` is merged with a `Name` tag built from `var.name_prefix`.
- **Given** a change to the module, **When** pre-commit runs, **Then** `terraform fmt`, `terraform validate` and `tflint` all pass with no findings.
