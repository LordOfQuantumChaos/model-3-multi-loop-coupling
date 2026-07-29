"""
Canonical intrinsic (unseeded) simulation defaults.

INTRINSIC_DEFAULT = v6 rebalanced bootstrap @ PRODUCTION_FRAMES (6000).
6000 frames balances full handoff + limit-cycle settling without the slow
pump-variance drift seen on a few borderline seeds at 8000+.
"""

from __future__ import annotations

from typing import Any, Dict

from driven_loop.experiments.adaptive_memory import ADAPTIVE_DISABLED
from driven_loop.experiments.fluid_physics import FLUID_DISABLED
from driven_loop.experiments.gyro_pll import GYRO_PLL_DISABLED
from driven_loop.experiments.qslt_resonance import QSLT_RESONANCE_DISABLED
from driven_loop.experiments.known_frequencies import KNOWN_FREQUENCIES_DISABLED
from driven_loop.experiments.gravity_well import GR_DISABLED
from driven_loop.experiments.plasma_flow import PLASMA_DISABLED
from driven_loop.experiments.pulse import PULSE_DISABLED
from driven_loop.experiments.predictive_adaptive import PAC_DISABLED
from driven_loop.stability_gates import MODE3_PUMP_STABILITY_REL_VAR

# Recommended simulation length for production / validation runs
PRODUCTION_FRAMES = 6000

# Shorter length used in early v5 hunts and quick smoke tests
LEGACY_HUNT_FRAMES = 2400

# v4 pump limit-cycle core (tuned winner knobs)
_PUMP_CORE_BASE: Dict[str, Any] = dict(
    forcing_enabled=False,
    gamma=0.0,
    beta=0.0,
    pump_limit_cycle_enabled=True,
    pump_mode=3,
    pump_vdp_enabled=True,
    pump_softening=0.55,
    pump_hardening=3.4,
    pump_vdp_mu=0.42,
    pump_vdp_dev_scale=0.08,
    vdp_enabled=False,
    threshold_excitation_enabled=False,
    gyro_enabled=False,
    dissipation_minimal=True,
    beta_minimal=0.0,
    internal_dynamics_enabled=True,
    internal_dynamics_strength=0.55,
    internal_dynamics_mode=3,
    tension_curvature_stiffness=0.25,
    asymmetry_strength=0.06,
    instability_gain=0.0,
    mode_selective_damp_enabled=True,
    mode_protect=3,
    mode_damp_from=4,
    mode_damp_non_pump_only=True,
    mode_damp_strength=0.25,
    conservative_coupling_enabled=False,
    mode_interaction_enabled=False,
    radial_stiffness=0.22,
    cubic_stiffness=0.25,
    alpha=0.022,
    initial_noise=0.008,
    integrator="verlet",
    tension_stiffness=1.0,
    reparam_interval=8,
    pump_stability_rel_var=0.03,
    initial_mode_seed=0.0,
)

_FIELD_V5 = dict(
    field_restoring_enabled=True,
    field_dev_strength=0.15,
    field_transmit_strength=0.08,
    field_stretch_strength=0.12,
    field_bend_strength=0.08,
    field_kernel_sigma=10.0,
)

_GAMMA_RAMP_V5 = dict(
    gamma_ramp_enabled=True,
    gamma_ramp_initial=0.018,
    gamma_ramp_decay_frames=1000,
    gamma_ramp_k=3,
)

_FIELD_V6 = dict(
    field_restoring_enabled=True,
    field_dev_strength=0.10,
    field_transmit_strength=0.05,
    field_stretch_strength=0.08,
    field_bend_strength=0.05,
    field_kernel_sigma=10.0,
)

_GAMMA_RAMP_V6 = dict(
    gamma_ramp_enabled=True,
    gamma_ramp_initial=0.0116,
    gamma_ramp_decay_frames=1200,
    gamma_ramp_k=3,
)

# Legacy v5 winner (field + gamma ramp, 73% on seeds 500-529 @ 2400f)
INTRINSIC_V5_WINNER: Dict[str, Any] = {
    **_PUMP_CORE_BASE,
    **_FIELD_V5,
    **_GAMMA_RAMP_V5,
    "frames": LEGACY_HUNT_FRAMES,
}

# Phase A (optional): k=1 drain — helps seed 53 mode selection but regresses seed 25; off in production
# pump_stability_rel_var: MODE3_PUMP_STABILITY_REL_VAR (0.055) so near-miss tails
# (e.g. pump_mode_rel_var≈0.0527 with all loops mode-3) classify as stable.
_PHASE_A_LOW_MODE = dict(
    mode_damp_low_modes_enabled=False,
    mode_damp_low_strength=0.0,
    mode_damp_low_max_mode=1,
    mode_damp_low_ramp_only=True,
    mode_damp_low_decay_frames=700,
    pump_stability_rel_var=MODE3_PUMP_STABILITY_REL_VAR,
)

# Phase B: excess-only pump-mode amplitude limiter — tightens pump breathing (seeds 53/90)
_PHASE_B_PUMP_LIMITER = dict(
    pump_amplitude_limiter_enabled=True,
    pump_amplitude_limiter_strength=1.0,
    pump_amplitude_limiter_scale=0.075,
)

# v6 rebalanced bootstrap — production length 6000 frames
INTRINSIC_V6_DEFAULT: Dict[str, Any] = {
    **_PUMP_CORE_BASE,
    **_FIELD_V6,
    **_GAMMA_RAMP_V6,
    "frames": PRODUCTION_FRAMES,
    **_PHASE_A_LOW_MODE,
    **_PHASE_B_PUMP_LIMITER,
    **PULSE_DISABLED,
    **PLASMA_DISABLED,
    **GR_DISABLED,
    **ADAPTIVE_DISABLED,
    **PAC_DISABLED,
    **FLUID_DISABLED,
    **GYRO_PLL_DISABLED,
    **QSLT_RESONANCE_DISABLED,
    **KNOWN_FREQUENCIES_DISABLED,
}

# Current production default for unseeded intrinsic simulation (single loop)
INTRINSIC_DEFAULT: Dict[str, Any] = INTRINSIC_V6_DEFAULT

# Loop lattice: 2x2 grid, velocity-only bonds (validated 100% stable mode 3 @ 2400f)
_LATTICE_V6 = dict(
    loop_lattice_enabled=True,
    loop_lattice_rows=2,
    loop_lattice_cols=2,
    loop_lattice_spacing=2.4,
    loop_lattice_coupling=0.012,
    loop_lattice_bond_width=0.4,
    loop_lattice_velocity_only=True,
    loop_lattice_phase_jitter=0.02,
)

# Shorter production length for lattice batches (4 rings per run)
LATTICE_FRAMES = 2400

INTRINSIC_LATTICE_DEFAULT: Dict[str, Any] = {
    **INTRINSIC_V6_DEFAULT,
    **_LATTICE_V6,
    "frames": LATTICE_FRAMES,
}

# 3x3 production lattice (constrained winner: weaker coupling, no pulse)
_LATTICE_3X3_V6 = dict(
    loop_lattice_enabled=True,
    loop_lattice_rows=3,
    loop_lattice_cols=3,
    loop_lattice_spacing=2.4,
    loop_lattice_coupling=0.006,
    loop_lattice_bond_width=0.4,
    loop_lattice_velocity_only=True,
    loop_lattice_phase_jitter=0.02,
)

INTRINSIC_LATTICE_3X3_DEFAULT: Dict[str, Any] = {
    **INTRINSIC_V6_DEFAULT,
    **_LATTICE_3X3_V6,
    "frames": PRODUCTION_FRAMES,
}

# Back-compat — prefer driven_loop.experiments.pulse for new experiment scripts
from driven_loop.experiments.pulse import LATTICE_PULSE_TRANSFER  # noqa: E402, F401