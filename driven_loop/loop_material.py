"""
Loop material properties — Young's modulus, density, damping, cross-section.

When material_properties_enabled=True, E / rho / zeta scale the production-tuned
force coefficients (alpha, tension, radial, beta) and nodal mass relative to a
reference cross-section. Production behavior is unchanged when disabled.

Absolute beam-theory coefficients are available via material_absolute_mode=True
with calibration scales.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from driven_loop.core import SimConfig

# Reference geometry for relative scaling (dimensionless sim units)
_REF_CROSS_SECTION_RADIUS = 0.01


@dataclass(frozen=True)
class LoopMaterialResolved:
    """Effective coefficients after material resolution."""

    enabled: bool
    youngs_modulus: float
    density: float
    damping_ratio: float
    poisson_ratio: float
    cross_section_area: float
    second_moment: float
    linear_density: float
    mass_per_node: float
    segment_length: float
    alpha: float
    tension_stiffness: float
    tension_curvature_stiffness: float
    radial_stiffness: float
    beta: float
    bending_scale: float
    axial_scale: float
    mass_scale: float


def circular_cross_section(radius: float) -> tuple[float, float]:
    """Area A and second moment I for a solid circular rod."""
    r = max(float(radius), 1e-12)
    area = math.pi * r * r
    moment = math.pi * r**4 / 4.0
    return area, moment


def ring_segment_length(R0: float, N: int) -> float:
    return 2.0 * math.pi * float(R0) / max(int(N), 1)


def _section_properties(config: SimConfig) -> tuple[float, float, float]:
    area = float(getattr(config, "cross_section_area", 0.0))
    moment = float(getattr(config, "second_moment_area", 0.0))
    r_cs = float(getattr(config, "cross_section_radius", _REF_CROSS_SECTION_RADIUS))
    if area <= 0.0 or moment <= 0.0:
        area, moment = circular_cross_section(r_cs)
    return area, moment, r_cs


def resolve_loop_material(config: SimConfig) -> LoopMaterialResolved:
    """
    Map material inputs to simulator coefficients.

    Relative mode (default): scales legacy tuned coeffs by E·I, E·A, rho·A ratios.
    Absolute mode: beam-theory EI/ds⁴ etc. with calibration multipliers.
    """
    R0 = float(config.R0)
    N = int(config.N)
    ds = ring_segment_length(R0, N)

    if not getattr(config, "material_properties_enabled", False):
        return LoopMaterialResolved(
            enabled=False,
            youngs_modulus=0.0,
            density=0.0,
            damping_ratio=0.0,
            poisson_ratio=0.0,
            cross_section_area=0.0,
            second_moment=0.0,
            linear_density=0.0,
            mass_per_node=1.0,
            segment_length=ds,
            alpha=float(config.alpha),
            tension_stiffness=float(config.tension_stiffness),
            tension_curvature_stiffness=float(config.tension_curvature_stiffness),
            radial_stiffness=float(config.radial_stiffness),
            beta=float(config.beta),
            bending_scale=1.0,
            axial_scale=1.0,
            mass_scale=1.0,
        )

    E = max(float(getattr(config, "youngs_modulus", 1.0)), 1e-12)
    rho = max(float(getattr(config, "material_density", 1.0)), 1e-12)
    zeta = max(float(getattr(config, "damping_ratio", 0.02)), 0.0)
    nu = float(getattr(config, "poisson_ratio", 0.3))
    zeta_ref = max(float(getattr(config, "material_damping_reference", 0.02)), 1e-12)

    area, moment, r_cs = _section_properties(config)
    ref_area, ref_moment = circular_cross_section(_REF_CROSS_SECTION_RADIUS)

    E_ref = max(float(getattr(config, "youngs_modulus_reference", 1.0)), 1e-12)
    rho_ref = max(float(getattr(config, "material_density_reference", 1.0)), 1e-12)

    bend_scale = (E * moment) / max(E_ref * ref_moment, 1e-18)
    axial_scale = (E * area) / max(E_ref * ref_area, 1e-18)
    mass_scale = (rho * area) / max(rho_ref * ref_area, 1e-18)

    cal_b = float(getattr(config, "material_calib_bending", 1.0))
    cal_t = float(getattr(config, "material_calib_tension", 1.0))
    cal_tc = float(getattr(config, "material_calib_tension_curvature", 1.0))
    cal_r = float(getattr(config, "material_calib_radial", 1.0))
    cal_d = float(getattr(config, "material_calib_damping", 1.0))
    damp_scale = (zeta / zeta_ref) * cal_d

    mu = rho * area
    m_node = max(mass_scale, 1e-6)

    if getattr(config, "material_absolute_mode", False):
        EI = E * moment
        EA = E * area
        ds4 = max(ds**4, 1e-24)
        alpha = cal_b * EI / ds4
        tension = cal_t * EA / max(ds, 1e-12)
        tension_curv = cal_tc * EI / max(ds**3, 1e-18)
        radial = cal_r * EA / max(R0 * R0, 1e-12)
        omega_ref = math.sqrt(max(EI / (mu * max(R0**4, 1e-12)), 0.0))
        beta = cal_d * 2.0 * zeta * omega_ref
        m_node = max(mu * ds, 1e-12)
    else:
        alpha = float(config.alpha) * bend_scale * cal_b
        tension = float(config.tension_stiffness) * axial_scale * cal_t
        tension_curv = (
            float(config.tension_curvature_stiffness) * bend_scale * cal_tc
        )
        radial = float(config.radial_stiffness) * axial_scale * cal_r
        beta = max(float(config.beta), float(config.beta_minimal)) * damp_scale
        if float(config.beta) == 0.0 and float(config.beta_minimal) == 0.0:
            beta = 0.02 * damp_scale

    blend = float(getattr(config, "material_legacy_blend", 0.0))
    blend = min(max(blend, 0.0), 1.0)
    if blend > 0.0:
        alpha = (1.0 - blend) * alpha + blend * float(config.alpha)
        tension = (1.0 - blend) * tension + blend * float(config.tension_stiffness)
        tension_curv = (1.0 - blend) * tension_curv + blend * float(
            config.tension_curvature_stiffness
        )
        radial = (1.0 - blend) * radial + blend * float(config.radial_stiffness)
        beta = (1.0 - blend) * beta + blend * float(config.beta)

    return LoopMaterialResolved(
        enabled=True,
        youngs_modulus=E,
        density=rho,
        damping_ratio=zeta,
        poisson_ratio=nu,
        cross_section_area=area,
        second_moment=moment,
        linear_density=mu,
        mass_per_node=m_node,
        segment_length=ds,
        alpha=alpha,
        tension_stiffness=tension,
        tension_curvature_stiffness=tension_curv,
        radial_stiffness=radial,
        beta=beta,
        bending_scale=bend_scale,
        axial_scale=axial_scale,
        mass_scale=mass_scale,
    )


def material_summary(resolved: LoopMaterialResolved) -> dict:
    return {
        "material_properties_enabled": resolved.enabled,
        "youngs_modulus": round(resolved.youngs_modulus, 6),
        "material_density": round(resolved.density, 6),
        "damping_ratio": round(resolved.damping_ratio, 6),
        "poisson_ratio": round(resolved.poisson_ratio, 4),
        "cross_section_area": round(resolved.cross_section_area, 8),
        "second_moment_area": round(resolved.second_moment, 10),
        "linear_density": round(resolved.linear_density, 8),
        "mass_per_node": round(resolved.mass_per_node, 6),
        "bending_scale": round(resolved.bending_scale, 4),
        "axial_scale": round(resolved.axial_scale, 4),
        "mass_scale": round(resolved.mass_scale, 4),
        "resolved_alpha": round(resolved.alpha, 6),
        "resolved_tension_stiffness": round(resolved.tension_stiffness, 6),
        "resolved_radial_stiffness": round(resolved.radial_stiffness, 6),
        "resolved_beta": round(resolved.beta, 6),
    }