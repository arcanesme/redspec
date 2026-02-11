"""FastAPI application for the Redspec web UI."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

_WEB_DIR = Path(__file__).parent
_TEMPLATES_DIR = _WEB_DIR / "templates"
_STATIC_DIR = _WEB_DIR / "static"


# ---------- Request / response models ----------


class YAMLBody(BaseModel):
    yaml_content: str


class ValidateRequest(BaseModel):
    yaml_content: str
    lint: bool = False


class GenerateRequest(BaseModel):
    yaml_content: str
    theme: str | None = None
    direction: str | None = None
    dpi: int | None = None
    format: str | None = None
    glow: bool | None = None
    polish: str | None = None


class ExportRequest(BaseModel):
    yaml_content: str
    format: str = Field(description="Export format: mermaid, plantuml, or drawio.")


class GalleryUpdateRequest(BaseModel):
    yaml_content: str | None = None
    name: str | None = None


# ---------- Helpers ----------


def _parse_yaml_content(yaml_content: str) -> dict:
    """Parse YAML string to dict, raising HTTPException on failure."""
    import yaml as pyyaml

    try:
        raw = pyyaml.safe_load(yaml_content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {exc}")
    if not isinstance(raw, dict):
        raise HTTPException(status_code=400, detail="YAML must be a mapping")
    return raw


def _resolve_slug_dir(output_dir: Path, slug: str) -> Path:
    """Resolve and validate a gallery slug directory."""
    slug_dir = (output_dir / slug).resolve()
    try:
        slug_dir.relative_to(output_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Forbidden")
    if not slug_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Diagram '{slug}' not found")
    return slug_dir


# ---------- Application factory ----------


def create_app(output_dir: Path | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    if output_dir is None:
        output_dir = Path("./output")
    output_dir.mkdir(parents=True, exist_ok=True)

    app = FastAPI(title="Redspec", version="0.1.0")
    templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    # ---- Pages ----

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "index.html")

    # ---- Templates ----

    @app.get("/api/templates")
    async def list_templates() -> list[str]:
        from redspec.yaml_io.scaffold import _TEMPLATES

        return list(_TEMPLATES.keys())

    @app.get("/api/templates/{name}")
    async def get_template(name: str) -> JSONResponse:
        from redspec.yaml_io.scaffold import _TEMPLATES

        if name not in _TEMPLATES:
            raise HTTPException(status_code=404, detail=f"Template {name!r} not found")
        return JSONResponse({"name": name, "content": _TEMPLATES[name]})

    # ---- Validate (with optional lint) ----

    @app.post("/api/validate")
    async def validate_yaml(body: ValidateRequest) -> JSONResponse:
        from redspec.models.diagram import DiagramSpec

        raw = _parse_yaml_content(body.yaml_content)

        try:
            spec = DiagramSpec.model_validate(raw)
        except Exception as exc:
            return JSONResponse({"valid": False, "error": str(exc)})

        result: dict[str, Any] = {
            "valid": True,
            "name": spec.diagram.name,
            "resources": len(spec.resources),
            "connections": len(spec.connections),
        }

        if body.lint:
            from redspec.linter import lint as run_lint

            warnings = run_lint(spec)
            result["lint_warnings"] = [
                {"rule": w.rule, "message": w.message, "resource_name": w.resource_name}
                for w in warnings
            ]

        return JSONResponse(result)

    # ---- Schema ----

    @app.get("/api/schema")
    async def get_schema() -> JSONResponse:
        from redspec.schemas.generator import generate_schema

        return JSONResponse(generate_schema())

    # ---- Generate ----

    @app.post("/api/generate")
    async def generate_diagram(body: GenerateRequest) -> FileResponse:
        from redspec.generator.output_organizer import organize_output
        from redspec.generator.pipeline import generate as run_pipeline
        from redspec.icons.registry import IconRegistry
        from redspec.models.diagram import DiagramSpec

        raw = _parse_yaml_content(body.yaml_content)

        try:
            if "diagram" not in raw:
                raw["diagram"] = {}
            if body.theme:
                raw["diagram"]["theme"] = body.theme
            if body.direction:
                raw["diagram"]["direction"] = body.direction
            if body.dpi:
                raw["diagram"]["dpi"] = body.dpi
            if body.polish:
                from redspec.models.diagram import VALID_POLISH_PRESETS

                if body.polish not in VALID_POLISH_PRESETS:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid polish preset {body.polish!r}. "
                        f"Valid presets: {', '.join(sorted(VALID_POLISH_PRESETS))}",
                    )
                raw["diagram"]["polish"] = body.polish

            spec = DiagramSpec.model_validate(raw)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        out_format = body.format or "png"
        registry = IconRegistry()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_output = str(Path(tmpdir) / f"diagram.{out_format}")

            tmp_yaml = Path(tmpdir) / "spec.yaml"
            tmp_yaml.write_text(body.yaml_content, encoding="utf-8")

            generated = run_pipeline(
                spec,
                tmp_output,
                icon_registry=registry,
                out_format=out_format,
                glow=body.glow,
            )

            organized = organize_output(
                generated_file=generated,
                source_yaml=tmp_yaml,
                output_dir=output_dir,
                diagram_name=spec.diagram.name,
                theme=spec.diagram.theme,
                direction=spec.diagram.direction,
                dpi=spec.diagram.dpi,
                format=out_format,
            )

        slug = organized.parent.name
        media_types: dict[str, str] = {
            "png": "image/png",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
        }
        return FileResponse(
            path=str(organized),
            media_type=media_types.get(out_format, "application/octet-stream"),
            headers={"X-Diagram-Slug": slug},
        )

    # ---- Export (text-based formats) ----

    @app.post("/api/export")
    async def export_diagram(body: ExportRequest) -> JSONResponse:
        from redspec.models.diagram import DiagramSpec

        raw = _parse_yaml_content(body.yaml_content)

        try:
            spec = DiagramSpec.model_validate(raw)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        fmt = body.format.lower()
        if fmt == "mermaid":
            from redspec.exporters.mermaid import export_mermaid
            text = export_mermaid(spec)
        elif fmt == "plantuml":
            from redspec.exporters.plantuml import export_plantuml
            text = export_plantuml(spec)
        elif fmt == "drawio":
            from redspec.exporters.drawio import export_drawio
            text = export_drawio(spec)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown export format: {fmt!r}")

        return JSONResponse({"format": fmt, "content": text})

    # ---- Gallery CRUD ----

    @app.get("/api/gallery")
    async def gallery() -> list[dict[str, Any]]:
        from redspec.generator.output_organizer import list_gallery

        return list_gallery(output_dir)

    @app.get("/api/gallery/{slug}/spec")
    async def gallery_spec(slug: str) -> JSONResponse:
        """Return the parsed spec JSON for a gallery entry."""
        from redspec.models.diagram import DiagramSpec

        slug_dir = _resolve_slug_dir(output_dir, slug)
        spec_file = slug_dir / "spec.yaml"
        if not spec_file.exists():
            raise HTTPException(status_code=404, detail="spec.yaml not found")

        raw = _parse_yaml_content(spec_file.read_text(encoding="utf-8"))
        try:
            spec = DiagramSpec.model_validate(raw)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc))

        return JSONResponse(spec.model_dump(by_alias=True, exclude_none=True))

    @app.get("/api/gallery/{slug}/{file}")
    async def gallery_file(slug: str, file: str) -> FileResponse:
        file_path = (output_dir / slug / file).resolve()
        try:
            file_path.relative_to(output_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="Forbidden")

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(path=str(file_path))

    @app.delete("/api/gallery/{slug}")
    async def gallery_delete(slug: str) -> JSONResponse:
        """Delete a gallery entry by slug."""
        slug_dir = _resolve_slug_dir(output_dir, slug)
        shutil.rmtree(slug_dir)
        return JSONResponse({"deleted": slug})

    @app.patch("/api/gallery/{slug}")
    async def gallery_update(slug: str, body: GalleryUpdateRequest) -> JSONResponse:
        """Update a gallery entry's spec.yaml or metadata name."""
        slug_dir = _resolve_slug_dir(output_dir, slug)

        if body.yaml_content is not None:
            spec_file = slug_dir / "spec.yaml"
            spec_file.write_text(body.yaml_content, encoding="utf-8")

        if body.name is not None:
            meta_file = slug_dir / "metadata.json"
            if meta_file.exists():
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
            else:
                meta = {}
            meta["name"] = body.name
            meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        return JSONResponse({"updated": slug})

    # ---- Resources ----

    @app.get("/api/resources")
    async def list_resources() -> list[str]:
        from redspec.icons.registry import IconRegistry

        registry = IconRegistry()
        return list(registry.list_all())

    return app
