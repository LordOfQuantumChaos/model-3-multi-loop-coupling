"""
Intrinsic-only import / config profile for mode-3 lattice work.

Purpose
-------
The full `driven_loop.core` force stack historically imported optional product
plugins (PAC, plasma, radiation, QSLT, …) at module load time. For outsider
review of **mode-3 multi-loop coupling**, only the intrinsic lattice path is
required.

This module:
  1. Names the **intrinsic** vs **optional plugin** module sets.
  2. Provides lazy loaders so optional plugins are imported on first use only.
  3. Documents config flags that must stay off for an intrinsic-only claim.

Used by `driven_loop.core` (lazy optional symbols) and the mode-3 package docs.
"""

from __future__ import annotations

import importlib
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Module sets (for audit / package manifests)
# ---------------------------------------------------------------------------

# Always needed for 3×3 intrinsic mode-3 dynamics + coupling.
INTRINSIC_CORE_MODULES: Tuple[str, ...] = (
    "driven_loop.sim_config",
    "driven_loop.defaults",
    "driven_loop.lattice_coupling",
    "driven_loop.lattice_topology",
    "driven_loop.multi_loop",
    "driven_loop.loop_material",
    "driven_loop.seed53_corner_fix",  # bond scale used by lattice_coupling
    "driven_loop.validation_metrics",
    "driven_loop.stress",
    # Shared activity / early-out GR helpers (no-op when GR flags off)
    "driven_loop.gravity_well",
)

# Loaded only when a config flag enables the feature (or first force call needs it).
OPTIONAL_PLUGIN_MODULES: Dict[str, str] = {
    "adaptive_memory": "driven_loop.adaptive_memory",
    "predictive_adaptive_controller": "driven_loop.predictive_adaptive_controller",
    "fluid_time": "driven_loop.fluid_time",
    "gyro_pll_memory": "driven_loop.gyro_pll_memory",
    "qslt_resonance": "driven_loop.qslt_resonance",
    "known_frequencies": "driven_loop.known_frequencies",
    "compression_twist": "driven_loop.compression_twist",
    "plasma_fluid": "driven_loop.plasma_fluid",
    "plasma_physics": "driven_loop.plasma_physics",
    "spiral_plasma": "driven_loop.spiral_plasma",
    "radiation_impacts": "driven_loop.radiation_impacts",
    "pulse_transport": "driven_loop.pulse_transport",
}

# Config attribute → expected "off" for intrinsic-only evidence claims.
INTRINSIC_OFF_FLAGS: Tuple[str, ...] = (
    "traveling_pulse_enabled",
    "plasma_enabled",
    "plasma_flow_enabled",
    "plasma_fluid_enabled",
    "gr_well_enabled",
    "gr_gyro_barrier_enabled",
    "gr_orbital_steering_enabled",
    "enable_central_potential",
    "adaptive_gyro_memory_enabled",
    "predictive_adaptive_controller_enabled",
    "time_fluid_enabled",
    "gyro_pll_memory_enabled",
    "qslt_resonance_enabled",
    "known_frequencies_enabled",
    "compression_test_enabled",
    "radiation_impact_enabled",
)

# Attribute name on core → (module_key, symbol_name)
# Used by driven_loop.core module-level __getattr__ for lazy optional symbols.
CORE_OPTIONAL_ATTRS: Dict[str, Tuple[str, str]] = {
    # adaptive_memory
    "AdaptiveGyroMemory": ("adaptive_memory", "AdaptiveGyroMemory"),
    "ImpactRecoveryTracker": ("adaptive_memory", "ImpactRecoveryTracker"),
    "adaptive_memory_active": ("adaptive_memory", "adaptive_memory_active"),
    # PAC
    "PredictiveAdaptiveController": (
        "predictive_adaptive_controller",
        "PredictiveAdaptiveController",
    ),
    "predictive_adaptive_active": (
        "predictive_adaptive_controller",
        "predictive_adaptive_active",
    ),
    # fluid time
    "FluidTimeState": ("fluid_time", "FluidTimeState"),
    "fluid_time_summary": ("fluid_time", "fluid_time_summary"),
    "fluid_time_update": ("fluid_time", "fluid_time_update"),
    "time_fluid_active": ("fluid_time", "time_fluid_active"),
    "time_fluid_scale": ("fluid_time", "time_fluid_scale"),
    # gyro PLL
    "GyroPLLMemory": ("gyro_pll_memory", "GyroPLLMemory"),
    "gyro_pll_active": ("gyro_pll_memory", "gyro_pll_active"),
    "gyro_pll_forces": ("gyro_pll_memory", "gyro_pll_forces"),
    "gyro_pll_gyro_multiplier": ("gyro_pll_memory", "gyro_pll_gyro_multiplier"),
    "gyro_pll_summary": ("gyro_pll_memory", "gyro_pll_summary"),
    # qslt / known freq
    "qslt_resonance_forces": ("qslt_resonance", "qslt_resonance_forces"),
    "qslt_resonance_active": ("qslt_resonance", "qslt_resonance_active"),
    "known_frequencies_forces": ("known_frequencies", "known_frequencies_forces"),
    "known_frequencies_active": ("known_frequencies", "known_frequencies_active"),
    # compression
    "CompressionTwistTracker": ("compression_twist", "CompressionTwistTracker"),
    "compression_radial_forces": ("compression_twist", "compression_radial_forces"),
    "compression_test_active": ("compression_twist", "compression_test_active"),
    "loop_center": ("compression_twist", "loop_center"),
    # plasma fluid
    "PlasmaFluidState": ("plasma_fluid", "PlasmaFluidState"),
    "plasma_fluid_active": ("plasma_fluid", "plasma_fluid_active"),
    "plasma_fluid_forces": ("plasma_fluid", "plasma_fluid_forces"),
    "plasma_fluid_summary": ("plasma_fluid", "plasma_fluid_summary"),
    "plasma_fluid_update": ("plasma_fluid", "plasma_fluid_update"),
    # radiation
    "apply_radiation_impact": ("radiation_impacts", "apply_radiation_impact"),
    "maybe_radiation_impact": ("radiation_impacts", "maybe_radiation_impact"),
    # plasma physics
    "PlasmaPhysicsState": ("plasma_physics", "PlasmaPhysicsState"),
    "energy_containment_score": ("plasma_physics", "energy_containment_score"),
    "plasma_active": ("plasma_physics", "plasma_active"),
    "plasma_needs_state": ("plasma_physics", "plasma_needs_state"),
    "sync_score_from_corr": ("plasma_physics", "sync_score_from_corr"),
    # spiral plasma
    "spiral_plasma_flow_forces": ("spiral_plasma", "spiral_plasma_flow_forces"),
    # pulse transport (hopping / phase advance — not core ring forces)
    "advance_traveling_pulse_phase": ("pulse_transport", "advance_traveling_pulse_phase"),
    "inter_loop_hop_eligible": ("pulse_transport", "inter_loop_hop_eligible"),
    "lattice_neighbor_loops": ("pulse_transport", "lattice_neighbor_loops"),
    "loop_pump_phases_from_deviation": (
        "pulse_transport",
        "loop_pump_phases_from_deviation",
    ),
    "mean_pairwise_phase_drift": ("pulse_transport", "mean_pairwise_phase_drift"),
    "perform_inter_loop_hop": ("pulse_transport", "perform_inter_loop_hop"),
    "traveling_pulse_active": ("pulse_transport", "traveling_pulse_active"),
    "traveling_pulse_burst_active": ("pulse_transport", "traveling_pulse_burst_active"),
}

_plugin_cache: Dict[str, Any] = {}


def load_plugin(key: str) -> Any:
    """Import an optional plugin module by key (cached)."""
    if key not in OPTIONAL_PLUGIN_MODULES:
        raise KeyError(f"Unknown optional plugin key: {key!r}")
    if key not in _plugin_cache:
        _plugin_cache[key] = importlib.import_module(OPTIONAL_PLUGIN_MODULES[key])
    return _plugin_cache[key]


def load_core_optional_attr(name: str) -> Any:
    """Resolve a lazy optional symbol for driven_loop.core."""
    if name not in CORE_OPTIONAL_ATTRS:
        raise AttributeError(name)
    key, attr = CORE_OPTIONAL_ATTRS[name]
    return getattr(load_plugin(key), attr)


def optional_plugins_loaded() -> List[str]:
    """Keys of optional plugins already imported this process."""
    return sorted(_plugin_cache.keys())


def reset_plugin_cache() -> None:
    """Test helper: drop cached plugin modules (does not unload sys.modules)."""
    _plugin_cache.clear()


def _flag_on(config: Any, name: str) -> bool:
    return bool(getattr(config, name, False))


def intrinsic_violations(config: Any) -> List[str]:
    """Return list of flags that are on but should be off for intrinsic-only."""
    bad: List[str] = []
    for name in INTRINSIC_OFF_FLAGS:
        if _flag_on(config, name):
            bad.append(name)
    # Plasma may also be implied by flow flag alone (covered above).
    return bad


def is_intrinsic_only_config(config: Any) -> bool:
    """True when optional product stacks appear disabled on config."""
    return len(intrinsic_violations(config)) == 0


def describe_profile() -> Dict[str, Any]:
    return {
        "name": "intrinsic_only_mode3",
        "intrinsic_core_modules": list(INTRINSIC_CORE_MODULES),
        "optional_plugin_modules": dict(OPTIONAL_PLUGIN_MODULES),
        "intrinsic_off_flags": list(INTRINSIC_OFF_FLAGS),
        "note": (
            "Mode-3 multi-loop coupling demos should use INTRINSIC_LATTICE_3X3_DEFAULT "
            "(or equivalent) so optional plugins stay off and are never imported."
        ),
    }


def assert_intrinsic_claim(
    config: Any,
    *,
    context: str = "intrinsic evidence run",
) -> None:
    """Raise ValueError if config is not intrinsic-only (strict claim path)."""
    bad = intrinsic_violations(config)
    if bad:
        raise ValueError(
            f"{context}: not intrinsic-only; enabled flags: {', '.join(bad)}"
        )


def plugin_import_report(modules_present: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    """
    Summarize which optional plugin modules are currently in sys.modules.

    If modules_present is None, reads importlib sys.modules.
    """
    import sys

    present = set(modules_present if modules_present is not None else sys.modules.keys())
    loaded = {
        key: path
        for key, path in OPTIONAL_PLUGIN_MODULES.items()
        if path in present
    }
    not_loaded = {
        key: path
        for key, path in OPTIONAL_PLUGIN_MODULES.items()
        if path not in present
    }
    return {
        "optional_loaded": loaded,
        "optional_not_loaded": not_loaded,
        "cache_keys": optional_plugins_loaded(),
    }
