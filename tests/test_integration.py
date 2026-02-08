"""End-to-end integration tests."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from redspec.exceptions import ConnectionTargetNotFoundError, DuplicateResourceNameError
from redspec.generator.pipeline import generate
from redspec.icons.registry import IconRegistry
from redspec.models.diagram import DiagramSpec
from redspec.yaml_io.parser import parse_yaml


def test_minimal_yaml_to_png(minimal_yaml_path, tmp_path):
    spec = parse_yaml(minimal_yaml_path)
    output = tmp_path / "minimal.png"

    result = generate(spec, str(output))

    assert result.exists()
    assert result.suffix == ".png"
    # PNG files start with the PNG magic bytes
    data = result.read_bytes()
    assert data[:4] == b"\x89PNG"


def test_nested_containers_to_png(nested_yaml_path, tmp_path):
    spec = parse_yaml(nested_yaml_path)
    output = tmp_path / "nested.png"

    result = generate(spec, str(output))

    assert result.exists()
    data = result.read_bytes()
    assert data[:4] == b"\x89PNG"


def test_svg_output(minimal_yaml_path, tmp_path):
    spec = parse_yaml(minimal_yaml_path)
    output = tmp_path / "minimal.svg"

    result = generate(spec, str(output), out_format="svg")

    assert result.exists()
    assert result.suffix == ".svg"
    content = result.read_text()
    assert "<svg" in content


def test_duplicate_names_rejected(tmp_path):
    spec = DiagramSpec.model_validate({
        "resources": [
            {"type": "azure/vm", "name": "same-name"},
            {"type": "azure/vm", "name": "same-name"},
        ]
    })
    output = tmp_path / "dup.png"

    with pytest.raises(DuplicateResourceNameError, match="same-name"):
        generate(spec, str(output))


def test_connections_reference_valid_names(tmp_path):
    spec = DiagramSpec.model_validate({
        "resources": [{"type": "azure/vm", "name": "vm1"}],
        "connections": [{"from": "vm1", "to": "nonexistent"}],
    })
    output = tmp_path / "bad_conn.png"

    with pytest.raises(ConnectionTargetNotFoundError):
        generate(spec, str(output))
