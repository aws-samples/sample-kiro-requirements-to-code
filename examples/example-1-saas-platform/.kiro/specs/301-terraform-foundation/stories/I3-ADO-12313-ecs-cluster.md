---
trackerId: ADO-12313
ref: I3
parent: 301
title: "ECS Fargate cluster — cluster, task execution role, ALB, service scaffolding"
state: New
sprint: S2
owner: alice
effort: 3
priority: 1
tags: [infra, terraform, ecs, PI1]
dependsOn: [I2]
lastSync: 2026-07-18T09:42:00Z
---

## Context

Third infrastructure story in Feature 301, covering requirement R3. Implements DEC-102 (ECS Fargate over EKS) by provisioning the container platform the FastAPI service runs on. Scheduled for Sprint 2 because it consumes the subnets and security groups from I2.

## Goal

As a platform engineer, I want an ECS Fargate cluster fronted by an ALB so that the API service can be deployed as a container without managing any EC2 capacity.

## Scope

- New Terraform module at `infra/terraform/modules/ecs/` following the module conventions (`main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, `README.md`)
- ECS cluster with Fargate and Fargate Spot capacity providers, Container Insights enabled
- Task execution role: ECR pull, CloudWatch Logs write, and `secretsmanager:GetSecretValue` scoped to explicit secret ARNs
- Task role, separate from the execution role, for application-level AWS permissions
- ECR repository with immutable tags and enhanced scanning
- Application Load Balancer in the public subnets, HTTPS listener terminating TLS 1.2+, HTTP listener redirecting to HTTPS
- Target group with health check on `/health/ready`, deregistration delay tuned for graceful SIGTERM handling
- ALB access logs delivered to S3
- Service scaffolding: parameterised `aws_ecs_service` and `aws_ecs_task_definition` with a placeholder container image, desired count, tasks spread across the 2 AZs from I2
- CloudWatch log group per service with retention
- Outputs: cluster name/ARN, service name, ALB DNS name and zone ID, target group ARN, ECR repository URL, task/execution role ARNs
- Wire the module into the root composition and `environments/dev.tfvars`

## Out of Scope

- The real application container image and its task definition revision — owned by the API deployment stories
- Service auto-scaling policies (added once the API has real load metrics)
- WAF rules in front of the ALB and CloudFront — both deferred to PI 2 per `work-item-map.yaml`
- Blue/green or canary deployment via CodeDeploy — rolling updates only in PI 1
- EKS migration, explicitly rejected in DEC-102
- Production tfvars and manual approval gate for prod apply

## Dependencies

- Requires: I2 (VPC module provides private subnets for tasks, public subnets for the ALB, and the ALB and ECS task security groups)
- Blocks: API service deployment stories in Epic 2, which need the cluster, ECR repository and target group

## Acceptance Criteria

- **Given** the module at `infra/terraform/modules/ecs/`, **When** I run `terraform validate` and `terraform plan -var-file=environments/dev.tfvars`, **Then** the plan succeeds and shows an ECS cluster, task definition, service, ALB, listeners, target group, ECR repository and IAM roles.
- **Given** the cluster configuration, **When** I inspect its capacity providers, **Then** `FARGATE` and `FARGATE_SPOT` are attached and no EC2 capacity provider or launch template exists.
- **Given** the ECS service, **When** I inspect its network configuration, **Then** tasks are placed in the private subnet IDs from I2 with `assign_public_ip = false` and the ECS task security group attached.
- **Given** `desired_count = 2`, **When** the service reaches a steady state, **Then** tasks are distributed across both availability zones.
- **Given** the task execution role, **When** I inspect its policy, **Then** ECR and CloudWatch Logs actions are scoped to explicit resource ARNs and no statement uses `Resource: "*"` other than `ecr:GetAuthorizationToken`, which has no resource-level permissions.
- **Given** the task role and the execution role, **When** I compare them, **Then** they are two distinct roles and the application's AWS permissions are attached only to the task role.
- **Given** the ALB HTTPS listener, **When** I inspect its SSL policy, **Then** it enforces TLS 1.2 or higher, and the HTTP listener returns a 301 redirect to HTTPS.
- **Given** the target group health check, **When** a task reports `/health/ready` as healthy, **Then** the ALB routes traffic to it; **When** the check fails twice, **Then** the task is deregistered.
- **Given** ALB access logging is enabled, **When** requests are served, **Then** access log objects appear in the configured S3 bucket prefix.
- **Given** the ECR repository, **When** I attempt to overwrite an existing tag, **Then** the push is rejected because tag immutability is enabled, and enhanced scanning reports findings for each pushed image.
- **Given** the module outputs, **When** consumed by the root composition, **Then** `cluster_name`, `cluster_arn`, `service_name`, `alb_dns_name`, `alb_zone_id`, `target_group_arn`, `ecr_repository_url`, `task_role_arn` and `task_execution_role_arn` are available.
- **Given** a change to the module, **When** pre-commit and CI run, **Then** `terraform fmt`, `terraform validate`, `tflint` and `checkov` all pass with no high-severity findings.
