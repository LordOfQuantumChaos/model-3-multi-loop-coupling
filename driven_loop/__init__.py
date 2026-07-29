"""
Driven elastic loop dynamics — Mode-3 multi-loop coupling (standalone).

Copyright (c) 2026 Joe Louis Vanderpool
Quantum Chaos Technologies L.L.C., Goodman, Missouri, USA
PROPRIETARY — See LICENSE at package root (and in this folder).

This public package exports only the Mode-3 lattice coupling surface.
AetherMind / Helix product modules are intentionally not imported here.
"""

from __future__ import annotations

from driven_loop.core import (
    SimConfig,
    classify_regime,
    is_trivial_collapse,
    ranked_stability_score,
    run_simulation,
    stats_to_row,
)
from driven_loop.sim_config import CONFIG_SECTIONS
from driven_loop.defaults import (
    INTRINSIC_DEFAULT,
    INTRINSIC_LATTICE_3X3_DEFAULT,
    INTRINSIC_LATTICE_DEFAULT,
    INTRINSIC_V5_WINNER,
    INTRINSIC_V6_DEFAULT,
    LATTICE_FRAMES,
    LEGACY_HUNT_FRAMES,
    PRODUCTION_FRAMES,
)
from driven_loop.experiments import (
    ADAPTIVE_DISABLED,
    FLUID_DISABLED,
    FLUID_PLL_MEMORY_STACK,
    GR_DISABLED,
    GYRO_PLL_DISABLED,
    PAC_DISABLED,
    PLASMA_DISABLED,
    PULSE_DISABLED,
    QSLT_RESONANCE_DISABLED,
    KNOWN_FREQUENCIES_DISABLED,
    apply_adaptive_experiment,
    apply_gr_experiment,
    apply_plasma_experiment,
    apply_pulse_experiment,
    build_experiment_config,
    fluid_experiment,
    gyro_pll_experiment,
    lattice_pulse_hopping,
)
from driven_loop.stress import compare_stress, mode3_stable, run_seed
from driven_loop.stability_gates import (
    DEFAULT_PUMP_STABILITY_REL_VAR,
    MODE3_PUMP_STABILITY_REL_VAR,
    STRICT_PUMP_STABILITY_REL_VAR,
    describe_stability_gates,
)
from driven_loop.lattice_topology import (
    loop_lattice_centers,
    loop_lattice_neighbor_pairs,
)
from driven_loop.lattice_coupling import (
    inter_loop_pair_coupling_forces,
    loop_lattice_coupling_forces,
)

__version__ = "1.0.1"

__all__ = [
    "SimConfig",
    "CONFIG_SECTIONS",
    "INTRINSIC_DEFAULT",
    "INTRINSIC_LATTICE_DEFAULT",
    "INTRINSIC_LATTICE_3X3_DEFAULT",
    "INTRINSIC_V5_WINNER",
    "INTRINSIC_V6_DEFAULT",
    "LATTICE_FRAMES",
    "LEGACY_HUNT_FRAMES",
    "PRODUCTION_FRAMES",
    "ADAPTIVE_DISABLED",
    "FLUID_DISABLED",
    "FLUID_PLL_MEMORY_STACK",
    "GR_DISABLED",
    "GYRO_PLL_DISABLED",
    "PAC_DISABLED",
    "PLASMA_DISABLED",
    "PULSE_DISABLED",
    "QSLT_RESONANCE_DISABLED",
    "KNOWN_FREQUENCIES_DISABLED",
    "apply_adaptive_experiment",
    "apply_gr_experiment",
    "apply_plasma_experiment",
    "apply_pulse_experiment",
    "build_experiment_config",
    "fluid_experiment",
    "gyro_pll_experiment",
    "lattice_pulse_hopping",
    "classify_regime",
    "compare_stress",
    "is_trivial_collapse",
    "mode3_stable",
    "ranked_stability_score",
    "run_seed",
    "run_simulation",
    "stats_to_row",
    "MODE3_PUMP_STABILITY_REL_VAR",
    "DEFAULT_PUMP_STABILITY_REL_VAR",
    "STRICT_PUMP_STABILITY_REL_VAR",
    "describe_stability_gates",
    "loop_lattice_centers",
    "loop_lattice_neighbor_pairs",
    "inter_loop_pair_coupling_forces",
    "loop_lattice_coupling_forces",
    "__version__",
]
