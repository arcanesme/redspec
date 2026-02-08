"""Top-level diagram specification models."""

from pydantic import BaseModel, Field, field_validator

from redspec.generator.themes import VALID_THEMES
from redspec.models.resource import ConnectionDef, ResourceDef

_VALID_DIRECTIONS: frozenset[str] = frozenset({"TB", "LR", "BT", "RL"})


class DiagramMeta(BaseModel):
    """Metadata about the diagram."""

    name: str = "Azure Architecture"
    layout: str = "auto"
    direction: str = "TB"
    theme: str = "default"
    dpi: int = 150

    @field_validator("direction", mode="before")
    @classmethod
    def _uppercase_direction(cls, v: str) -> str:
        v = v.upper()
        if v not in _VALID_DIRECTIONS:
            msg = f"direction must be one of {sorted(_VALID_DIRECTIONS)}, got {v!r}"
            raise ValueError(msg)
        return v

    @field_validator("theme")
    @classmethod
    def _validate_theme(cls, v: str) -> str:
        if v not in VALID_THEMES:
            msg = f"theme must be one of {sorted(VALID_THEMES)}, got {v!r}"
            raise ValueError(msg)
        return v

    @field_validator("dpi")
    @classmethod
    def _validate_dpi(cls, v: int) -> int:
        if not 72 <= v <= 600:
            msg = f"dpi must be between 72 and 600, got {v}"
            raise ValueError(msg)
        return v


class DiagramSpec(BaseModel):
    """Root model for an entire diagram YAML file."""

    diagram: DiagramMeta = Field(default_factory=DiagramMeta)
    resources: list[ResourceDef] = Field(default_factory=list)
    connections: list[ConnectionDef] = Field(default_factory=list)
