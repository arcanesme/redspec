"""Tests for include / composition support (B2)."""

import pytest

from redspec.exceptions import IncludeFileNotFoundError
from redspec.yaml_io.includes import resolve_includes


class TestResolveIncludes:
    def test_single_include_merges_resources(self, tmp_path):
        networking = tmp_path / "networking.yaml"
        networking.write_text(
            "resources:\n  - type: azure/vnet\n    name: vnet1\n",
            encoding="utf-8",
        )

        raw = {
            "includes": ["networking.yaml"],
            "resources": [{"type": "azure/vm", "name": "vm1"}],
        }
        result = resolve_includes(raw, tmp_path)
        assert len(result["resources"]) == 2
        names = [r["name"] for r in result["resources"]]
        assert "vm1" in names
        assert "vnet1" in names

    def test_multiple_includes(self, tmp_path):
        net = tmp_path / "net.yaml"
        net.write_text("resources:\n  - type: azure/vnet\n    name: vnet1\n", encoding="utf-8")

        compute = tmp_path / "compute.yaml"
        compute.write_text("resources:\n  - type: azure/vm\n    name: vm1\n", encoding="utf-8")

        raw = {"includes": ["net.yaml", "compute.yaml"], "resources": []}
        result = resolve_includes(raw, tmp_path)
        assert len(result["resources"]) == 2

    def test_nested_includes(self, tmp_path):
        inner = tmp_path / "inner.yaml"
        inner.write_text("resources:\n  - type: azure/vm\n    name: inner-vm\n", encoding="utf-8")

        outer = tmp_path / "outer.yaml"
        outer.write_text(
            "includes:\n  - inner.yaml\nresources:\n  - type: azure/vnet\n    name: outer-vnet\n",
            encoding="utf-8",
        )

        raw = {"includes": ["outer.yaml"], "resources": []}
        result = resolve_includes(raw, tmp_path)
        names = [r["name"] for r in result["resources"]]
        assert "inner-vm" in names
        assert "outer-vnet" in names

    def test_missing_include_raises(self, tmp_path):
        raw = {"includes": ["nonexistent.yaml"]}
        with pytest.raises(IncludeFileNotFoundError, match="nonexistent"):
            resolve_includes(raw, tmp_path)

    def test_circular_include_handled(self, tmp_path):
        a = tmp_path / "a.yaml"
        b = tmp_path / "b.yaml"
        a.write_text(
            "includes:\n  - b.yaml\nresources:\n  - type: azure/vm\n    name: a-vm\n",
            encoding="utf-8",
        )
        b.write_text(
            "includes:\n  - a.yaml\nresources:\n  - type: azure/vm\n    name: b-vm\n",
            encoding="utf-8",
        )

        raw = {"includes": ["a.yaml"], "resources": []}
        result = resolve_includes(raw, tmp_path)
        names = [r["name"] for r in result["resources"]]
        assert "a-vm" in names
        assert "b-vm" in names

    def test_connections_merged(self, tmp_path):
        include = tmp_path / "conns.yaml"
        include.write_text(
            "connections:\n  - from: a\n    to: b\n",
            encoding="utf-8",
        )

        raw = {"includes": ["conns.yaml"], "connections": [{"from": "c", "to": "d"}]}
        result = resolve_includes(raw, tmp_path)
        assert len(result["connections"]) == 2

    def test_no_includes_noop(self):
        raw = {"resources": [{"type": "azure/vm", "name": "vm1"}]}
        result = resolve_includes(raw, None)
        assert result == raw
