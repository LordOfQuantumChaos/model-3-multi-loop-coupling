"""
Unit tests for multi-loop coupling (no multi-hour campaign required).

Run from repository root:

  python -m pytest tests/ -q
  python -m mode3_coupling test
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mode3_coupling.bootstrap import ensure_package_simulation

ensure_package_simulation(prefer_package=True)

from driven_loop.lattice_coupling import (  # noqa: E402
    dual_loop_coupling_forces,
    inter_loop_pair_coupling_forces,
)
from driven_loop.lattice_topology import (  # noqa: E402
    loop_lattice_centers,
    loop_lattice_neighbor_pairs,
)
from driven_loop.multi_loop import loop_state_slice, num_sim_loops  # noqa: E402
from driven_loop.seed53_corner_fix import lattice_bond_coupling_scale  # noqa: E402


def test_pair_coupling_action_reaction_position():
    """Forces on A and B must sum to zero (action–reaction)."""
    n = 16
    rng = np.random.default_rng(42)
    xa, ya = rng.normal(size=n), rng.normal(size=n)
    xb, yb = xa + 0.15, ya - 0.08
    vxa = vya = vxb = vyb = np.zeros(n)
    fa_x, fa_y, fb_x, fb_y = inter_loop_pair_coupling_forces(
        xa, ya, vxa, vya, xb, yb, vxb, vyb, coupling=0.05, position_coupling=True
    )
    assert float(np.max(np.abs(fa_x + fb_x))) < 1e-10
    assert float(np.max(np.abs(fa_y + fb_y))) < 1e-10


def test_3x3_has_twelve_bonds():
    cfg = SimpleNamespace(loop_lattice_rows=3, loop_lattice_cols=3)
    pairs = loop_lattice_neighbor_pairs(cfg)
    assert len(pairs) == 12


def test_lattice_centers_shape():
    cfg = SimpleNamespace(
        loop_lattice_rows=3,
        loop_lattice_cols=3,
        loop_lattice_spacing=2.4,
        R0=1.0,
    )
    centers = loop_lattice_centers(cfg)
    assert len(centers) == 9


def test_num_sim_loops_3x3():
    cfg = SimpleNamespace(
        loop_lattice_enabled=True,
        loop_lattice_rows=3,
        loop_lattice_cols=3,
    )
    assert num_sim_loops(cfg) == 9


def test_loop_state_slice_bounds():
    cfg = SimpleNamespace(N=32)
    s = loop_state_slice(cfg, 0)
    assert s.start == 0
    assert s.stop == 32
    s1 = loop_state_slice(cfg, 1)
    assert s1.start == 32
    assert s1.stop == 64


def test_bond_scale_callable():
    cfg = SimpleNamespace(
        loop_lattice_rows=3,
        loop_lattice_cols=3,
        corner_coupling_boost=1.4,
        corner_boost_enabled=False,
    )
    scale = lattice_bond_coupling_scale(cfg, 0, 1)
    assert np.isfinite(scale)
    assert scale > 0


def test_package_info():
    from mode3_coupling import package_info

    info = package_info()
    assert info["name"]
    assert "not_scope" in info
    assert info["MODE3_PUMP_STABILITY_REL_VAR"] == 0.055
