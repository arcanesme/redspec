"""Tests for YAML parsing."""

import pytest

from redspec.exceptions import YAMLParseError
from redspec.yaml_io.parser import parse_yaml


def test_parse_minimal_yaml(minimal_yaml_path):
    spec = parse_yaml(minimal_yaml_path)
    assert spec.diagram.name == "Minimal Test"
    assert len(spec.resources) == 2
    assert len(spec.connections) == 1


def test_parse_nested_yaml(nested_yaml_path):
    spec = parse_yaml(nested_yaml_path)
    assert spec.diagram.name == "Nested Containers Test"
    assert len(spec.resources) == 1
    rg = spec.resources[0]
    assert rg.type == "azure/resource-group"
    assert len(rg.children) == 2
    vnet = rg.children[0]
    assert vnet.type == "azure/vnet"
    assert len(vnet.children) == 1


def test_parse_nonexistent_file(tmp_path):
    with pytest.raises(YAMLParseError, match="Cannot read file"):
        parse_yaml(tmp_path / "nonexistent.yaml")


def test_parse_invalid_yaml(tmp_path):
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text("{{{{not yaml", encoding="utf-8")
    with pytest.raises(YAMLParseError, match="Invalid YAML"):
        parse_yaml(bad_file)


def test_parse_non_mapping_yaml(tmp_path):
    bad_file = tmp_path / "list.yaml"
    bad_file.write_text("- item1\n- item2\n", encoding="utf-8")
    with pytest.raises(YAMLParseError, match="Expected a YAML mapping"):
        parse_yaml(bad_file)


def test_parse_invalid_schema(tmp_path):
    bad_file = tmp_path / "bad_schema.yaml"
    bad_file.write_text(
        "resources:\n  - name: missing-type\n", encoding="utf-8"
    )
    with pytest.raises(YAMLParseError, match="Validation error"):
        parse_yaml(bad_file)
