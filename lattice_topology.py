"""
Spatial loop-lattice topology and bond geometry.

Grid layout
-----------
Loops are indexed row-major on a ``rows × cols`` grid. Each cell holds one ring.
Neighbour bonds use **4-connectivity** (east/west/north/south only — no diagonals):

::

    0 — 1 — 2
    |   |   |
    3 — 4 — 5
    |   |   |
    6 — 7 — 8   (3×3 example: 12 bonds total)

Corner rings have 2 bonds, edges 3, interior 4. This matches the pulse-hop
neighbour set and the velocity/position coupling graph.

Bond geometry
-------------
For each pair ``(a, b)`` we compute the centre-to-centre angle, align arc
indices so facing contact points couple (``loop_lattice_bond_arc_offset``), and
apply a Gaussian mask along each ring (reuses ``traveling_pulse_envelope`` shape
with ``loop_lattice_bond_width`` — same math as pulse localization, separate role).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Set, Tuple

import numpy as np

if TYPE_CHECKING:
    from driven_loop.core import SimConfig


def loop_lattice_centers(config: SimConfig) -> List[Tuple[float, float]]:
    rows = max(1, config.loop_lattice_rows)
    cols = max(1, config.loop_lattice_cols)
    spacing = config.loop_lattice_spacing * config.R0
    centers: List[Tuple[float, float]] = []
    for row in range(rows):
        for col in range(cols):
            cx = (col - (cols - 1) / 2.0) * spacing
            cy = (row - (rows - 1) / 2.0) * spacing
            centers.append((cx, cy))
    return centers


def loop_lattice_neighbor_pairs(config: SimConfig) -> List[Tuple[int, int]]:
    """Undirected nearest-neighbour bonds (each pair once, a < b)."""
    rows = max(1, config.loop_lattice_rows)
    cols = max(1, config.loop_lattice_cols)
    pairs: List[Tuple[int, int]] = []
    for row in range(rows):
        for col in range(cols):
            idx = row * cols + col
            if col + 1 < cols:
                pairs.append((idx, idx + 1))
            if row + 1 < rows:
                pairs.append((idx, idx + cols))
    return pairs


def _neighbor_adjacency(config: SimConfig) -> Dict[int, Set[int]]:
    """Adjacency list derived from ``loop_lattice_neighbor_pairs`` (single source of truth)."""
    adj: Dict[int, Set[int]] = {}
    for idx_a, idx_b in loop_lattice_neighbor_pairs(config):
        adj.setdefault(idx_a, set()).add(idx_b)
        adj.setdefault(idx_b, set()).add(idx_a)
    return adj


def loop_lattice_neighbors_of(config: SimConfig, loop_index: int) -> List[int]:
    """Sorted neighbour indices for pulse hops and diagnostics."""
    return sorted(_neighbor_adjacency(config).get(loop_index, ()))


def lattice_bond_angle(
    centers: List[Tuple[float, float]], idx_a: int, idx_b: int
) -> float:
    """Angle (radians) from loop ``idx_a`` centre toward ``idx_b``."""
    ax, ay = centers[idx_a]
    bx, by = centers[idx_b]
    return float(np.arctan2(by - ay, bx - ax))


def loop_lattice_bond_arc_offset(
    config: SimConfig,
    idx_a: int,
    idx_b: int,
) -> int:
    """
    Index shift so each loop couples arc points facing the neighbour, not same phase.
    """
    centers = loop_lattice_centers(config)
    bond_angle = lattice_bond_angle(centers, idx_a, idx_b)
    n = config.N
    ia = int(round((bond_angle % (2 * np.pi)) / (2 * np.pi) * n)) % n
    ib = int(round(((bond_angle + np.pi) % (2 * np.pi)) / (2 * np.pi) * n)) % n
    return (ib - ia) % n


def loop_lattice_phase_offset(config: SimConfig, loop_index: int) -> float:
    if config.loop_lattice_phase_jitter <= 0:
        return 0.0
    seed = (config.seed or 0) + loop_index * 997
    rng = np.random.RandomState(seed)
    return float(rng.uniform(-config.loop_lattice_phase_jitter, config.loop_lattice_phase_jitter))


def loop_reference_radius(config: SimConfig, loop_index: int = 0) -> float:
    if config.loop_lattice_enabled:
        if config.loop_lattice_radius_jitter > 0:
            seed = (config.seed or 0) + loop_index * 131
            rng = np.random.RandomState(seed)
            scale = 1.0 + config.loop_lattice_radius_jitter * (rng.rand() - 0.5) * 2.0
            return config.R0 * scale
        return config.R0
    if config.dual_loop_enabled and loop_index == 1:
        return config.R0 * config.dual_loop_radius_scale
    return config.R0