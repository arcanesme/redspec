"""Top-level diagram specification models."""

from pydantic import BaseModel, Field

from redspec.models.resource import ConnectionDef, ResourceDef


class DiagramMeta(BaseModel):
    """Metadata about the diagram."""

    name: str = "Azure Architecture"
    layout: str = "auto"


class DiagramSpec(BaseModel):
    """Root model for an entire diagram YAML file."""

    diagram: DiagramMeta = Field(default_factory=DiagramMeta)
    resources: list[ResourceDef] = Field(default_factory=list)
    connections: list[ConnectionDef] = Field(default_factory=list)
