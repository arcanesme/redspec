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


def _make_gallery_entry(output_dir, slug, name="Test", fmt="png", yaml_content=None):
    """Helper to create a fake gallery entry."""
    import datetime

    d = output_dir / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / f"diagram.{fmt}").write_bytes(b"\x00")
    yaml_text = yaml_content or (
        f"diagram:\n  name: {name}\n"
        "resources:\n  - type: azure/vm\n    name: vm1\nconnections: []\n"
    )
    (d / "spec.yaml").write_text(yaml_text, encoding="utf-8")
    (d / "metadata.json").write_text(json.dumps({
        "name": name, "slug": slug, "format": fmt,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }))
    return d


_VALID_YAML = """\
diagram:
  name: Test
resources:
  - type: azure/vm
    name: vm1
connections: []
"""


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
        resp = client.post("/api/validate", json={"yaml_content": _VALID_YAML})
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is True
        assert data["name"] == "Test"
        assert data["resources"] == 1
        assert data["connections"] == 0

    def test_invalid_yaml(self, client):
        resp = client.post("/api/validate", json={"yaml_content": "{{not yaml"})
        assert resp.status_code == 400

    def test_non_mapping_yaml(self, client):
        resp = client.post("/api/validate", json={"yaml_content": "- item1\n- item2"})
        assert resp.status_code == 400

    def test_validate_with_lint(self, client):
        yaml_with_orphan = (
            "diagram:\n  name: Test\n"
            "resources:\n  - type: azure/vm\n    name: orphan-vm\n"
            "connections: []\n"
        )
        resp = client.post("/api/validate", json={
            "yaml_content": yaml_with_orphan,
            "lint": True,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is True
        assert "lint_warnings" in data
        assert isinstance(data["lint_warnings"], list)

    def test_validate_without_lint(self, client):
        resp = client.post("/api/validate", json={
            "yaml_content": _VALID_YAML,
            "lint": False,
        })
        data = resp.json()
        assert "lint_warnings" not in data

    def test_validate_backward_compat_no_lint_field(self, client):
        """Old clients that don't send `lint` field still work."""
        resp = client.post("/api/validate", json={"yaml_content": _VALID_YAML})
        data = resp.json()
        assert data["valid"] is True
        assert "lint_warnings" not in data


class TestSchemaAPI:
    def test_get_schema(self, client):
        resp = client.get("/api/schema")
        assert resp.status_code == 200
        data = resp.json()
        assert "$schema" in data
        assert "title" in data


class TestGalleryAPI:
    def test_empty_gallery(self, client):
        resp = client.get("/api/gallery")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_populated_gallery(self, client, tmp_path):
        output_dir = tmp_path / "output"
        _make_gallery_entry(output_dir, "test-diagram", name="Test Diagram")

        resp = client.get("/api/gallery")
        assert resp.status_code == 200
        entries = resp.json()
        assert len(entries) == 1
        assert entries[0]["name"] == "Test Diagram"

    def test_gallery_file_serving(self, client, tmp_path):
        output_dir = tmp_path / "output"
        _make_gallery_entry(output_dir, "test")

        resp = client.get("/api/gallery/test/diagram.png")
        assert resp.status_code == 200

    def test_gallery_file_not_found(self, client):
        resp = client.get("/api/gallery/nonexistent/diagram.png")
        assert resp.status_code == 404

    def test_gallery_path_traversal_blocked(self, client, tmp_path):
        resp = client.get("/api/gallery/../../../etc/passwd")
        assert resp.status_code in (403, 404)


class TestGalleryDelete:
    def test_delete_existing(self, client, tmp_path):
        output_dir = tmp_path / "output"
        _make_gallery_entry(output_dir, "to-delete")

        resp = client.delete("/api/gallery/to-delete")
        assert resp.status_code == 200
        assert resp.json() == {"deleted": "to-delete"}
        assert not (output_dir / "to-delete").exists()

    def test_delete_nonexistent(self, client):
        resp = client.delete("/api/gallery/nope")
        assert resp.status_code == 404


class TestGalleryUpdate:
    def test_update_name(self, client, tmp_path):
        output_dir = tmp_path / "output"
        _make_gallery_entry(output_dir, "my-app", name="Old Name")

        resp = client.patch("/api/gallery/my-app", json={"name": "New Name"})
        assert resp.status_code == 200
        assert resp.json() == {"updated": "my-app"}

        meta = json.loads((output_dir / "my-app" / "metadata.json").read_text())
        assert meta["name"] == "New Name"

    def test_update_yaml_content(self, client, tmp_path):
        output_dir = tmp_path / "output"
        _make_gallery_entry(output_dir, "my-app")

        new_yaml = "diagram:\n  name: Updated\nresources: []\nconnections: []\n"
        resp = client.patch("/api/gallery/my-app", json={"yaml_content": new_yaml})
        assert resp.status_code == 200

        spec_text = (output_dir / "my-app" / "spec.yaml").read_text()
        assert "Updated" in spec_text

    def test_update_nonexistent(self, client):
        resp = client.patch("/api/gallery/nope", json={"name": "X"})
        assert resp.status_code == 404


class TestGallerySpec:
    def test_get_parsed_spec(self, client, tmp_path):
        output_dir = tmp_path / "output"
        _make_gallery_entry(output_dir, "my-app", name="My App")

        resp = client.get("/api/gallery/my-app/spec")
        assert resp.status_code == 200
        data = resp.json()
        assert data["diagram"]["name"] == "My App"
        assert isinstance(data["resources"], list)

    def test_get_spec_nonexistent(self, client):
        resp = client.get("/api/gallery/nope/spec")
        assert resp.status_code == 404


class TestExportAPI:
    def test_export_mermaid(self, client):
        resp = client.post("/api/export", json={
            "yaml_content": _VALID_YAML,
            "format": "mermaid",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["format"] == "mermaid"
        assert isinstance(data["content"], str)
        assert len(data["content"]) > 0

    def test_export_plantuml(self, client):
        resp = client.post("/api/export", json={
            "yaml_content": _VALID_YAML,
            "format": "plantuml",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["format"] == "plantuml"

    def test_export_drawio(self, client):
        resp = client.post("/api/export", json={
            "yaml_content": _VALID_YAML,
            "format": "drawio",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["format"] == "drawio"

    def test_export_unknown_format(self, client):
        resp = client.post("/api/export", json={
            "yaml_content": _VALID_YAML,
            "format": "nope",
        })
        assert resp.status_code == 400

    def test_export_invalid_yaml(self, client):
        resp = client.post("/api/export", json={
            "yaml_content": "{{bad",
            "format": "mermaid",
        })
        assert resp.status_code == 400


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
        """Backward compat: glow field absent -> 200."""
        resp = client.post("/api/generate", json={
            "yaml_content": self._YAML,
            "format": "svg",
            "theme": "dark",
        })
        assert resp.status_code == 200
