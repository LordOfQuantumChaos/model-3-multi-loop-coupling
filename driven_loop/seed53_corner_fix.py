"""
Seed-53 targeted corner-loop fix and generalized corner boost (experiment only).

When fix_seed_53_enabled and seed matches target_seed, boosts lattice bonds
touching target_corner_loop and known-frequency amplitude on that loop
when loop activity exceeds memory_threshold. Optional 55° helical phase offset
on the corner loop's known-frequency drive.

When generalized_corner_boost_enabled, the same boosts apply to every lattice
corner loop (all seeds).
"""

from __future__ import annotations

from typing import List

import numpy as np

from driven_loop.core import SimConfig


def seed53_fix_active(config: SimConfig) -> bool:
    if not getattr(config, "fix_seed_53_enabled", False):
        return False
    target = int(getattr(config, "target_seed", 53))
    seed = getattr(config, "seed", None)
    return seed is not None and int(seed) == target


def generalized_corner_boost_active(config: SimConfig) -> bool:
    return bool(getattr(config, "generalized_corner_boost_enabled", False))


def corner_boost_active(config: SimConfig) -> bool:
    return seed53_fix_active(config) or generalized_corner_boost_active(config)


def corner_loop_indices(config: SimConfig) -> List[int]:
    rows = int(getattr(config, "loop_lattice_rows", 1))
    cols = int(getattr(config, "loop_lattice_cols", 1))
    if rows < 1 or cols < 1:
        return []
    last_row = rows - 1
    last_col = cols - 1
    return [0, last_col, last_row * cols, rows * cols - 1]


def is_corner_loop(config: SimConfig, loop_index: int) -> bool:
    if generalized_corner_boost_active(config):
        return loop_index in corner_loop_indices(config)
    if not seed53_fix_active(config):
        return False
    return loop_index == int(getattr(config, "target_corner_loop", 2))


def _bond_touches_corner(config: SimConfig, idx_a: int, idx_b: int) -> bool:
    if generalized_corner_boost_active(config):
        corners = set(corner_loop_indices(config))
        return idx_a in corners or idx_b in corners
    if not seed53_fix_active(config):
        return False
    corner = int(getattr(config, "target_corner_loop", 2))
    return idx_a == corner or idx_b == corner


def lattice_bond_coupling_scale(
    config: SimConfig,
    idx_a: int,
    idx_b: int,
) -> float:
    if not corner_boost_active(config):
        return 1.0
    if _bond_touches_corner(config, idx_a, idx_b):
        return float(getattr(config, "corner_coupling_boost", 1.4))
    return 1.0


def corner_frequency_amplitude_scale(
    config: SimConfig,
    loop_index: int,
    *,
    loop_activity: float | None = None,
    adaptive_memory=None,
) -> float:
    if not corner_boost_active(config) or not is_corner_loop(config, loop_index):
        return 1.0
    thresh = float(getattr(config, "memory_threshold", 0.35))
    boost = float(getattr(config, "corner_freq_amplitude_boost", 1.25))
    if adaptive_memory is not None:
        activity = float(adaptive_memory.activity_ema[loop_index])
    elif loop_activity is not None:
        activity = float(loop_activity)
    else:
        return 1.0
    return boost if activity > thresh else 1.0


def apply_helical_known_frequency_forces(
    config: SimConfig,
    drive: float,
    phase: np.ndarray,
    nx: np.ndarray,
    ny: np.ndarray,
    loop_index: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Decompose known-frequency drive into normal + tangential at helical_angle.
    Applies helical_phase_shift on the spatial mode.
    """
    k = int(getattr(config, "known_frequencies_mode", 3))
    shift = float(getattr(config, "helical_phase_shift", 0.35))
    alpha = np.deg2rad(float(getattr(config, "helical_angle", 55.0)))
    spatial = np.sin(k * phase + shift)
    fn = drive * spatial * np.cos(alpha)
    ft = drive * spatial * np.sin(alpha)
    tx = -ny
    ty = nx
    return fn * nx + ft * tx, fn * ny + ft * ty