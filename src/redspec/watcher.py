"""Watch mode: auto-regenerate diagrams on file save."""

from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from pathlib import Path


def _get_mtime(path: Path) -> float:
    """Get file modification time, returning 0 if file doesn't exist."""
    try:
        return os.stat(path).st_mtime
    except OSError:
        return 0.0


def watch_loop(
    yaml_file: Path,
    on_rebuild: Callable[[Path], None],
    on_error: Callable[[Exception], None] | None = None,
    on_first_build: Callable[[Path], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
    poll_interval: float = 0.5,
) -> None:
    """Poll a YAML file for changes and trigger rebuilds.

    Args:
        yaml_file: Path to the YAML file to watch.
        on_rebuild: Called with the generated file path after each rebuild.
        on_error: Called with the exception on rebuild errors.
        on_first_build: Called once after the first successful build.
        should_stop: Return True to stop the loop.
        poll_interval: Seconds between polls.
    """
    from redspec.exceptions import RedspecError, YAMLParseError

    last_mtime = 0.0
    first_build_done = False

    while True:
        if should_stop and should_stop():
            break

        current_mtime = _get_mtime(yaml_file)
        if current_mtime > last_mtime:
            last_mtime = current_mtime
            try:
                result = _rebuild(yaml_file)
                if not first_build_done:
                    first_build_done = True
                    if on_first_build:
                        on_first_build(result)
                on_rebuild(result)
            except (RedspecError, YAMLParseError) as exc:
                if on_error:
                    on_error(exc)
            except Exception as exc:
                if on_error:
                    on_error(exc)

        time.sleep(poll_interval)


def _rebuild(yaml_file: Path) -> Path:
    """Parse and render the YAML file, returning the output path."""
    import tempfile

    from redspec.generator.pipeline import generate as run_pipeline
    from redspec.icons.registry import IconRegistry
    from redspec.yaml_io.parser import parse_yaml

    spec = parse_yaml(yaml_file)
    registry = IconRegistry()

    tmpdir = tempfile.mkdtemp(prefix="redspec-watch-")
    output = str(Path(tmpdir) / "diagram.svg")

    return run_pipeline(
        spec,
        output,
        icon_registry=registry,
        out_format="svg",
    )
