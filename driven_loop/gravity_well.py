"""
GR-inspired central gravity well + gyroscopic potential barrier (experiment only).

Attraction:  F_gr ∝ −activity · r̂ / r²  (softened near r=0)
Stabilizer:  gyro damping scales with proximity  gyro_strength · (1 + R0/r)
Steering:    tangential kick when radial infall exceeds threshold (accretion orbit)

Also: weak **central_potential** path (enable_central_potential) — simple 1/r²
pull + linear radial multiplicative gyro damping, **no torque injection**.

Production: gr_well_enabled=False, enable_central_potential=False.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Tuple

import numpy as np

if TYPE_CHECKING:
    from driven_loop.sim_config import SimConfig


def _well_center(config: SimConfig) -> Tuple[float, float]:
    return float(config.gr_well_center_x), float(config.gr_well_center_y)


def _radial_geometry(
    x: np.ndarray,
    y: np.ndarray,
    cx: float,
    cy: float,
    softening: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rx = x - cx
    ry = y - cy
    r = np.sqrt(rx * rx + ry * ry + softening * softening)
    inv_r = 1.0 / r
    nx = rx * inv_r
    ny = ry * inv_r
    return rx, ry, r, nx, ny


def local_activity(
    config: SimConfig,
    vx: np.ndarray,
    vy: np.ndarray,
    deviation: np.ndarray,
    dx4: np.ndarray,
    dy4: np.ndarray,
) -> np.ndarray:
    from driven_loop.loop_material import resolve_loop_material

    mat = resolve_loop_material(config)
    kinetic = vx * vx + vy * vy
    curvature = dx4 * dx4 + dy4 * dy4
    potential = 0.5 * mat.radial_stiffness * deviation * deviation
    potential += 0.25 * config.cubic_stiffness * deviation ** 4
    return kinetic + mat.alpha * curvature + potential


def central_potential_active(config: "SimConfig") -> bool:
    """Instant off switch for the weak central potential experiment."""
    return bool(getattr(config, "enable_central_potential", False))


def central_potential_strength(config: "SimConfig") -> float:
    s = float(getattr(config, "central_potential_strength", 0.0) or 0.0)
    if s <= 0.0 and central_potential_active(config):
        # Fall back to gr_strength if user only set that
        s = float(getattr(config, "gr_strength", 0.0) or 0.0)
    return s


def central_potential_forces(
    config: "SimConfig",
    x: np.ndarray,
    y: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Weak central attractive force (1/r² style), linear geometry only.

    force_scale = -strength / r²
    fx += force_scale * x
    fy += force_scale * y

    No activity weighting, no torque. Soft floor min_r near origin.
    """
    if not central_potential_active(config):
        z = np.zeros_like(x)
        return z, z
    strength = central_potential_strength(config)
    if strength <= 0.0:
        z = np.zeros_like(x)
        return z, z

    min_r = float(getattr(config, "central_potential_min_r", 0.15) or 0.15)
    # Distance from lattice origin (well center at 0,0 for this experiment)
    r = np.sqrt(x * x + y * y) + 1e-8
    r = np.maximum(r, min_r)
    force_scale = -strength / (r * r)
    return force_scale * x, force_scale * y


def apply_central_gyro_velocity_damping(
    config: "SimConfig",
    x: np.ndarray,
    y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    dt: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Linear distance-dependent gyro damping (multiplicative on velocity).

    Stronger near center, milder farther out:
      gyro_factor = gyro_base * (1 + gyro_radial_boost * (R0 / r))
      v *= (1 - gyro_factor * dt)   with soft cap so scale stays positive
    """
    if not central_potential_active(config):
        return vx, vy
    gyro_base = float(getattr(config, "central_gyro_base", 0.12) or 0.0)
    if gyro_base <= 0.0:
        return vx, vy

    boost = float(getattr(config, "central_gyro_radial_boost", 0.35) or 0.0)
    R0 = float(getattr(config, "R0", 1.0) or 1.0)
    min_r = float(getattr(config, "central_potential_min_r", 0.15) or 0.15)
    cap = float(getattr(config, "central_gyro_dt_cap", 0.25) or 0.25)

    r = np.sqrt(x * x + y * y) + 1e-8
    r = np.maximum(r, min_r)
    # Linear (not exponential) radial boost
    gyro_factor = gyro_base * (1.0 + boost * (R0 / r))
    damp = gyro_factor * float(dt)
    if cap > 0:
        damp = np.minimum(damp, cap)
    scale = np.maximum(1.0 - damp, 0.0)
    return vx * scale, vy * scale


def central_potential_diagnostics(
    config: "SimConfig",
    x: np.ndarray,
    y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
) -> Dict[str, float]:
    """Ring / energy diagnostics near the lattice center."""
    if not central_potential_active(config):
        return {"enabled": 0.0}
    r = np.sqrt(x * x + y * y)
    min_r = float(getattr(config, "central_potential_min_r", 0.15) or 0.15)
    R0 = float(getattr(config, "R0", 1.0) or 1.0)
    kinetic = vx * vx + vy * vy
    near = r < 0.5 * R0
    very_near = r < min_r * 1.5
    return {
        "enabled": 1.0,
        "mean_r": float(np.mean(r)),
        "min_r_obs": float(np.min(r)),
        "frac_near_half_R0": float(np.mean(near)),
        "frac_very_near_min": float(np.mean(very_near)),
        "mean_kinetic": float(np.mean(kinetic)),
        "mean_kinetic_near": float(np.mean(kinetic[near])) if np.any(near) else 0.0,
        "max_kinetic": float(np.max(kinetic)),
    }


def gravity_well_attraction(
    config: SimConfig,
    x: np.ndarray,
    y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    deviation: np.ndarray,
    dx4: np.ndarray,
    dy4: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    if not config.gr_well_enabled or config.gr_strength <= 0:
        z = np.zeros_like(x)
        return z, z

    cx, cy = _well_center(config)
    _, _, r, nx, ny = _radial_geometry(x, y, cx, cy, config.gr_well_softening)
    activity = local_activity(config, vx, vy, deviation, dx4, dy4)
    r2 = np.maximum(r * r, config.gr_well_min_radius ** 2)
    magnitude = config.gr_strength * activity / r2
    if config.gr_force_cap > 0:
        magnitude = np.minimum(magnitude, config.gr_force_cap)
    # Inward pull toward well center
    return -magnitude * nx, -magnitude * ny


def gr_gyro_barrier_forces(
    config: SimConfig,
    x: np.ndarray,
    y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    *,
    gyro_gain_mult: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Proximity-scaled gyro damping — magnetic-like resistance near the well."""
    if not config.gr_gyro_barrier_enabled or config.gyro_strength <= 0:
        z = np.zeros_like(x)
        return z, z

    cx, cy = _well_center(config)
    _, _, r, _, _ = _radial_geometry(x, y, cx, cy, config.gr_well_softening)
    proximity = 1.0 + config.gr_gyro_proximity_scale * (config.R0 / r)
    speed = np.sqrt(vx * vx + vy * vy)
    speed_gate = np.tanh(speed / max(config.gyro_speed_scale, 1e-6))
    gyro = config.gyro_strength * gyro_gain_mult * proximity * (1.0 + speed_gate)
    return -gyro * vx, -gyro * vy


def gr_orbital_steering_forces(
    config: SimConfig,
    x: np.ndarray,
    y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    *,
    torque_gain_mult: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Tangential torque when infall speed exceeds threshold — promotes stable orbit."""
    if not config.gr_orbital_steering_enabled or config.gr_orbital_strength <= 0:
        z = np.zeros_like(x)
        return z, z

    cx, cy = _well_center(config)
    rx, ry, r, nx, ny = _radial_geometry(x, y, cx, cy, config.gr_well_softening)
    v_rad = (vx * rx + vy * ry) / r
    inward = v_rad < -config.gr_orbital_infall_threshold
    if not np.any(inward):
        z = np.zeros_like(x)
        return z, z

    tx = -ny
    ty = nx
    proximity = 1.0 + config.gr_gyro_proximity_scale * (config.R0 / r)
    steer = config.gr_orbital_strength * torque_gain_mult * np.abs(v_rad) * proximity
    steer = np.where(inward, steer, 0.0)
    # Bias tangential direction using sign of existing azimuthal motion
    v_tan = (vx * tx + vy * ty)
    sign = np.sign(v_tan)
    sign = np.where(sign == 0, 1.0, sign)
    return steer * sign * tx, steer * sign * ty


def gravity_well_stabilizer_forces(
    config: SimConfig,
    x: np.ndarray,
    y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    deviation: np.ndarray,
    dx4: np.ndarray,
    dy4: np.ndarray,
    *,
    gyro_gain_mult: float = 1.0,
    torque_gain_mult: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, float]]:
    """Combined GR well + gyro barrier + orbital steering."""
    diag: Dict[str, float] = {}
    if not (
        config.gr_well_enabled
        or config.gr_gyro_barrier_enabled
        or config.gr_orbital_steering_enabled
    ):
        z = np.zeros_like(x)
        return z, z, diag

    fx_gr, fy_gr = gravity_well_attraction(
        config, x, y, vx, vy, deviation, dx4, dy4,
    )
    fx_gy, fy_gy = gr_gyro_barrier_forces(
        config, x, y, vx, vy, gyro_gain_mult=gyro_gain_mult,
    )
    fx_or, fy_or = gr_orbital_steering_forces(
        config, x, y, vx, vy, torque_gain_mult=torque_gain_mult,
    )

    fx = fx_gr + fx_gy + fx_or
    fy = fy_gr + fy_gy + fy_or
    diag["gr_force_rms"] = float(np.sqrt(np.mean(fx_gr * fx_gr + fy_gr * fy_gr)))
    diag["gr_gyro_rms"] = float(np.sqrt(np.mean(fx_gy * fx_gy + fy_gy * fy_gy)))
    diag["gr_orbit_rms"] = float(np.sqrt(np.mean(fx_or * fx_or + fy_or * fy_or)))
    return fx, fy, diag