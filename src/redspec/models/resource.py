"""Resource and connection definitions."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ResourceDef(BaseModel):
    """A single Azure resource, optionally containing child resources."""

    type: str
    name: str
    children: list[ResourceDef] = Field(default_factory=list)


class ConnectionDef(BaseModel):
    """A connection (edge) between two named resources."""

    source: str = Field(alias="from")
    to: str
    label: str | None = None
    style: str | None = None
    color: str | None = None
    penwidth: str | None = None
    arrowhead: str | None = None
    arrowtail: str | None = None
    direction: str | None = None
    minlen: str | None = None
    constraint: str | None = None

    model_config = {"populate_by_name": True}
