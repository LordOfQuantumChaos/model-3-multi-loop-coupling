"""
Compose multi-layer experiment stacks (all opt-in; production unchanged).

Usage::

    from driven_loop.experiments.full_stack import build_experiment_config
    from driven_loop.defaults import INTRINSIC_LATTICE_3X3_DEFAULT

    cfg = build_experiment_config(
        INTRINSIC_LATTICE_3X3_DEFAULT,
        gr_profile="well_stabilized",
        adaptive_profile="stabilized_radiation_adaptive",
    )
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from driven_loop.experiments.adaptive_memory import (
    ADAPTIVE_DISABLED,
    adaptive_experiment,
)
from driven_loop.experiments.fluid_physics import FLUID_DISABLED, fluid_experiment
from driven_loop.experiments.gyro_pll import GYRO_PLL_DISABLED, gyro_pll_experiment
from driven_loop.experiments.gravity_well import GR_DISABLED, gr_experiment
from driven_loop.experiments.plasma_flow import PLASMA_DISABLED, plasma_scenario
from driven_loop.experiments.pulse import PULSE_DISABLED, apply_pulse_experiment
from driven_loop.experiments.qslt_resonance import (
    QSLT_RESONANCE_DISABLED,
    apply_qslt_resonance,
)
from driven_loop.experiments.known_frequencies import KNOWN_FREQUENCIES_DISABLED
from driven_loop.experiments.compression_twist import (
    COMPRESSION_TWIST_DISABLED,
    compression_twist_experiment,
)

EXPERIMENT_STACK_PROFILES: Dict[str, Dict[str, Optional[str]]] = {
    "production": {
        "pulse": None, "plasma": None, "gr": None, "adaptive": None,
        "fluid": None, "gyro_pll": None,
    },
    "gr_stabilized": {
        "pulse": None, "plasma": None, "gr": "well_stabilized", "adaptive": None,
        "fluid": None, "gyro_pll": None,
    },
    "gr_radiation_adaptive": {
        "pulse": None, "plasma": None, "gr": "well_stabilized",
        "adaptive": "stabilized_radiation_adaptive", "fluid": None, "gyro_pll": None,
    },
    "gr_plasma_fluid_stack": {
        "pulse": None, "plasma": None, "gr": "well_stabilized",
        "adaptive": None, "fluid": "gr_plasma_fluid_stack", "gyro_pll": None,
    },
    "fluid_gr_stack": {
        "pulse": None, "plasma": None, "gr": "well_stabilized",
        "adaptive": None, "fluid": "fluid_gr_stack", "gyro_pll": None,
    },
    "fluid_pll_memory_stack": {
        "pulse": None, "plasma": None, "gr": "well_stabilized",
        "adaptive": None, "fluid": "fluid_pll_memory_stack", "gyro_pll": None,
    },
    "pulse_hopping": {
        "pulse": "lattice_hopping_burst", "plasma": None, "gr": None,
        "adaptive": None, "fluid": None, "gyro_pll": None,
    },
    "shield_panel_plasma": {
        "pulse": None, "plasma": "helical_55_gentle", "gr": None,
        "adaptive": None, "fluid": None, "gyro_pll": None,
    },
    # GR well + gentle always-on 55° helix plasma (KF applied separately via known_frequencies)
    "gr_gentle_helix_plasma": {
        "pulse": None, "plasma": "helical_55_gentle", "gr": "well_stabilized",
        "adaptive": None, "fluid": None, "gyro_pll": None,
    },
    # GR + gentle helix with phase-lock hiding (energy-spike sync only)
    "gr_sync_hiding_plasma": {
        "pulse": None, "plasma": "helical_55_sync_hiding", "gr": "well_stabilized",
        "adaptive": None, "fluid": None, "gyro_pll": None,
    },
    # GR + dual ±55° mirror-balance plasma + frequency-stability feedback
    "gr_mirror_balance_plasma": {
        "pulse": None, "plasma": "helical_55_mirror_balance", "gr": "well_stabilized",
        "adaptive": None, "fluid": None, "gyro_pll": None,
    },
}


def build_experiment_config(
    base: Dict[str, Any],
    *,
    pulse: Optional[str] = None,
    plasma: Optional[str] = None,
    gr_profile: Optional[str] = None,
    adaptive_profile: Optional[str] = None,
    fluid_profile: Optional[str] = None,
    gyro_pll_profile: Optional[str] = None,
    resonance_hz: Optional[float] = None,
    resonance_profile: Optional[str] = None,
    resonance_strength: Optional[float] = None,
    stack: Optional[str] = None,
) -> Dict[str, Any]:
    """Merge base dict with any combination of experiment overlays."""
    layers = EXPERIMENT_STACK_PROFILES.get(stack or "production", {})
    pulse_p = pulse if pulse is not None else layers.get("pulse")
    plasma_p = plasma if plasma is not None else layers.get("plasma")
    gr_p = gr_profile if gr_profile is not None else layers.get("gr")
    adapt_p = adaptive_profile if adaptive_profile is not None else layers.get("adaptive")
    fluid_p = fluid_profile if fluid_profile is not None else layers.get("fluid")
    pll_p = gyro_pll_profile if gyro_pll_profile is not None else layers.get("gyro_pll")

    out = {
        **base,
        **PULSE_DISABLED,
        **PLASMA_DISABLED,
        **GR_DISABLED,
        **ADAPTIVE_DISABLED,
        **FLUID_DISABLED,
        **GYRO_PLL_DISABLED,
        **QSLT_RESONANCE_DISABLED,
        **KNOWN_FREQUENCIES_DISABLED,
    }
    if pulse_p:
        out = apply_pulse_experiment(out, pulse_p)
    if plasma_p:
        out = {**out, **plasma_scenario(plasma_p)}
    if gr_p:
        out = {**out, **gr_experiment(gr_p)}
    if adapt_p:
        out = {**out, **adaptive_experiment(adapt_p)}
    if fluid_p:
        out = {**out, **fluid_experiment(fluid_p)}
    if pll_p:
        out = {**out, **gyro_pll_experiment(pll_p)}
    if resonance_hz is not None or resonance_profile is not None:
        out = apply_qslt_resonance(
            out,
            frequency_hz=resonance_hz,
            profile=resonance_profile,
            strength=resonance_strength,
        )
    return out