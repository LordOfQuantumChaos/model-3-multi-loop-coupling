"""Bootstrap standalone package: put repo root on sys.path for `import driven_loop`."""

from __future__ import annotations

import sys
from pathlib import Path

_BOOTSTRAPPED = False


def package_root() -> Path:
    """Repository root (parent of mode3_coupling/)."""
    return Path(__file__).resolve().parents[1]


def simulation_root() -> Path:
    """Root that contains the `driven_loop` package (repo root in standalone layout)."""
    return package_root()


def ensure_package_simulation(*, prefer_package: bool = True) -> Path:
    global _BOOTSTRAPPED
    root = simulation_root()
    if not prefer_package:
        return root
    if (root / "driven_loop" / "core.py").is_file():
        s = str(root)
        if s in sys.path:
            sys.path.remove(s)
        sys.path.insert(0, s)
        _BOOTSTRAPPED = True
    return root


def simulation_available() -> bool:
    return (simulation_root() / "driven_loop" / "core.py").is_file()
