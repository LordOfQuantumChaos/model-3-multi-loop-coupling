"""
Driven elastic loop dynamics — simulation, phase diagrams, and discovery tools.

Copyright (c) 2024-2026 Joe Louis Vanderpool
Quantum Chaos Technologies L.L.C., Goodman, Missouri, USA
PROPRIETARY — See LICENSE at package root.
"""

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
    PLASMA_DISABLED,
    PULSE_DISABLED,
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

# AetherMind permanent public surface (v2.1)
from driven_loop.aethermind import (  # noqa: E402
    AETHERMIND_PERMANENT_UPGRADES,
    AETHERMIND_VERSION,
    create_aethermind as create_aethermind_session,
)
from driven_loop.aethermind_complete import (  # noqa: E402
    AETHERMIND_COMPLETE_VERSION,
    AETHERMIND_PERMANENT,
    AETHERMIND_PERMANENT_FEATURES,
    EvidenceSignal,
    build_evidence_from_components,
    create_aethermind,
    create_gyro as create_aether_gyro,
)
from driven_loop.scientific_knowledge import (  # noqa: E402
    get_scientific_fact,
    query_scientific_knowledge,
)
from driven_loop.panel_registry import (  # noqa: E402
    build_panel_registry,
    save_panel_registry,
)
from driven_loop.learning_support import (  # noqa: E402
    LearningSupportModule,
    create_learning_support,
)
from driven_loop.loop_specialists import get_loop7, get_loop9  # noqa: E402
from driven_loop.aether_lattice import create_lattice  # noqa: E402
from driven_loop.reliability_core import (  # noqa: E402
    AetherBrain,
    AetherGyroCoreFacade,
    ReliabilityCore,
    create_aether_brain,
    create_reliability_core,
)

__version__ = "1.8.0"
__all__ = [
    "SimConfig",
    "CONFIG_SECTIONS",
    "INTRINSIC_DEFAULT",
    "INTRINSIC_LATTICE_DEFAULT",
    "INTRINSIC_LATTICE_3X3_DEFAULT",
    "INTRINSIC_V5_WINNER",
    "INTRINSIC_V6_DEFAULT",
    "LATTICE_FRAMES",
    "ADAPTIVE_DISABLED",
    "FLUID_DISABLED",
    "FLUID_PLL_MEMORY_STACK",
    "GR_DISABLED",
    "GYRO_PLL_DISABLED",
    "PLASMA_DISABLED",
    "PULSE_DISABLED",
    "PRODUCTION_FRAMES",
    "apply_adaptive_experiment",
    "apply_gr_experiment",
    "apply_plasma_experiment",
    "apply_pulse_experiment",
    "build_experiment_config",
    "fluid_experiment",
    "gyro_pll_experiment",
    "lattice_pulse_hopping",
    "LEGACY_HUNT_FRAMES",
    "classify_regime",
    "compare_stress",
    "is_trivial_collapse",
    "mode3_stable",
    "ranked_stability_score",
    "run_seed",
    "run_simulation",
    "stats_to_row",
    # AetherMind v2.2 permanent
    "AETHERMIND_VERSION",
    "AETHERMIND_COMPLETE_VERSION",
    "AETHERMIND_PERMANENT",
    "AETHERMIND_PERMANENT_UPGRADES",
    "AETHERMIND_PERMANENT_FEATURES",
    "EvidenceSignal",
    "build_evidence_from_components",
    "create_aethermind",
    "create_aethermind_session",
    "create_aether_gyro",
    "get_scientific_fact",
    "query_scientific_knowledge",
    "build_panel_registry",
    "save_panel_registry",
    "LearningSupportModule",
    "create_learning_support",
    "get_loop7",
    "get_loop9",
    "create_lattice",
    # Drop-in AetherGyro / reliability facade
    "AetherBrain",
    "AetherGyroCoreFacade",
    "ReliabilityCore",
    "create_aether_brain",
    "create_reliability_core",
    "__version__",
]