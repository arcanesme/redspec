"""Parse and validate a YAML architecture file into a DiagramSpec."""

from pathlib import Path

import yaml

from redspec.exceptions import YAMLParseError
from redspec.models.diagram import DiagramSpec


def parse_yaml(path: str | Path) -> DiagramSpec:
    """Load a YAML file and return a validated DiagramSpec.

    Raises YAMLParseError for any YAML syntax or validation issue.
    """
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise YAMLParseError(f"Cannot read file: {path}: {exc}") from exc

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise YAMLParseError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise YAMLParseError(f"Expected a YAML mapping at top level, got {type(data).__name__}")

    try:
        return DiagramSpec.model_validate(data)
    except Exception as exc:
        raise YAMLParseError(f"Validation error in {path}: {exc}") from exc
