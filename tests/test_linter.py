"""Tests for the linter (E1)."""

import pytest

from redspec.linter import lint
from redspec.models.diagram import DiagramSpec
from redspec.models.lint import LintConfig


class TestMaxNestingDepth:
    def test_shallow_ok(self):
        spec = DiagramSpec.model_validate({
            "resources": [{"type": "azure/vm", "name": "vm1"}],
        })
        warnings = lint(spec)
        assert not any(w.rule == "max_nesting_depth" for w in warnings)

    def test_deep_nesting_triggers(self):
        # Build 6-deep nesting (default max is 5)
        inner = {"type": "azure/vm", "name": "leaf"}
        for i in range(5):
            inner = {"type": "azure/resource-group", "name": f"level-{4 - i}", "children": [inner]}
        spec = DiagramSpec.model_validate({"resources": [inner]})
        warnings = lint(spec)
        depth_warnings = [w for w in warnings if w.rule == "max_nesting_depth"]
        assert len(depth_warnings) >= 1
        assert "leaf" in depth_warnings[0].resource_name

    def test_custom_max_depth(self):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/resource-group", "name": "rg", "children": [
                    {"type": "azure/vnet", "name": "vnet", "children": [
                        {"type": "azure/vm", "name": "vm1"},
                    ]},
                ]},
            ],
        })
        config = LintConfig(max_nesting_depth=2)
        warnings = lint(spec, config)
        depth_warnings = [w for w in warnings if w.rule == "max_nesting_depth"]
        assert len(depth_warnings) >= 1


class TestNamingPattern:
    def test_valid_names(self):
        spec = DiagramSpec.model_validate({
            "resources": [{"type": "azure/vm", "name": "web-app-01"}],
        })
        warnings = lint(spec)
        assert not any(w.rule == "naming_pattern" for w in warnings)

    def test_invalid_name_uppercase(self):
        spec = DiagramSpec.model_validate({
            "resources": [{"type": "azure/vm", "name": "WebApp"}],
        })
        warnings = lint(spec)
        name_warnings = [w for w in warnings if w.rule == "naming_pattern"]
        assert len(name_warnings) == 1
        assert "WebApp" in name_warnings[0].message

    def test_custom_pattern(self):
        spec = DiagramSpec.model_validate({
            "resources": [{"type": "azure/vm", "name": "WebApp"}],
        })
        config = LintConfig(naming_pattern=r"^[A-Z]")
        warnings = lint(spec, config)
        assert not any(w.rule == "naming_pattern" for w in warnings)


class TestOrphanResources:
    def test_connected_resources_ok(self):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [{"from": "a", "to": "b"}],
        })
        warnings = lint(spec)
        assert not any(w.rule == "orphan_resources" for w in warnings)

    def test_orphan_detected(self):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "connected"},
                {"type": "azure/vm", "name": "orphan"},
            ],
            "connections": [{"from": "connected", "to": "connected"}],
        })
        warnings = lint(spec)
        orphan_warnings = [w for w in warnings if w.rule == "orphan_resources"]
        assert len(orphan_warnings) == 1
        assert orphan_warnings[0].resource_name == "orphan"

    def test_disabled(self):
        spec = DiagramSpec.model_validate({
            "resources": [{"type": "azure/vm", "name": "orphan"}],
        })
        config = LintConfig(orphan_resources=False)
        warnings = lint(spec, config)
        assert not any(w.rule == "orphan_resources" for w in warnings)


class TestDuplicateConnections:
    def test_no_duplicates_ok(self):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [{"from": "a", "to": "b"}],
        })
        warnings = lint(spec)
        assert not any(w.rule == "duplicate_connections" for w in warnings)

    def test_duplicate_detected(self):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [
                {"from": "a", "to": "b"},
                {"from": "a", "to": "b"},
            ],
        })
        warnings = lint(spec)
        dup_warnings = [w for w in warnings if w.rule == "duplicate_connections"]
        assert len(dup_warnings) == 1

    def test_disabled(self):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [
                {"from": "a", "to": "b"},
                {"from": "a", "to": "b"},
            ],
        })
        config = LintConfig(duplicate_connections=False)
        warnings = lint(spec, config)
        assert not any(w.rule == "duplicate_connections" for w in warnings)
