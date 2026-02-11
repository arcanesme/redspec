"""Command-line interface for redspec."""

import tempfile
from pathlib import Path

import click


@click.group()
def main() -> None:
    """Redspec -- generate architecture diagrams from YAML."""
    from redspec.icons.migration import migrate_flat_cache

    migrate_flat_cache()


@main.command()
@click.argument("yaml_file", type=click.Path(exists=True, dir_okay=False))
@click.option("-o", "--output", default=None, help="Output file path (direct mode).")
@click.option(
    "-d",
    "--output-dir",
    default=None,
    type=click.Path(file_okay=False),
    help="Organized output directory.",
)
@click.option(
    "--format",
    "out_format",
    type=click.Choice(["png", "svg", "pdf"]),
    default="png",
    help="Output format (default: png).",
)
@click.option("--strict", is_flag=True, default=False, help="Fail on missing icons.")
@click.option(
    "--direction",
    type=click.Choice(["TB", "LR", "BT", "RL"], case_sensitive=False),
    default=None,
    help="Layout direction (overrides YAML).",
)
@click.option(
    "--dpi",
    type=click.IntRange(72, 600),
    default=None,
    help="Output DPI, 72-600 (overrides YAML).",
)
@click.option(
    "--export-format",
    type=click.Choice(["mermaid", "plantuml", "drawio"]),
    default=None,
    help="Export to text-based format instead of rendering.",
)
@click.option("--report", is_flag=True, default=False, help="Generate PDF report instead of plain diagram.")
@click.option(
    "--polish",
    type=click.Choice(["minimal", "standard", "premium", "ultra"], case_sensitive=False),
    default=None,
    help="Visual polish preset (overrides YAML).",
)
@click.option("--glow/--no-glow", default=None, help="Enable or disable glow effects.")
def generate(
    yaml_file: str,
    output: str | None,
    output_dir: str | None,
    out_format: str,
    strict: bool,
    direction: str | None,
    dpi: int | None,
    export_format: str | None,
    report: bool,
    polish: str | None,
    glow: bool | None,
) -> None:
    """Generate a diagram from a YAML architecture file."""
    from redspec.generator.output_organizer import organize_output
    from redspec.generator.pipeline import generate as run_pipeline
    from redspec.icons.downloader import download_icons
    from redspec.icons.packs import ALL_PACKS
    from redspec.icons.registry import IconRegistry
    from redspec.yaml_io.parser import parse_yaml

    if output and output_dir:
        raise click.UsageError("Cannot use both -o/--output and -d/--output-dir.")

    # Text-based export mode
    if export_format:
        spec = parse_yaml(yaml_file)
        if export_format == "mermaid":
            from redspec.exporters.mermaid import export_mermaid
            text = export_mermaid(spec)
        elif export_format == "plantuml":
            from redspec.exporters.plantuml import export_plantuml
            text = export_plantuml(spec)
        elif export_format == "drawio":
            from redspec.exporters.drawio import export_drawio
            text = export_drawio(spec)
        else:
            raise click.UsageError(f"Unknown export format: {export_format}")

        if output:
            Path(output).write_text(text, encoding="utf-8")
            click.echo(f"Exported to {output}")
        else:
            click.echo(text)
        return

    azure_pack = ALL_PACKS["azure"]
    if not azure_pack.downloaded_marker.exists():
        click.echo("Icons not found, downloading on first run...")
        download_icons()

    spec = parse_yaml(yaml_file)

    # Apply --polish override
    if polish:
        from redspec.models.diagram import PolishConfig

        spec.diagram.polish = PolishConfig(preset=polish)

    registry = IconRegistry()

    direction_val = direction.upper() if direction else None
    dpi_val = dpi

    if output:
        # Direct file output (backward compatible)
        result = run_pipeline(
            spec,
            output,
            icon_registry=registry,
            strict=strict,
            out_format=out_format,
            direction_override=direction_val,
            dpi_override=dpi_val,
            glow=glow,
        )

        # PDF report mode
        if report:
            _generate_report(spec, result)
            return

        click.echo(f"Diagram written to {result}")
    else:
        # Organized output mode
        target_dir = Path(output_dir) if output_dir else Path("./output")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_output = str(Path(tmpdir) / f"diagram.{out_format}")
            generated = run_pipeline(
                spec,
                tmp_output,
                icon_registry=registry,
                strict=strict,
                out_format=out_format,
                direction_override=direction_val,
                dpi_override=dpi_val,
                glow=glow,
            )

            # PDF report mode
            if report:
                _generate_report(spec, generated)
                return

            result = organize_output(
                generated_file=generated,
                source_yaml=Path(yaml_file),
                output_dir=target_dir,
                diagram_name=spec.diagram.name,
                theme=spec.diagram.theme,
                direction=direction_val or spec.diagram.direction,
                dpi=dpi_val or spec.diagram.dpi,
                format=out_format,
            )

        click.echo(f"Diagram written to {result}")


def _generate_report(spec, diagram_path: Path) -> None:
    """Generate a PDF report."""
    try:
        from redspec.exporters.pdf_report import generate_report
    except ImportError:
        click.echo(
            "reportlab is required for PDF reports. Install with:\n"
            "  pip install redspec[report]",
            err=True,
        )
        raise SystemExit(1)

    pdf_bytes = generate_report(spec, diagram_path)
    report_path = diagram_path.with_suffix(".pdf")
    report_path.write_bytes(pdf_bytes)
    click.echo(f"Report written to {report_path}")


@main.command("update-icons")
@click.argument("packs", nargs=-1)
@click.option("--all", "all_packs", is_flag=True, default=False, help="Download all known icon packs.")
@click.option("--list", "list_packs", is_flag=True, default=False, help="Show available packs with install status.")
def update_icons(packs: tuple[str, ...], all_packs: bool, list_packs: bool) -> None:
    """Download icon packs. Defaults to Azure only.

    Specify pack names to download specific packs, or use --all for everything.
    Use --list to see available packs and their install status.
    """
    from redspec.icons.packs import ALL_PACKS, DEFAULT_PACK_NAMES
    from redspec.icons.downloader import download_packs

    if list_packs:
        for name, pack in ALL_PACKS.items():
            status = "installed" if pack.downloaded_marker.exists() else "not installed"
            click.echo(f"  {name:<20s} {pack.display_name:<35s} [{status}]")
        return

    if all_packs:
        names = list(ALL_PACKS.keys())
    elif packs:
        names = list(packs)
    else:
        names = DEFAULT_PACK_NAMES

    results = download_packs(names, force=True)
    for name, count in results.items():
        click.echo(f"{name}: {count} icons extracted.")
    click.echo("Icons updated.")


@main.command("list-resources")
@click.option("--pack", default=None, help="Filter by pack namespace (e.g. azure, dynamics365).")
def list_resources(pack: str | None) -> None:
    """List all available resource icon types."""
    from redspec.icons.registry import IconRegistry

    registry = IconRegistry()
    for name in registry.list_all(namespace=pack):
        click.echo(name)


@main.command()
@click.argument("output", default="architecture.yaml")
@click.option(
    "--template",
    type=click.Choice(["azure", "m365", "dynamics365", "power-platform", "multi-cloud", "aws", "gcp", "k8s"]),
    default="azure",
    help="Template variant to generate.",
)
def init(output: str, template: str) -> None:
    """Create a starter YAML template."""
    from redspec.yaml_io.scaffold import generate_template

    path = Path(output)
    if path.exists():
        click.echo(f"File already exists: {path}", err=True)
        raise SystemExit(1)

    path.write_text(generate_template(template_name=template), encoding="utf-8")
    click.echo(f"Template written to {path}")


@main.command()
@click.argument("yaml_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--lint", is_flag=True, default=False, help="Run lint rules after validation.")
def validate(yaml_file: str, lint: bool) -> None:
    """Validate a YAML architecture file."""
    from redspec.exceptions import YAMLParseError
    from redspec.yaml_io.parser import parse_yaml

    try:
        spec = parse_yaml(yaml_file)
    except YAMLParseError as exc:
        click.echo(f"Validation failed: {exc}", err=True)
        raise SystemExit(1)

    n_res = len(spec.resources)
    n_conn = len(spec.connections)
    click.echo(f"Valid: {spec.diagram.name} ({n_res} resources, {n_conn} connections)")

    if lint:
        from redspec.linter import lint as run_lint

        warnings = run_lint(spec)
        if warnings:
            for w in warnings:
                click.echo(f"  WARN [{w.rule}]: {w.message}")
        else:
            click.echo("  No lint warnings.")


@main.command()
@click.option("--port", default=8000, type=int, help="Port to listen on.")
@click.option("--host", default="127.0.0.1", help="Host to bind to.")
@click.option(
    "-d",
    "--output-dir",
    default="./output",
    type=click.Path(file_okay=False),
    help="Output directory for generated diagrams.",
)
def serve(port: int, host: str, output_dir: str) -> None:
    """Start the Redspec web UI."""
    try:
        import uvicorn  # noqa: F401

        from redspec.web.app import create_app
    except ImportError:
        click.echo(
            "Web dependencies not installed. Install with:\n"
            "  pip install redspec[web]",
            err=True,
        )
        raise SystemExit(1)

    app = create_app(output_dir=Path(output_dir))
    click.echo(f"Starting Redspec web UI at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


@main.command()
@click.option("-o", "--output", default=None, help="Write schema JSON to file.")
@click.option("--bundled", is_flag=True, default=False, help="Print path to bundled schema file.")
def schema(output: str | None, bundled: bool) -> None:
    """Output the JSON Schema for redspec YAML files."""
    from redspec.schemas.generator import bundled_schema_path, generate_schema_json

    if bundled:
        click.echo(str(bundled_schema_path()))
        return

    json_text = generate_schema_json()

    if output:
        Path(output).write_text(json_text, encoding="utf-8")
        click.echo(f"Schema written to {output}")
    else:
        click.echo(json_text)


@main.command()
@click.argument("yaml_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--port", default=9876, type=int, help="Port for live-reload server.")
@click.option("--no-browser", is_flag=True, default=False, help="Don't open browser.")
@click.option(
    "--format",
    "out_format",
    type=click.Choice(["svg", "png", "pdf"]),
    default="svg",
    help="Output format (default: svg for speed).",
)
def watch(yaml_file: str, port: int, no_browser: bool, out_format: str) -> None:
    """Watch a YAML file and auto-regenerate on save."""
    import datetime

    from redspec.watch_server import WatchServer
    from redspec.watcher import watch_loop

    server = WatchServer(port=port, diagram_format=out_format)
    server.start()
    click.echo(f"Watch server running at {server.url}")

    yaml_path = Path(yaml_file)

    def on_first_build(path):
        server.update_diagram(path)
        if not no_browser:
            import webbrowser
            webbrowser.open(server.url)

    def on_rebuild(path):
        server.update_diagram(path)
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        click.echo(f"[{ts}] Rebuilt: {path}")

    def on_error(exc):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        click.echo(f"[{ts}] Error: {exc}", err=True)

    try:
        watch_loop(
            yaml_path,
            on_rebuild=on_rebuild,
            on_error=on_error,
            on_first_build=on_first_build,
        )
    except KeyboardInterrupt:
        click.echo("\nStopping watch mode...")
    finally:
        server.shutdown()


def _format_size(size_bytes: int) -> str:
    """Format byte count as human-readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def _list_spec_files(spec_dir: Path) -> list[Path]:
    """Return all files inside a spec directory, sorted by name."""
    return sorted(f for f in spec_dir.iterdir() if f.is_file())


@main.command()
@click.argument("names", nargs=-1)
@click.option(
    "-d",
    "--output-dir",
    default="./output",
    type=click.Path(file_okay=False),
    help="Output directory to clean (default: ./output).",
)
@click.option("--all", "all_", is_flag=True, default=False, help="Remove the entire output directory.")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be deleted without removing anything.")
@click.option("-y", "--yes", is_flag=True, default=False, help="Skip confirmation prompt.")
@click.option(
    "--file",
    "file_filter",
    default=None,
    help="Target a specific file within a spec (e.g. diagram.png, spec.yaml, metadata.json).",
)
@click.option("--edit", is_flag=True, default=False, help="Open the spec.yaml for editing in $EDITOR.")
def clean(
    names: tuple[str, ...],
    output_dir: str,
    all_: bool,
    dry_run: bool,
    yes: bool,
    file_filter: str | None,
    edit: bool,
) -> None:
    """List, edit, or delete generated diagram output.

    \b
    With no arguments:        list all generated specs with their files.
    With slug names:          delete those specs (or specific files with --file).
    With --edit <slug>:       open the spec.yaml in $EDITOR.
    With --all:               remove the entire output directory.
    """
    import shutil

    from redspec.generator.output_organizer import list_gallery, slugify

    out_path = Path(output_dir)

    if not out_path.is_dir():
        click.echo(f"Output directory does not exist: {out_path}")
        return

    # --- Edit mode ---
    if edit:
        if not names:
            raise click.UsageError("Specify a diagram slug to edit, e.g.: redspec clean --edit my-diagram")
        slug = slugify(names[0]) if " " in names[0] else names[0]
        target_file = out_path / slug / (file_filter or "spec.yaml")
        if not target_file.exists():
            click.echo(f"File not found: {target_file}", err=True)
            raise SystemExit(1)
        import os
        editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "vi"))
        click.edit(filename=str(target_file), editor=editor)
        return

    # --- Delete all ---
    if all_:
        entries = list_gallery(out_path)
        total_files = 0
        total_size = 0
        for entry in entries:
            slug_dir = out_path / entry.get("slug", "")
            if slug_dir.is_dir():
                for f in _list_spec_files(slug_dir):
                    total_files += 1
                    total_size += f.stat().st_size
        label = f"{len(entries)} diagram(s), {total_files} files ({_format_size(total_size)})"
        if dry_run:
            click.echo(f"Would delete {label}:")
            for entry in entries:
                slug = entry.get("slug", "?")
                slug_dir = out_path / slug
                click.echo(f"  {slug}/")
                if slug_dir.is_dir():
                    for f in _list_spec_files(slug_dir):
                        click.echo(f"    {f.name}  ({_format_size(f.stat().st_size)})")
            return
        if not yes:
            click.confirm(f"Delete {label} at {out_path}?", abort=True)
        shutil.rmtree(out_path)
        click.echo(f"Removed {label} from {out_path}")
        return

    # --- List mode (no names given) ---
    if not names:
        entries = list_gallery(out_path)
        if not entries:
            click.echo("No generated diagrams found.")
            return
        total_size = 0
        click.echo("Generated diagrams:\n")
        for entry in entries:
            slug = entry.get("slug", "?")
            name = entry.get("name", slug)
            fmt = entry.get("format", "?")
            ts = entry.get("timestamp", "")[:19]
            click.echo(f"  {slug}/  ({name}, {fmt}, {ts})")
            slug_dir = out_path / slug
            if slug_dir.is_dir():
                for f in _list_spec_files(slug_dir):
                    size = f.stat().st_size
                    total_size += size
                    click.echo(f"    {f.name:<20s} {_format_size(size):>10s}")
            click.echo("")
        click.echo(f"Total: {len(entries)} diagram(s), {_format_size(total_size)}")
        return

    # --- Delete specific slugs (or specific files within them) ---
    slugs = [slugify(n) if "/" not in n and " " in n else n for n in names]
    for slug in slugs:
        target = out_path / slug
        if not target.is_dir():
            click.echo(f"  Not found: {slug}", err=True)
            continue

        # Delete a single file within the spec
        if file_filter:
            target_file = target / file_filter
            if not target_file.is_file():
                click.echo(f"  File not found: {slug}/{file_filter}", err=True)
                continue
            if dry_run:
                click.echo(f"  Would delete: {slug}/{file_filter} ({_format_size(target_file.stat().st_size)})")
                continue
            if not yes:
                click.confirm(f"Delete {slug}/{file_filter}?", abort=True)
            target_file.unlink()
            click.echo(f"  Deleted: {slug}/{file_filter}")
            # If the directory is now empty (or only metadata.json left), clean up
            remaining = _list_spec_files(target)
            if not remaining:
                shutil.rmtree(target)
                click.echo(f"  Removed empty directory: {slug}/")
            continue

        # Delete the entire spec directory
        files = _list_spec_files(target)
        dir_size = sum(f.stat().st_size for f in files)
        if dry_run:
            click.echo(f"  Would delete: {slug}/  ({len(files)} files, {_format_size(dir_size)})")
            for f in files:
                click.echo(f"    {f.name:<20s} {_format_size(f.stat().st_size):>10s}")
            continue
        if not yes:
            click.confirm(f"Delete {slug}/ ({len(files)} files, {_format_size(dir_size)})?", abort=True)
        shutil.rmtree(target)
        click.echo(f"  Removed: {slug}/  ({len(files)} files, {_format_size(dir_size)})")


@main.command("import-azure")
@click.option("--subscription", required=True, help="Azure subscription ID.")
@click.option("--resource-group", default=None, help="Filter to a specific resource group.")
@click.option("-o", "--output", default="imported.yaml", help="Output YAML file path.")
def import_azure(subscription: str, resource_group: str | None, output: str) -> None:
    """Import architecture from a live Azure subscription."""
    try:
        from redspec.importers.azure_graph import import_from_resource_graph
    except ImportError:
        click.echo(
            "Azure dependencies required. Install with:\n"
            "  pip install redspec[azure]",
            err=True,
        )
        raise SystemExit(1)

    import yaml

    spec = import_from_resource_graph(subscription, resource_group=resource_group)

    # Serialize to YAML
    data = spec.model_dump(by_alias=True, exclude_none=True)
    yaml_text = yaml.dump(data, default_flow_style=False, sort_keys=False)

    Path(output).write_text(yaml_text, encoding="utf-8")
    click.echo(f"Imported {len(spec.resources)} resource groups to {output}")


@main.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--format",
    "out_format",
    type=click.Choice(["png", "svg", "pdf"]),
    default="png",
    help="Output format.",
)
@click.option(
    "--output-dir",
    default=None,
    type=click.Path(file_okay=False),
    help="Output directory (default: same as input).",
)
@click.option("--strict", is_flag=True, default=False, help="Fail on missing icons.")
@click.option(
    "--direction",
    type=click.Choice(["TB", "LR", "BT", "RL"], case_sensitive=False),
    default=None,
    help="Layout direction override.",
)
@click.option("--dpi", type=click.IntRange(72, 600), default=None, help="DPI override.")
def batch(
    directory: str,
    out_format: str,
    output_dir: str | None,
    strict: bool,
    direction: str | None,
    dpi: int | None,
) -> None:
    """Generate diagrams from all YAML files in a directory."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from redspec.generator.pipeline import generate as run_pipeline
    from redspec.icons.downloader import download_icons
    from redspec.icons.packs import ALL_PACKS
    from redspec.icons.registry import IconRegistry
    from redspec.yaml_io.parser import parse_yaml

    azure_pack = ALL_PACKS["azure"]
    if not azure_pack.downloaded_marker.exists():
        click.echo("Icons not found, downloading on first run...")
        download_icons()

    dir_path = Path(directory)
    yaml_files = sorted(dir_path.glob("*.yaml")) + sorted(dir_path.glob("*.yml"))

    if not yaml_files:
        click.echo(f"No YAML files found in {directory}")
        return

    target_dir = Path(output_dir) if output_dir else dir_path
    target_dir.mkdir(parents=True, exist_ok=True)
    registry = IconRegistry()
    direction_val = direction.upper() if direction else None

    success = 0
    errors = 0

    def process_file(yaml_file: Path) -> tuple[Path, str | None]:
        try:
            spec = parse_yaml(yaml_file)
            output_path = str(target_dir / f"{yaml_file.stem}.{out_format}")
            run_pipeline(
                spec,
                output_path,
                icon_registry=registry,
                strict=strict,
                out_format=out_format,
                direction_override=direction_val,
                dpi_override=dpi,
            )
            return yaml_file, None
        except Exception as exc:
            return yaml_file, str(exc)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_file, f) for f in yaml_files]
        for future in as_completed(futures):
            yaml_file, error = future.result()
            if error:
                errors += 1
                click.echo(f"  FAIL: {yaml_file.name}: {error}", err=True)
            else:
                success += 1
                click.echo(f"  OK: {yaml_file.name}")

    click.echo(f"\nBatch complete: {success} succeeded, {errors} failed")


@main.command()
@click.argument("old_yaml", type=click.Path(exists=True, dir_okay=False))
@click.argument("new_yaml", type=click.Path(exists=True, dir_okay=False))
@click.option("-o", "--output", default=None, help="Output diff diagram file.")
@click.option(
    "--format",
    "out_format",
    type=click.Choice(["svg", "png"]),
    default="svg",
    help="Output format.",
)
def diff(old_yaml: str, new_yaml: str, output: str | None, out_format: str) -> None:
    """Generate a visual diff between two YAML specs."""
    from redspec.diff import diff_specs
    from redspec.generator.diff_renderer import render_diff
    from redspec.yaml_io.parser import parse_yaml

    old_spec = parse_yaml(old_yaml)
    new_spec = parse_yaml(new_yaml)

    result = diff_specs(old_spec, new_spec)

    if result.is_empty:
        click.echo("No differences found.")
        return

    click.echo(f"Added: {len(result.added_resources)} resources, {len(result.added_connections)} connections")
    click.echo(f"Removed: {len(result.removed_resources)} resources, {len(result.removed_connections)} connections")
    click.echo(f"Changed: {len(result.changed_connections)} connections")

    if output:
        rendered = render_diff(old_spec, new_spec, output, out_format=out_format)
        click.echo(f"Diff diagram written to {rendered}")
