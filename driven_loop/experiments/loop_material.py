"""
Loop material experiment profiles (opt-in only).

Young's modulus, density, and damping_ratio are relative to reference values
(E_ref=1, rho_ref=1, zeta_ref=0.02) and scale production-tuned force coefficients.
"""

from __future__ import annotations

from typing import Any, Dict

MATERIAL_DISABLED: Dict[str, Any] = dict(
    material_properties_enabled=False,
    youngs_modulus=1.0,
    material_density=1.0,
    damping_ratio=0.02,
    poisson_ratio=0.3,
    cross_section_radius=0.01,
    cross_section_area=0.0,
    second_moment_area=0.0,
    youngs_modulus_reference=1.0,
    material_density_reference=1.0,
    material_damping_reference=0.02,
    material_calib_bending=1.0,
    material_calib_tension=1.0,
    material_calib_tension_curvature=1.0,
    material_calib_radial=1.0,
    material_calib_damping=1.0,
    material_legacy_blend=0.0,
    material_absolute_mode=False,
)

# Stiff, light ring (Helixene / carbon-nanotube analog)
HELIXENE_RING: Dict[str, Any] = {
    **MATERIAL_DISABLED,
    "material_properties_enabled": True,
    "youngs_modulus": 3.0,
    "material_density": 0.45,
    "damping_ratio": 0.008,
    "poisson_ratio": 0.19,
    "cross_section_radius": 0.008,
}

# Soft polymer — compliant, lossy
SOFT_POLYMER_RING: Dict[str, Any] = {
    **MATERIAL_DISABLED,
    "material_properties_enabled": True,
    "youngs_modulus": 0.35,
    "material_density": 0.85,
    "damping_ratio": 0.12,
    "poisson_ratio": 0.45,
    "cross_section_radius": 0.015,
}

# Dense metal microfiber
STEEL_MICROFIBER: Dict[str, Any] = {
    **MATERIAL_DISABLED,
    "material_properties_enabled": True,
    "youngs_modulus": 5.0,
    "material_density": 4.0,
    "damping_ratio": 0.02,
    "poisson_ratio": 0.30,
    "cross_section_radius": 0.006,
}

MATERIAL_LEGACY_BLEND_HALF: Dict[str, Any] = {
    **HELIXENE_RING,
    "material_legacy_blend": 0.5,
}

MATERIAL_PROFILES: Dict[str, Dict[str, Any]] = {
    "disabled": MATERIAL_DISABLED,
    "helixene_ring": HELIXENE_RING,
    "soft_polymer": SOFT_POLYMER_RING,
    "steel_microfiber": STEEL_MICROFIBER,
    "legacy_blend_half": MATERIAL_LEGACY_BLEND_HALF,
}


def loop_material_experiment(profile: str) -> Dict[str, Any]:
    if profile not in MATERIAL_PROFILES:
        raise KeyError(
            f"Unknown material profile {profile!r}; choose from {list(MATERIAL_PROFILES)}"
        )
    return dict(MATERIAL_PROFILES[profile])