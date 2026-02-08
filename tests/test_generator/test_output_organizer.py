"""Tests for the output organizer module."""

import json
import time
from pathlib import Path

from redspec.generator.output_organizer import list_gallery, organize_output, slugify


class TestSlugify:
    def test_simple(self):
        assert slugify("My Azure Arch") == "my-azure-arch"

    def test_special_characters(self):
        assert slugify("Hello, World!") == "hello-world"

    def test_multiple_spaces(self):
        assert slugify("  lots   of   spaces  ") == "lots-of-spaces"

    def test_underscores(self):
        assert slugify("under_score_name") == "under-score-name"

    def test_already_slug(self):
        assert slugify("already-a-slug") == "already-a-slug"

    def test_empty_string(self):
        assert slugify("") == ""

    def test_mixed_case(self):
        assert slugify("CamelCase And UPPER") == "camelcase-and-upper"


class TestOrganizeOutput:
    def test_creates_structure(self, tmp_path):
        # Create a fake generated file and source yaml
        gen_file = tmp_path / "input" / "test.png"
        gen_file.parent.mkdir()
        gen_file.write_bytes(b"fake png data")

        source_yaml = tmp_path / "input" / "spec.yaml"
        source_yaml.write_text("diagram:\n  name: Test\n")

        output_dir = tmp_path / "output"

        result = organize_output(
            generated_file=gen_file,
            source_yaml=source_yaml,
            output_dir=output_dir,
            diagram_name="My Test Diagram",
            theme="default",
            direction="TB",
            dpi=150,
        )

        assert result.exists()
        assert result.name == "diagram.png"
        assert result.parent.name == "my-test-diagram"

        # Check spec.yaml copied
        spec = result.parent / "spec.yaml"
        assert spec.exists()
        assert "name: Test" in spec.read_text()

        # Check metadata.json
        meta_file = result.parent / "metadata.json"
        assert meta_file.exists()
        meta = json.loads(meta_file.read_text())
        assert meta["name"] == "My Test Diagram"
        assert meta["slug"] == "my-test-diagram"
        assert meta["format"] == "png"
        assert meta["theme"] == "default"
        assert meta["direction"] == "TB"
        assert meta["dpi"] == 150
        assert "timestamp" in meta

    def test_overwrite(self, tmp_path):
        gen_file = tmp_path / "test.png"
        gen_file.write_bytes(b"first version")
        source_yaml = tmp_path / "spec.yaml"
        source_yaml.write_text("v1")
        output_dir = tmp_path / "output"

        organize_output(gen_file, source_yaml, output_dir, "Test")

        # Overwrite
        gen_file.write_bytes(b"second version")
        source_yaml.write_text("v2")
        result = organize_output(gen_file, source_yaml, output_dir, "Test")

        assert result.read_bytes() == b"second version"
        assert (result.parent / "spec.yaml").read_text() == "v2"


class TestListGallery:
    def test_empty_dir(self, tmp_path):
        assert list_gallery(tmp_path) == []

    def test_nonexistent_dir(self, tmp_path):
        assert list_gallery(tmp_path / "nope") == []

    def test_populated(self, tmp_path):
        gen_file = tmp_path / "test.png"
        gen_file.write_bytes(b"data")
        source = tmp_path / "spec.yaml"
        source.write_text("yaml")
        output_dir = tmp_path / "output"

        organize_output(gen_file, source, output_dir, "First")
        time.sleep(0.05)  # ensure different timestamps
        organize_output(gen_file, source, output_dir, "Second")

        entries = list_gallery(output_dir)
        assert len(entries) == 2
        # Newest first
        assert entries[0]["name"] == "Second"
        assert entries[1]["name"] == "First"

    def test_ignores_non_directories(self, tmp_path):
        (tmp_path / "stray-file.txt").write_text("hello")
        assert list_gallery(tmp_path) == []

    def test_ignores_dirs_without_metadata(self, tmp_path):
        (tmp_path / "some-dir").mkdir()
        assert list_gallery(tmp_path) == []
