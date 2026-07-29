"""
GR gravity-well experiments — opt-in only, production unchanged.
"""

from __future__ import annotations

from typing import Any, Dict

GR_DISABLED: Dict[str, Any] = dict(
    gr_well_enabled=False,
    gr_strength=0.0,
    gr_gyro_barrier_enabled=False,
    gr_orbital_steering_enabled=False,
    # Keep central_potential off in production GR_DISABLED
    enable_central_potential=False,
)

# User recipe: very weak 1/r² pull + linear radial gyro damp (no torque)
CENTRAL_POTENTIAL_WEAK: Dict[str, Any] = dict(
    enable_central_potential=True,
    central_potential_strength=0.0008,
    central_gyro_base=0.12,
    central_gyro_radial_boost=0.35,
    central_potential_min_r=0.15,
    central_gyro_dt_cap=0.25,
    # Do not enable full GR well / orbital torque for this experiment
    gr_well_enabled=False,
    gr_gyro_barrier_enabled=False,
    gr_orbital_steering_enabled=False,
    gr_strength=0.0,
)

# Mild central well (tests divergence without stabilizers)
GR_WELL_ONLY: Dict[str, Any] = {
    **GR_DISABLED,
    "gr_well_enabled": True,
    "gr_strength": 0.012,
    "gr_well_softening": 0.15,
    "gr_well_min_radius": 0.25,
    "gr_force_cap": 2.0,
}

# Proximity gyro barrier (no inward pull — isolates damping)
GR_GYRO_BARRIER_ONLY: Dict[str, Any] = {
    **GR_DISABLED,
    "gr_gyro_barrier_enabled": True,
    "gyro_enabled": True,
    "gyro_strength": 0.12,
    "gyro_mode": "local",
}

# Full accretion-disk style stabilization
GR_WELL_STABILIZED: Dict[str, Any] = {
    "gr_well_enabled": True,
    "gr_strength": 0.008,
    "gr_well_softening": 0.2,
    "gr_well_min_radius": 0.3,
    "gr_force_cap": 1.5,
    "gr_well_center_x": 0.0,
    "gr_well_center_y": 0.0,
    "gr_gyro_barrier_enabled": True,
    "gr_gyro_proximity_scale": 1.2,
    "gr_orbital_steering_enabled": True,
    "gr_orbital_strength": 0.06,
    "gr_orbital_infall_threshold": 0.02,
    "gyro_enabled": True,
    "gyro_strength": 0.10,
    "gyro_mode": "local",
}

GR_EXPERIMENT_PROFILES: Dict[str, Dict[str, Any]] = {
    "disabled": GR_DISABLED,
    "well_only": GR_WELL_ONLY,
    "gyro_barrier_only": GR_GYRO_BARRIER_ONLY,
    "well_stabilized": GR_WELL_STABILIZED,
    "central_potential_weak": CENTRAL_POTENTIAL_WEAK,
}


def gr_experiment(profile: str = "well_stabilized") -> Dict[str, Any]:
    if profile not in GR_EXPERIMENT_PROFILES:
        raise KeyError(
            f"Unknown GR profile {profile!r}; choose from {list(GR_EXPERIMENT_PROFILES)}"
        )
    return dict(GR_EXPERIMENT_PROFILES[profile])


def apply_gr_experiment(base: Dict[str, Any], profile: str = "well_stabilized") -> Dict[str, Any]:
    return {**base, **gr_experiment(profile)}