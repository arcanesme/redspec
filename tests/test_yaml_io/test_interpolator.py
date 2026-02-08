"""Tests for variable interpolation (B1)."""

import pytest

from redspec.exceptions import UndefinedVariableError
from redspec.yaml_io.interpolator import interpolate


class TestInterpolate:
    def test_simple_substitution(self):
        raw = {"name": "${env}-app"}
        result = interpolate(raw, {"env": "prod"})
        assert result["name"] == "prod-app"

    def test_nested_values(self):
        raw = {"diagram": {"name": "${env} Architecture"}, "items": ["${region}"]}
        result = interpolate(raw, {"env": "prod", "region": "eastus"})
        assert result["diagram"]["name"] == "prod Architecture"
        assert result["items"][0] == "eastus"

    def test_missing_variable_raises(self):
        raw = {"name": "${undefined}"}
        with pytest.raises(UndefinedVariableError, match="undefined"):
            interpolate(raw, {})

    def test_no_variables_noop(self):
        raw = {"name": "plain text", "count": 42}
        result = interpolate(raw, {})
        assert result == raw

    def test_escape_literal(self):
        raw = {"name": "$${literal}"}
        result = interpolate(raw, {})
        assert result["name"] == "${literal}"

    def test_multiple_vars_in_one_string(self):
        raw = {"name": "${env}-${region}-app"}
        result = interpolate(raw, {"env": "prod", "region": "eastus"})
        assert result["name"] == "prod-eastus-app"

    def test_non_string_values_preserved(self):
        raw = {"count": 42, "flag": True, "ratio": 3.14, "nothing": None}
        result = interpolate(raw, {"env": "prod"})
        assert result == raw
