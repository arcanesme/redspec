"""Command-line interface for redspec."""

from pathlib import Path

import click


@click.group()
def main() -> None:
    """Redspec -- generate architecture diagrams from YAML."""
    from redspec.icons.migration import migrate_flat_cache

    migrate_flat_cache()


@main.command()
@click.argument("yaml_file", type=click.Path(exists=True, dir_okay=False))
@click.option("-o", "--output", default=None, help="Output .drawio file path.")
@click.option("--strict", is_flag=True, default=False, help="Fail on missing icons.")
def generate(yaml_file: str, output: str | None, strict: bool) -> None:
    """Generate a .drawio diagram from a YAML architecture file."""
    from redspec.icons.downloader import download_icons
    from redspec.icons.packs import ALL_PACKS
    from redspec.icons.registry import IconRegistry
    from redspec.icons.embedder import embed_svg
    from redspec.generator.pipeline import generate as run_pipeline
    from redspec.yaml_io.parser import parse_yaml

    azure_pack = ALL_PACKS["azure"]
    if not azure_pack.downloaded_marker.exists():
        click.echo("Icons not found, downloading on first run...")
        download_icons()

    spec = parse_yaml(yaml_file)

    if output is None:
        output = str(Path(yaml_file).with_suffix(".drawio"))

    registry = IconRegistry()
    run_pipeline(spec, output, icon_registry=registry, embedder_fn=embed_svg, strict=strict)
    click.echo(f"Diagram written to {output}")


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
