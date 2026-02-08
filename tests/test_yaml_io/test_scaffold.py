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


def test_template_starts_with_schema_comment():
    text = generate_template()
    assert text.startswith("# yaml-language-server:")


def test_template_schema_opt_out():
    text = generate_template(include_schema_header=False)
    assert not text.startswith("# yaml-language-server:")


def test_aws_template_valid():
    text = generate_template("aws")
    data = yaml.safe_load(text)
    assert isinstance(data, dict)
    assert "resources" in data


def test_gcp_template_valid():
    text = generate_template("gcp")
    data = yaml.safe_load(text)
    assert isinstance(data, dict)


def test_k8s_template_valid():
    text = generate_template("k8s")
    data = yaml.safe_load(text)
    assert isinstance(data, dict)
