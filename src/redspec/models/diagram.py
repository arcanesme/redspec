"""Top-level diagram specification models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

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


# ---------------------------------------------------------------------------
# Polish configuration models
# ---------------------------------------------------------------------------

VALID_POLISH_PRESETS = frozenset({"minimal", "standard", "premium", "ultra"})


class GlowConfig(BaseModel):
    """Configurable glow effect settings."""

    enabled: bool = Field(default=True, description="Whether glow effects are active.")
    intensity: float = Field(default=0.8, ge=0.0, le=1.0, description="Glow intensity (0.0-1.0).")
    color: str | None = Field(default=None, description="Glow color override (hex). Defaults to theme accent color.")
    blur_radius: float = Field(default=10.0, ge=0.0, le=50.0, description="Glow blur radius in pixels (0-50).")
    layers: int = Field(default=2, ge=1, le=4, description="Number of layered glow passes (1-4).")


class ShadowConfig(BaseModel):
    """3D depth / shadow effect settings."""

    enabled: bool = Field(default=True, description="Whether shadow/depth effects are active.")
    elevation: Literal[0, 1, 2, 3, 4] = Field(default=2, description="Elevation level (0=flat, 4=highest).")
    color: str | None = Field(default=None, description="Shadow color override (hex).")
    opacity: float = Field(default=0.3, ge=0.0, le=1.0, description="Shadow opacity (0.0-1.0).")


class GradientConfig(BaseModel):
    """Cluster/node gradient settings."""

    enabled: bool = Field(default=True, description="Whether gradient fills are active.")
    style: Literal["linear", "radial", "azure"] = Field(
        default="azure", description="Gradient style. 'azure' uses official Azure design gradients."
    )
    intensity: float = Field(default=0.6, ge=0.0, le=1.0, description="Gradient intensity/opacity (0.0-1.0).")


class IconQualityConfig(BaseModel):
    """Icon rendering quality settings."""

    sharpening: bool = Field(default=True, description="Apply sharpening filter to icons.")
    glow: bool = Field(default=True, description="Apply subtle ambient glow to icons.")
    glow_intensity: float = Field(default=0.3, ge=0.0, le=1.0, description="Icon glow intensity (0.0-1.0).")


class PolishConfig(BaseModel):
    """Full visual polish configuration.

    Can be specified as a preset name string (``minimal``, ``standard``,
    ``premium``, ``ultra``) or as a full configuration object with granular
    overrides.  When a preset is given, it is expanded to its defaults
    before any overrides are applied.
    """

    preset: Literal["minimal", "standard", "premium", "ultra"] = Field(
        default="standard", description="Base polish preset that sets defaults for all sub-settings."
    )
    glow: GlowConfig = Field(default_factory=GlowConfig, description="Glow effect configuration.")
    shadow: ShadowConfig = Field(default_factory=ShadowConfig, description="Shadow / 3D depth configuration.")
    gradient: GradientConfig = Field(default_factory=GradientConfig, description="Gradient fill configuration.")
    icon_quality: IconQualityConfig = Field(default_factory=IconQualityConfig, description="Icon rendering quality.")
    glassmorphism: float = Field(
        default=0.45, ge=0.0, le=1.0, description="Glassmorphism fill-opacity for clusters (0.0-1.0)."
    )
    text_halo: bool = Field(default=True, description="Subtle text halo for readability on dark backgrounds.")

    @model_validator(mode="before")
    @classmethod
    def _expand_preset(cls, data: object) -> object:
        """Expand preset defaults, then layer user overrides on top.

        Accepts a plain string (``"premium"``) or a dict with optional
        ``preset`` key.  Preset defaults are applied first, then any
        user-supplied keys override them.
        """
        if isinstance(data, str):
            if data not in VALID_POLISH_PRESETS:
                raise ValueError(
                    f"Unknown polish preset {data!r}. "
                    f"Valid presets: {', '.join(sorted(VALID_POLISH_PRESETS))}"
                )
            defaults = _POLISH_PRESET_DEFAULTS.get(data, {})
            merged = dict(defaults)
            merged["preset"] = data
            return merged

        if isinstance(data, dict):
            preset = data.get("preset", "standard")
            if isinstance(preset, str) and preset in VALID_POLISH_PRESETS:
                defaults = _POLISH_PRESET_DEFAULTS.get(preset, {})
                merged: dict = {}
                for key, default_val in defaults.items():
                    user_val = data.get(key)
                    if user_val is not None and isinstance(default_val, dict) and isinstance(user_val, dict):
                        sub = dict(default_val)
                        sub.update(user_val)
                        merged[key] = sub
                    elif user_val is not None:
                        merged[key] = user_val
                    else:
                        merged[key] = default_val
                merged["preset"] = preset
                return merged

        return data


# ---------------------------------------------------------------------------
# Preset defaults — merged via get_polish_defaults()
# ---------------------------------------------------------------------------

_POLISH_PRESET_DEFAULTS: dict[str, dict] = {
    "minimal": {
        "glow": {"enabled": False, "intensity": 0.0, "blur_radius": 0.0, "layers": 1},
        "shadow": {"enabled": False, "elevation": 0, "opacity": 0.0},
        "gradient": {"enabled": False, "intensity": 0.0},
        "icon_quality": {"sharpening": False, "glow": False, "glow_intensity": 0.0},
        "glassmorphism": 0.0,
        "text_halo": False,
    },
    "standard": {
        "glow": {"enabled": True, "intensity": 0.5, "blur_radius": 6.0, "layers": 1},
        "shadow": {"enabled": True, "elevation": 1, "opacity": 0.2},
        "gradient": {"enabled": True, "style": "linear", "intensity": 0.3},
        "icon_quality": {"sharpening": False, "glow": True, "glow_intensity": 0.2},
        "glassmorphism": 0.35,
        "text_halo": True,
    },
    "premium": {
        "glow": {"enabled": True, "intensity": 0.8, "blur_radius": 10.0, "layers": 2},
        "shadow": {"enabled": True, "elevation": 2, "opacity": 0.3},
        "gradient": {"enabled": True, "style": "azure", "intensity": 0.6},
        "icon_quality": {"sharpening": True, "glow": True, "glow_intensity": 0.3},
        "glassmorphism": 0.45,
        "text_halo": True,
    },
    "ultra": {
        "glow": {"enabled": True, "intensity": 1.0, "blur_radius": 16.0, "layers": 3},
        "shadow": {"enabled": True, "elevation": 3, "opacity": 0.4},
        "gradient": {"enabled": True, "style": "azure", "intensity": 0.8},
        "icon_quality": {"sharpening": True, "glow": True, "glow_intensity": 0.5},
        "glassmorphism": 0.55,
        "text_halo": True,
    },
}


def get_polish_defaults(preset: str) -> dict:
    """Return the default configuration dict for a polish preset."""
    return _POLISH_PRESET_DEFAULTS.get(preset, _POLISH_PRESET_DEFAULTS["standard"])


def resolve_polish(config: PolishConfig) -> PolishConfig:
    """Return a fully-resolved ``PolishConfig``.

    Preset defaults are already applied during model validation (see
    ``_expand_preset``), so this function simply returns the config as-is.
    It exists as a stable public API entry point for callers that want an
    explicit *resolve* step.
    """
    return config


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
    polish: PolishConfig | None = Field(
        default=None,
        description="Visual polish configuration. Accepts a preset name ('minimal', 'standard', 'premium', 'ultra') or a full configuration object.",
    )

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
