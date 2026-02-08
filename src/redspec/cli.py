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
def generate(
    yaml_file: str,
    output: str | None,
    output_dir: str | None,
    out_format: str,
    strict: bool,
    direction: str | None,
    dpi: int | None,
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

    azure_pack = ALL_PACKS["azure"]
    if not azure_pack.downloaded_marker.exists():
        click.echo("Icons not found, downloading on first run...")
        download_icons()

    spec = parse_yaml(yaml_file)
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
        )
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
            )
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
    type=click.Choice(["azure", "m365", "dynamics365", "power-platform", "multi-cloud"]),
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
def validate(yaml_file: str) -> None:
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
