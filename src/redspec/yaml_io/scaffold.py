"""Generate starter YAML templates for architecture diagrams."""

_SCHEMA_COMMENT = "# yaml-language-server: $schema=https://redspec.dev/schemas/redspec-spec.json\n"

_TEMPLATES: dict[str, str] = {
    "azure": """\
diagram:
  name: My Azure Architecture
  layout: auto
  direction: TB
  theme: default

resources:
  - type: azure/resource-group
    name: rg-main
    children:
      - type: azure/vnet
        name: vnet-main
        children:
          - type: azure/subnet
            name: subnet-app
      - type: azure/app-service
        name: app-web
      - type: azure/sql-database
        name: sql-main

connections:
  - from: app-web
    to: sql-main
    label: reads/writes
    color: "#0078D4"
""",
    "m365": """\
diagram:
  name: Microsoft 365 Architecture
  layout: auto
  direction: TB
  theme: default

resources:
  - type: m365/chat
    name: teams-chat
  - type: m365/mail
    name: exchange-mail
  - type: m365/cloud
    name: onedrive-storage

connections:
  - from: teams-chat
    to: exchange-mail
    label: notifications
""",
    "dynamics365": """\
diagram:
  name: Dynamics 365 Architecture
  layout: auto
  direction: TB
  theme: default

resources:
  - type: dynamics365/sales
    name: crm-sales
  - type: dynamics365/customerservices
    name: support-portal
  - type: dynamics365/finance
    name: finance-system

connections:
  - from: support-portal
    to: crm-sales
    label: case escalation
""",
    "power-platform": """\
diagram:
  name: Power Platform Architecture
  layout: auto
  direction: TB
  theme: default

resources:
  - type: power-platform/powerapps
    name: field-app
  - type: power-platform/powerautomate
    name: approval-flow
  - type: power-platform/dataverse
    name: data-store

connections:
  - from: field-app
    to: approval-flow
    label: triggers
  - from: approval-flow
    to: data-store
    label: writes
""",
    "multi-cloud": """\
diagram:
  name: Enterprise Integration
  layout: auto
  direction: TB
  theme: default

resources:
  - type: azure/resource-group
    name: rg-backend
    children:
      - type: azure/app-service
        name: api-gateway
      - type: azure/sql-database
        name: main-db
  - type: m365/chat
    name: teams-collab
  - type: power-platform/powerapps
    name: field-app
  - type: dynamics365/sales
    name: crm

connections:
  - from: field-app
    to: api-gateway
    label: REST
  - from: crm
    to: api-gateway
    label: data sync
  - from: teams-collab
    to: api-gateway
    label: notifications
""",
    "aws": """\
diagram:
  name: My AWS Architecture
  layout: auto
  direction: TB
  theme: default

resources:
  - type: aws/vpc
    name: vpc-main
    children:
      - type: aws/ec2
        name: web-server
      - type: aws/rds
        name: database
  - type: aws/s3
    name: static-assets
  - type: aws/cloudfront
    name: cdn

connections:
  - from: cdn
    to: web-server
    label: origin
  - from: web-server
    to: database
    label: queries
  - from: cdn
    to: static-assets
    label: static content
""",
    "gcp": """\
diagram:
  name: My GCP Architecture
  layout: auto
  direction: TB
  theme: default

resources:
  - type: gcp/vpc
    name: vpc-main
    children:
      - type: gcp/compute-engine
        name: app-server
      - type: gcp/cloud-sql
        name: database
  - type: gcp/gcs
    name: storage-bucket
  - type: gcp/load-balancing
    name: load-balancer

connections:
  - from: load-balancer
    to: app-server
    label: traffic
  - from: app-server
    to: database
    label: queries
  - from: app-server
    to: storage-bucket
    label: files
""",
    "k8s": """\
diagram:
  name: Kubernetes Deployment
  layout: auto
  direction: TB
  theme: default

resources:
  - type: k8s/namespace
    name: production
    children:
      - type: k8s/deployment
        name: web-deploy
      - type: k8s/service
        name: web-svc
      - type: k8s/ingress
        name: web-ingress

connections:
  - from: web-ingress
    to: web-svc
    label: routes
  - from: web-svc
    to: web-deploy
    label: selects
""",
}


def generate_template(template_name: str = "azure", include_schema_header: bool = True) -> str:
    """Return a YAML template string for the given template variant.

    Args:
        template_name: One of "azure", "m365", "dynamics365",
                       "power-platform", "multi-cloud", "aws", "gcp", "k8s".
        include_schema_header: Whether to prepend the yaml-language-server
                               schema comment.

    Returns:
        A multi-line YAML string with an example architecture.
    """
    content = _TEMPLATES[template_name]
    if include_schema_header:
        return _SCHEMA_COMMENT + content
    return content
