"""Variable interpolation for YAML values."""

from __future__ import annotations

import re
from typing import Any

from redspec.exceptions import UndefinedVariableError

_VAR_PATTERN = re.compile(r"(?<!\$)\$\{([^}]+)\}")
_ESCAPE_PATTERN = re.compile(r"\$\$\{")


def interpolate(raw: dict[str, Any], variables: dict[str, str]) -> dict[str, Any]:
    """Recursively replace ${key} patterns in string values.

    Raises UndefinedVariableError for unresolved references.
    Escaped references ($${{literal}}) are converted to ${literal}.
    """
    return _walk(raw, variables)


def _walk(obj: Any, variables: dict[str, str]) -> Any:
    if isinstance(obj, str):
        return _replace_string(obj, variables)
    if isinstance(obj, dict):
        return {k: _walk(v, variables) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_walk(item, variables) for item in obj]
    return obj


def _replace_string(text: str, variables: dict[str, str]) -> str:
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key not in variables:
            raise UndefinedVariableError(key)
        return variables[key]

    result = _VAR_PATTERN.sub(replacer, text)
    result = _ESCAPE_PATTERN.sub("${", result)
    return result
