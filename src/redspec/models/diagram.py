"""Top-level diagram specification models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from redspec.models.resource import ConnectionDef, ConnectionStyleDef, ResourceDef


class AnnotationDef(BaseModel):
    """A free-text annotation on the diagram."""

    text: str = Field(description="Annotation text.")
    position: str | None = Field(default=None, description="Position hint (e.g. 'top-right').")


class ZoneDef(BaseModel):
    """A swimlane / zone grouping resources."""

    name: str = Field(description="Zone display name.")
    resources: list[str] = Field(default_factory=list, description="Resource names belonging to this zone.")
    style: str | None = Field(default=None, description="Zone style preset (dmz, private, public).")


class DiagramMeta(BaseModel):
    """Metadata about the diagram."""

    name: str = Field(default="Azure Architecture", description="Diagram display name.", examples=["My Azure Architecture"])
    layout: str = Field(default="auto", description="Layout engine.", examples=["auto"])
    direction: Literal["TB", "LR", "BT", "RL"] = Field(default="TB", description="Graph layout direction.", examples=["TB", "LR"])
    theme: Literal["default", "light", "dark", "presentation"] = Field(default="default", description="Visual theme.", examples=["default", "dark"])
    dpi: int = Field(default=150, ge=72, le=600, description="Output DPI (72-600).", examples=[150, 300])
    legend: bool = Field(default=False, description="Auto-generate icon legend.")
    annotations: list[AnnotationDef] = Field(default_factory=list, description="Free-text annotations.")
    animation: str | None = Field(default=None, description="SVG animation type (flow, pulse, build).")

    @field_validator("direction", mode="before")
    @classmethod
    def _uppercase_direction(cls, v: str) -> str:
        return v.upper()


class DiagramSpec(BaseModel):
    """Root model for an entire diagram YAML file."""

    diagram: DiagramMeta = Field(default_factory=DiagramMeta, description="Diagram metadata (name, theme, direction, etc.).")
    resources: list[ResourceDef] = Field(default_factory=list, description="Top-level resources.")
    connections: list[ConnectionDef] = Field(default_factory=list, description="Connections between resources.")
    variables: dict[str, str] = Field(default_factory=dict, description="Variable definitions for ${key} interpolation.")
    connection_styles: list[ConnectionStyleDef] = Field(default_factory=list, description="Named reusable connection style presets.")
    zones: list[ZoneDef] = Field(default_factory=list, description="Swimlane / zone groupings.")
