"""Generate JSON Schema from Pydantic models for IDE support."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def generate_schema() -> dict[str, Any]:
    """Generate the JSON Schema for DiagramSpec.

    Returns a dict suitable for JSON serialization.
    """
    from redspec.models.diagram import DiagramSpec

    schema = DiagramSpec.model_json_schema(
        mode="validation",
        ref_template="#/$defs/{model}",
    )

    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = "https://redspec.dev/schemas/redspec-spec.json"
    schema["title"] = "Redspec Diagram Specification"
    schema["description"] = "Schema for redspec YAML architecture diagram files."

    return schema


def generate_schema_json(indent: int = 2) -> str:
    """Generate the JSON Schema as a formatted JSON string."""
    return json.dumps(generate_schema(), indent=indent)


def bundled_schema_path() -> Path:
    """Return the path to the bundled (checked-in) schema file."""
    return Path(__file__).parent / "redspec-spec.json"
