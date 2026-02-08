"""End-to-end integration tests."""

import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import MagicMock

from redspec.generator.pipeline import generate
from redspec.icons.embedder import embed_svg
from redspec.icons.registry import IconRegistry
from redspec.yaml_io.parser import parse_yaml


def _make_mock_registry(sample_svg: Path) -> IconRegistry:
    """Create a mock registry that returns sample_svg for any resolve call."""
    registry = MagicMock(spec=IconRegistry)
    registry.resolve.return_value = sample_svg
    return registry


def test_minimal_yaml_to_drawio(minimal_yaml_path, sample_svg, tmp_path):
    spec = parse_yaml(minimal_yaml_path)
    registry = _make_mock_registry(sample_svg)
    output = tmp_path / "minimal.drawio"

    result = generate(spec, str(output), icon_registry=registry, embedder_fn=embed_svg)

    assert result == output
    assert output.exists()

    # Parse XML and verify structure
    tree = ET.parse(output)
    root = tree.getroot()
    assert root.tag == "mxfile"

    diagrams = root.findall("diagram")
    assert len(diagrams) == 1

    model = diagrams[0].find("mxGraphModel")
    assert model is not None

    root_elem = model.find("root")
    assert root_elem is not None

    cells = root_elem.findall("mxCell")
    # At least: 2 default cells + 2 resource nodes + 1 edge = 5
    assert len(cells) >= 5


def test_nested_containers_to_drawio(nested_yaml_path, sample_svg, tmp_path):
    spec = parse_yaml(nested_yaml_path)
    registry = _make_mock_registry(sample_svg)
    output = tmp_path / "nested.drawio"

    result = generate(spec, str(output), icon_registry=registry, embedder_fn=embed_svg)

    assert output.exists()

    tree = ET.parse(output)
    root = tree.getroot()

    diagrams = root.findall("diagram")
    assert len(diagrams) == 1

    model = diagrams[0].find("mxGraphModel")
    root_elem = model.find("root")
    cells = root_elem.findall("mxCell")

    # Should have: 2 default + 3 containers (rg, vnet, subnet) + 2 nodes (app, db) + 1 edge = 8+
    assert len(cells) >= 8

    # Verify at least one cell has container style
    styles = [c.get("style", "") for c in cells]
    container_cells = [s for s in styles if "container=1" in s]
    assert len(container_cells) >= 1


def test_duplicate_names_rejected(sample_svg, tmp_path):
    import pytest
    from redspec.exceptions import DuplicateResourceNameError
    from redspec.models.diagram import DiagramSpec

    spec = DiagramSpec.model_validate({
        "resources": [
            {"type": "azure/vm", "name": "same-name"},
            {"type": "azure/vm", "name": "same-name"},
        ]
    })
    registry = _make_mock_registry(sample_svg)
    output = tmp_path / "dup.drawio"

    with pytest.raises(DuplicateResourceNameError, match="same-name"):
        generate(spec, str(output), icon_registry=registry, embedder_fn=embed_svg)


def test_connections_reference_valid_names(sample_svg, tmp_path):
    import pytest
    from redspec.exceptions import ConnectionTargetNotFoundError
    from redspec.models.diagram import DiagramSpec

    spec = DiagramSpec.model_validate({
        "resources": [{"type": "azure/vm", "name": "vm1"}],
        "connections": [{"from": "vm1", "to": "nonexistent"}],
    })
    registry = _make_mock_registry(sample_svg)
    output = tmp_path / "bad_conn.drawio"

    with pytest.raises(ConnectionTargetNotFoundError):
        generate(spec, str(output), icon_registry=registry, embedder_fn=embed_svg)
