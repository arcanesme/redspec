"""Tests for edge creation."""

import pytest
from drawpyo import File, Page
from drawpyo.diagram import Object

from redspec.exceptions import ConnectionTargetNotFoundError
from redspec.generator.edges import create_edges
from redspec.models.resource import ConnectionDef


def _make_page():
    file = File(file_name="test.drawio", file_path="/tmp")
    page = Page(file=file, name="Test")
    file.add_page(page)
    return page


def test_create_edges_basic():
    page = _make_page()
    obj_a = Object(value="A", page=page, width=64, height=64)
    obj_b = Object(value="B", page=page, width=64, height=64)

    connections = [ConnectionDef(**{"from": "A", "to": "B", "label": "link"})]
    name_map = {"A": obj_a, "B": obj_b}

    edges = create_edges(connections, name_map, page)
    assert len(edges) == 1
    assert edges[0].source == obj_a
    assert edges[0].target == obj_b


def test_create_edges_missing_source():
    page = _make_page()
    obj_b = Object(value="B", page=page, width=64, height=64)

    connections = [ConnectionDef(**{"from": "missing", "to": "B"})]
    name_map = {"B": obj_b}

    with pytest.raises(ConnectionTargetNotFoundError, match="from"):
        create_edges(connections, name_map, page)


def test_create_edges_missing_target():
    page = _make_page()
    obj_a = Object(value="A", page=page, width=64, height=64)

    connections = [ConnectionDef(**{"from": "A", "to": "missing"})]
    name_map = {"A": obj_a}

    with pytest.raises(ConnectionTargetNotFoundError, match="to"):
        create_edges(connections, name_map, page)


def test_create_edges_dashed_style():
    page = _make_page()
    obj_a = Object(value="A", page=page, width=64, height=64)
    obj_b = Object(value="B", page=page, width=64, height=64)

    connections = [ConnectionDef(**{"from": "A", "to": "B", "style": "dashed"})]
    name_map = {"A": obj_a, "B": obj_b}

    edges = create_edges(connections, name_map, page)
    assert len(edges) == 1


def test_create_edges_empty_connections():
    page = _make_page()
    edges = create_edges([], {}, page)
    assert edges == []
