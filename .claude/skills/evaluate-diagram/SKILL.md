---
context: fork
agent: diagram-evaluator
allowed-tools: Read, Glob, Grep
argument-hint: "<yaml-or-drawio-file>"
---

# evaluate-diagram

Review an Azure architecture diagram for completeness, security, reliability, and best practices.

## Workflow

1. Read the file specified in `$ARGUMENTS` (YAML spec or .drawio file)
2. If it's a YAML file, analyze the resource definitions and connections directly
3. If it's a .drawio file, parse the XML to extract resource names, types, and connections
4. Evaluate the architecture against the checklist below
5. Output a structured review with findings categorized by severity

## Evaluation Criteria

### 1. Completeness
- Missing common companion resources (e.g., VNet without NSG, App Service without App Service Plan)
- Resources that typically require supporting services (e.g., AKS without ACR, App Service without Key Vault for secrets)
- Missing monitoring/logging (no Log Analytics Workspace)
- Missing DNS or traffic management for public-facing services

### 2. Security
- Resources outside of VNet/Subnet that should have network isolation
- Missing Network Security Groups on subnets
- No private endpoints for PaaS services (SQL, Storage, Redis, Cosmos)
- Missing Key Vault for secret management
- Missing API Management or Application Gateway in front of APIs
- Direct public exposure of backend services

### 3. Reliability
- Single points of failure (single VM instead of scale set, single database without replication)
- No load balancer for multi-instance services
- Missing redundancy for critical components
- No Front Door or Traffic Manager for multi-region scenarios

### 4. Naming Conventions
- Inconsistent naming patterns (mixing camelCase and kebab-case)
- Missing standard prefixes (e.g., `rg-`, `vnet-`, `snet-`, `app-`, `sql-`, `kv-`, `st`)
- Names that don't indicate environment or purpose

### 5. Connections
- Orphaned resources with no connections to anything
- Missing obvious data flows (e.g., app service with database but no connection shown)
- Connections that bypass security boundaries

### 6. Structure
- Flat resources that should be nested in containers (e.g., services not inside a resource group)
- Resources that should be in a VNet/Subnet but aren't
- Overly deep nesting that reduces clarity

## Output Format

Structure the review as:

```
## Architecture Review: <diagram name>

### Summary
<1-2 sentence overall assessment>

### Findings

#### Critical
- [SECURITY] <finding> — <recommendation>
- [RELIABILITY] <finding> — <recommendation>

#### Important
- [COMPLETENESS] <finding> — <recommendation>
- [STRUCTURE] <finding> — <recommendation>

#### Suggestions
- [NAMING] <finding> — <recommendation>
- [CONNECTIONS] <finding> — <recommendation>

### Positive Observations
- <things done well>
```

## Azure Well-Architected Framework Reference

When evaluating, consider these pillars:
- **Security**: Defense in depth, network isolation, identity management, encryption
- **Reliability**: Redundancy, failover, health monitoring, disaster recovery
- **Cost Optimization**: Right-sizing, reserved instances, shared resources
- **Operational Excellence**: Monitoring, alerting, automation, IaC
- **Performance Efficiency**: Scaling, caching, CDN, async processing
