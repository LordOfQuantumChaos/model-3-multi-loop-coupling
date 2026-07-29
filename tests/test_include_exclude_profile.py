"""
Include / exclude discipline for intrinsic mode-3 claims.
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mode3_coupling.bootstrap import ensure_package_simulation

ensure_package_simulation(prefer_package=True)


def _sim_from_dict(d: dict):
    from driven_loop.sim_config import SimConfig

    fields = {f.name for f in dataclasses.fields(SimConfig)}
    return SimConfig(**{k: v for k, v in d.items() if k in fields})


def test_intrinsic_profile_lists_off_flags():
    from driven_loop.intrinsic_profile import (
        INTRINSIC_OFF_FLAGS,
        describe_profile,
    )

    prof = describe_profile()
    assert "intrinsic_off_flags" in prof
    assert len(INTRINSIC_OFF_FLAGS) >= 5
    assert "traveling_pulse_enabled" in INTRINSIC_OFF_FLAGS


def test_package_3x3_defaults_enable_lattice():
    from mode3_coupling import lattice_3x3_default_overrides

    ov = lattice_3x3_default_overrides()
    assert ov.get("loop_lattice_enabled") is True
    assert ov.get("loop_lattice_rows") == 3
    assert ov.get("loop_lattice_cols") == 3
    assert ov.get("loop_lattice_coupling") == 0.006
    assert ov.get("pump_mode") == 3
