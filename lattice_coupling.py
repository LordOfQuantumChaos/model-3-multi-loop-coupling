"""Inter-loop spring/velocity coupling: dual ring and spatial lattice bonds."""

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

import numpy as np

from driven_loop.lattice_topology import (
    lattice_bond_angle,
    loop_lattice_bond_arc_offset,
    loop_lattice_centers,
    loop_lattice_neighbor_pairs,
)

if TYPE_CHECKING:
    from driven_loop.core import SimConfig


def inter_loop_pair_coupling_forces(
    x_a: np.ndarray,
    y_a: np.ndarray,
    vx_a: np.ndarray,
    vy_a: np.ndarray,
    x_b: np.ndarray,
    y_b: np.ndarray,
    vx_b: np.ndarray,
    vy_b: np.ndarray,
    coupling: float,
    velocity_frac: float = 0.15,
    position_coupling: bool = True,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Spring (+ optional) and velocity damping between arc-aligned points on two loops."""
    k = coupling
    if position_coupling:
        fx_a = k * (x_b - x_a) - velocity_frac * k * (vx_b - vx_a)
        fy_a = k * (y_b - y_a) - velocity_frac * k * (vy_b - vy_a)
        fx_b = -k * (x_b - x_a) + velocity_frac * k * (vx_b - vx_a)
        fy_b = -k * (y_b - y_a) + velocity_frac * k * (vy_b - vy_a)
    else:
        fx_a = -velocity_frac * k * (vx_b - vx_a)
        fy_a = -velocity_frac * k * (vy_b - vy_a)
        fx_b = velocity_frac * k * (vx_b - vx_a)
        fy_b = velocity_frac * k * (vy_b - vy_a)
    return fx_a, fy_a, fx_b, fy_b


def dual_loop_coupling_forces(
    config: SimConfig,
    x: np.ndarray,
    y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Weak spring + velocity coupling between aligned points on two concentric rings."""
    if not config.dual_loop_enabled or config.dual_loop_coupling <= 0:
        return np.zeros_like(x), np.zeros_like(y)

    n = config.N
    fx_a, fy_a, fx_b, fy_b = inter_loop_pair_coupling_forces(
        x[:n], y[:n], vx[:n], vy[:n],
        x[n:], y[n:], vx[n:], vy[n:],
        config.dual_loop_coupling,
    )
    fx = np.concatenate([fx_a, fx_b])
    fy = np.concatenate([fy_a, fy_b])
    return fx, fy


def loop_lattice_coupling_forces(
    config: SimConfig,
    x: np.ndarray,
    y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Nearest-neighbor coupling on a rows×cols grid of spatially separated loops."""
    from driven_loop.core import arc_length_phase, traveling_pulse_envelope
    from driven_loop.multi_loop import loop_state_slice

    if not config.loop_lattice_enabled or config.loop_lattice_coupling <= 0:
        return np.zeros_like(x), np.zeros_like(y)

    fx = np.zeros_like(x)
    fy = np.zeros_like(y)
    k = config.loop_lattice_coupling
    n = config.N

    centers = loop_lattice_centers(config)
    width = max(config.loop_lattice_bond_width, 1e-6)
    phase_grid = arc_length_phase(n)

    for idx_a, idx_b in loop_lattice_neighbor_pairs(config):
        sl_a = loop_state_slice(config, idx_a)
        sl_b = loop_state_slice(config, idx_b)
        bond_angle = lattice_bond_angle(centers, idx_a, idx_b)
        mask_a = traveling_pulse_envelope(phase_grid, bond_angle, width)
        mask_b = traveling_pulse_envelope(phase_grid, bond_angle + np.pi, width)
        mask_a = mask_a / (np.max(mask_a) + 1e-12)
        mask_b = mask_b / (np.max(mask_b) + 1e-12)

        offset = loop_lattice_bond_arc_offset(config, idx_a, idx_b)
        order = (np.arange(n) + offset) % n
        from driven_loop.seed53_corner_fix import lattice_bond_coupling_scale

        bond_k = k * lattice_bond_coupling_scale(config, idx_a, idx_b)
        v_frac = float(getattr(config, "loop_lattice_velocity_frac", 0.15) or 0.15)
        fx_a, fy_a, fx_b, fy_b = inter_loop_pair_coupling_forces(
            x[sl_a], y[sl_a], vx[sl_a], vy[sl_a],
            x[sl_b][order], y[sl_b][order], vx[sl_b][order], vy[sl_b][order],
            bond_k,
            velocity_frac=v_frac,
            position_coupling=not config.loop_lattice_velocity_only,
        )
        inv = np.empty(n, dtype=int)
        inv[order] = np.arange(n)
        fx[sl_a] += fx_a * mask_a
        fy[sl_a] += fy_a * mask_a
        fx[sl_b] += fx_b[inv] * mask_b
        fy[sl_b] += fy_b[inv] * mask_b

    return fx, fy