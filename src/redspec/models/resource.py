"""Resource and connection definitions."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NodeStyle(BaseModel):
    """Per-node visual overrides for custom styling."""

    color: str | None = Field(default=None, description="Fill color (CSS/hex).")
    shape: str | None = Field(default=None, description="Graphviz shape (box, ellipse, etc.).")
    border: str | None = Field(default=None, description="Border style (e.g. 'dashed').")
    fontcolor: str | None = Field(default=None, description="Label font color.")


class ResourceDef(BaseModel):
    """A single resource, optionally containing child resources."""

    type: str = Field(description="Resource type identifier (e.g. 'azure/app-service').", examples=["azure/app-service", "azure/vm", "aws/ec2"])
    name: str = Field(description="Unique display name for this resource.", examples=["web-app", "prod-db"])
    children: list[ResourceDef] = Field(default_factory=list, description="Nested child resources (rendered inside a cluster).")
    metadata: dict[str, str] = Field(default_factory=dict, description="Arbitrary key-value metadata (SKU, cost, owner).")
    style: NodeStyle | None = Field(default=None, description="Per-node visual overrides.")


class ConnectionStyleDef(BaseModel):
    """Named reusable connection style preset."""

    name: str = Field(description="Preset name for referencing.", examples=["data-flow", "auth-flow"])
    color: str | None = Field(default=None, description="Edge color.")
    style: str | None = Field(default=None, description="Edge style (e.g. 'dashed').")
    penwidth: str | None = Field(default=None, description="Edge pen width.")
    arrowhead: str | None = Field(default=None, description="Arrowhead shape.")


class ConnectionDef(BaseModel):
    """A connection (edge) between two named resources."""

    source: str = Field(alias="from", description="Source resource name.", examples=["web-app"])
    to: str = Field(description="Target resource name.", examples=["prod-db"])
    label: str | None = Field(default=None, description="Edge label text.")
    style: str | None = Field(default=None, description="Edge style (e.g. 'dashed').")
    color: str | None = Field(default=None, description="Edge color (hex or named).")
    penwidth: str | None = Field(default=None, description="Edge pen width.")
    arrowhead: str | None = Field(default=None, description="Arrowhead shape (vee, diamond, etc.).")
    arrowtail: str | None = Field(default=None, description="Arrowtail shape.")
    direction: str | None = Field(default=None, description="Edge direction (forward, back, both, none).")
    minlen: str | None = Field(default=None, description="Minimum edge length.")
    constraint: str | None = Field(default=None, description="Whether edge affects ranking (true/false).")
    style_ref: str | None = Field(default=None, description="Reference to a named connection style preset.")

    model_config = {"populate_by_name": True}
