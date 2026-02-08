"""Import Azure architecture from Resource Graph."""

from __future__ import annotations

from typing import Any

from redspec.models.diagram import DiagramSpec
from redspec.models.resource import ConnectionDef, ResourceDef

# ARM resource type -> redspec type mapping
_ARM_TYPE_MAP: dict[str, str] = {
    "microsoft.compute/virtualmachines": "azure/vm",
    "microsoft.web/sites": "azure/app-service",
    "microsoft.sql/servers/databases": "azure/sql-database",
    "microsoft.sql/servers": "azure/sql-server",
    "microsoft.network/virtualnetworks": "azure/vnet",
    "microsoft.network/virtualnetworks/subnets": "azure/subnet",
    "microsoft.network/networkinterfaces": "azure/nic",
    "microsoft.network/publicipaddresses": "azure/public-ip",
    "microsoft.network/networksecuritygroups": "azure/nsg",
    "microsoft.network/loadbalancers": "azure/load-balancer",
    "microsoft.network/applicationgateways": "azure/application-gateway",
    "microsoft.network/azurefirewalls": "azure/firewall",
    "microsoft.network/privateendpoints": "azure/private-endpoint",
    "microsoft.storage/storageaccounts": "azure/storage",
    "microsoft.keyvault/vaults": "azure/key-vault",
    "microsoft.containerregistry/registries": "azure/container-registry",
    "microsoft.containerservice/managedclusters": "azure/aks",
    "microsoft.dbforpostgresql/servers": "azure/postgresql",
    "microsoft.dbformysql/servers": "azure/mysql",
    "microsoft.cache/redis": "azure/redis",
    "microsoft.documentdb/databaseaccounts": "azure/cosmos-db",
    "microsoft.eventhub/namespaces": "azure/event-hub",
    "microsoft.servicebus/namespaces": "azure/service-bus",
    "microsoft.logic/workflows": "azure/logic-apps",
    "microsoft.insights/components": "azure/application-insights",
    "microsoft.operationalinsights/workspaces": "azure/log-analytics",
}


def _map_arm_type(arm_type: str) -> str:
    """Map an ARM resource type to a redspec type."""
    return _ARM_TYPE_MAP.get(arm_type.lower(), f"azure/{arm_type.split('/')[-1].lower()}")


def _infer_connections(resources: list[dict[str, Any]]) -> list[ConnectionDef]:
    """Infer connections from known Azure patterns."""
    connections: list[ConnectionDef] = []
    resource_names = {r["name"] for r in resources}

    for r in resources:
        arm_type = r.get("type", "").lower()
        name = r["name"]
        properties = r.get("properties", {})

        # Private endpoint connections
        if arm_type == "microsoft.network/privateendpoints":
            target_id = properties.get("privateLinkServiceConnections", [{}])
            if isinstance(target_id, list):
                for plsc in target_id:
                    target = plsc.get("properties", {}).get("privateLinkServiceId", "")
                    target_name = target.split("/")[-1] if target else ""
                    if target_name in resource_names:
                        connections.append(ConnectionDef(source=name, to=target_name, label="private link"))

        # Subnet memberships via ipConfigurations
        if arm_type == "microsoft.network/networkinterfaces":
            ip_configs = properties.get("ipConfigurations", [])
            for ip_config in ip_configs:
                subnet_id = ip_config.get("properties", {}).get("subnet", {}).get("id", "")
                subnet_name = subnet_id.split("/")[-1] if subnet_id else ""
                if subnet_name in resource_names:
                    connections.append(ConnectionDef(source=name, to=subnet_name, label="attached"))

    return connections


def import_from_resource_graph(
    subscription_id: str,
    resource_group: str | None = None,
) -> DiagramSpec:
    """Query Azure Resource Graph and build a DiagramSpec.

    Requires azure-identity and azure-mgmt-resourcegraph.
    """
    try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.resourcegraph import ResourceGraphClient
        from azure.mgmt.resourcegraph.models import QueryRequest
    except ImportError:
        raise ImportError(
            "Azure dependencies required. Install with: pip install redspec[azure]"
        )

    credential = DefaultAzureCredential()
    client = ResourceGraphClient(credential)

    query = "Resources"
    if resource_group:
        query += f" | where resourceGroup =~ '{resource_group}'"

    request = QueryRequest(
        subscriptions=[subscription_id],
        query=query,
    )
    response = client.resources(request)

    # Group by resource group
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in response.data:
        rg = row.get("resourceGroup", "default")
        groups.setdefault(rg, []).append(row)

    resources: list[ResourceDef] = []
    all_raw: list[dict[str, Any]] = []

    for rg_name, rg_resources in groups.items():
        children: list[ResourceDef] = []
        for r in rg_resources:
            all_raw.append(r)
            redspec_type = _map_arm_type(r.get("type", ""))
            children.append(ResourceDef(
                type=redspec_type,
                name=r["name"],
                metadata={"arm_type": r.get("type", ""), "location": r.get("location", "")},
            ))

        resources.append(ResourceDef(
            type="azure/resource-group",
            name=rg_name,
            children=children,
        ))

    connections = _infer_connections(all_raw)

    return DiagramSpec(
        diagram={"name": f"Azure Subscription {subscription_id[:8]}..."},
        resources=resources,
        connections=connections,
    )
