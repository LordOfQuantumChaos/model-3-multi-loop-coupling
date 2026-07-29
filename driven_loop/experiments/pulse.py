"""
Traveling-pulse / inter-loop hopping — EXPERIMENT ONLY.

Use only when studying energy transfer or lattice synchronization.
Production lattice and single-loop paths keep traveling_pulse_enabled=False.

Profiles
--------
``lattice_hopping`` / ``lattice_hopping_burst`` (recommended):
  Short bursts + drift-conditional hops (~5–10 per 6000f). See
  ``driven_loop.pulse_transport`` for the runtime gate logic.

``lattice_hopping_legacy``:
  Continuous ramp pulse with stochastic skip_prob hops (high rate).

``lattice_pulse_local``:
  Burst pulse without inter-loop transfer.

Usage::

  from driven_loop.experiments.pulse import apply_pulse_experiment
  cfg = apply_pulse_experiment(INTRINSIC_LATTICE_DEFAULT, "lattice_hopping_burst")
"""

from __future__ import annotations

from typing import Any, Dict

# Explicit off-state merged into all production defaults
PULSE_DISABLED: Dict[str, Any] = dict(
    traveling_pulse_enabled=False,
    traveling_pulse_inter_loop_transfer=False,
    traveling_pulse_skip_prob=0.0,
    traveling_pulse_burst_mode=False,
    traveling_pulse_conditional_hop=False,
)

# Burst + drift-conditional hops (~5–10 transfers per 6000f run, weaker kicks)
_LATTICE_HOPPING_BURST: Dict[str, Any] = dict(
    traveling_pulse_enabled=True,
    traveling_pulse_injection="kick",
    traveling_pulse_ramp_only=False,
    traveling_pulse_strength=0.010,
    traveling_pulse_speed=0.07,
    traveling_pulse_skip_prob=0.0,
    traveling_pulse_inter_loop_transfer=True,
    traveling_pulse_active_loop=0,
    traveling_pulse_burst_mode=True,
    traveling_pulse_burst_length=45,
    traveling_pulse_burst_period=550,
    traveling_pulse_conditional_hop=True,
    traveling_pulse_drift_threshold=0.75,
    traveling_pulse_hop_prob=0.018,
    traveling_pulse_max_hops_per_run=10,
    traveling_pulse_hop_cooldown_frames=180,
)

# Legacy continuous ramp pulse (high hop rate — prefer lattice_hopping_burst)
_LATTICE_HOPPING_LEGACY: Dict[str, Any] = dict(
    traveling_pulse_enabled=True,
    traveling_pulse_injection="kick",
    traveling_pulse_ramp_only=True,
    traveling_pulse_strength=0.028,
    traveling_pulse_speed=0.07,
    traveling_pulse_skip_prob=0.012,
    traveling_pulse_inter_loop_transfer=True,
    traveling_pulse_active_loop=0,
    traveling_pulse_burst_mode=False,
    traveling_pulse_conditional_hop=False,
)

# Same burst hopper but no inter-loop transfer (local desync study)
_LATTICE_PULSE_LOCAL: Dict[str, Any] = {
    **_LATTICE_HOPPING_BURST,
    "traveling_pulse_inter_loop_transfer": False,
    "traveling_pulse_max_hops_per_run": 0,
}

PULSE_EXPERIMENT_PROFILES: Dict[str, Dict[str, Any]] = {
    "lattice_hopping": _LATTICE_HOPPING_BURST,
    "lattice_hopping_burst": _LATTICE_HOPPING_BURST,
    "lattice_hopping_legacy": _LATTICE_HOPPING_LEGACY,
    "lattice_pulse_local": _LATTICE_PULSE_LOCAL,
}


def lattice_pulse_hopping(profile: str = "lattice_hopping") -> Dict[str, Any]:
    """Return a pulse experiment overlay dict (does not copy base config)."""
    if profile not in PULSE_EXPERIMENT_PROFILES:
        raise KeyError(
            f"Unknown pulse profile {profile!r}; choose from {list(PULSE_EXPERIMENT_PROFILES)}"
        )
    return dict(PULSE_EXPERIMENT_PROFILES[profile])


def apply_pulse_experiment(base: Dict[str, Any], profile: str = "lattice_hopping") -> Dict[str, Any]:
    """Merge base config with an experiment-only pulse profile."""
    return {**base, **lattice_pulse_hopping(profile)}


# Back-compat alias used by older scripts
LATTICE_PULSE_TRANSFER: Dict[str, Any] = _LATTICE_HOPPING_LEGACY