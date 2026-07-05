"""Locate the skillctl registry and rules root.

Resolution order (first match wins):

1. ``SKILLCTL_HOME`` environment variable — explicit override
2. ``.skillctl/`` in the current working directory
3. ``.skillctl/`` walked up from cwd to the filesystem root

If nothing is found, callers should either run ``skillctl init`` or pass an
explicit path to the lower-level functions.
"""

from __future__ import annotations

import os
from pathlib import Path


def find_home(start: Path | None = None) -> Path | None:
    """Find the nearest ``.skillctl/`` directory, or return None."""
    env = os.environ.get("SKILLCTL_HOME")
    if env:
        p = Path(env).expanduser().resolve()
        return p if p.exists() else None

    cwd = (start or Path.cwd()).resolve()
    for candidate in [cwd, *cwd.parents]:
        marker = candidate / ".skillctl"
        if marker.is_dir():
            return marker
    return None


def require_home(start: Path | None = None) -> Path:
    """Find the home directory, or raise a helpful error."""
    home = find_home(start)
    if home is None:
        raise FileNotFoundError(
            "No .skillctl/ directory found. Run `skillctl init` in your "
            "project root, or set SKILLCTL_HOME to point at one."
        )
    return home


def index_path(home: Path | None = None) -> Path:
    """Path to the registry index file."""
    h = home or require_home()
    return h / "index.yaml"
