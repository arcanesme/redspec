---
context: fork
agent: diagram-generator
allowed-tools: Read, Write, Bash, Glob, Grep
argument-hint: "<architecture description>"
---

# generate-diagram

Generate an Azure architecture diagram from a natural-language description.

## Workflow

1. Parse the user's architecture description from `$ARGUMENTS`
2. Write a valid redspec YAML spec based on the description
3. Save the YAML file to disk (use a descriptive filename based on the description, e.g., `three-tier-web-app.yaml`)
4. Run `redspec generate <yaml_file>` to produce the `.drawio` file
5. Report both output file paths to the user

## YAML Schema Reference

The YAML file has three top-level sections:

```yaml
diagram:
  name: "<Diagram Title>"
  layout: auto

resources:
  - type: azure/<resource-type>
    name: <unique-name>
    children:          # only for container types
      - type: azure/<resource-type>
        name: <unique-name>

connections:
  - from: <source-name>
    to: <target-name>
    label: <optional-label>
    style: dashed      # optional
```

## Supported Azure Resource Types

### Container types (can have `children`):
- `azure/resource-group` — gray dashed box
- `azure/vnet` or `azure/virtual-network` — blue box
- `azure/subnet` — purple box
- `azure/subscription` — yellow box

### Leaf resource aliases:
| Alias | Resolves to |
|-------|-------------|
| `azure/vm` | virtual-machines |
| `azure/aks` | kubernetes-services |
| `azure/sql-database` | sql-database |
| `azure/app-service` | app-services |
| `azure/nsg` | network-security-groups |
| `azure/lb` | load-balancers |
| `azure/agw` | application-gateways |
| `azure/func` | function-apps |
| `azure/kv` | key-vaults |
| `azure/acr` | container-registries |
| `azure/apim` | api-management-services |
| `azure/storage` | storage-accounts |
| `azure/cosmos` | azure-cosmos-db |
| `azure/redis` | cache-redis |
| `azure/frontdoor` | front-doors |
| `azure/law` | log-analytics-workspaces |
| `azure/adf` | data-factory |

You can also use any full Azure icon name (e.g., `azure/application-gateways`).

## Rules

- Every resource `name` must be unique across the entire spec (including nested children)
- Use `azure/` prefix for all resource types
- Container types can nest other containers (e.g., resource-group > vnet > subnet > app-service)
- Connections reference resources by `name` — they work across any nesting level
- Group related resources logically in resource groups and VNets
- Add meaningful connection labels describing the data flow

## CLI Command

```bash
redspec generate <yaml_file> -o <output.drawio>
```

If `-o` is omitted, output defaults to the same filename with `.drawio` extension.
