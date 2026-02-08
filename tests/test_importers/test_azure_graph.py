"""Tests for Azure Resource Graph import (D2)."""

from unittest.mock import MagicMock, patch

from redspec.importers.azure_graph import _map_arm_type, import_from_resource_graph


class TestArmTypeMapping:
    def test_vm_mapping(self):
        assert _map_arm_type("Microsoft.Compute/virtualMachines") == "azure/vm"

    def test_app_service_mapping(self):
        assert _map_arm_type("Microsoft.Web/sites") == "azure/app-service"

    def test_sql_database_mapping(self):
        assert _map_arm_type("Microsoft.Sql/servers/databases") == "azure/sql-database"

    def test_storage_mapping(self):
        assert _map_arm_type("Microsoft.Storage/storageAccounts") == "azure/storage"

    def test_unknown_type_fallback(self):
        result = _map_arm_type("Microsoft.Custom/myResource")
        assert result == "azure/myresource"

    def test_case_insensitive(self):
        assert _map_arm_type("MICROSOFT.COMPUTE/VIRTUALMACHINES") == "azure/vm"


class TestImportFromResourceGraph:
    def test_groups_by_resource_group(self):
        mock_response = MagicMock()
        mock_response.data = [
            {"name": "vm1", "type": "Microsoft.Compute/virtualMachines", "resourceGroup": "rg-prod", "location": "eastus", "properties": {}},
            {"name": "db1", "type": "Microsoft.Sql/servers/databases", "resourceGroup": "rg-prod", "location": "eastus", "properties": {}},
            {"name": "vm2", "type": "Microsoft.Compute/virtualMachines", "resourceGroup": "rg-dev", "location": "westus", "properties": {}},
        ]

        with patch("redspec.importers.azure_graph.DefaultAzureCredential"), \
             patch("redspec.importers.azure_graph.ResourceGraphClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.resources.return_value = mock_response
            mock_client_cls.return_value = mock_client

            spec = import_from_resource_graph("sub-123")

        # Should have 2 resource groups
        assert len(spec.resources) == 2
        rg_names = {r.name for r in spec.resources}
        assert "rg-prod" in rg_names
        assert "rg-dev" in rg_names

        # rg-prod should have 2 children
        rg_prod = next(r for r in spec.resources if r.name == "rg-prod")
        assert len(rg_prod.children) == 2

    def test_resource_types_mapped(self):
        mock_response = MagicMock()
        mock_response.data = [
            {"name": "vm1", "type": "Microsoft.Compute/virtualMachines", "resourceGroup": "rg", "location": "eastus", "properties": {}},
        ]

        with patch("redspec.importers.azure_graph.DefaultAzureCredential"), \
             patch("redspec.importers.azure_graph.ResourceGraphClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.resources.return_value = mock_response
            mock_client_cls.return_value = mock_client

            spec = import_from_resource_graph("sub-123")

        child = spec.resources[0].children[0]
        assert child.type == "azure/vm"
        assert child.metadata["arm_type"] == "Microsoft.Compute/virtualMachines"
