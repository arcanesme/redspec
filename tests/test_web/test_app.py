"""Tests for the Redspec web API."""

import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
httpx = pytest.importorskip("httpx")
from starlette.testclient import TestClient  # noqa: E402

from redspec.web.app import create_app  # noqa: E402


@pytest.fixture
def app(tmp_path):
    return create_app(output_dir=tmp_path / "output")


@pytest.fixture
def client(app):
    return TestClient(app)


class TestPageRoutes:
    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Redspec" in resp.text


class TestTemplateAPI:
    def test_list_templates(self, client):
        resp = client.get("/api/templates")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert "azure" in data

    def test_get_azure_template(self, client):
        resp = client.get("/api/templates/azure")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "azure"
        assert "resources:" in data["content"]

    def test_get_unknown_template_404(self, client):
        resp = client.get("/api/templates/nonexistent")
        assert resp.status_code == 404


class TestValidateAPI:
    def test_valid_yaml(self, client):
        yaml_content = """
diagram:
  name: Test
resources:
  - type: azure/vm
    name: vm1
connections: []
"""
        resp = client.post("/api/validate", json={"yaml_content": yaml_content})
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is True
        assert data["name"] == "Test"
        assert data["resources"] == 1
        assert data["connections"] == 0

    def test_invalid_yaml(self, client):
        resp = client.post("/api/validate", json={"yaml_content": "{{not yaml"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is False

    def test_non_mapping_yaml(self, client):
        resp = client.post("/api/validate", json={"yaml_content": "- item1\n- item2"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is False


class TestGalleryAPI:
    def test_empty_gallery(self, client):
        resp = client.get("/api/gallery")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_populated_gallery(self, client, tmp_path):
        # Manually create a gallery entry
        output_dir = tmp_path / "output"
        slug_dir = output_dir / "test-diagram"
        slug_dir.mkdir(parents=True)
        (slug_dir / "diagram.png").write_bytes(b"fake png")
        (slug_dir / "spec.yaml").write_text("diagram:\n  name: Test")
        (slug_dir / "metadata.json").write_text(json.dumps({
            "name": "Test Diagram",
            "slug": "test-diagram",
            "format": "png",
            "timestamp": "2024-01-01T00:00:00+00:00",
        }))

        resp = client.get("/api/gallery")
        assert resp.status_code == 200
        entries = resp.json()
        assert len(entries) == 1
        assert entries[0]["name"] == "Test Diagram"

    def test_gallery_file_serving(self, client, tmp_path):
        output_dir = tmp_path / "output"
        slug_dir = output_dir / "test"
        slug_dir.mkdir(parents=True)
        (slug_dir / "diagram.png").write_bytes(b"fake png data")
        (slug_dir / "metadata.json").write_text(json.dumps({
            "name": "Test", "slug": "test", "format": "png",
            "timestamp": "2024-01-01T00:00:00+00:00",
        }))

        resp = client.get("/api/gallery/test/diagram.png")
        assert resp.status_code == 200

    def test_gallery_file_not_found(self, client):
        resp = client.get("/api/gallery/nonexistent/diagram.png")
        assert resp.status_code == 404

    def test_gallery_path_traversal_blocked(self, client, tmp_path):
        # Try to traverse out of the output directory
        resp = client.get("/api/gallery/../../../etc/passwd")
        assert resp.status_code in (403, 404)


class TestGenerateGlow:
    _YAML = "resources:\n  - type: azure/vm\n    name: vm1\nconnections: []\n"

    def test_glow_true_returns_200(self, client):
        resp = client.post("/api/generate", json={
            "yaml_content": self._YAML,
            "format": "svg",
            "theme": "dark",
            "glow": True,
        })
        assert resp.status_code == 200

    def test_glow_false_returns_200(self, client):
        resp = client.post("/api/generate", json={
            "yaml_content": self._YAML,
            "format": "svg",
            "theme": "dark",
            "glow": False,
        })
        assert resp.status_code == 200

    def test_glow_omitted_returns_200(self, client):
        """Backward compat: glow field absent → 200."""
        resp = client.post("/api/generate", json={
            "yaml_content": self._YAML,
            "format": "svg",
            "theme": "dark",
        })
        assert resp.status_code == 200
