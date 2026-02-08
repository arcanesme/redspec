"""PDF report generation with diagram, inventory table, and connection matrix."""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from redspec.models.diagram import DiagramSpec
    from redspec.models.resource import ResourceDef


def _collect_all_resources(resources: list[ResourceDef]) -> list[ResourceDef]:
    """Flatten the resource tree."""
    result: list[ResourceDef] = []
    for r in resources:
        result.append(r)
        result.extend(_collect_all_resources(r.children))
    return result


def generate_report(spec: DiagramSpec, diagram_path: Path | None = None) -> bytes:
    """Generate a multi-page PDF report.

    Returns PDF as bytes. Requires reportlab.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            Image,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError:
        raise ImportError(
            "reportlab is required for PDF reports. Install with: pip install redspec[report]"
        )

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story: list = []

    # Title page
    story.append(Spacer(1, 2 * inch))
    story.append(Paragraph(spec.diagram.name, styles["Title"]))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(
        f"Theme: {spec.diagram.theme} | Direction: {spec.diagram.direction} | DPI: {spec.diagram.dpi}",
        styles["Normal"],
    ))
    story.append(Spacer(1, inch))

    # Diagram image
    if diagram_path and diagram_path.exists():
        try:
            img = Image(str(diagram_path), width=6 * inch, height=4 * inch)
            img.hAlign = "CENTER"
            story.append(img)
        except Exception:
            story.append(Paragraph("(Diagram image could not be loaded)", styles["Normal"]))

    story.append(Spacer(1, inch))

    # Resource inventory table
    all_resources = _collect_all_resources(spec.resources)
    story.append(Paragraph("Resource Inventory", styles["Heading2"]))
    story.append(Spacer(1, 0.25 * inch))

    table_data = [["Name", "Type", "Metadata"]]
    for r in all_resources:
        meta = ", ".join(f"{k}={v}" for k, v in r.metadata.items()) if r.metadata else ""
        table_data.append([r.name, r.type, meta])

    if len(table_data) > 1:
        t = Table(table_data, colWidths=[2 * inch, 2.5 * inch, 2 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No resources defined.", styles["Normal"]))

    story.append(Spacer(1, 0.5 * inch))

    # Connection matrix
    story.append(Paragraph("Connection Matrix", styles["Heading2"]))
    story.append(Spacer(1, 0.25 * inch))

    if spec.connections:
        conn_data = [["From", "To", "Label"]]
        for c in spec.connections:
            conn_data.append([c.source, c.to, c.label or ""])
        ct = Table(conn_data, colWidths=[2 * inch, 2 * inch, 2.5 * inch])
        ct.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(ct)
    else:
        story.append(Paragraph("No connections defined.", styles["Normal"]))

    doc.build(story)
    return buf.getvalue()
