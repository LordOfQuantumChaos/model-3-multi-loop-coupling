"""Opt-in experiment configs — not used in production stress or validation paths."""

from driven_loop.experiments.adaptive_memory import (
    ADAPTIVE_EXPERIMENT_PROFILES,
    ADAPTIVE_DISABLED,
    STABILIZED_RADIATION,
    STABILIZED_RADIATION_ADAPTIVE,
    adaptive_experiment,
    apply_adaptive_experiment,
)
from driven_loop.experiments.full_stack import (
    EXPERIMENT_STACK_PROFILES,
    build_experiment_config,
)
from driven_loop.experiments.gravity_well import (
    GR_EXPERIMENT_PROFILES,
    GR_DISABLED,
    GR_WELL_STABILIZED,
    apply_gr_experiment,
    gr_experiment,
)
from driven_loop.experiments.plasma_flow import (
    PLASMA_EXPERIMENT_PROFILES,
    PLASMA_SCENARIO_PROFILES,
    PLASMA_DISABLED,
    apply_plasma_experiment,
    plasma_scenario,
)
from driven_loop.experiments.pulse import (
    PULSE_EXPERIMENT_PROFILES,
    PULSE_DISABLED,
    apply_pulse_experiment,
    lattice_pulse_hopping,
)
from driven_loop.experiments.fluid_physics import (
    FLUID_DISABLED,
    FLUID_PLL_MEMORY_STACK,
    fluid_experiment,
)
from driven_loop.experiments.gyro_pll import (
    GYRO_PLL_DISABLED,
    GYRO_PLL_GENTLE,
    gyro_pll_experiment,
)
from driven_loop.experiments.qslt_resonance import (
    QSLT_RESONANCE_DISABLED,
    QSLT_RESONANCE_PROFILES,
    apply_qslt_resonance,
    qslt_resonance_at_hz,
    qslt_resonance_experiment,
)
from driven_loop.experiments.known_frequencies import (
    KNOWN_FREQUENCIES_DISABLED,
    KNOWN_FREQUENCY_PROFILES,
    apply_known_frequencies,
    known_frequencies_experiment,
)
from driven_loop.experiments.predictive_adaptive import (
    PAC_DISABLED,
    PAC_EXPERIMENT_PROFILES,
    PAC_GENTLE,
    PAC_STRONG,
    apply_pac_experiment,
    pac_experiment,
)

__all__ = [
    "ADAPTIVE_DISABLED",
    "ADAPTIVE_EXPERIMENT_PROFILES",
    "GR_DISABLED",
    "GR_EXPERIMENT_PROFILES",
    "GR_WELL_STABILIZED",
    "PLASMA_DISABLED",
    "PLASMA_EXPERIMENT_PROFILES",
    "PLASMA_SCENARIO_PROFILES",
    "PULSE_DISABLED",
    "PULSE_EXPERIMENT_PROFILES",
    "STABILIZED_RADIATION",
    "STABILIZED_RADIATION_ADAPTIVE",
    "EXPERIMENT_STACK_PROFILES",
    "FLUID_DISABLED",
    "FLUID_PLL_MEMORY_STACK",
    "GYRO_PLL_DISABLED",
    "GYRO_PLL_GENTLE",
    "KNOWN_FREQUENCIES_DISABLED",
    "KNOWN_FREQUENCY_PROFILES",
    "PAC_DISABLED",
    "PAC_EXPERIMENT_PROFILES",
    "PAC_GENTLE",
    "PAC_STRONG",
    "QSLT_RESONANCE_DISABLED",
    "QSLT_RESONANCE_PROFILES",
    "adaptive_experiment",
    "apply_known_frequencies",
    "apply_qslt_resonance",
    "known_frequencies_experiment",
    "apply_adaptive_experiment",
    "apply_gr_experiment",
    "apply_pac_experiment",
    "apply_plasma_experiment",
    "apply_pulse_experiment",
    "build_experiment_config",
    "fluid_experiment",
    "gr_experiment",
    "gyro_pll_experiment",
    "lattice_pulse_hopping",
    "pac_experiment",
    "plasma_scenario",
    "qslt_resonance_at_hz",
    "qslt_resonance_experiment",
]