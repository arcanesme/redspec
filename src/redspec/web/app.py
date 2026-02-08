"""FastAPI application for the Redspec web UI."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

_WEB_DIR = Path(__file__).parent
_TEMPLATES_DIR = _WEB_DIR / "templates"
_STATIC_DIR = _WEB_DIR / "static"


class YAMLBody(BaseModel):
    yaml_content: str


class GenerateRequest(BaseModel):
    yaml_content: str
    theme: str | None = None
    direction: str | None = None
    dpi: int | None = None
    format: str | None = None


def create_app(output_dir: Path | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    if output_dir is None:
        output_dir = Path("./output")
    output_dir.mkdir(parents=True, exist_ok=True)

    app = FastAPI(title="Redspec", version="0.1.0")
    templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "index.html")

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

    @app.post("/api/validate")
    async def validate_yaml(body: YAMLBody) -> JSONResponse:
        import yaml as pyyaml

        from redspec.models.diagram import DiagramSpec

        try:
            raw = pyyaml.safe_load(body.yaml_content)
            if not isinstance(raw, dict):
                return JSONResponse({"valid": False, "error": "YAML must be a mapping"})
            spec = DiagramSpec.model_validate(raw)
            return JSONResponse({
                "valid": True,
                "name": spec.diagram.name,
                "resources": len(spec.resources),
                "connections": len(spec.connections),
            })
        except Exception as exc:
            return JSONResponse({"valid": False, "error": str(exc)})

    @app.post("/api/generate")
    async def generate_diagram(body: GenerateRequest) -> FileResponse:
        import yaml as pyyaml

        from redspec.generator.output_organizer import organize_output
        from redspec.generator.pipeline import generate as run_pipeline
        from redspec.icons.registry import IconRegistry
        from redspec.models.diagram import DiagramSpec

        try:
            raw = pyyaml.safe_load(body.yaml_content)
            if not isinstance(raw, dict):
                raise HTTPException(status_code=400, detail="YAML must be a mapping")

            # Apply overrides
            if "diagram" not in raw:
                raw["diagram"] = {}
            if body.theme:
                raw["diagram"]["theme"] = body.theme
            if body.direction:
                raw["diagram"]["direction"] = body.direction
            if body.dpi:
                raw["diagram"]["dpi"] = body.dpi

            spec = DiagramSpec.model_validate(raw)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        out_format = body.format or "png"
        registry = IconRegistry()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_output = str(Path(tmpdir) / f"diagram.{out_format}")

            # Write temp YAML for organize_output
            tmp_yaml = Path(tmpdir) / "spec.yaml"
            tmp_yaml.write_text(body.yaml_content, encoding="utf-8")

            generated = run_pipeline(
                spec,
                tmp_output,
                icon_registry=registry,
                out_format=out_format,
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

    @app.get("/api/gallery")
    async def gallery() -> list[dict[str, Any]]:
        from redspec.generator.output_organizer import list_gallery

        return list_gallery(output_dir)

    @app.get("/api/gallery/{slug}/{file}")
    async def gallery_file(slug: str, file: str) -> FileResponse:
        file_path = (output_dir / slug / file).resolve()
        # Path traversal protection
        try:
            file_path.relative_to(output_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="Forbidden")

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(path=str(file_path))

    @app.get("/api/resources")
    async def list_resources() -> list[str]:
        from redspec.icons.registry import IconRegistry

        registry = IconRegistry()
        return list(registry.list_all())

    return app
