"""
Adaptive gyro memory + radiation impact experiment overlays.
"""

from __future__ import annotations

from typing import Any, Dict

from driven_loop.experiments.gravity_well import GR_WELL_STABILIZED

ADAPTIVE_DISABLED: Dict[str, Any] = dict(
    adaptive_gyro_memory_enabled=False,
    radiation_impact_enabled=False,
)

_RADIATION_PROXY: Dict[str, Any] = dict(
    radiation_impact_enabled=True,
    radiation_impact_prob=0.004,
    radiation_impact_strength=0.10,
    radiation_impact_tangential_fraction=0.65,
    radiation_impact_warmup_frames=800,
)

# Implicit memory only: stabilized GR + radiation kicks
STABILIZED_RADIATION: Dict[str, Any] = {
    **GR_WELL_STABILIZED,
    **_RADIATION_PROXY,
    "adaptive_gyro_memory_enabled": False,
}

# Explicit adaptive memory on top of stabilized + radiation
STABILIZED_RADIATION_ADAPTIVE: Dict[str, Any] = {
    **STABILIZED_RADIATION,
    "adaptive_gyro_memory_enabled": True,
    "adaptive_memory_activity_decay": 0.996,
    "adaptive_memory_impact_decay": 0.992,
    "adaptive_memory_learning_rate": 0.035,
    "adaptive_memory_activity_ref": 0.02,
    "adaptive_memory_gyro_scale": 0.55,
    "adaptive_memory_torque_scale": 0.45,
    "adaptive_memory_gain_min": 0.75,
    "adaptive_memory_gain_max": 2.25,
}

ADAPTIVE_EXPERIMENT_PROFILES: Dict[str, Dict[str, Any]] = {
    "disabled": ADAPTIVE_DISABLED,
    "stabilized_radiation": STABILIZED_RADIATION,
    "stabilized_radiation_adaptive": STABILIZED_RADIATION_ADAPTIVE,
}


def adaptive_experiment(profile: str) -> Dict[str, Any]:
    if profile not in ADAPTIVE_EXPERIMENT_PROFILES:
        raise KeyError(
            f"Unknown adaptive profile {profile!r}; "
            f"choose from {list(ADAPTIVE_EXPERIMENT_PROFILES)}"
        )
    return dict(ADAPTIVE_EXPERIMENT_PROFILES[profile])


def apply_adaptive_experiment(
    base: Dict[str, Any], profile: str = "stabilized_radiation_adaptive",
) -> Dict[str, Any]:
    return {**base, **adaptive_experiment(profile)}