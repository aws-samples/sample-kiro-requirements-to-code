---
inclusion: always
---

# Technology Guidelines

## Mandated Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Cloud | AWS | [Why] |
| Language | [Language + version] | [Why] |
| Framework | [Framework] | [Why] |
| Database | [Database] | [Why] |
| IaC | Terraform >= [version] | [Why] |
| CI/CD | [CI system] | [Why] |
| Container/Compute | [ECS/EKS/Lambda/etc.] | [Why] |
| Auth | [Auth system] | [Why] |
| OS | Linux | [Mandatory for new components] |

## Constraints

- [Hard constraint 1]
- [Hard constraint 2]
- [Hard constraint 3]

## Compatibility Matrix

| Component | Current | Target | Flexibility |
|-----------|---------|--------|-------------|
| [Component 1] | [Current state] | [Target state] | High/Medium/Low |
| [Component 2] | [Current state] | [Target state] | High/Medium/Low |

## Security Baseline

- All secrets via [secret management approach]
- Encryption at rest: [approach]
- Encryption in transit: TLS 1.2+
- IAM: [approach to least privilege]
- Scanning: [tools and approach]
