#!/usr/bin/env python3
"""Standalone demo — no monorepo required."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mode3_coupling.cli import cmd_demo

if __name__ == "__main__":
    raise SystemExit(cmd_demo())
