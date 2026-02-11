<p align="center">
  <strong>REDSPEC</strong><br>
  <em>Generate architecture diagrams from YAML declarations</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/version-0.1.0-red" alt="Version">
</p>

---

Redspec turns YAML architecture definitions into polished diagrams. Describe your infrastructure once, render it as PNG, SVG, or PDF, export to Mermaid/PlantUML/Draw.io, and keep everything version-controlled.

## Features

- **YAML-first** -- declare resources, connections, and groups in plain text
- **Multi-cloud** -- Azure, AWS, GCP, Kubernetes, Microsoft 365, Dynamics 365, Power Platform
- **Multiple output formats** -- PNG, SVG, PDF, plus text exports (Mermaid, PlantUML, Draw.io)
- **Themes** -- default, light, dark, presentation, or register your own
- **Web UI** -- interactive editor with live preview, gallery, and export controls
- **Watch mode** -- auto-regenerate on file save with live-reload
- **Diff visualization** -- compare two specs and see what changed
- **Azure import** -- pull live architecture from Azure Resource Graph
- **Linting** -- naming patterns, orphan detection, nesting depth checks
- **Batch processing** -- generate diagrams from an entire directory in parallel
- **GitHub Action** -- CI/CD integration for diagram generation on PRs
- **JSON Schema** -- IDE autocomplete and validation via yaml-language-server

## Quick Start

### Install

```bash
pip install redspec
```

For the web UI:

```bash
pip install redspec[web]
```

For Azure import:

```bash
pip install redspec[azure]
```

### Prerequisites

Redspec uses [Graphviz](https://graphviz.org/) under the hood. Install it for your platform:

```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows
choco install graphviz
```

### Create Your First Diagram

```bash
# Generate a starter YAML file
redspec init architecture.yaml

# Generate the diagram
redspec generate architecture.yaml -o diagram.png
```

## YAML Specification

```yaml
diagram:
  name: My Architecture
  theme: dark          # default | light | dark | presentation
  direction: TB        # TB | LR | BT | RL
  dpi: 150             # 72-600
  legend: true         # auto-generate icon legend
  animation: flow      # flow | pulse | build (SVG only)

variables:
  env: production
  region: eastus

resources:
  - type: azure/vnet
    name: main-vnet
    children:
      - type: azure/subnet
        name: app-subnet
        zone: private
        children:
          - type: azure/app-service
            name: web-app
      - type: azure/subnet
        name: db-subnet
        zone: private
        children:
          - type: azure/sql-database
            name: app-db

  - type: azure/application-gateway
    name: app-gateway
    zone: dmz

connection_styles:
  secure:
    style: bold
    color: "#00C853"

connections:
  - source: app-gateway
    to: web-app
    label: HTTPS
    style_ref: secure
  - source: web-app
    to: app-db
    label: SQL
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `redspec init [file]` | Create a starter YAML template |
| `redspec generate <yaml>` | Generate a diagram from YAML |
| `redspec validate <yaml>` | Validate a YAML file (with optional `--lint`) |
| `redspec batch <dir>` | Generate diagrams from all YAML files in a directory |
| `redspec diff <old> <new>` | Visual diff between two specs |
| `redspec watch <yaml>` | Watch and auto-regenerate on save |
| `redspec serve` | Start the web UI |
| `redspec clean` | List, edit, or delete generated output |
| `redspec import-azure` | Import from a live Azure subscription |
| `redspec update-icons` | Download icon packs |
| `redspec list-resources` | List available resource types |
| `redspec schema` | Output the JSON Schema |

### Generate Options

```bash
redspec generate arch.yaml \
  -o diagram.png \            # direct output path
  -d ./output \               # organized output directory
  --format svg \              # png | svg | pdf
  --theme dark \              # override theme
  --direction LR \            # override layout direction
  --dpi 300 \                 # override DPI
  --strict \                  # fail on missing icons
  --export-format mermaid \   # export to text format instead
  --report                    # generate PDF report
```

### Templates

```bash
redspec init my-infra.yaml --template azure        # Azure (default)
redspec init my-infra.yaml --template aws          # AWS
redspec init my-infra.yaml --template gcp          # Google Cloud
redspec init my-infra.yaml --template k8s          # Kubernetes
redspec init my-infra.yaml --template m365         # Microsoft 365
redspec init my-infra.yaml --template dynamics365  # Dynamics 365
redspec init my-infra.yaml --template power-platform
redspec init my-infra.yaml --template multi-cloud  # Cross-platform
```

### Clean Command

```bash
redspec clean                          # list generated diagrams with file details
redspec clean my-diagram               # delete a specific diagram
redspec clean --file diagram.png my-diagram  # delete a single file
redspec clean --edit my-diagram        # open spec.yaml in $EDITOR
redspec clean --all                    # remove entire output directory
redspec clean --dry-run --all          # preview what would be deleted
```

### Diff

```bash
redspec diff old.yaml new.yaml -o diff.svg
```

Outputs a visual diagram highlighting added (green), removed (red), and changed (orange) resources and connections.

### Watch Mode

```bash
redspec watch arch.yaml --port 9876 --format svg
```

Opens a browser with live-reload. Every time you save the YAML file, the diagram regenerates automatically.

## Web UI

```bash
redspec serve --port 8000
```

The web interface provides:

- **YAML editor** with syntax highlighting and autocomplete (Ctrl+Space)
- **Live preview** via WebSocket with debounced auto-generation
- **Template picker** for quick starts
- **Theme/direction/DPI controls** in the toolbar
- **Export dropdown** for Mermaid, PlantUML, and Draw.io
- **Diff modal** for comparing two YAML specs side-by-side
- **Gallery** with delete, load-into-editor, and download actions
- **Custom theme builder** for registering new themes at runtime
- **Zoom controls** for the preview panel

### Web API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/validate` | POST | Validate YAML with optional lint |
| `/api/generate` | POST | Generate diagram |
| `/api/export` | POST | Export to text format |
| `/api/diff` | POST | Diff two YAML specs |
| `/api/schema` | GET | JSON Schema |
| `/api/gallery` | GET | List gallery entries |
| `/api/gallery/{slug}` | DELETE | Delete a gallery entry |
| `/api/gallery/{slug}` | PATCH | Update spec or metadata |
| `/api/gallery/{slug}/spec` | GET | Parsed spec as JSON |
| `/api/themes/custom` | POST | Register a custom theme |
| `/api/templates` | GET | List available templates |
| `/api/resources` | GET | List resource types |

## Icon Packs

| Pack | Namespace | Description |
|------|-----------|-------------|
| Azure | `azure/` | Azure Public Service Icons (default, auto-downloads) |
| Microsoft 365 | `m365/` | Microsoft 365 Content Icons |
| Dynamics 365 | `dynamics365/` | Dynamics 365 Scalable Icons |
| Power Platform | `power-platform/` | Power Platform Scalable Icons |

Multi-cloud resource types (`aws/`, `gcp/`, `k8s/`) are mapped via the [diagrams](https://diagrams.mingrammer.com/) library and do not require separate icon downloads.

```bash
# Download all icon packs
redspec update-icons --all

# Check install status
redspec update-icons --list

# List all available resource types
redspec list-resources
redspec list-resources --pack dynamics365
```

## Azure Import

Pull a live architecture from an Azure subscription:

```bash
pip install redspec[azure]
redspec import-azure --subscription <subscription-id> -o imported.yaml
redspec import-azure --subscription <sub-id> --resource-group my-rg -o rg.yaml
```

This queries Azure Resource Graph, maps ARM resource types to redspec types, groups by resource group, and infers connections from known patterns (private endpoints, subnet attachments).

## Linting

```bash
redspec validate arch.yaml --lint
```

Built-in rules:
- **max_nesting_depth** -- warn when resource nesting exceeds threshold (default: 5)
- **naming_pattern** -- enforce naming conventions (default: `^[a-z0-9][a-z0-9-]*$`)
- **orphan_resources** -- detect resources with no connections
- **duplicate_connections** -- flag repeated source/target pairs

## GitHub Action

Add to your workflow to auto-generate diagrams on PRs:

```yaml
- uses: ./.github/actions/redspec-generate
  with:
    yaml-pattern: "**/*.yaml"
    output-dir: ./redspec-output
    format: svg
    post-comment: true
```

The action generates diagrams, uploads artifacts, and posts a PR comment with embedded images.

## Project Structure

```
src/redspec/
  cli.py              # CLI commands (Click)
  diff.py             # Spec diffing logic
  linter.py           # Validation rules
  watcher.py          # File watch loop
  watch_server.py     # WebSocket live-reload server
  generator/
    pipeline.py       # Main generation flow
    renderer.py       # Graphviz rendering with zones, legends, animations
    node_mapper.py    # Resource type -> diagram node mapping
    style_map.py      # Container/cluster style attributes
    themes.py         # Theme definitions + custom registration
    svg_enhancer.py   # SVG post-processing (glow effects)
    svg_animator.py   # SVG animation injection (flow/pulse/build)
    diff_renderer.py  # Diff visualization rendering
    output_organizer.py # Structured output with metadata
  models/
    diagram.py        # DiagramSpec, DiagramMeta, ZoneDef, AnnotationDef
    resource.py       # ResourceDef, ConnectionDef, ConnectionStyleDef
    lint.py           # LintConfig, LintWarning
  yaml_io/
    parser.py         # YAML parsing + validation
    scaffold.py       # Template generation (8 templates)
    includes.py       # File inclusion support
    interpolator.py   # Variable interpolation (${key})
  schemas/            # JSON Schema generation
  icons/              # Icon pack management
  exporters/          # Mermaid, PlantUML, Draw.io, PDF report
  importers/          # Azure Resource Graph import
  web/                # FastAPI web application
    app.py            # API endpoints
    templates/        # Jinja2 HTML
    static/           # JavaScript + CSS
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev,web]"

# Run tests
pytest

# Run linter
ruff check src/

# Type checking
mypy
```

## License

MIT
