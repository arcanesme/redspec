"""Configurable validation rules beyond Pydantic schema checks."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from redspec.models.lint import LintConfig, LintWarning

if TYPE_CHECKING:
    from redspec.models.diagram import DiagramSpec
    from redspec.models.resource import ResourceDef


def _collect_all_resources(resources: list[ResourceDef], depth: int = 0) -> list[tuple[ResourceDef, int]]:
    """Collect all resources with their nesting depth."""
    result: list[tuple[ResourceDef, int]] = []
    for r in resources:
        result.append((r, depth))
        result.extend(_collect_all_resources(r.children, depth + 1))
    return result


def lint(spec: DiagramSpec, rules: LintConfig | None = None) -> list[LintWarning]:
    """Run lint rules on a DiagramSpec and return warnings."""
    if rules is None:
        rules = LintConfig()

    warnings: list[LintWarning] = []

    all_resources = _collect_all_resources(spec.resources)

    # Rule: max_nesting_depth
    for resource, depth in all_resources:
        if depth >= rules.max_nesting_depth:
            warnings.append(LintWarning(
                rule="max_nesting_depth",
                message=f"Resource '{resource.name}' is nested {depth} levels deep (max {rules.max_nesting_depth}).",
                resource_name=resource.name,
            ))

    # Rule: naming_pattern
    pattern = re.compile(rules.naming_pattern)
    for resource, _ in all_resources:
        if not pattern.match(resource.name):
            warnings.append(LintWarning(
                rule="naming_pattern",
                message=f"Resource name '{resource.name}' does not match pattern '{rules.naming_pattern}'.",
                resource_name=resource.name,
            ))

    # Rule: orphan_resources
    if rules.orphan_resources:
        connected_names: set[str] = set()
        for conn in spec.connections:
            connected_names.add(conn.source)
            connected_names.add(conn.to)

        from redspec.generator.style_map import is_container_type
        for resource, _ in all_resources:
            if not is_container_type(resource.type) and resource.name not in connected_names:
                warnings.append(LintWarning(
                    rule="orphan_resources",
                    message=f"Resource '{resource.name}' has no connections.",
                    resource_name=resource.name,
                ))

    # Rule: duplicate_connections
    if rules.duplicate_connections:
        seen_pairs: set[tuple[str, str]] = set()
        for conn in spec.connections:
            pair = (conn.source, conn.to)
            if pair in seen_pairs:
                warnings.append(LintWarning(
                    rule="duplicate_connections",
                    message=f"Duplicate connection from '{conn.source}' to '{conn.to}'.",
                    resource_name=conn.source,
                ))
            seen_pairs.add(pair)

    return warnings
