"""Shared test fixtures."""

import shutil
import tempfile
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Return a temporary directory for test outputs."""
    return tmp_path


@pytest.fixture
def sample_svg() -> Path:
    """Path to a minimal valid SVG file."""
    return FIXTURES_DIR / "sample.svg"


@pytest.fixture
def minimal_yaml_path() -> Path:
    """Path to the minimal test YAML fixture."""
    return FIXTURES_DIR / "minimal.yaml"


@pytest.fixture
def nested_yaml_path() -> Path:
    """Path to the nested containers test YAML fixture."""
    return FIXTURES_DIR / "nested_containers.yaml"


@pytest.fixture
def mock_icon_dir(tmp_path, sample_svg):
    """Create a temp directory with fake SVG icons for registry tests."""
    icon_dir = tmp_path / "icons"
    icon_dir.mkdir()

    # Create fake icon files with realistic Azure naming
    icons = {
        "10035-icon-service-App-Services.svg": sample_svg,
        "10137-icon-service-SQL-Database.svg": sample_svg,
        "10061-icon-service-Virtual-Machines.svg": sample_svg,
        "10076-icon-service-Virtual-Networks.svg": sample_svg,
        "10029-icon-service-Resource-Groups.svg": sample_svg,
        "10038-icon-service-Function-Apps.svg": sample_svg,
        "10042-icon-service-Kubernetes-Services.svg": sample_svg,
        "10086-icon-service-Subnets-With-Delegation.svg": sample_svg,
    }
    for name, src in icons.items():
        shutil.copy(src, icon_dir / name)

    return icon_dir


@pytest.fixture
def mock_multi_pack_dir(tmp_path, sample_svg):
    """Create a temp directory with fake SVGs for multiple icon packs."""
    base = tmp_path / "icons"

    # Azure pack
    azure_dir = base / "azure"
    azure_dir.mkdir(parents=True)
    azure_icons = {
        "10035-icon-service-App-Services.svg": sample_svg,
        "10137-icon-service-SQL-Database.svg": sample_svg,
        "10061-icon-service-Virtual-Machines.svg": sample_svg,
    }
    for name, src in azure_icons.items():
        shutil.copy(src, azure_dir / name)

    # Dynamics 365 pack
    d365_dir = base / "dynamics365"
    d365_dir.mkdir()
    for name in ("Sales_scalable.svg", "Finance_scalable.svg"):
        shutil.copy(sample_svg, d365_dir / name)

    # Power Platform pack
    pp_dir = base / "power-platform"
    pp_dir.mkdir()
    for name in ("PowerApps_scalable.svg", "Dataverse_scalable.svg"):
        shutil.copy(sample_svg, pp_dir / name)

    return base
