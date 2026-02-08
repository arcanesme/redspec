"""Tests for node_mapper: resource type -> Diagrams node class."""

from diagrams.azure.compute import AppServices, KubernetesServices, VirtualMachine
from diagrams.azure.database import CosmosDb, SQLDatabases
from diagrams.azure.network import Firewall, VirtualNetworkGateways, VirtualNetworks
from diagrams.azure.security import KeyVaults
from diagrams.azure.integration import APIManagement
from diagrams.azure.storage import StorageAccounts

from redspec.generator.node_mapper import resolve_node_class


class TestResolveNodeClass:
    def test_direct_match(self):
        assert resolve_node_class("app-service") is AppServices

    def test_with_namespace_prefix(self):
        assert resolve_node_class("azure/app-service") is AppServices

    def test_case_insensitive(self):
        assert resolve_node_class("Azure/App-Service") is AppServices

    def test_vm_alias(self):
        assert resolve_node_class("vm") is VirtualMachine

    def test_aks_alias(self):
        assert resolve_node_class("aks") is KubernetesServices

    def test_sql_database(self):
        assert resolve_node_class("azure/sql-database") is SQLDatabases

    def test_cosmos(self):
        assert resolve_node_class("cosmos") is CosmosDb

    def test_storage(self):
        assert resolve_node_class("storage") is StorageAccounts

    def test_firewall(self):
        assert resolve_node_class("azure/firewall") is Firewall

    def test_key_vault(self):
        assert resolve_node_class("kv") is KeyVaults

    def test_apim(self):
        assert resolve_node_class("apim") is APIManagement

    def test_vpn_gateway(self):
        assert resolve_node_class("azure/vpn-gateway") is VirtualNetworkGateways

    def test_vnet(self):
        assert resolve_node_class("azure/vnet") is VirtualNetworks

    def test_unknown_returns_none(self):
        assert resolve_node_class("totally-unknown-xyz-123") is None

    def test_resource_group_returns_none(self):
        # Resource groups render as Clusters, not nodes
        assert resolve_node_class("azure/resource-group") is None

    def test_fuzzy_match(self):
        # "cosmos-db" contains "cosmos" which is in the map
        cls = resolve_node_class("azure/cosmos-db")
        assert cls is CosmosDb
