"""Include / composition support for YAML specs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from redspec.exceptions import IncludeFileNotFoundError


def resolve_includes(raw: dict[str, Any], base_dir: Path, _seen: set[str] | None = None) -> dict[str, Any]:
    """Resolve 'includes' directive by merging resources and connections.

    The 'diagram' metadata comes from the root file only.
    Raises IncludeFileNotFoundError if an included file doesn't exist.
    Detects circular includes.
    """
    if _seen is None:
        _seen = set()

    includes = raw.pop("includes", None)
    if not includes:
        return raw

    if not isinstance(includes, list):
        includes = [includes]

    for include_path_str in includes:
        include_path = (base_dir / include_path_str).resolve()
        canonical = str(include_path)

        if canonical in _seen:
            continue  # Skip circular includes silently
        _seen.add(canonical)

        if not include_path.exists():
            raise IncludeFileNotFoundError(str(include_path_str))

        text = include_path.read_text(encoding="utf-8")
        included = yaml.safe_load(text)
        if not isinstance(included, dict):
            continue

        # Recursively resolve includes in included files
        included = resolve_includes(included, include_path.parent, _seen)

        # Merge resources and connections
        if "resources" in included:
            raw.setdefault("resources", []).extend(included["resources"])
        if "connections" in included:
            raw.setdefault("connections", []).extend(included["connections"])

    return raw
