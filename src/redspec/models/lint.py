"""Lint configuration and warning models."""

from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, Field


class LintConfig(BaseModel):
    """Configurable lint rules."""

    max_nesting_depth: int = Field(default=5, description="Maximum allowed resource nesting depth.")
    naming_pattern: str = Field(default=r"^[a-z0-9][a-z0-9-]*$", description="Regex pattern for resource names.")
    orphan_resources: bool = Field(default=True, description="Warn on resources with zero connections.")
    duplicate_connections: bool = Field(default=True, description="Warn on duplicate from/to pairs.")


@dataclass
class LintWarning:
    """A single lint warning."""

    rule: str
    message: str
    resource_name: str | None = None
