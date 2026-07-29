"""
Plasma flow scenarios — EXPERIMENT ONLY (Shield Panel / barb geometry tests).

Four comparison scenarios (see scripts/run_plasma_scenario_compare.py):

  1. baseline          — no plasma
  2. radial_only       — straight radial spray
  3. tangential_only   — pure angular twist
  4. helical_55_barb   — 55° helix matching barb scattering angle

Production keeps plasma_enabled=False.
"""

from __future__ import annotations

from typing import Any, Dict

_COMMON_ON: Dict[str, Any] = dict(
    plasma_enabled=True,
    plasma_flow_enabled=True,  # back-compat alias
    plasma_k=3,
    plasma_omega=0.15,
    plasma_snap_enabled=True,
    plasma_snap_threshold=0.04,
    plasma_snap_strength=0.35,
)

# Gentle 55° helix with energy gate — plasma only where local energy exceeds threshold
_HELICAL_55_ENERGY_GATED: Dict[str, Any] = {
    "plasma_enabled": True,
    "plasma_flow_enabled": True,
    "plasma_k": 3,
    "plasma_omega": 0.15,
    "plasma_geometry": "helical",
    "plasma_strength": 0.08,
    "plasma_tangential": 0.05,
    "plasma_helix_angle": 55.0,
    "plasma_snap_enabled": False,
    "plasma_energy_gate_enabled": True,
    "plasma_energy_threshold": 0.02,
}

# Gentle 55° helix — spiral only (stability-friendly next-run tuning)
_GENTLE_HELICAL_55: Dict[str, Any] = {
    "plasma_enabled": True,
    "plasma_flow_enabled": True,
    "plasma_k": 3,
    "plasma_omega": 0.15,
    "plasma_geometry": "helical",
    "plasma_strength": 0.008,
    "plasma_tangential": 0.005,
    "plasma_helix_angle": 55.0,
    "plasma_snap_enabled": False,
    "plasma_synchronization_enabled": False,
}

# Gentle helix + phase-lock "hiding": sync to pump mode on energy spikes only
_GENTLE_HELICAL_55_SYNC_HIDING: Dict[str, Any] = {
    **_GENTLE_HELICAL_55,
    "plasma_synchronization_enabled": True,
    "plasma_phase_lock_strength": 0.3,
    "plasma_helical_path_bias": 0.4,
    "plasma_sync_threshold": 0.02,
    "plasma_mirror_balance_enabled": False,
}

# Mirror-balance: 55° helical mirror + frequency-stability feedback
# Strength/bias raised so *when* energy exceeds threshold, plasma actually moves metrics.
# (Earlier 0.008/0.35/0.45 was inert vs GR+KF at thr=0.02.)
_GENTLE_HELICAL_55_MIRROR_BALANCE: Dict[str, Any] = {
    **_GENTLE_HELICAL_55,
    "plasma_synchronization_enabled": True,  # phase-lock to nearest known freq
    "plasma_mirror_balance_enabled": True,
    # Drive amplitude when engaged (still energy-gated by sync path)
    "plasma_strength": 0.04,
    "plasma_tangential": 0.025,
    "plasma_phase_lock_strength": 0.65,
    "plasma_helical_path_bias": 0.55,
    "plasma_helical_mirror_bias": 0.75,
    "balance_feedback_strength": 0.45,
    # Slightly softer gate so spikes engage more often
    "plasma_sync_threshold": 0.01,
}

# Stronger influence preset (opt-in name)
_MIRROR_BALANCE_STRONG: Dict[str, Any] = {
    **_GENTLE_HELICAL_55_MIRROR_BALANCE,
    "plasma_strength": 0.06,
    "plasma_tangential": 0.04,
    "plasma_phase_lock_strength": 0.8,
    "plasma_helical_mirror_bias": 0.85,
    "balance_feedback_strength": 0.55,
    "plasma_sync_threshold": 0.008,
}

# Diverge preset: low energy gate + always-on *early* window so plasma moves metrics,
# then returns to gated mode so long runs can re-settle into mode-3.
# Window 0..1500 of a 6000f production run (~25% always-on).
_MIRROR_BALANCE_DIVERGE: Dict[str, Any] = {
    **_GENTLE_HELICAL_55_MIRROR_BALANCE,
    "plasma_strength": 0.04,
    "plasma_tangential": 0.025,
    "plasma_phase_lock_strength": 0.7,
    "plasma_helical_mirror_bias": 0.8,
    "balance_feedback_strength": 0.5,
    "plasma_sync_threshold": 0.002,
    "plasma_always_on_window_enabled": True,
    "plasma_always_on_start_frame": 0,
    "plasma_always_on_end_frame": 1500,
    "plasma_always_on_engage": 1.0,
}

# Pulse-hop linked reconnection (requires pulse experiment overlay)
PLASMA_PULSE_LINKED: Dict[str, Any] = {
    **_GENTLE_HELICAL_55,
    "plasma_snap_enabled": True,
    "plasma_snap_threshold": 0.03,
    "plasma_snap_strength": 0.03,
    "plasma_snap_ramp_frames": 5,
    "plasma_snap_on_pulse_hop": True,
    "plasma_snap_use_deviation": True,
}

PLASMA_DISABLED: Dict[str, Any] = dict(
    plasma_enabled=False,
    plasma_flow_enabled=False,
    plasma_strength=0.0,
    plasma_tangential=0.0,
    plasma_helix_angle=55.0,
    plasma_geometry="helical",
    plasma_snap_enabled=False,
    plasma_synchronization_enabled=False,
    plasma_phase_lock_strength=0.3,
    plasma_helical_path_bias=0.4,
    plasma_sync_threshold=0.02,
    plasma_mirror_balance_enabled=False,
    plasma_helical_mirror_bias=0.45,
    balance_feedback_strength=0.2,
)

# Scenario 1 — baseline (no plasma)
SCENARIO_BASELINE: Dict[str, Any] = dict(PLASMA_DISABLED)

# Scenario 2 — straight radial plasma flow
SCENARIO_RADIAL: Dict[str, Any] = {
    **_COMMON_ON,
    "plasma_geometry": "radial",
    "plasma_strength": 0.08,
    "plasma_tangential": 0.0,
    "plasma_helix_angle": 0.0,
}

# Scenario 3 — pure angular / tangential flow
SCENARIO_TANGENTIAL: Dict[str, Any] = {
    **_COMMON_ON,
    "plasma_geometry": "tangential",
    "plasma_strength": 0.0,
    "plasma_tangential": 0.05,
    "plasma_helix_angle": 90.0,
}

# Scenario 4 — helical 55° (barb-matched resonance hypothesis)
SCENARIO_HELICAL_55: Dict[str, Any] = {
    **_COMMON_ON,
    "plasma_geometry": "helical",
    "plasma_strength": 0.08,
    "plasma_tangential": 0.05,
    "plasma_helix_angle": 55.0,
}

PLASMA_SCENARIO_PROFILES: Dict[str, Dict[str, Any]] = {
    "baseline": SCENARIO_BASELINE,
    "radial_only": SCENARIO_RADIAL,
    "tangential_only": SCENARIO_TANGENTIAL,
    "helical_55_barb": SCENARIO_HELICAL_55,
    "helical_55_gentle": _GENTLE_HELICAL_55,
    "helical_55_energy_gated": _HELICAL_55_ENERGY_GATED,
    "helical_55_sync_hiding": _GENTLE_HELICAL_55_SYNC_HIDING,
    "helical_55_mirror_balance": _GENTLE_HELICAL_55_MIRROR_BALANCE,
    "helical_55_mirror_balance_strong": _MIRROR_BALANCE_STRONG,
    "helical_55_mirror_balance_diverge": _MIRROR_BALANCE_DIVERGE,
    "plasma_pulse_linked": PLASMA_PULSE_LINKED,
}

# Legacy names
PLASMA_EXPERIMENT_PROFILES: Dict[str, Dict[str, Any]] = {
    **PLASMA_SCENARIO_PROFILES,
    "gentle_spiral": SCENARIO_HELICAL_55,
    "strong_spiral": {
        **SCENARIO_HELICAL_55,
        "plasma_strength": 0.12,
        "plasma_tangential": 0.08,
    },
    "tangential_only_legacy": SCENARIO_TANGENTIAL,
}


def plasma_scenario(profile: str) -> Dict[str, Any]:
    if profile not in PLASMA_SCENARIO_PROFILES:
        raise KeyError(
            f"Unknown plasma scenario {profile!r}; "
            f"choose from {list(PLASMA_SCENARIO_PROFILES)}"
        )
    return dict(PLASMA_SCENARIO_PROFILES[profile])


def plasma_flow_profile(profile: str = "helical_55_barb") -> Dict[str, Any]:
    if profile in PLASMA_EXPERIMENT_PROFILES:
        return dict(PLASMA_EXPERIMENT_PROFILES[profile])
    return plasma_scenario(profile)


def apply_plasma_experiment(base: Dict[str, Any], profile: str = "helical_55_barb") -> Dict[str, Any]:
    return {**base, **plasma_flow_profile(profile)}