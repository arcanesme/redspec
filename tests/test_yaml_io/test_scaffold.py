"""Tests for YAML scaffold template generation."""

import yaml

from redspec.yaml_io.scaffold import generate_template


def test_template_is_valid_yaml():
    text = generate_template()
    data = yaml.safe_load(text)
    assert isinstance(data, dict)
    assert "resources" in data
    assert "connections" in data


def test_template_has_diagram_meta():
    text = generate_template()
    data = yaml.safe_load(text)
    assert "diagram" in data
    assert "name" in data["diagram"]


def test_template_has_resources():
    text = generate_template()
    data = yaml.safe_load(text)
    assert len(data["resources"]) > 0


def test_template_has_connections():
    text = generate_template()
    data = yaml.safe_load(text)
    assert len(data["connections"]) > 0
