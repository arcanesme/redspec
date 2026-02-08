"""Tests for JSON Schema generation (D4)."""

import json

from redspec.schemas.generator import (
    bundled_schema_path,
    generate_schema,
    generate_schema_json,
)


class TestGenerateSchema:
    def test_has_schema_keyword(self):
        schema = generate_schema()
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"

    def test_has_id(self):
        schema = generate_schema()
        assert schema["$id"] == "https://redspec.dev/schemas/redspec-spec.json"

    def test_has_properties(self):
        schema = generate_schema()
        props = schema["properties"]
        assert "diagram" in props
        assert "resources" in props
        assert "connections" in props

    def test_direction_produces_enum(self):
        schema = generate_schema()
        defs = schema.get("$defs", {})
        diagram_meta = defs.get("DiagramMeta", {})
        direction_prop = diagram_meta.get("properties", {}).get("direction", {})
        assert "enum" in direction_prop
        assert set(direction_prop["enum"]) == {"TB", "LR", "BT", "RL"}

    def test_theme_produces_enum(self):
        schema = generate_schema()
        defs = schema.get("$defs", {})
        diagram_meta = defs.get("DiagramMeta", {})
        theme_prop = diagram_meta.get("properties", {}).get("theme", {})
        assert "enum" in theme_prop
        assert set(theme_prop["enum"]) == {"default", "light", "dark", "presentation"}

    def test_dpi_has_min_max(self):
        schema = generate_schema()
        defs = schema.get("$defs", {})
        diagram_meta = defs.get("DiagramMeta", {})
        dpi_prop = diagram_meta.get("properties", {}).get("dpi", {})
        assert dpi_prop.get("minimum") == 72
        assert dpi_prop.get("maximum") == 600

    def test_connection_from_alias(self):
        schema = generate_schema()
        defs = schema.get("$defs", {})
        conn_def = defs.get("ConnectionDef", {})
        props = conn_def.get("properties", {})
        assert "from" in props

    def test_all_diagram_meta_fields_have_description(self):
        schema = generate_schema()
        defs = schema.get("$defs", {})
        diagram_meta = defs.get("DiagramMeta", {})
        for field_name, field_schema in diagram_meta.get("properties", {}).items():
            assert "description" in field_schema, f"DiagramMeta.{field_name} missing description"

    def test_all_resource_def_fields_have_description(self):
        schema = generate_schema()
        defs = schema.get("$defs", {})
        resource_def = defs.get("ResourceDef", {})
        for field_name, field_schema in resource_def.get("properties", {}).items():
            assert "description" in field_schema, f"ResourceDef.{field_name} missing description"

    def test_variables_in_schema(self):
        schema = generate_schema()
        props = schema["properties"]
        assert "variables" in props

    def test_connection_styles_in_schema(self):
        schema = generate_schema()
        props = schema["properties"]
        assert "connection_styles" in props

    def test_zones_in_schema(self):
        schema = generate_schema()
        props = schema["properties"]
        assert "zones" in props


class TestGenerateSchemaJson:
    def test_valid_json(self):
        text = generate_schema_json()
        data = json.loads(text)
        assert "$schema" in data

    def test_indented(self):
        text = generate_schema_json(indent=4)
        assert "\n    " in text


class TestBundledSchema:
    def test_bundled_file_exists(self):
        path = bundled_schema_path()
        assert path.exists()

    def test_bundled_matches_generated(self):
        path = bundled_schema_path()
        bundled = json.loads(path.read_text(encoding="utf-8"))
        generated = generate_schema()
        assert bundled == generated
