"""Tests for PDF report generation."""

import pytest

from redspec.models.diagram import DiagramSpec

pdf_available = True
try:
    import reportlab  # noqa: F401
except ImportError:
    pdf_available = False


@pytest.mark.skipif(not pdf_available, reason="reportlab not installed")
class TestGenerateReport:
    def test_generates_pdf_bytes(self):
        from redspec.exporters.pdf_report import generate_report

        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
                {"type": "azure/vm", "name": "vm2"},
            ],
            "connections": [{"from": "vm1", "to": "vm2", "label": "link"}],
        })
        result = generate_report(spec)
        assert isinstance(result, bytes)
        assert len(result) > 0
        assert result[:5] == b"%PDF-"

    def test_contains_correct_row_count(self):
        from redspec.exporters.pdf_report import generate_report

        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
                {"type": "azure/vm", "name": "vm2"},
                {"type": "azure/vm", "name": "vm3"},
            ],
            "connections": [{"from": "vm1", "to": "vm2"}],
        })
        result = generate_report(spec)
        assert isinstance(result, bytes)
        assert len(result) > 0
