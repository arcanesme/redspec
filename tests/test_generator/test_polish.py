"""Tests for the premium polish configuration system."""

import pytest

from redspec.models.diagram import (
    DiagramMeta,
    DiagramSpec,
    GlowConfig,
    GradientConfig,
    IconQualityConfig,
    PolishConfig,
    ShadowConfig,
    VALID_POLISH_PRESETS,
    get_polish_defaults,
    resolve_polish,
)


class TestPolishConfig:
    """PolishConfig model creation and validation."""

    def test_default_values(self):
        """PolishConfig() defaults to 'standard' preset values."""
        cfg = PolishConfig()
        assert cfg.preset == "standard"
        assert cfg.glow.enabled is True
        assert cfg.shadow.enabled is True
        assert cfg.gradient.enabled is True
        assert cfg.glassmorphism == 0.35  # standard preset default
        assert cfg.text_halo is True

    def test_string_preset_expansion(self):
        cfg = PolishConfig.model_validate("premium")
        assert cfg.preset == "premium"

    def test_string_preset_all_valid(self):
        for name in VALID_POLISH_PRESETS:
            cfg = PolishConfig.model_validate(name)
            assert cfg.preset == name

    def test_invalid_string_preset_raises(self):
        with pytest.raises(ValueError, match="Unknown polish preset"):
            PolishConfig.model_validate("neon")

    def test_dict_with_preset(self):
        cfg = PolishConfig.model_validate({"preset": "ultra"})
        assert cfg.preset == "ultra"

    def test_dict_with_overrides(self):
        cfg = PolishConfig.model_validate({
            "preset": "minimal",
            "glow": {"enabled": True, "intensity": 0.5},
        })
        assert cfg.preset == "minimal"
        assert cfg.glow.enabled is True
        assert cfg.glow.intensity == 0.5

    def test_glassmorphism_range(self):
        PolishConfig(glassmorphism=0.0)
        PolishConfig(glassmorphism=1.0)
        with pytest.raises(ValueError):
            PolishConfig(glassmorphism=1.5)
        with pytest.raises(ValueError):
            PolishConfig(glassmorphism=-0.1)


class TestGlowConfig:
    def test_defaults(self):
        cfg = GlowConfig()
        assert cfg.enabled is True
        assert cfg.intensity == 0.8
        assert cfg.color is None
        assert cfg.blur_radius == 10.0
        assert cfg.layers == 2

    def test_intensity_range(self):
        GlowConfig(intensity=0.0)
        GlowConfig(intensity=1.0)
        with pytest.raises(ValueError):
            GlowConfig(intensity=1.5)

    def test_blur_radius_range(self):
        GlowConfig(blur_radius=0.0)
        GlowConfig(blur_radius=50.0)
        with pytest.raises(ValueError):
            GlowConfig(blur_radius=60.0)

    def test_layers_range(self):
        GlowConfig(layers=1)
        GlowConfig(layers=4)
        with pytest.raises(ValueError):
            GlowConfig(layers=0)
        with pytest.raises(ValueError):
            GlowConfig(layers=5)


class TestShadowConfig:
    def test_defaults(self):
        cfg = ShadowConfig()
        assert cfg.enabled is True
        assert cfg.elevation == 2
        assert cfg.opacity == 0.3

    def test_valid_elevations(self):
        for e in (0, 1, 2, 3, 4):
            cfg = ShadowConfig(elevation=e)
            assert cfg.elevation == e

    def test_invalid_elevation(self):
        with pytest.raises(ValueError):
            ShadowConfig(elevation=5)


class TestGradientConfig:
    def test_defaults(self):
        cfg = GradientConfig()
        assert cfg.enabled is True
        assert cfg.style == "azure"
        assert cfg.intensity == 0.6

    def test_valid_styles(self):
        for s in ("linear", "radial", "azure"):
            cfg = GradientConfig(style=s)
            assert cfg.style == s

    def test_invalid_style(self):
        with pytest.raises(ValueError):
            GradientConfig(style="conic")


class TestIconQualityConfig:
    def test_defaults(self):
        cfg = IconQualityConfig()
        assert cfg.sharpening is True
        assert cfg.glow is True
        assert cfg.glow_intensity == 0.3


class TestPresetDefaults:
    def test_all_presets_have_defaults(self):
        for name in VALID_POLISH_PRESETS:
            defaults = get_polish_defaults(name)
            assert isinstance(defaults, dict)
            assert "glow" in defaults
            assert "shadow" in defaults
            assert "gradient" in defaults
            assert "icon_quality" in defaults

    def test_minimal_disables_everything(self):
        defaults = get_polish_defaults("minimal")
        assert defaults["glow"]["enabled"] is False
        assert defaults["shadow"]["enabled"] is False
        assert defaults["gradient"]["enabled"] is False
        assert defaults["icon_quality"]["glow"] is False
        assert defaults["glassmorphism"] == 0.0
        assert defaults["text_halo"] is False

    def test_ultra_maximizes_everything(self):
        defaults = get_polish_defaults("ultra")
        assert defaults["glow"]["enabled"] is True
        assert defaults["glow"]["intensity"] == 1.0
        assert defaults["glow"]["layers"] == 3
        assert defaults["shadow"]["elevation"] == 3
        assert defaults["gradient"]["intensity"] == 0.8

    def test_unknown_preset_returns_standard(self):
        defaults = get_polish_defaults("nonexistent")
        assert defaults == get_polish_defaults("standard")


class TestResolvePolish:
    def test_resolve_minimal(self):
        cfg = PolishConfig.model_validate("minimal")
        resolved = resolve_polish(cfg)
        assert resolved.glow.enabled is False
        assert resolved.shadow.enabled is False
        assert resolved.glassmorphism == 0.0

    def test_resolve_premium(self):
        cfg = PolishConfig.model_validate("premium")
        resolved = resolve_polish(cfg)
        assert resolved.glow.enabled is True
        assert resolved.glow.intensity == 0.8
        assert resolved.glow.layers == 2
        assert resolved.shadow.elevation == 2
        assert resolved.gradient.style == "azure"

    def test_resolve_preserves_preset(self):
        cfg = PolishConfig(preset="ultra")
        resolved = resolve_polish(cfg)
        assert resolved.preset == "ultra"


class TestDiagramMetaPolish:
    def test_polish_default_is_none(self):
        meta = DiagramMeta()
        assert meta.polish is None

    def test_polish_string_preset(self):
        meta = DiagramMeta.model_validate({"polish": "premium"})
        assert meta.polish is not None
        assert meta.polish.preset == "premium"

    def test_polish_full_config(self):
        meta = DiagramMeta.model_validate({
            "theme": "presentation",
            "polish": {
                "preset": "ultra",
                "glow": {"intensity": 0.9, "color": "#FF0000"},
                "shadow": {"elevation": 4},
            },
        })
        assert meta.polish is not None
        assert meta.polish.preset == "ultra"
        assert meta.polish.glow.intensity == 0.9
        assert meta.polish.glow.color == "#FF0000"
        assert meta.polish.shadow.elevation == 4

    def test_polish_none_is_valid(self):
        meta = DiagramMeta.model_validate({"polish": None})
        assert meta.polish is None

    def test_diagram_spec_with_polish(self):
        spec = DiagramSpec.model_validate({
            "diagram": {
                "theme": "dark",
                "polish": "premium",
            },
            "resources": [{"type": "azure/vm", "name": "vm1"}],
        })
        assert spec.diagram.polish is not None
        assert spec.diagram.polish.preset == "premium"
