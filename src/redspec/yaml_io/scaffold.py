"""Generate starter YAML templates for architecture diagrams."""


_TEMPLATES: dict[str, str] = {
    "azure": """\
diagram:
  name: My Azure Architecture
  layout: auto

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
""",
    "m365": """\
diagram:
  name: Microsoft 365 Architecture
  layout: auto

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
}


def generate_template(template_name: str = "azure") -> str:
    """Return a YAML template string for the given template variant.

    Args:
        template_name: One of "azure", "m365", "dynamics365",
                       "power-platform", "multi-cloud".

    Returns:
        A multi-line YAML string with an example architecture.
    """
    return _TEMPLATES[template_name]
