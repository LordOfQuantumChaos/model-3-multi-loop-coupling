"""
Fluid plasma + fluid time experiment overlays (opt-in only).
"""

from __future__ import annotations

from typing import Any, Dict

from driven_loop.experiments.gravity_well import GR_WELL_STABILIZED
from driven_loop.experiments.gyro_pll import GYRO_PLL_GENTLE

FLUID_DISABLED: Dict[str, Any] = dict(
    plasma_fluid_enabled=False,
    time_fluid_enabled=False,
)

# Gentle plasma fluid (55° helix source, no discrete spiral snap)
PLASMA_FLUID_GENTLE: Dict[str, Any] = {
    "plasma_enabled": True,
    "plasma_fluid_enabled": True,
    "plasma_fluid_density_init": 0.01,
    "plasma_fluid_injection": 0.004,
    "plasma_fluid_tangential_injection": 0.0025,
    "plasma_fluid_viscosity": 0.06,
    "plasma_fluid_pressure_strength": 0.05,
    "plasma_fluid_advection_strength": 0.04,
    "plasma_fluid_gamma": 1.35,
    "plasma_fluid_activity_coupling": 0.02,
    "plasma_fluid_rho_max": 0.25,
    "plasma_helix_angle": 55.0,
    "plasma_k": 3,
    "plasma_omega": 0.15,
    # discrete spiral off when fluid handles transport
    "plasma_strength": 0.0,
    "plasma_tangential": 0.0,
    "plasma_snap_enabled": False,
}

# Time as fluid — local tau field modulates stabilization strength
TIME_FLUID_GENTLE: Dict[str, Any] = {
    "time_fluid_enabled": True,
    "time_fluid_density": 1.0,
    "time_fluid_viscosity": 0.07,
    "time_fluid_advection": 0.12,
    "time_fluid_activity_coupling": 0.08,
    "time_fluid_injection": 0.002,
    "time_fluid_omega": 0.1,
    "time_fluid_force_coupling": 0.35,
    "time_fluid_tau_min": 0.5,
    "time_fluid_tau_max": 3.0,
}

# GR + gentle plasma fluid only (no time fluid, no PLL)
GR_PLASMA_FLUID_STACK: Dict[str, Any] = {
    **GR_WELL_STABILIZED,
    **PLASMA_FLUID_GENTLE,
}

# Full fluid stack on GR-stabilized substrate (5×5 / Shield Panel path)
FLUID_GR_STACK: Dict[str, Any] = {
    **GR_PLASMA_FLUID_STACK,
    **TIME_FLUID_GENTLE,
}

# Fluid plasma + fluid time + PLL gyro memory (collective rhythm lock)
FLUID_PLL_MEMORY_STACK: Dict[str, Any] = {
    **FLUID_GR_STACK,
    **GYRO_PLL_GENTLE,
}

FLUID_EXPERIMENT_PROFILES: Dict[str, Dict[str, Any]] = {
    "disabled": FLUID_DISABLED,
    "plasma_fluid_gentle": PLASMA_FLUID_GENTLE,
    "time_fluid_gentle": TIME_FLUID_GENTLE,
    "gr_plasma_fluid_stack": GR_PLASMA_FLUID_STACK,
    "fluid_gr_stack": FLUID_GR_STACK,
    "fluid_pll_memory_stack": FLUID_PLL_MEMORY_STACK,
}


def fluid_experiment(profile: str) -> Dict[str, Any]:
    if profile not in FLUID_EXPERIMENT_PROFILES:
        raise KeyError(
            f"Unknown fluid profile {profile!r}; choose from {list(FLUID_EXPERIMENT_PROFILES)}"
        )
    return dict(FLUID_EXPERIMENT_PROFILES[profile])


def apply_fluid_experiment(base: Dict[str, Any], profile: str) -> Dict[str, Any]:
    return {**base, **fluid_experiment(profile)}