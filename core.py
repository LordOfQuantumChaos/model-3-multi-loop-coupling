"""Driven-loop dynamics engine.

Import profile
--------------
Intrinsic lattice / mode-3 path loads only core + lattice + gravity_well helpers.
Optional product plugins (PAC, plasma, radiation, QSLT, pulse hop, ...) are
resolved lazily via module ``__getattr__`` — see ``driven_loop.intrinsic_profile``.
"""

from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from collections import Counter

# SimConfig lives in its own module (sectioned fields + helpers).
# Re-exported here so existing `from driven_loop.core import SimConfig` keeps working.
from driven_loop.sim_config import CONFIG_SECTIONS, SimConfig  # noqa: F401

# --- Intrinsic core (always required for mode-3 multi-loop coupling) ---
from driven_loop.lattice_coupling import (
    dual_loop_coupling_forces,
    inter_loop_pair_coupling_forces,
    loop_lattice_coupling_forces,
)
from driven_loop.lattice_topology import (
    lattice_bond_angle,
    loop_lattice_bond_arc_offset,
    loop_lattice_centers,
    loop_lattice_neighbor_pairs,
    loop_lattice_neighbors_of,
    loop_lattice_phase_offset,
    loop_reference_radius,
)
from driven_loop.multi_loop import (
    is_multi_loop_system,
    loop_state_slice,
    num_sim_loops,
    primary_loop_index,
)
from driven_loop.gravity_well import (
    apply_central_gyro_velocity_damping,
    central_potential_diagnostics,
    central_potential_forces,
    gravity_well_stabilizer_forces,
    local_activity,
)
from driven_loop.loop_material import material_summary, resolve_loop_material
from driven_loop.intrinsic_profile import (
    CORE_OPTIONAL_ATTRS,
    load_core_optional_attr,
)

# Optional plugin symbols (PAC, plasma, radiation, QSLT, pulse transport, ...)
# are bound as lazy proxies so bare names inside this module work (LOAD_GLOBAL).
# Module __getattr__ alone is NOT enough for in-module bare names (NameError).


class _LazyOptional:
    """Resolve optional plugin attr on first use; cache into module globals."""

    __slots__ = ("_name",)

    def __init__(self, name: str) -> None:
        object.__setattr__(self, "_name", name)

    def _resolve(self) -> Any:
        name = object.__getattribute__(self, "_name")
        val = load_core_optional_attr(name)
        globals()[name] = val
        return val

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._resolve()(*args, **kwargs)

    def __getattr__(self, item: str) -> Any:
        return getattr(self._resolve(), item)

    def __repr__(self) -> str:
        return f"<LazyOptional {object.__getattribute__(self, '_name')!r}>"


for _opt_name in CORE_OPTIONAL_ATTRS:
    globals()[_opt_name] = _LazyOptional(_opt_name)
del _opt_name


def __getattr__(name: str) -> Any:
    """External access: from driven_loop.core import gyro_pll_active."""
    if name in CORE_OPTIONAL_ATTRS:
        return load_core_optional_attr(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> List[str]:
    return sorted(set(globals().keys()) | set(CORE_OPTIONAL_ATTRS.keys()))



def tail_window_for(frames: int) -> int:
    return max(200, min(500, frames // 8))


def fourth_derivative_stencil(arr: np.ndarray) -> np.ndarray:
    return (
        np.roll(arr, -2)
        - 4 * np.roll(arr, -1)
        + 6 * arr
        - 4 * np.roll(arr, 1)
        + np.roll(arr, 2)
    )


def fourth_derivative_uniform(arr: np.ndarray, spacing: float, spacing_ref: float) -> np.ndarray:
    return fourth_derivative_stencil(arr) * (spacing_ref / spacing) ** 4


def second_derivative_stencil(arr: np.ndarray) -> np.ndarray:
    return np.roll(arr, -1) - 2 * arr + np.roll(arr, 1)


def second_derivative_uniform(arr: np.ndarray, spacing: float, spacing_ref: float) -> np.ndarray:
    return second_derivative_stencil(arr) * (spacing_ref / spacing) ** 2


def asymmetry_modulation(
    phase: np.ndarray, strength: float, mode: int, phase_offset: float
) -> np.ndarray:
    if strength == 0.0:
        return np.ones_like(phase)
    return 1.0 + strength * np.cos(mode * phase + phase_offset)


def sector_mask(phase: np.ndarray, mode: int, phase_offset: float) -> np.ndarray:
    return 0.5 * (1.0 + np.cos(mode * phase + phase_offset))


def segment_lengths(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    dx = np.roll(x, -1) - x
    dy = np.roll(y, -1) - y
    return np.sqrt(dx**2 + dy**2 + 1e-12)


def perimeter(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.sum(segment_lengths(x, y)))


def tension_forces(
    x: np.ndarray, y: np.ndarray, target_h: float, stiffness: float
) -> Tuple[np.ndarray, np.ndarray]:
    dx = np.roll(x, -1) - x
    dy = np.roll(y, -1) - y
    lengths = np.sqrt(dx**2 + dy**2 + 1e-12)
    stretch = lengths - target_h
    tx = dx / lengths
    ty = dy / lengths
    fmag = stiffness * stretch
    fx_seg = fmag * tx
    fy_seg = fmag * ty
    return fx_seg - np.roll(fx_seg, 1), fy_seg - np.roll(fy_seg, 1)


def tension_curvature_forces(
    x: np.ndarray,
    y: np.ndarray,
    target_h: float,
    curvature_stiffness: float,
    spacing_ref: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """Force from d²(stretch)/ds² — smooths sharp tension gradients, supports wave-like internal motion."""
    if curvature_stiffness == 0.0:
        return np.zeros_like(x), np.zeros_like(y)

    seg_len = segment_lengths(x, y)
    n = len(x)
    seg_spacing = float(np.sum(seg_len)) / n
    d2_stretch = second_derivative_uniform(seg_len - target_h, seg_spacing, spacing_ref)

    dx = np.roll(x, -1) - x
    dy = np.roll(y, -1) - y
    lengths = np.sqrt(dx**2 + dy**2 + 1e-12)
    tx = dx / lengths
    ty = dy / lengths
    fmag = -curvature_stiffness * d2_stretch
    fx_seg = fmag * tx
    fy_seg = fmag * ty
    return fx_seg - np.roll(fx_seg, 1), fy_seg - np.roll(fy_seg, 1)


def internal_dynamics_forces(
    x: np.ndarray,
    y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    phase: np.ndarray,
    target_h: float,
    strength: float,
    mode: int,
    enabled: bool,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Stretch–velocity coupling: pumps energy from segment stretch anomalies into normal motion.
    Can sustain motion without external forcing when strength is large enough.
    """
    if not enabled or strength == 0.0:
        return np.zeros_like(x), np.zeros_like(y)

    stretch = segment_lengths(x, y) - target_h
    stretch_anom = stretch - np.mean(stretch)
    envelope = np.sin(mode * phase)
    r = np.sqrt(x**2 + y**2 + 1e-12)
    nx = x / r
    ny = y / r
    vn = vx * nx + vy * ny
    # Stress bias seeds motion from rest; velocity coupling sustains it.
    stress = 0.4 * strength * stretch_anom * envelope
    pump = strength * stretch_anom * vn * envelope
    drive = stress + pump
    return drive * nx, drive * ny


def arc_length_phase(N: int) -> np.ndarray:
    return 2 * np.pi * np.arange(N) / N


def resample_uniform_arclength(
    x: np.ndarray, y: np.ndarray, vx: np.ndarray, vy: np.ndarray, N: int
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    seg_len = segment_lengths(x, y)
    total_L = float(np.sum(seg_len))
    if total_L < 1e-10:
        return x, y, vx, vy

    cum = np.concatenate([[0.0], np.cumsum(seg_len[:-1])])
    targets = np.linspace(0.0, total_L, N, endpoint=False)
    x_new = np.zeros(N)
    y_new = np.zeros(N)
    vx_new = np.zeros(N)
    vy_new = np.zeros(N)

    for k, s in enumerate(targets):
        i = int(np.searchsorted(cum, s, side="right") - 1)
        i = min(max(i, 0), N - 1)
        j = (i + 1) % N
        s0 = cum[i]
        s1 = total_L if i == N - 1 else cum[i + 1]
        alpha = 0.0 if s1 <= s0 else (s - s0) / (s1 - s0)
        x_new[k] = (1 - alpha) * x[i] + alpha * x[j]
        y_new[k] = (1 - alpha) * y[i] + alpha * y[j]
        vx_new[k] = (1 - alpha) * vx[i] + alpha * vx[j]
        vy_new[k] = (1 - alpha) * vy[i] + alpha * vy[j]

    x_new -= np.mean(x_new)
    y_new -= np.mean(y_new)
    return x_new, y_new, vx_new, vy_new


def mean_segment_stretch(x: np.ndarray, y: np.ndarray, target_h: float) -> float:
    return float(np.mean(np.abs(segment_lengths(x, y) - target_h) / (target_h + 1e-12)))


def radial_potential(deviation: np.ndarray, cubic_stiffness: float) -> np.ndarray:
    return deviation**2 + (cubic_stiffness / 4.0) * deviation**4


def radial_restoring_accel(
    deviation: np.ndarray, nx: np.ndarray, ny: np.ndarray,
    radial_stiffness: float, cubic_stiffness: float,
) -> Tuple[np.ndarray, np.ndarray]:
    dU = 2.0 * deviation + cubic_stiffness * deviation**3
    return -radial_stiffness * dU * nx, -radial_stiffness * dU * ny


def effective_velocity_damping(
    config: SimConfig,
    phase: np.ndarray,
    deviation: np.ndarray,
) -> np.ndarray:
    """
    Per-point velocity damping coefficient.
    Combines baseline, sector instability, threshold anti-damping, and Van der Pol term.
    Van der Pol: beta_eff -= mu * (1 - (dev/s)^2)  -> negative damping at small |dev|.
    Threshold: beta_eff -= gain * smooth_step(threshold - |dev|)  -> pump when nearly circular.
    """
    beta = (
        resolve_loop_material(config).beta
        - config.instability_gain * sector_mask(
            phase, config.instability_mode, config.instability_phase
        )
    )

    if config.threshold_excitation_enabled and config.threshold_excitation_gain > 0:
        below = 0.5 * (
            1.0
            + np.tanh(
                (config.threshold_deformation - np.abs(deviation))
                / max(config.threshold_sharpness, 1e-6)
            )
        )
        beta = beta - config.threshold_excitation_gain * below

    if config.vdp_enabled and config.vdp_mu != 0:
        scale = max(config.vdp_dev_scale, 1e-6)
        x_norm = np.clip(deviation / scale, -1.5, 1.5)
        vdp_term = config.vdp_mu * (1.0 - x_norm**2)
        if config.vdp_cap_enabled:
            cap = np.exp(-((np.abs(deviation) / max(config.vdp_cap_dev_scale, 1e-6)) ** 2))
            vdp_term = vdp_term * cap
        beta = beta - vdp_term

    return beta


def local_gyro_coefficient(
    config: SimConfig,
    vx: np.ndarray,
    vy: np.ndarray,
    deviation: np.ndarray,
    dx4: np.ndarray,
    dy4: np.ndarray,
) -> np.ndarray:
    """
    Per-point gyro: each node damps in proportion to its own motion and amplitude.
    Weak local motion -> low damping (allow growth). Strong speed, |dev|, or curvature -> damp.
    """
    local_speed = np.sqrt(vx**2 + vy**2)
    amp = np.abs(deviation)
    curvature = np.sqrt(dx4**2 + dy4**2)

    speed_gate = np.tanh(local_speed / max(config.gyro_speed_scale, 1e-6))
    amp_gate = np.tanh(amp / max(config.gyro_amp_scale, 1e-6))
    curv_gate = np.tanh(curvature / max(config.gyro_curv_scale, 1e-6))

    # Runaway suppression: any local hot spot triggers damping at that point only.
    motion_score = np.maximum(np.maximum(speed_gate, amp_gate), curv_gate)

    # Deformation onset: nearly circular points feel little gyro brake.
    onset = 0.5 * (
        1.0
        + np.tanh(
            (amp - config.gyro_onset_deformation) / max(config.gyro_onset_sharpness, 1e-6)
        )
    )

    return config.gyro_strength * motion_score * onset


def apply_gyro_damping(
    config: SimConfig,
    vx: np.ndarray,
    vy: np.ndarray,
    deviation: np.ndarray,
    dx4: np.ndarray,
    dy4: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return gyro force contribution (fx_gyro, fy_gyro) — already negative damping."""
    if not config.gyro_enabled or config.gyro_strength <= 0:
        return np.zeros_like(vx), np.zeros_like(vy)

    if config.gyro_mode == "local":
        gyro = local_gyro_coefficient(config, vx, vy, deviation, dx4, dy4)
    else:
        kinetic = float(np.mean(vx**2 + vy**2))
        gyro = config.gyro_strength * (1.0 + np.tanh(kinetic / 50.0))

    return -gyro * vx, -gyro * vy


def extract_protected_mode_band(arr: np.ndarray, protect: int) -> np.ndarray:
    """Keep only the protected pump Fourier mode (k and N-k)."""
    n = len(arr)
    fft = np.fft.fft(arr)
    mask = np.zeros(n)
    half = n // 2
    if 0 < protect <= half:
        mask[protect] = 1.0
        if protect < n - protect:
            mask[n - protect] = 1.0
    return np.real(np.fft.ifft(fft * mask))


def extract_damped_mode_band(arr: np.ndarray, protect: int, damp_from: int) -> np.ndarray:
    """Keep only Fourier modes >= damp_from, excluding the protected pump mode."""
    n = len(arr)
    fft = np.fft.fft(arr)
    mask = np.zeros(n)
    half = n // 2
    for k in range(1, half + 1):
        if k == protect:
            continue
        if k >= damp_from:
            mask[k] = 1.0
            if k < n - k:
                mask[n - k] = 1.0
    return np.real(np.fft.ifft(fft * mask))


def extract_non_pump_modes(arr: np.ndarray, protect: int) -> np.ndarray:
    """Keep all Fourier modes except the protected pump mode (and DC)."""
    n = len(arr)
    fft = np.fft.fft(arr)
    mask = np.ones(n)
    half = n // 2
    if 0 < protect <= half:
        mask[protect] = 0.0
        if protect < n - protect:
            mask[n - protect] = 0.0
    mask[0] = 0.0
    return np.real(np.fft.ifft(fft * mask))


def traveling_pulse_envelope(
    phase: np.ndarray, pulse_phase: float, width: float
) -> np.ndarray:
    delta = np.angle(np.exp(1j * (phase - pulse_phase)))
    return np.exp(-0.5 * (delta / max(width, 1e-6)) ** 2)


def traveling_pulse_beta_reduction(
    config: SimConfig,
    phase: np.ndarray,
    pulse_phase: float,
    frame: int = 0,
    pulse_active: bool = True,
) -> np.ndarray:
    # Gate on config before importing pulse_transport (lazy optional).
    if (
        not pulse_active
        or not getattr(config, "traveling_pulse_enabled", False)
        or config.traveling_pulse_injection != "anti_damp"
        or not traveling_pulse_active(config, frame)
    ):
        return np.zeros(len(phase))

    env = traveling_pulse_envelope(phase, pulse_phase, config.traveling_pulse_width)
    shape = np.sin(config.traveling_pulse_shape_mode * phase)
    return config.traveling_pulse_strength * env * np.maximum(shape, 0.0)


def traveling_pulse_forces(
    config: SimConfig,
    phase: np.ndarray,
    nx: np.ndarray,
    ny: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    pulse_phase: float,
    frame: int = 0,
    pulse_active: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """Localized pulse injection: drive, tangential kick, or handled via anti_damp."""
    if (
        not pulse_active
        or not getattr(config, "traveling_pulse_enabled", False)
        or not traveling_pulse_active(config, frame)
    ):
        return np.zeros_like(nx), np.zeros_like(ny)

    if config.traveling_pulse_injection == "anti_damp":
        return np.zeros_like(nx), np.zeros_like(ny)

    env = traveling_pulse_envelope(phase, pulse_phase, config.traveling_pulse_width)
    k = config.traveling_pulse_shape_mode
    strength = config.traveling_pulse_strength * env

    if config.traveling_pulse_injection == "drive":
        fn = strength * np.sin(k * phase)
        return fn * nx, fn * ny

    if config.traveling_pulse_injection == "kick":
        tx = -ny
        ty = nx
        return strength * tx, strength * ty

    return np.zeros_like(nx), np.zeros_like(ny)


def low_mode_parasite_damping_forces(
    config: SimConfig,
    vx: np.ndarray,
    vy: np.ndarray,
    nx: np.ndarray,
    ny: np.ndarray,
    frame: int = 0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Extra drain on low Fourier modes (k=1..max) — keeps basin from mode-1 takeover."""
    if not config.mode_damp_low_modes_enabled or config.mode_damp_low_strength <= 0:
        return np.zeros_like(vx), np.zeros_like(vy)
    if config.mode_damp_low_ramp_only and config.gamma_ramp_enabled:
        damp_end = config.mode_damp_low_decay_frames
        if damp_end is None:
            damp_end = config.gamma_ramp_decay_frames
        if frame >= damp_end:
            return np.zeros_like(vx), np.zeros_like(vy)

    vn = vx * nx + vy * ny
    n = len(vn)
    fft = np.fft.fft(vn)
    mask = np.zeros(n)
    max_k = max(1, int(config.mode_damp_low_max_mode))
    for k in range(1, max_k + 1):
        if k < n - k:
            mask[k] = 1.0
            mask[n - k] = 1.0
    vn_low = np.real(np.fft.ifft(fft * mask))
    damp = -config.mode_damp_low_strength * vn_low
    return damp * nx, damp * ny


def mode_selective_damping_forces(
    config: SimConfig,
    vx: np.ndarray,
    vy: np.ndarray,
    nx: np.ndarray,
    ny: np.ndarray,
    deviation: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Damp only parasitic modes in the normal-velocity field; protect the pump mode.
    Lets the preferred mode self-excite while suppressing runaway harmonics.
    """
    if not config.mode_selective_damp_enabled or config.mode_damp_strength <= 0:
        return np.zeros_like(vx), np.zeros_like(vy)

    vn = vx * nx + vy * ny
    if config.mode_damp_non_pump_only:
        vn_para = extract_non_pump_modes(vn, config.mode_protect)
    else:
        vn_para = extract_damped_mode_band(
            vn, config.mode_protect, config.mode_damp_from
        )
    damp_n = -config.mode_damp_strength * vn_para
    return damp_n * nx, damp_n * ny


def conservative_mode_coupling_forces(
    config: SimConfig,
    deviation: np.ndarray,
    phase: np.ndarray,
    nx: np.ndarray,
    ny: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Conservative coupling potential U = eps/2 * (dev * sin(k*phi))^2.
    Energy sloshes within the pump mode without external drive.
    """
    if not config.conservative_coupling_enabled or config.conservative_coupling_eps <= 0:
        return np.zeros_like(deviation), np.zeros_like(deviation)

    k = config.conservative_coupling_mode
    envelope = np.sin(k * phase)
    dU = config.conservative_coupling_eps * deviation * envelope**2
    return -dU * nx, -dU * ny


def pump_mode_duffing_forces(
    config: SimConfig,
    deviation: np.ndarray,
    phase: np.ndarray,
    nx: np.ndarray,
    ny: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Duffing saturator on the pump mode only: U = -soft/2 * q^2 + hard/4 * q^4, q = dev*sin(k*phi).
    Positive softening destabilizes the circular state; hardening caps amplitude.
    """
    if not config.pump_limit_cycle_enabled:
        return np.zeros_like(deviation), np.zeros_like(deviation)
    if config.pump_softening <= 0 and config.pump_hardening <= 0:
        return np.zeros_like(deviation), np.zeros_like(deviation)

    k = config.pump_mode
    envelope = np.sin(k * phase)
    q = deviation * envelope
    fn = (config.pump_softening * q - config.pump_hardening * q**3) * envelope
    return fn * nx, fn * ny


def pump_amplitude_limiter_forces(
    config: SimConfig,
    deviation: np.ndarray,
    nx: np.ndarray,
    ny: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Soft cap on pump-mode amplitude: pulls only the protected modal band when
    excursions grow too large, tightening long-run limit cycles without
    dumping energy into k=1,2 (unlike global low-mode damp).
    """
    if (
        not config.pump_amplitude_limiter_enabled
        or config.pump_amplitude_limiter_strength <= 0
        or not config.pump_limit_cycle_enabled
    ):
        return np.zeros_like(deviation), np.zeros_like(deviation)

    dev_pump = extract_protected_mode_band(deviation, config.pump_mode)
    scale = max(config.pump_amplitude_limiter_scale, 1e-6)
    over = np.maximum(np.abs(dev_pump) / scale - 1.0, 0.0)
    fn = (
        -config.pump_amplitude_limiter_strength
        * dev_pump
        * over**2
        / (1.0 + over**2)
    )
    return fn * nx, fn * ny


def pump_mode_vdp_forces(
    config: SimConfig,
    vx: np.ndarray,
    vy: np.ndarray,
    nx: np.ndarray,
    ny: np.ndarray,
    deviation: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Van der Pol damping applied only to the pump-mode normal velocity component.
    Negative damping at small pump amplitude, positive at large amplitude -> limit cycle.
    """
    if not config.pump_limit_cycle_enabled or not config.pump_vdp_enabled:
        return np.zeros_like(vx), np.zeros_like(vy)
    if config.pump_vdp_mu <= 0:
        return np.zeros_like(vx), np.zeros_like(vy)

    vn = vx * nx + vy * ny
    vn_pump = extract_protected_mode_band(vn, config.pump_mode)
    dev_pump = extract_protected_mode_band(deviation, config.pump_mode)
    scale = max(config.pump_vdp_dev_scale, 1e-6)
    amp = np.clip(dev_pump / scale, -2.0, 2.0)
    beta_pump = config.pump_vdp_mu * (1.0 - amp**2)
    damp_n = -beta_pump * vn_pump
    return damp_n * nx, damp_n * ny


def field_curvature_tension_forces(
    config: SimConfig,
    dx4: np.ndarray,
    dy4: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Symmetric field-mediated bending resistance (mesh-aware curvature, not /dx**4).
    Local excess curvature relative to a short-range field average is pushed back.
    """
    if config.field_curvature_tension <= 0:
        return np.zeros_like(dx4), np.zeros_like(dy4)

    ft = config.field_curvature_tension
    smooth_x = 0.5 * dx4 + 0.25 * np.roll(dx4, 1) + 0.25 * np.roll(dx4, -1)
    smooth_y = 0.5 * dy4 + 0.25 * np.roll(dy4, 1) + 0.25 * np.roll(dy4, -1)
    return -ft * (dx4 - smooth_x), -ft * (dy4 - smooth_y)


def velocity_beta_coefficient(
    config: SimConfig,
    phase: np.ndarray,
    deviation: np.ndarray,
) -> np.ndarray:
    n_pts = len(deviation)
    if config.pump_limit_cycle_enabled:
        beta_eff = np.zeros(n_pts)
    elif config.dissipation_minimal:
        beta_eff = np.full(config.N, config.beta_minimal)
        if config.vdp_enabled or config.threshold_excitation_enabled:
            beta_base = resolve_loop_material(config).beta
            beta_eff = beta_eff + (
                effective_velocity_damping(config, phase, deviation) - beta_base
            )
    else:
        beta_eff = effective_velocity_damping(config, phase, deviation)
    return beta_eff


def frame_energy_ledger(
    config: SimConfig,
    x: np.ndarray,
    y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    phase: np.ndarray,
    deviation: np.ndarray,
    dx4: np.ndarray,
    dy4: np.ndarray,
    frame: int,
    target_h: float,
    spacing_ref: float,
) -> Dict[str, float]:
    """Per-frame energy storage and power accounting (inject / dissipate / stored)."""
    n_pts = len(x)
    if len(phase) != n_pts:
        if is_multi_loop_system(config):
            phase = np.concatenate(
                [arc_length_phase(config.N) for _ in range(num_sim_loops(config))]
            )
        else:
            phase = arc_length_phase(n_pts)

    r = np.sqrt(x**2 + y**2 + 1e-12)
    nx = x / r
    ny = y / r
    beta_eff = velocity_beta_coefficient(config, phase, deviation)
    mat = resolve_loop_material(config)

    kinetic = 0.5 * mat.mass_per_node * float(np.mean(vx**2 + vy**2))
    bending = 0.5 * mat.alpha * float(np.mean(dx4**2 + dy4**2))
    radial = 0.5 * float(np.mean(radial_potential(deviation, config.cubic_stiffness)))
    stretch = mean_segment_stretch(x, y, target_h)
    stretch_e = 0.5 * stretch**2
    stored = kinetic + bending + radial + stretch_e

    power_drive = 0.0
    gamma_eff = effective_drive_gamma(config, frame)
    if gamma_eff > 0:
        drive_k = effective_drive_mode(config)
        drive = gamma_eff * np.sin(drive_k * phase)
        power_drive = float(np.mean((drive * nx) * vx + (drive * ny) * vy))

    bfx, bfy = mode_bootstrap_forces(config, phase, nx, ny, frame)
    power_bootstrap = float(np.mean(bfx * vx + bfy * vy))

    power_beta = float(-np.mean(beta_eff * (vx**2 + vy**2)))

    msx, msy = mode_selective_damping_forces(config, vx, vy, nx, ny, deviation)
    power_mode_damp = float(np.mean(msx * vx + msy * vy))

    pvx, pvy = pump_mode_vdp_forces(config, vx, vy, nx, ny, deviation)
    power_pump_vdp = float(np.mean(pvx * vx + pvy * vy))

    if not config.pump_limit_cycle_enabled:
        gfx, gfy = apply_gyro_damping(config, vx, vy, deviation, dx4, dy4)
        power_gyro = float(np.mean(gfx * vx + gfy * vy))
    else:
        power_gyro = 0.0

    power_inject = power_drive + power_bootstrap
    power_diss = power_beta + power_mode_damp + power_pump_vdp + power_gyro

    return {
        "stored": stored,
        "power_inject": power_inject,
        "power_diss": power_diss,
        "power_drive": power_drive,
        "power_bootstrap": power_bootstrap,
        "kinetic": kinetic,
        "bending": bending,
        "radial": radial,
    }


def circular_field_smooth(arr: np.ndarray, sigma_nodes: float) -> np.ndarray:
    """Gaussian propagation of a scalar field around the closed loop."""
    n = len(arr)
    idx = np.arange(n)
    dist = np.minimum(idx, n - idx).astype(float)
    kernel = np.exp(-0.5 * (dist / max(sigma_nodes, 0.5)) ** 2)
    kernel /= np.sum(kernel) + 1e-12
    return np.real(np.fft.ifft(np.fft.fft(arr) * np.fft.fft(kernel)))


def distributed_field_restoring_forces(
    config: SimConfig,
    x: np.ndarray,
    y: np.ndarray,
    deviation: np.ndarray,
    nx: np.ndarray,
    ny: np.ndarray,
    spacing_ref: float,
    target_h: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Field-mediated restoring: local bend/stretch/deviation creates stress that propagates
    around the loop via smoothed coupling. Neighboring and distant segments feel pushback.
    """
    if not config.field_restoring_enabled:
        return np.zeros_like(deviation), np.zeros_like(deviation)

    sigma = config.field_kernel_sigma
    fn = np.zeros_like(deviation)

    if config.field_dev_strength > 0 or config.field_transmit_strength > 0:
        dev_field = circular_field_smooth(deviation, sigma)
        dev_stress = deviation - dev_field
        fn = fn - config.field_dev_strength * dev_stress
        if config.field_transmit_strength > 0:
            transmitted = circular_field_smooth(dev_stress, sigma)
            fn = fn - config.field_transmit_strength * transmitted

    if config.field_stretch_strength > 0:
        stretch = segment_lengths(x, y) - target_h
        stretch_anom = stretch - np.mean(stretch)
        stretch_field = circular_field_smooth(stretch_anom, sigma)
        stretch_stress = stretch_anom - stretch_field
        fn = fn + config.field_stretch_strength * stretch_stress

    if config.field_bend_strength > 0:
        seg_spacing = perimeter(x, y) / len(x)
        lap_dev = second_derivative_uniform(deviation, seg_spacing, spacing_ref)
        fn = fn - config.field_bend_strength * lap_dev

    return fn * nx, fn * ny


def effective_drive_gamma(config: SimConfig, frame: int) -> float:
    if config.gamma_ramp_enabled and config.gamma_ramp_initial > 0:
        t = frame / max(config.gamma_ramp_decay_frames, 1)
        decay = np.exp(-3.0 * t)
        return float(config.gamma_ramp_initial * decay + config.gamma * (1.0 - decay))
    if config.forcing_enabled:
        return config.gamma
    return 0.0


def effective_drive_mode(config: SimConfig) -> int:
    if config.gamma_ramp_enabled:
        return config.gamma_ramp_k
    return config.k


def mode_bootstrap_forces(
    config: SimConfig,
    phase: np.ndarray,
    nx: np.ndarray,
    ny: np.ndarray,
    frame: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Adiabatic mode-shaped bias that decays — pulls system into pump basin without permanent seed."""
    if not config.mode_bootstrap_enabled or config.mode_bootstrap_strength <= 0:
        return np.zeros_like(phase), np.zeros_like(phase)

    t = frame / max(config.mode_bootstrap_decay_frames, 1)
    strength = config.mode_bootstrap_strength * np.exp(-3.0 * t)
    envelope = np.sin(config.mode_bootstrap_mode * phase)
    fn = strength * envelope
    return fn * nx, fn * ny


def mode_interaction_forces(
    config: SimConfig,
    deviation: np.ndarray,
    phase: np.ndarray,
    nx: np.ndarray,
    ny: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Nonlinear triad-style interaction: dev^2 * cos(k*phi) couples pump mode to its harmonics.
    Enables modes to feed each other (self-driven -> self-excited).
    """
    if not config.mode_interaction_enabled or config.mode_interaction_strength <= 0:
        return np.zeros_like(deviation), np.zeros_like(deviation)

    k = config.mode_interaction_mode
    fn = config.mode_interaction_strength * (deviation**2) * np.cos(k * phase)
    fn2 = 0.5 * config.mode_interaction_strength * deviation * np.sin(2 * k * phase)
    return (fn + fn2) * nx, (fn + fn2) * ny


def _slice_fluid_state(
    state: Optional[Any],
    loop_index: int,
    n: int,
    kind: str,
) -> Optional[Any]:
    """Slice multi-loop fluid state. kind is 'plasma_fluid' or 'fluid_time'."""
    if state is None:
        return None
    if kind == "plasma_fluid":
        full_len = len(state.rho)
        if full_len == n:
            return state
        sl = slice(loop_index * n, (loop_index + 1) * n)
        return PlasmaFluidState(rho=state.rho[sl], u=state.u[sl])
    if kind == "fluid_time":
        full_len = len(state.tau)
        if full_len == n:
            return state
        sl = slice(loop_index * n, (loop_index + 1) * n)
        return FluidTimeState(tau=state.tau[sl], tau_u=state.tau_u[sl])
    return None


def compute_forces_single_loop(
    config: SimConfig,
    x: np.ndarray,
    y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    phase: np.ndarray,
    spacing_ref: float,
    target_h: float,
    frame: int = 0,
    pulse_phase: float = 0.0,
    reference_radius: Optional[float] = None,
    pulse_active: bool = True,
    plasma_state: Optional[PlasmaPhysicsState] = None,
    loop_index: int = 0,
    adaptive_memory: Optional[AdaptiveGyroMemory] = None,
    plasma_fluid_state: Optional[PlasmaFluidState] = None,
    fluid_time_state: Optional[FluidTimeState] = None,
    gyro_pll_memory: Optional[GyroPLLMemory] = None,
    predictive_controller: Optional[PredictiveAdaptiveController] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    N = len(x)
    mat = resolve_loop_material(config)
    gyro_mult, torque_mult = (
        adaptive_memory.multipliers(loop_index) if adaptive_memory is not None else (1.0, 1.0)
    )
    pll_gyro_mult = (
        gyro_pll_gyro_multiplier(config, gyro_pll_memory, loop_index)
        if gyro_pll_memory is not None
        else 1.0
    )
    gyro_mult *= pll_gyro_mult
    pac_mult = (
        predictive_controller.gyro_multiplier(loop_index)
        if predictive_controller is not None
        else 1.0
    )
    gyro_mult *= pac_mult
    ft_sub = (
        _slice_fluid_state(fluid_time_state, loop_index, N, "fluid_time")
        if fluid_time_state is not None
        else None
    )
    time_scale = (
        time_fluid_scale(config, ft_sub)
        if ft_sub is not None and time_fluid_active(config)
        else np.ones(N, dtype=float)
    )
    R_ref = config.R0 if reference_radius is None else reference_radius
    seg_spacing = perimeter(x, y) / N
    dx4 = fourth_derivative_uniform(x, seg_spacing, spacing_ref)
    dy4 = fourth_derivative_uniform(y, seg_spacing, spacing_ref)

    asym = asymmetry_modulation(
        phase, config.asymmetry_strength, config.asymmetry_mode, config.asymmetry_phase
    )
    fx = -mat.alpha * asym * dx4
    fy = -mat.alpha * asym * dy4

    fcx, fcy = field_curvature_tension_forces(config, dx4, dy4)
    fx += fcx
    fy += fcy

    r = np.sqrt(x**2 + y**2 + 1e-12)
    nx = x / r
    ny = y / r
    deviation = r - R_ref

    beta_eff = velocity_beta_coefficient(config, phase, deviation)
    beta_eff = beta_eff - traveling_pulse_beta_reduction(
        config, phase, pulse_phase, frame, pulse_active
    )
    fx -= beta_eff * vx
    fy -= beta_eff * vy

    ftx, fty = tension_forces(x, y, target_h, mat.tension_stiffness)
    fx += ftx
    fy += fty

    ftcx, ftcy = tension_curvature_forces(
        x, y, target_h, mat.tension_curvature_stiffness, spacing_ref
    )
    fx += ftcx
    fy += ftcy

    fix, fiy = internal_dynamics_forces(
        x, y, vx, vy, phase, target_h,
        config.internal_dynamics_strength,
        config.internal_dynamics_mode,
        config.internal_dynamics_enabled,
    )
    fx += fix
    fy += fiy

    gamma_eff = effective_drive_gamma(config, frame)
    if gamma_eff > 0:
        drive_k = effective_drive_mode(config)
        drive = gamma_eff * np.sin(drive_k * phase)
        fx += drive * nx
        fy += drive * ny

    ffx, ffy = distributed_field_restoring_forces(
        config, x, y, deviation, nx, ny, spacing_ref, target_h
    )
    fx += ffx
    fy += ffy

    bfx, bfy = mode_bootstrap_forces(config, phase, nx, ny, frame)
    fx += bfx
    fy += bfy

    frx, fry = radial_restoring_accel(
        deviation, nx, ny, mat.radial_stiffness, config.cubic_stiffness
    )
    fx += frx
    fy += fry

    ccx, ccy = conservative_mode_coupling_forces(config, deviation, phase, nx, ny)
    fx += ccx
    fy += ccy

    mix, miy = mode_interaction_forces(config, deviation, phase, nx, ny)
    fx += mix
    fy += miy

    pdx, pdy = pump_mode_duffing_forces(config, deviation, phase, nx, ny)
    fx += pdx
    fy += pdy

    plx, ply = pump_amplitude_limiter_forces(config, deviation, nx, ny)
    fx += plx
    fy += ply

    pvx, pvy = pump_mode_vdp_forces(config, vx, vy, nx, ny, deviation)
    fx += pvx
    fy += pvy

    msx, msy = mode_selective_damping_forces(config, vx, vy, nx, ny, deviation)
    fx += msx
    fy += msy

    lmx, lmy = low_mode_parasite_damping_forces(config, vx, vy, nx, ny, frame)
    fx += lmx
    fy += lmy

    if getattr(config, "traveling_pulse_enabled", False):
        tpx, tpy = traveling_pulse_forces(
            config, phase, nx, ny, vx, vy, pulse_phase, frame, pulse_active
        )
        fx += tpx
        fy += tpy

    if plasma_fluid_state is not None:
        pf_sub = _slice_fluid_state(plasma_fluid_state, loop_index, N, "plasma_fluid")
        if pf_sub is not None and plasma_fluid_active(config):
            pffx, pffy = plasma_fluid_forces(config, pf_sub, nx, ny)
            fx += pffx
            fy += pffy
    elif getattr(config, "plasma_enabled", False) or getattr(
        config, "plasma_flow_enabled", False
    ):
        if plasma_active(config):
            local_energy = None
            if (
                config.plasma_energy_gate_enabled
                or getattr(config, "plasma_synchronization_enabled", False)
                or getattr(config, "plasma_mirror_balance_enabled", False)
            ):
                local_energy = local_activity(
                    config, vx, vy, deviation, dx4, dy4,
                )
            spx, spy = spiral_plasma_flow_forces(
                config, phase, nx, ny, frame,
                deviation=deviation,
                plasma_state=plasma_state,
                local_energy=local_energy,
                loop_index=loop_index,
            )
            fx += spx
            fy += spy
            if getattr(config, "plasma_mirror_balance_enabled", False):
                from driven_loop.plasma_physics import plasma_mirror_balance_feedback_forces

                mfx, mfy = plasma_mirror_balance_feedback_forces(
                    config,
                    deviation,
                    nx,
                    ny,
                    local_energy=local_energy,
                    state=plasma_state,
                    loop_index=loop_index,
                    frame=frame,
                )
                fx += mfx
                fy += mfy

    gwx, gwy, _ = gravity_well_stabilizer_forces(
        config, x, y, vx, vy, deviation, dx4, dy4,
        gyro_gain_mult=gyro_mult,
        torque_gain_mult=torque_mult,
    )
    gwx *= time_scale
    gwy *= time_scale
    fx += gwx
    fy += gwy

    # Weak experimental central potential (1/r²) — opt-in only, no torque
    cpx, cpy = central_potential_forces(config, x, y)
    cpx *= time_scale
    cpy *= time_scale
    fx += cpx
    fy += cpy

    if not config.pump_limit_cycle_enabled:
        gfx, gfy = apply_gyro_damping(config, vx, vy, deviation, dx4, dy4)
        # PAC multiplies classic gyro damping (GR path already uses gyro_mult).
        gfx *= pac_mult
        gfy *= pac_mult
    else:
        gfx, gfy = np.zeros_like(vx), np.zeros_like(vy)
    gfx *= time_scale
    gfy *= time_scale
    fx += gfx
    fy += gfy

    if gyro_pll_memory is not None and gyro_pll_active(config):
        pllx, plly = gyro_pll_forces(config, gyro_pll_memory, loop_index, nx, ny)
        pllx *= time_scale
        plly *= time_scale
        fx += pllx
        fy += plly

    if getattr(config, "qslt_resonance_enabled", False):
        qrx, qry = qslt_resonance_forces(config, phase, nx, ny, frame)
        fx += qrx
        fy += qry

    if getattr(config, "known_frequencies_enabled", False):
        loop_act = float(np.mean(local_activity(config, vx, vy, deviation, dx4, dy4)))
        kfx, kfy = known_frequencies_forces(
            config,
            phase,
            nx,
            ny,
            frame,
            loop_index=loop_index,
            adaptive_memory=adaptive_memory,
            loop_activity=loop_act,
            plasma_state=plasma_state,
        )
        fx += kfx
        fy += kfy

    if getattr(config, "compression_test_enabled", False) and compression_test_active(
        config
    ):
        cfx, cfy = compression_radial_forces(
            config,
            x,
            y,
            frame,
            mat.mass_per_node,
            center=loop_center(x, y),
        )
        fx += cfx
        fy += cfy

    return fx, fy, deviation, dx4, dy4


def compute_forces(
    config: SimConfig,
    x: np.ndarray,
    y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    phase: np.ndarray,
    spacing_ref: float,
    target_h: float,
    frame: int = 0,
    pulse_phase: float = 0.0,
    active_loop: int = 0,
    plasma_state: Optional[PlasmaPhysicsState] = None,
    adaptive_memory: Optional[AdaptiveGyroMemory] = None,
    plasma_fluid_state: Optional[PlasmaFluidState] = None,
    fluid_time_state: Optional[FluidTimeState] = None,
    gyro_pll_memory: Optional[GyroPLLMemory] = None,
    predictive_controller: Optional[PredictiveAdaptiveController] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if not is_multi_loop_system(config):
        return compute_forces_single_loop(
            config, x, y, vx, vy, phase, spacing_ref, target_h, frame, pulse_phase,
            plasma_state=plasma_state,
            adaptive_memory=adaptive_memory,
            plasma_fluid_state=plasma_fluid_state,
            fluid_time_state=fluid_time_state,
            gyro_pll_memory=gyro_pll_memory,
            predictive_controller=predictive_controller,
        )

    n = config.N
    num_loops = num_sim_loops(config)
    fx = np.zeros(num_loops * n)
    fy = np.zeros(num_loops * n)
    deviations: List[np.ndarray] = []
    dx4_parts: List[np.ndarray] = []
    dy4_parts: List[np.ndarray] = []

    for loop_i in range(num_loops):
        sl = loop_state_slice(config, loop_i)
        phase_l = arc_length_phase(n)
        r_ref = loop_reference_radius(config, loop_i)
        apply_pulse = loop_i == active_loop
        fxl, fyl, dev_l, dx4_l, dy4_l = compute_forces_single_loop(
            config,
            x[sl],
            y[sl],
            vx[sl],
            vy[sl],
            phase_l,
            spacing_ref,
            target_h,
            frame,
            pulse_phase if apply_pulse else 0.0,
            reference_radius=r_ref,
            pulse_active=apply_pulse,
            plasma_state=plasma_state,
            loop_index=loop_i,
            adaptive_memory=adaptive_memory,
            plasma_fluid_state=plasma_fluid_state,
            fluid_time_state=fluid_time_state,
            gyro_pll_memory=gyro_pll_memory,
            predictive_controller=predictive_controller,
        )
        fx[sl] = fxl
        fy[sl] = fyl
        deviations.append(dev_l)
        dx4_parts.append(dx4_l)
        dy4_parts.append(dy4_l)

    if config.loop_lattice_enabled:
        cx, cy = loop_lattice_coupling_forces(config, x, y, vx, vy)
    else:
        cx, cy = dual_loop_coupling_forces(config, x, y, vx, vy)
    fx += cx
    fy += cy

    deviation = np.concatenate(deviations)
    dx4 = np.concatenate(dx4_parts)
    dy4 = np.concatenate(dy4_parts)
    return fx, fy, deviation, dx4, dy4


def verlet_step(
    config: SimConfig, x, y, vx, vy, phase, spacing_ref, target_h,
    frame: int = 0, pulse_phase: float = 0.0, active_loop: int = 0,
    plasma_state: Optional[PlasmaPhysicsState] = None,
    adaptive_memory: Optional[AdaptiveGyroMemory] = None,
    plasma_fluid_state: Optional[PlasmaFluidState] = None,
    fluid_time_state: Optional[FluidTimeState] = None,
    gyro_pll_memory: Optional[GyroPLLMemory] = None,
    predictive_controller: Optional[PredictiveAdaptiveController] = None,
) -> Tuple[np.ndarray, ...]:
    dt = config.dt
    fx, fy, deviation, dx4, dy4 = compute_forces(
        config, x, y, vx, vy, phase, spacing_ref, target_h, frame, pulse_phase, active_loop,
        plasma_state=plasma_state,
        adaptive_memory=adaptive_memory,
        plasma_fluid_state=plasma_fluid_state,
        fluid_time_state=fluid_time_state,
        gyro_pll_memory=gyro_pll_memory,
        predictive_controller=predictive_controller,
    )
    inv_m = 1.0 / resolve_loop_material(config).mass_per_node
    vx_half = vx + 0.5 * dt * fx * inv_m
    vy_half = vy + 0.5 * dt * fy * inv_m
    x_new = x + dt * vx_half
    y_new = y + dt * vy_half
    remove_center_of_mass_drift(config, x_new, y_new)

    fx2, fy2, deviation, dx4, dy4 = compute_forces(
        config, x_new, y_new, vx_half, vy_half, phase, spacing_ref, target_h,
        frame, pulse_phase, active_loop,
        plasma_state=plasma_state,
        adaptive_memory=adaptive_memory,
        plasma_fluid_state=plasma_fluid_state,
        fluid_time_state=fluid_time_state,
        gyro_pll_memory=gyro_pll_memory,
        predictive_controller=predictive_controller,
    )
    vx_new = vx_half + 0.5 * dt * fx2 * inv_m
    vy_new = vy_half + 0.5 * dt * fy2 * inv_m
    # Linear radial gyro damping (multiplicative) — only if enable_central_potential
    vx_new, vy_new = apply_central_gyro_velocity_damping(
        config, x_new, y_new, vx_new, vy_new, dt
    )
    return x_new, y_new, vx_new, vy_new, deviation, dx4, dy4


def euler_step(
    config: SimConfig, x, y, vx, vy, phase, spacing_ref, target_h,
    frame: int = 0, pulse_phase: float = 0.0, active_loop: int = 0,
    plasma_state: Optional[PlasmaPhysicsState] = None,
    adaptive_memory: Optional[AdaptiveGyroMemory] = None,
    plasma_fluid_state: Optional[PlasmaFluidState] = None,
    fluid_time_state: Optional[FluidTimeState] = None,
    gyro_pll_memory: Optional[GyroPLLMemory] = None,
    predictive_controller: Optional[PredictiveAdaptiveController] = None,
) -> Tuple[np.ndarray, ...]:
    dt = config.dt
    fx, fy, deviation, dx4, dy4 = compute_forces(
        config, x, y, vx, vy, phase, spacing_ref, target_h, frame, pulse_phase, active_loop,
        plasma_state=plasma_state,
        adaptive_memory=adaptive_memory,
        plasma_fluid_state=plasma_fluid_state,
        fluid_time_state=fluid_time_state,
        gyro_pll_memory=gyro_pll_memory,
        predictive_controller=predictive_controller,
    )
    inv_m = 1.0 / resolve_loop_material(config).mass_per_node
    vx_new = vx + fx * inv_m * dt
    vy_new = vy + fy * inv_m * dt
    x_new = x + vx_new * dt
    y_new = y + vy_new * dt
    remove_center_of_mass_drift(config, x_new, y_new)
    vx_new, vy_new = apply_central_gyro_velocity_damping(
        config, x_new, y_new, vx_new, vy_new, dt
    )
    return x_new, y_new, vx_new, vy_new, deviation, dx4, dy4


def integrate_step(
    config, x, y, vx, vy, phase, spacing_ref, target_h,
    frame: int = 0, pulse_phase: float = 0.0, active_loop: int = 0,
    plasma_state: Optional[PlasmaPhysicsState] = None,
    adaptive_memory: Optional[AdaptiveGyroMemory] = None,
    plasma_fluid_state: Optional[PlasmaFluidState] = None,
    fluid_time_state: Optional[FluidTimeState] = None,
    gyro_pll_memory: Optional[GyroPLLMemory] = None,
    predictive_controller: Optional[PredictiveAdaptiveController] = None,
):
    if config.integrator == "verlet":
        return verlet_step(
            config, x, y, vx, vy, phase, spacing_ref, target_h, frame, pulse_phase, active_loop,
            plasma_state=plasma_state,
            adaptive_memory=adaptive_memory,
            plasma_fluid_state=plasma_fluid_state,
            fluid_time_state=fluid_time_state,
            gyro_pll_memory=gyro_pll_memory,
            predictive_controller=predictive_controller,
        )
    return euler_step(
        config, x, y, vx, vy, phase, spacing_ref, target_h, frame, pulse_phase, active_loop,
        plasma_state=plasma_state,
        adaptive_memory=adaptive_memory,
        plasma_fluid_state=plasma_fluid_state,
        fluid_time_state=fluid_time_state,
        gyro_pll_memory=gyro_pll_memory,
        predictive_controller=predictive_controller,
    )


def init_single_loop(
    config: SimConfig,
    radius: float,
    phase_offset: float = 0.0,
    center: Tuple[float, float] = (0.0, 0.0),
) -> Tuple[np.ndarray, np.ndarray]:
    N, R0 = config.N, radius
    phase = arc_length_phase(N) + phase_offset
    x = R0 * np.cos(phase) + center[0]
    y = R0 * np.sin(phase) + center[1]

    if config.initial_noise > 0:
        x += config.initial_noise * np.random.randn(N)
        y += config.initial_noise * np.random.randn(N)

    if config.initial_mode_seed > 0:
        dev_seed = config.initial_mode_seed * np.sin(config.pump_mode * phase)
        cx, cy = center
        r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2 + 1e-12)
        scale = (R0 + dev_seed) / r
        x = cx + (x - cx) * scale
        y = cy + (y - cy) * scale
    return x, y


def remove_center_of_mass_drift(
    config: SimConfig,
    x: np.ndarray,
    y: np.ndarray,
) -> None:
    """Prevent COM drift; lattice uses per-loop removal so neighbors stay independent."""
    if config.loop_lattice_enabled:
        for loop_i in range(num_sim_loops(config)):
            sl = loop_state_slice(config, loop_i)
            x[sl] -= np.mean(x[sl])
            y[sl] -= np.mean(y[sl])
    else:
        x -= np.mean(x)
        y -= np.mean(y)


def init_state(config: SimConfig) -> Tuple[np.ndarray, ...]:
    if config.seed is not None:
        np.random.seed(config.seed)

    N = config.N
    phase = arc_length_phase(N)

    if config.loop_lattice_enabled:
        centers = loop_lattice_centers(config)
        num_loops = len(centers)
        xs: List[np.ndarray] = []
        ys: List[np.ndarray] = []
        for loop_i, center in enumerate(centers):
            xi, yi = init_single_loop(
                config,
                loop_reference_radius(config, loop_i),
                loop_lattice_phase_offset(config, loop_i),
                center=center,
            )
            xs.append(xi)
            ys.append(yi)
        x = np.concatenate(xs)
        y = np.concatenate(ys)
        remove_center_of_mass_drift(config, x, y)
        vx = np.zeros(num_loops * N)
        vy = np.zeros(num_loops * N)
        target_h = config.target_segment_length or (perimeter(xs[0], ys[0]) / N)
        return x, y, vx, vy, phase, target_h

    if config.dual_loop_enabled:
        x1, y1 = init_single_loop(config, config.R0)
        x2, y2 = init_single_loop(
            config,
            loop_reference_radius(config, 1),
            config.dual_loop_phase_offset,
        )
        x = np.concatenate([x1, x2])
        y = np.concatenate([y1, y2])
        x -= np.mean(x)
        y -= np.mean(y)
        vx = np.zeros(2 * N)
        vy = np.zeros(2 * N)
        target_h = config.target_segment_length or (perimeter(x[:N], y[:N]) / N)
        return x, y, vx, vy, phase, target_h

    x, y = init_single_loop(config, config.R0)
    x -= np.mean(x)
    y -= np.mean(y)
    vx = np.zeros(N)
    vy = np.zeros(N)
    target_h = config.target_segment_length or (perimeter(x, y) / N)
    return x, y, vx, vy, phase, target_h


def estimate_lyapunov(config: SimConfig) -> float:
    """
    Benettin-style largest Lyapunov exponent estimate (1/s).
    Positive -> chaotic/unstable separation; negative -> convergent.
    """
    ly_cfg = replace(config, compute_emergent_mode=False, compute_lyapunov=False)
    eps = config.lyapunov_perturbation
    spacing_ref = 2 * np.pi * ly_cfg.R0 / 256

    x1, y1, vx1, vy1, phase, target_h = init_state(ly_cfg)
    x2 = x1 + eps * np.random.randn(ly_cfg.N)
    y2 = y1 + eps * np.random.randn(ly_cfg.N)
    x2 -= np.mean(x2)
    y2 -= np.mean(y2)
    vx2, vy2 = vx1.copy(), vy1.copy()

    local_logs: List[float] = []
    counter = 0

    for frame in range(config.lyapunov_frames):
        if ly_cfg.reparam_interval > 0 and frame > 0 and frame % ly_cfg.reparam_interval == 0:
            x1, y1, vx1, vy1 = resample_uniform_arclength(x1, y1, vx1, vy1, ly_cfg.N)
            x2, y2, vx2, vy2 = resample_uniform_arclength(x2, y2, vx2, vy2, ly_cfg.N)

        x1, y1, vx1, vy1, *_ = integrate_step(
            ly_cfg, x1, y1, vx1, vy1, phase, spacing_ref, target_h
        )
        x2, y2, vx2, vy2, *_ = integrate_step(
            ly_cfg, x2, y2, vx2, vy2, phase, spacing_ref, target_h
        )

        dist = float(np.sqrt(np.mean((x1 - x2) ** 2 + (y1 - y2) ** 2)))
        counter += 1

        if counter >= config.lyapunov_rescale_every:
            local_logs.append(np.log(dist / eps + 1e-30))
            scale = eps / (dist + 1e-30)
            x2 = x1 + (x2 - x1) * scale
            y2 = y1 + (y2 - y1) * scale
            vx2 = vx1 + (vx2 - vx1) * scale
            vy2 = vy1 + (vy2 - vy1) * scale
            counter = 0

    if not local_logs:
        return float("nan")

    dt_interval = config.lyapunov_rescale_every * ly_cfg.dt
    return float(np.mean(local_logs) / dt_interval)


def analyze_emergent_modes(
    forced_energies: np.ndarray,
    free_energies: np.ndarray,
    drive_mode: int,
) -> Dict[str, Any]:
    """Compare late-time FFT spectra: forced (gamma>0) minus unforced (gamma=0)."""
    f_spec = np.mean(forced_energies[-50:], axis=0)
    u_spec = np.mean(free_energies[-50:], axis=0)
    residual = f_spec - u_spec

    emergent_mode = int(np.argmax(residual[1:]) + 1)
    total_forced = float(np.sum(f_spec[1:]) + 1e-12)
    drive_share = float(f_spec[drive_mode] / total_forced) if drive_mode < len(f_spec) else 0.0
    residual_share = float(np.sum(np.abs(residual[1:])) / (total_forced + 1e-12))

    return {
        "emergent_mode": emergent_mode,
        "drive_mode": drive_mode,
        "drive_mode_share": round(drive_share, 4),
        "residual_mode_share": round(residual_share, 4),
        "drive_locked": emergent_mode == drive_mode,
        "emergent_differs_from_drive": emergent_mode != drive_mode,
    }


def classify_regime(
    avg_deformation: float, is_stable: bool,
    relative_deformation_var: float, equilibrium_type: str,
) -> str:
    if equilibrium_type == "frozen":
        return "Frozen"
    if is_stable:
        return "Stable"
    if avg_deformation > 1.5:
        return "Expanding"
    if relative_deformation_var > 0.08:
        return "Breathing"
    return "Collapsing"


def stability_score_from_stats(stats: Dict[str, Any]) -> float:
    return stats["relative_activity_var"] + stats["relative_deformation_var"]


def is_trivial_collapse(stats: Dict[str, Any], min_deformation: float = 0.03) -> bool:
    return stats["avg_deformation"] < min_deformation


def ranked_stability_score(stats: Dict[str, Any]) -> float:
    if is_trivial_collapse(stats):
        return float("inf")
    return stability_score_from_stats(stats)


def stats_to_row(stats: Dict[str, Any]) -> Dict[str, Any]:
    return {
        k: v for k, v in stats.items()
        if not k.startswith("_") and k != "mode_energies"
    }


def classify_pairwise_sync(mean_corr: float) -> str:
    if mean_corr >= 0.85:
        return "locked"
    if mean_corr >= 0.55:
        return "partial"
    return "desync"


def analyze_pairwise_sync(
    per_loop_series: np.ndarray,
    *,
    prefix: str = "",
    include_matrix: bool = False,
) -> Dict[str, Any]:
    """
    Pairwise Pearson correlation of per-loop time series (tail window).
    per_loop_series shape: (n_frames, n_loops)
    """
    pfx = f"{prefix}_" if prefix else ""
    if per_loop_series.ndim != 2 or per_loop_series.shape[1] < 2:
        return {f"{pfx}mean_pairwise_corr": float("nan"), f"{pfx}sync_class": "n/a"}

    corr = np.corrcoef(per_loop_series.T)
    upper = corr[np.triu_indices(corr.shape[0], k=1)]
    mean_c = float(np.mean(upper))
    out: Dict[str, Any] = {
        f"{pfx}mean_pairwise_corr": round(mean_c, 4),
        f"{pfx}min_pairwise_corr": round(float(np.min(upper)), 4),
        f"{pfx}max_pairwise_corr": round(float(np.max(upper)), 4),
        f"{pfx}sync_class": classify_pairwise_sync(mean_c),
    }
    if include_matrix:
        key = "pairwise_corr" if not prefix else f"{prefix}_pairwise_corr"
        out[key] = np.round(corr, 4).tolist()
    return out


def analyze_lattice_sync(per_loop_pump: np.ndarray) -> Dict[str, Any]:
    """Pump-amplitude sync across loops (tail window)."""
    return analyze_pairwise_sync(per_loop_pump, include_matrix=True)


def per_loop_stored_energy(
    config: SimConfig,
    x: np.ndarray,
    y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    phase: np.ndarray,
    deviation: np.ndarray,
    dx4: np.ndarray,
    dy4: np.ndarray,
    frame: int,
    target_h: float,
    spacing_ref: float,
) -> List[float]:
    """Instantaneous stored energy per loop in a multi-loop lattice."""
    values: List[float] = []
    for loop_i in range(num_sim_loops(config)):
        sl = loop_state_slice(config, loop_i)
        ph = phase[sl] if len(phase) == len(x) else arc_length_phase(config.N)
        ledger = frame_energy_ledger(
            config,
            x[sl],
            y[sl],
            vx[sl],
            vy[sl],
            ph,
            deviation[sl],
            dx4[sl],
            dy4[sl],
            frame,
            target_h,
            spacing_ref,
        )
        values.append(ledger["stored"])
    return values


def analyze_pulse_hopping(active_loop_history: List[int], num_loops: int) -> Dict[str, Any]:
    """Summarize inter-loop pulse transfers from active_loop index trace."""
    if len(active_loop_history) < 2:
        return {"transfers": 0, "unique_loops_visited": 0}

    hops = 0
    for i in range(1, len(active_loop_history)):
        if active_loop_history[i] != active_loop_history[i - 1]:
            hops += 1
    visited = len(set(active_loop_history))
    counts = Counter(active_loop_history)
    return {
        "transfers": hops,
        "unique_loops_visited": visited,
        "visit_fraction": round(visited / max(num_loops, 1), 4),
        "loop_visit_counts": dict(counts),
    }


def _simulate(
    config: SimConfig,
    record_shapes: bool = False,
) -> Optional[Dict[str, Any]]:
    N, R0, dt = config.N, config.R0, config.dt
    spacing_ref = 2 * np.pi * R0 / 256

    x, y, vx, vy, phase, target_h = init_state(config)
    initial_perimeter = perimeter(x, y)

    activity_history: List[float] = []
    deformation_history: List[float] = []
    stretch_history: List[float] = []
    perimeter_history: List[float] = []
    mode_history: List[int] = []
    mode_energies_list: List[np.ndarray] = []
    stored_energy_history: List[float] = []
    inject_power_history: List[float] = []
    diss_power_history: List[float] = []
    pulse_phase_history: List[float] = []
    active_loop_history: List[int] = []
    per_loop_pump_history: Optional[List[List[float]]] = None
    per_loop_mode_history: Optional[List[List[int]]] = None
    per_loop_stored_history: Optional[List[List[float]]] = None
    # Track per-loop histories for any multi-loop system (lattice AND dual-loop)
    # so primary-only vibration metrics are available for TMD-style comparisons.
    if is_multi_loop_system(config):
        n_loops = num_sim_loops(config)
        per_loop_pump_history = [[] for _ in range(n_loops)]
        per_loop_mode_history = [[] for _ in range(n_loops)]
        per_loop_stored_history = [[] for _ in range(n_loops)]
    x_history: List[np.ndarray] = []
    y_history: List[np.ndarray] = []
    success = True
    pulse_phase = config.traveling_pulse_initial_phase
    active_loop = config.traveling_pulse_active_loop
    pulse_hop_count = 0
    last_pulse_hop_frame = -10**9
    plasma_state: Optional[Any] = None
    if getattr(config, "plasma_enabled", False) or getattr(
        config, "plasma_flow_enabled", False
    ):
        if plasma_needs_state(config):
            plasma_state = PlasmaPhysicsState(len(x), nodes_per_loop=int(config.N))
    adaptive_memory: Optional[Any] = None
    predictive_controller: Optional[Any] = None
    recovery_tracker: Optional[Any] = None
    radiation_impact_total = 0
    plasma_fluid_state: Optional[Any] = None
    fluid_time_state: Optional[Any] = None
    if getattr(config, "plasma_fluid_enabled", False) and plasma_fluid_active(config):
        plasma_fluid_state = PlasmaFluidState.create(len(x), config)
    if getattr(config, "time_fluid_enabled", False) and time_fluid_active(config):
        fluid_time_state = FluidTimeState.create(len(x), config)
    gyro_pll_memory: Optional[Any] = None
    compression_tracker: Optional[Any] = None

    if config.loop_lattice_enabled:
        n_loops_init = num_sim_loops(config)
        if getattr(config, "gyro_pll_memory_enabled", False) and gyro_pll_active(config):
            gyro_pll_memory = GyroPLLMemory.create(config)
        if getattr(config, "adaptive_gyro_memory_enabled", False) and adaptive_memory_active(
            config
        ):
            adaptive_memory = AdaptiveGyroMemory(n_loops_init)
        if getattr(
            config, "predictive_adaptive_controller_enabled", False
        ) and predictive_adaptive_active(config):
            predictive_controller = PredictiveAdaptiveController(n_loops_init)
        if config.radiation_impact_enabled:
            recovery_tracker = ImpactRecoveryTracker(
                recovery_threshold=config.pump_stability_rel_var,
            )
    elif getattr(
        config, "predictive_adaptive_controller_enabled", False
    ) and predictive_adaptive_active(config):
        predictive_controller = PredictiveAdaptiveController(1)

    if getattr(config, "compression_test_enabled", False) and compression_test_active(
        config
    ):
        if config.loop_lattice_enabled:
            centers = loop_lattice_centers(config)
            slices = [loop_state_slice(config, i) for i in range(num_sim_loops(config))]
            compression_tracker = CompressionTwistTracker.from_state(
                config, x, y, loop_slices=slices, centers=centers,
            )
        else:
            compression_tracker = CompressionTwistTracker.from_state(config, x, y)

    for frame in range(config.frames):
        if config.reparam_interval > 0 and frame > 0 and frame % config.reparam_interval == 0:
            if is_multi_loop_system(config):
                xs, ys, vxs, vys = [], [], [], []
                for loop_i in range(num_sim_loops(config)):
                    sl = loop_state_slice(config, loop_i)
                    xr, yr, vxr, vyr = resample_uniform_arclength(
                        x[sl], y[sl], vx[sl], vy[sl], N
                    )
                    xs.append(xr)
                    ys.append(yr)
                    vxs.append(vxr)
                    vys.append(vyr)
                x = np.concatenate(xs)
                y = np.concatenate(ys)
                vx = np.concatenate(vxs)
                vy = np.concatenate(vys)
            else:
                x, y, vx, vy = resample_uniform_arclength(x, y, vx, vy, N)

        if config.traveling_pulse_enabled:
            pulse_phase_history.append(float(pulse_phase))
            if config.loop_lattice_enabled:
                active_loop_history.append(int(active_loop))

        try:
            x, y, vx, vy, deviation, dx4, dy4 = integrate_step(
                config, x, y, vx, vy, phase, spacing_ref, target_h,
                frame, pulse_phase, active_loop,
                plasma_state=plasma_state,
                adaptive_memory=adaptive_memory,
                plasma_fluid_state=plasma_fluid_state,
                fluid_time_state=fluid_time_state,
                gyro_pll_memory=gyro_pll_memory,
                predictive_controller=predictive_controller,
            )
        except Exception:
            success = False
            break

        if gyro_pll_memory is not None and is_multi_loop_system(config):
            pll_phases = loop_pump_phases_from_deviation(config, deviation, N)
            gyro_pll_memory.update(config, pll_phases)

        if plasma_fluid_state is not None or fluid_time_state is not None:
            n_pts = config.N
            n_loops_fluid = num_sim_loops(config) if is_multi_loop_system(config) else 1
            for loop_i in range(n_loops_fluid):
                sl = (
                    loop_state_slice(config, loop_i)
                    if is_multi_loop_system(config)
                    else slice(0, n_pts)
                )
                ph = phase[sl] if len(phase) == len(x) else arc_length_phase(n_pts)
                act = local_activity(
                    config, vx[sl], vy[sl], deviation[sl], dx4[sl], dy4[sl],
                )
                if plasma_fluid_state is not None:
                    pf_loop = PlasmaFluidState(
                        rho=plasma_fluid_state.rho[sl], u=plasma_fluid_state.u[sl],
                    )
                    plasma_fluid_update(config, pf_loop, ph, act, frame)
                    plasma_fluid_state.rho[sl] = pf_loop.rho
                    plasma_fluid_state.u[sl] = pf_loop.u
                if fluid_time_state is not None:
                    ft_loop = FluidTimeState(
                        tau=fluid_time_state.tau[sl], tau_u=fluid_time_state.tau_u[sl],
                    )
                    fluid_time_update(config, ft_loop, act, vx[sl], vy[sl], ph, frame)
                    fluid_time_state.tau[sl] = ft_loop.tau
                    fluid_time_state.tau_u[sl] = ft_loop.tau_u

        if config.radiation_impact_enabled and config.loop_lattice_enabled:
            if maybe_radiation_impact(config, frame):
                hit_loop = apply_radiation_impact(config, x, y, vx, vy)
                radiation_impact_total += 1
                if adaptive_memory is not None:
                    adaptive_memory.register_impact(hit_loop)
                if recovery_tracker is not None:
                    recovery_tracker.on_impact(frame, hit_loop)

        if adaptive_memory is not None and is_multi_loop_system(config):
            loop_activities = []
            for loop_i in range(num_sim_loops(config)):
                sl = loop_state_slice(config, loop_i)
                act = local_activity(
                    config, vx[sl], vy[sl], deviation[sl], dx4[sl], dy4[sl],
                )
                loop_activities.append(float(np.mean(act)))
            adaptive_memory.update(config, np.asarray(loop_activities, dtype=float))

        if predictive_controller is not None:
            if is_multi_loop_system(config):
                pac_activities = []
                for loop_i in range(num_sim_loops(config)):
                    sl = loop_state_slice(config, loop_i)
                    act = local_activity(
                        config, vx[sl], vy[sl], deviation[sl], dx4[sl], dy4[sl],
                    )
                    pac_activities.append(float(np.mean(act)))
                predictive_controller.update(
                    config, np.asarray(pac_activities, dtype=float),
                )
            else:
                act = local_activity(config, vx, vy, deviation, dx4, dy4)
                predictive_controller.update(
                    config, np.asarray([float(np.mean(act))], dtype=float),
                )

        prev_pulse_hop_count = pulse_hop_count
        if config.traveling_pulse_enabled:
            pump_phases = None
            if config.traveling_pulse_conditional_hop and is_multi_loop_system(config):
                pump_phases = loop_pump_phases_from_deviation(config, deviation, N)

            pulse_phase, active_loop, pulse_hop_count, last_pulse_hop_frame = (
                advance_traveling_pulse_phase(
                    config,
                    pulse_phase,
                    active_loop,
                    frame,
                    loop_pump_phases=pump_phases,
                    hop_count=pulse_hop_count,
                    last_hop_frame=last_pulse_hop_frame,
                )
            )
        if (
            plasma_state is not None
            and config.plasma_snap_on_pulse_hop
            and pulse_hop_count > prev_pulse_hop_count
            and is_multi_loop_system(config)
        ):
            plasma_state.trigger_hop_snap(
                config, deviation, loop_state_slice(config, active_loop),
            )

        speed = np.sqrt(vx**2 + vy**2)
        kinetic = speed**2
        curvature = dx4**2 + dy4**2
        potential = radial_potential(deviation, config.cubic_stiffness)
        stretch_energy = mean_segment_stretch(x, y, target_h) ** 2
        activity = float(np.mean(kinetic + config.alpha * curvature + potential + stretch_energy))

        if not np.isfinite(activity) or activity > 1e8:
            success = False
            break

        activity_history.append(activity)
        if config.track_energy_ledger:
            ledger = frame_energy_ledger(
                config, x, y, vx, vy, phase, deviation, dx4, dy4,
                frame, target_h, spacing_ref,
            )
            stored_energy_history.append(ledger["stored"])
            inject_power_history.append(ledger["power_inject"])
            diss_power_history.append(ledger["power_diss"])

        if is_multi_loop_system(config):
            pidx = primary_loop_index(config)
            psl = loop_state_slice(config, pidx)
            dev_primary = deviation[psl]
            stretches = [
                mean_segment_stretch(x[loop_state_slice(config, i)], y[loop_state_slice(config, i)], target_h)
                for i in range(num_sim_loops(config))
            ]
            perims = [
                perimeter(x[loop_state_slice(config, i)], y[loop_state_slice(config, i)])
                for i in range(num_sim_loops(config))
            ]
            stretch_val = float(np.mean(stretches))
            perim_val = float(np.mean(perims))
        else:
            dev_primary = deviation
            stretch_val = mean_segment_stretch(x, y, target_h)
            perim_val = perimeter(x, y)

        deformation_history.append(float(np.max(np.abs(dev_primary))))
        stretch_history.append(stretch_val)
        perimeter_history.append(perim_val)

        if compression_tracker is not None:
            if config.loop_lattice_enabled:
                slices = [loop_state_slice(config, i) for i in range(num_sim_loops(config))]
            else:
                slices = [slice(0, config.N)]
            compression_tracker.update(config, x, y, frame, slices)

        fft_vals = np.fft.fft(dev_primary)
        energies = (np.abs(fft_vals[: config.mode_window]) ** 2) / (N**2)
        mode_energies_list.append(energies)
        mode_history.append(int(np.argmax(energies[1:]) + 1))

        if per_loop_pump_history is not None and per_loop_mode_history is not None:
            loop_stored = None
            if per_loop_stored_history is not None and config.track_energy_ledger:
                loop_stored = per_loop_stored_energy(
                    config, x, y, vx, vy, phase, deviation, dx4, dy4,
                    frame, target_h, spacing_ref,
                )
            for loop_i in range(len(per_loop_pump_history)):
                sl = loop_state_slice(config, loop_i)
                dev_l = deviation[sl]
                fft_l = np.fft.fft(dev_l)
                pump_amp = float(np.abs(fft_l[config.pump_mode]) / N)
                per_loop_pump_history[loop_i].append(pump_amp)
                e_loop = (np.abs(fft_l[: config.mode_window]) ** 2) / (N**2)
                per_loop_mode_history[loop_i].append(int(np.argmax(e_loop[1:]) + 1))
                if loop_stored is not None:
                    per_loop_stored_history[loop_i].append(loop_stored[loop_i])

            if recovery_tracker is not None and len(per_loop_pump_history[0]) >= 20:
                rel_vars = []
                for loop_i in range(len(per_loop_pump_history)):
                    tail_p = per_loop_pump_history[loop_i][-20:]
                    rel_vars.append(float(np.std(tail_p) / (np.mean(tail_p) + 1e-8)))
                recovery_tracker.update(frame, float(np.mean(rel_vars)))

        if record_shapes and frame % config.record_stride == 0:
            x_history.append(x.copy())
            y_history.append(y.copy())

    tail_n = tail_window_for(config.frames)
    if not success or len(activity_history) < tail_n:
        return None

    tail = slice(-tail_n, None)
    mode_energies = np.array(mode_energies_list)

    avg_activity = float(np.mean(activity_history[tail]))
    avg_deformation = float(np.mean(deformation_history[tail]))
    activity_var = float(np.std(activity_history[tail]))
    deform_var = float(np.std(deformation_history[tail]))

    rel_activity_var = activity_var / (avg_activity + 1e-8)
    rel_deform_var = deform_var / (avg_deformation + 1e-8)
    pump_tail = mode_energies[tail, config.pump_mode]
    pump_rel_var = float(np.std(pump_tail) / (np.mean(pump_tail) + 1e-8))
    is_stable = (
        rel_activity_var < config.stability_rel_var_threshold
        and rel_deform_var < config.stability_rel_var_threshold
    )
    pump_mode_stable = pump_rel_var < config.pump_stability_rel_var

    if avg_deformation < config.frozen_threshold:
        equilibrium_type = "frozen"
    elif config.pump_limit_cycle_enabled:
        equilibrium_type = (
            "stable_oscillation"
            if pump_mode_stable and avg_deformation >= config.frozen_threshold
            else "unstable"
        )
    elif is_stable:
        equilibrium_type = "stable_oscillation"
    else:
        equilibrium_type = "unstable"

    dominant_mode = Counter(mode_history[tail]).most_common(1)[0][0]
    drift_percent = (
        (activity_history[-1] - activity_history[0])
        / (abs(activity_history[0]) + 1e-12) * 100
    )

    energy_stats: Dict[str, float] = {}
    if config.track_energy_ledger and stored_energy_history:
        dt = config.dt
        tail_inj = inject_power_history[tail]
        tail_diss = diss_power_history[tail]
        total_injected = float(np.sum(tail_inj) * dt)
        total_dissipated = float(-np.sum(tail_diss) * dt)
        delta_stored = float(stored_energy_history[-1] - stored_energy_history[-tail_n])
        energy_balance = total_injected - total_dissipated - delta_stored
        energy_stats = {
            "energy_balance": round(energy_balance, 6),
            "total_injected": round(total_injected, 6),
            "total_dissipated": round(total_dissipated, 6),
            "delta_stored": round(delta_stored, 6),
            "mean_stored_energy": round(float(np.mean(stored_energy_history[tail])), 6),
        }

    lattice_stats: Dict[str, Any] = {}
    if per_loop_pump_history is not None and per_loop_mode_history is not None:
        pump_arr = np.array(per_loop_pump_history, dtype=float).T
        pump_tail_arr = pump_arr[tail, :]
        loop_rows = []
        for loop_i in range(pump_arr.shape[1]):
            pt = pump_tail_arr[:, loop_i]
            pv = float(np.std(pt) / (np.mean(pt) + 1e-8))
            loop_rows.append({
                "loop": loop_i,
                "dominant_mode": Counter(per_loop_mode_history[loop_i][tail]).most_common(1)[0][0],
                "pump_mode_rel_var": round(pv, 5),
                "stable": pv < config.pump_stability_rel_var,
            })
        lattice_stats = {
            "per_loop": loop_rows,
            "all_loops_mode3_stable": all(r["dominant_mode"] == config.pump_mode for r in loop_rows),
            **analyze_lattice_sync(pump_tail_arr),
        }
        if per_loop_stored_history is not None and per_loop_stored_history[0]:
            stored_arr = np.array(per_loop_stored_history, dtype=float).T
            stored_tail_arr = stored_arr[tail, :]
            lattice_stats["mean_per_loop_stored_energy"] = round(
                float(np.mean(stored_tail_arr)), 6
            )
            lattice_stats["per_loop_stored_energy_std"] = round(
                float(np.std(np.mean(stored_tail_arr, axis=0))), 6
            )
            lattice_stats.update(analyze_pairwise_sync(stored_tail_arr, prefix="energy"))
        if config.traveling_pulse_enabled and active_loop_history:
            lattice_stats["pulse_hopping"] = {
                **analyze_pulse_hopping(
                    active_loop_history, len(per_loop_pump_history)
                ),
                "conditional_hop_count": pulse_hop_count,
                "burst_mode": config.traveling_pulse_burst_mode,
                "conditional_hop": config.traveling_pulse_conditional_hop,
                "drift_threshold": config.traveling_pulse_drift_threshold,
            }
        lattice_stats["_per_loop_pump_tail"] = pump_tail_arr

    if radiation_impact_total > 0:
        lattice_stats["radiation_impact_count"] = radiation_impact_total
    if adaptive_memory is not None:
        lattice_stats["adaptive_memory"] = adaptive_memory.summary()
    if predictive_controller is not None:
        lattice_stats["predictive_adaptive_controller"] = predictive_controller.summary()
    if recovery_tracker is not None:
        lattice_stats["impact_recovery"] = recovery_tracker.summary(config.frames)
    if plasma_fluid_state is not None:
        lattice_stats["plasma_fluid"] = plasma_fluid_summary(plasma_fluid_state)
    if fluid_time_state is not None:
        lattice_stats["fluid_time"] = fluid_time_summary(fluid_time_state)
    if gyro_pll_memory is not None:
        lattice_stats["gyro_pll_memory"] = gyro_pll_summary(gyro_pll_memory)
    if getattr(config, "enable_central_potential", False):
        lattice_stats["central_potential"] = central_potential_diagnostics(
            config, x, y, vx, vy
        )
    compression_stats: Dict[str, Any] = {}
    if compression_tracker is not None:
        compression_stats["compression_twist"] = compression_tracker.summary(config)

    win_checklist: Dict[str, Any] = {}
    if energy_stats:
        # Inline containment score (same formula as plasma_physics helper) so
        # intrinsic lattice runs do not import the plasma module just for this.
        inj = float(energy_stats.get("total_injected", 0.0))
        diss = float(energy_stats.get("total_dissipated", 0.0))
        denom = abs(inj) + abs(diss) + 1e-12
        residual = abs(inj - diss)
        win_checklist["energy_containment"] = round(
            float(np.clip(1.0 - residual / denom, 0.0, 1.0)), 4
        )
        win_checklist["energy_balance_abs"] = round(
            abs(energy_stats.get("energy_balance", 0.0)), 6
        )
    if lattice_stats.get("mean_pairwise_corr") is not None:
        # Inline corr→[0,1] map (same as plasma_physics.sync_score_from_corr).
        c = float(lattice_stats["mean_pairwise_corr"])
        win_checklist["sync_score"] = (
            0.0 if not np.isfinite(c) else round(float(np.clip((c + 1.0) * 0.5, 0.0, 1.0)), 4)
        )
    if plasma_state is not None:
        win_checklist["plasma_snap_events"] = plasma_state.snap_events
        win_checklist["plasma_hop_snap_events"] = plasma_state.hop_snap_events
        win_checklist["plasma_active_snap_frames"] = plasma_state.active_snap_frames
        if getattr(config, "plasma_synchronization_enabled", False) or getattr(
            config, "plasma_mirror_balance_enabled", False
        ):
            win_checklist["plasma_sync_lock_events"] = plasma_state.sync_lock_events
            if plasma_state.loop_presence_ema:
                win_checklist["plasma_mean_presence"] = round(
                    float(np.mean(list(plasma_state.loop_presence_ema.values()))), 6
                )

    result: Dict[str, Any] = {
        "success": True,
        "avg_activity": round(avg_activity, 4),
        "avg_deformation": round(avg_deformation, 4),
        "avg_segment_stretch": round(float(np.mean(stretch_history[tail])), 5),
        "perimeter_ratio": round(float(np.mean(perimeter_history[tail])) / (initial_perimeter + 1e-12), 4),
        "dominant_mode": dominant_mode,
        "stable": is_stable,
        "equilibrium_type": equilibrium_type,
        "regime": classify_regime(avg_deformation, is_stable, rel_deform_var, equilibrium_type),
        "drift_percent": round(drift_percent, 4),
        "activity_variation": round(activity_var, 5),
        "deformation_variation": round(deform_var, 5),
        "relative_activity_var": round(rel_activity_var, 5),
        "relative_deformation_var": round(rel_deform_var, 5),
        "pump_mode_rel_var": round(pump_rel_var, 5),
        "pump_mode_stable": pump_mode_stable,
        "stability_score": round(rel_activity_var + rel_deform_var, 5),
        "final_activity": round(activity_history[-1], 4),
        **energy_stats,
        **lattice_stats,
        **compression_stats,
        **({"win_checklist": win_checklist} if win_checklist else {}),
        "mode_energies": mode_energies,
        **{k: v for k, v in asdict(config).items() if k != "seed"},
        **(
            {"loop_material": material_summary(resolve_loop_material(config))}
            if config.material_properties_enabled
            else {}
        ),
        "_activity_history": activity_history,
        "_deformation_history": deformation_history,
        "_x_history": x_history,
        "_y_history": y_history,
        "_pulse_phase_history": pulse_phase_history,
        "_active_loop_history": active_loop_history,
    }
    if config.track_energy_ledger and stored_energy_history:
        result["_stored_energy_history"] = stored_energy_history
        result["_inject_power_history"] = inject_power_history
        result["_diss_power_history"] = diss_power_history
    return result


def run_simulation(config: SimConfig, show_animation: bool = False) -> Dict[str, Any]:
    raw = _simulate(config, record_shapes=show_animation)
    if raw is None:
        return {
            "success": False,
            "equilibrium_type": "unstable",
            "dominant_mode": -1,
            "regime": "Collapsing",
            "avg_activity": float("nan"),
            "avg_deformation": float("nan"),
            "lyapunov": float("nan"),
        }

    result = dict(raw)

    if config.compute_emergent_mode and config.forcing_enabled and config.gamma > 0:
        free_cfg = replace(
            config,
            forcing_enabled=False,
            gamma=0.0,
            compute_emergent_mode=False,
            compute_lyapunov=False,
        )
        free_raw = _simulate(free_cfg)
        if free_raw:
            result.update(analyze_emergent_modes(
                result["mode_energies"], free_raw["mode_energies"], config.k
            ))

    if config.compute_lyapunov:
        result["lyapunov"] = round(estimate_lyapunov(config), 4)
    else:
        result["lyapunov"] = float("nan")

    if not show_animation:
        for key in (
            "_activity_history",
            "_deformation_history",
            "_x_history",
            "_y_history",
            "_pulse_phase_history",
            "_per_loop_fft",
            "_per_loop_pump_tail",
            "_active_loop_history",
        ):
            result.pop(key, None)

    return result


def simulate(
    config: SimConfig, *, record_shapes: bool = False
) -> Optional[Dict[str, Any]]:
    """Low-level run returning full diagnostics (including internal history keys)."""
    return _simulate(config, record_shapes=record_shapes)


def run_batch(
    config: SimConfig, overrides: List[Dict[str, Any]], stage: str = ""
) -> List[Dict[str, Any]]:
    results = []
    for override in overrides:
        cfg = replace(config, **{k: v for k, v in override.items() if k != "stage"})
        stats = run_simulation(cfg)
        if stats.get("success", True):
            stats["stage"] = override.get("stage", stage)
            results.append(stats)
    return results