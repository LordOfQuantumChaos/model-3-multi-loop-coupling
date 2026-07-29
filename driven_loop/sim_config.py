"""
SimConfig — single flat configuration for driven-loop simulations.

All experiment layers are **opt-in** (default False / zero strength). Production
profiles live in ``driven_loop.defaults`` and build on these defaults.

Field names and defaults are stable API surface for ``SimConfig(**dict)`` and
``asdict(config)``. Fields are ordered into readable sections only.

Sections
--------
1. Geometry & time
2. Core ring mechanics
3. External forcing
4. Gyroscopic response
5. Internal dynamics & symmetry breaking
6. Dissipation, VdP, thresholds, mode damping
7. Pump limit-cycle
8. Field restoring
9. Bootstrap & gamma ramp
10. Traveling pulse
11. Plasma flow / sync / mirror-balance
12. GR gravity well
13. Adaptive gyro memory
14. Radiation impacts
15. Plasma fluid
16. Time fluid
17. Gyro PLL memory
18. QSLT resonance
19. Known frequencies
20. Corner / seed-53 fixes
21. Loop material properties
22. Compression-twist test
23. Dual-loop & lattice topology
24. Run control & diagnostics
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields, replace
from typing import Any, Dict, List, Mapping, Optional, Tuple

# ---------------------------------------------------------------------------
# Section metadata (for docs / introspection — not required by the solver)
# ---------------------------------------------------------------------------

CONFIG_SECTIONS: Tuple[Tuple[str, str], ...] = (
    ("geometry", "Geometry & time"),
    ("mechanics", "Core ring mechanics"),
    ("forcing", "External forcing"),
    ("gyro", "Gyroscopic response"),
    ("internal", "Internal dynamics & symmetry breaking"),
    ("dissipation", "Dissipation, VdP, thresholds, mode damping"),
    ("pump", "Pump limit-cycle"),
    ("field", "Field restoring"),
    ("bootstrap", "Bootstrap & gamma ramp"),
    ("pulse", "Traveling pulse"),
    ("plasma", "Plasma flow / sync / mirror-balance"),
    ("gr", "GR gravity well"),
    ("adaptive_memory", "Adaptive gyro memory"),
    ("predictive_adaptive", "Predictive adaptive gyro controller"),
    ("radiation", "Radiation impacts"),
    ("plasma_fluid", "Plasma fluid"),
    ("time_fluid", "Time fluid"),
    ("gyro_pll", "Gyro PLL memory"),
    ("qslt", "QSLT resonance"),
    ("known_frequencies", "Known frequencies"),
    ("corner_fix", "Corner / seed-53 fixes"),
    ("material", "Loop material properties"),
    ("compression", "Compression-twist test"),
    ("lattice", "Dual-loop & lattice topology"),
    ("run", "Run control & diagnostics"),
)

# Master enable flags for experiment layers (used by enabled_layers()).
_LAYER_ENABLE_FLAGS: Tuple[Tuple[str, str], ...] = (
    ("forcing", "forcing_enabled"),
    ("gyro", "gyro_enabled"),
    ("internal_dynamics", "internal_dynamics_enabled"),
    ("vdp", "vdp_enabled"),
    ("threshold_excitation", "threshold_excitation_enabled"),
    ("mode_selective_damp", "mode_selective_damp_enabled"),
    ("conservative_coupling", "conservative_coupling_enabled"),
    ("mode_interaction", "mode_interaction_enabled"),
    ("pump_limit_cycle", "pump_limit_cycle_enabled"),
    ("field_restoring", "field_restoring_enabled"),
    ("mode_bootstrap", "mode_bootstrap_enabled"),
    ("gamma_ramp", "gamma_ramp_enabled"),
    ("mode_damp_low", "mode_damp_low_modes_enabled"),
    ("traveling_pulse", "traveling_pulse_enabled"),
    ("plasma", "plasma_enabled"),
    ("plasma_synchronization", "plasma_synchronization_enabled"),
    ("plasma_mirror_balance", "plasma_mirror_balance_enabled"),
    ("plasma_always_on_window", "plasma_always_on_window_enabled"),
    ("gr_well", "gr_well_enabled"),
    ("central_potential", "enable_central_potential"),
    ("adaptive_gyro_memory", "adaptive_gyro_memory_enabled"),
    ("predictive_adaptive_controller", "predictive_adaptive_controller_enabled"),
    ("radiation_impact", "radiation_impact_enabled"),
    ("plasma_fluid", "plasma_fluid_enabled"),
    ("time_fluid", "time_fluid_enabled"),
    ("gyro_pll_memory", "gyro_pll_memory_enabled"),
    ("qslt_resonance", "qslt_resonance_enabled"),
    ("known_frequencies", "known_frequencies_enabled"),
    ("fix_seed_53", "fix_seed_53_enabled"),
    ("generalized_corner_boost", "generalized_corner_boost_enabled"),
    ("material_properties", "material_properties_enabled"),
    ("compression_test", "compression_test_enabled"),
    ("dual_loop", "dual_loop_enabled"),
    ("loop_lattice", "loop_lattice_enabled"),
)


@dataclass
class SimConfig:
    """Flat simulation configuration. Prefer keyword construction: ``SimConfig(**d)``."""

    # ==================================================================
    # 1. Geometry & time
    # ==================================================================
    N: int = 256
    R0: float = 1.0
    dt: float = 0.01

    # ==================================================================
    # 2. Core ring mechanics
    # ==================================================================
    alpha: float = 0.028
    beta: float = 0.10
    radial_stiffness: float = 0.6
    cubic_stiffness: float = 0.6
    tension_stiffness: float = 1.0
    tension_curvature_stiffness: float = 0.0

    # ==================================================================
    # 3. External forcing
    # ==================================================================
    forcing_enabled: bool = False
    gamma: float = 0.20
    k: int = 5

    # ==================================================================
    # 4. Gyroscopic response
    # ==================================================================
    gyro_enabled: bool = False
    gyro_strength: float = 0.15
    gyro_mode: str = "global"  # "global" | "local"
    gyro_speed_scale: float = 0.04
    gyro_amp_scale: float = 0.14
    gyro_curv_scale: float = 80.0
    gyro_onset_deformation: float = 0.05
    gyro_onset_sharpness: float = 0.02

    # ==================================================================
    # 5. Internal dynamics & symmetry breaking
    # ==================================================================
    internal_dynamics_enabled: bool = False
    internal_dynamics_strength: float = 0.0
    internal_dynamics_mode: int = 3
    asymmetry_strength: float = 0.0
    asymmetry_mode: int = 2
    asymmetry_phase: float = 0.0
    instability_gain: float = 0.0
    instability_mode: int = 2
    instability_phase: float = 0.0

    # ==================================================================
    # 6. Dissipation, VdP, thresholds, mode damping
    # ==================================================================
    vdp_enabled: bool = False
    vdp_mu: float = 0.0
    vdp_dev_scale: float = 0.12
    vdp_cap_enabled: bool = True
    vdp_cap_dev_scale: float = 0.18
    threshold_excitation_enabled: bool = False
    threshold_excitation_gain: float = 0.0
    threshold_deformation: float = 0.08
    threshold_sharpness: float = 0.02
    mode_selective_damp_enabled: bool = False
    mode_protect: int = 3
    mode_damp_from: int = 4
    mode_damp_strength: float = 0.35
    mode_damp_non_pump_only: bool = False
    mode_damp_low_modes_enabled: bool = False
    mode_damp_low_strength: float = 0.0
    mode_damp_low_max_mode: int = 2
    mode_damp_low_ramp_only: bool = False
    mode_damp_low_decay_frames: Optional[int] = None
    conservative_coupling_enabled: bool = False
    conservative_coupling_eps: float = 0.0
    conservative_coupling_mode: int = 3
    mode_interaction_enabled: bool = False
    mode_interaction_strength: float = 0.0
    mode_interaction_mode: int = 3
    dissipation_minimal: bool = False
    beta_minimal: float = 0.02

    # ==================================================================
    # 7. Pump limit-cycle
    # ==================================================================
    pump_limit_cycle_enabled: bool = False
    pump_mode: int = 3
    pump_softening: float = 0.0
    pump_hardening: float = 0.0
    pump_vdp_enabled: bool = False
    pump_vdp_mu: float = 0.0
    pump_vdp_dev_scale: float = 0.14
    pump_amplitude_limiter_enabled: bool = False
    pump_amplitude_limiter_strength: float = 0.0
    pump_amplitude_limiter_scale: float = 0.11
    pump_stability_rel_var: float = 0.02
    initial_mode_seed: float = 0.0

    # ==================================================================
    # 8. Field restoring
    # ==================================================================
    field_restoring_enabled: bool = False
    field_dev_strength: float = 0.0
    field_transmit_strength: float = 0.0
    field_stretch_strength: float = 0.0
    field_bend_strength: float = 0.0
    field_kernel_sigma: float = 8.0
    field_curvature_tension: float = 0.0
    track_energy_ledger: bool = True

    # ==================================================================
    # 9. Bootstrap & gamma ramp
    # ==================================================================
    mode_bootstrap_enabled: bool = False
    mode_bootstrap_strength: float = 0.0
    mode_bootstrap_decay_frames: int = 500
    mode_bootstrap_mode: int = 3
    gamma_ramp_enabled: bool = False
    gamma_ramp_initial: float = 0.0
    gamma_ramp_decay_frames: int = 700
    gamma_ramp_k: int = 3

    # ==================================================================
    # 10. Traveling pulse (experiment — production default: off)
    # ==================================================================
    traveling_pulse_enabled: bool = False
    traveling_pulse_strength: float = 0.0
    traveling_pulse_speed: float = 0.08
    traveling_pulse_width: float = 0.55
    traveling_pulse_shape_mode: int = 3
    traveling_pulse_injection: str = "anti_damp"
    traveling_pulse_skip_prob: float = 0.0
    traveling_pulse_skip_jump: float = 1.2
    traveling_pulse_region_transfer: bool = False
    traveling_pulse_initial_phase: float = 0.0
    traveling_pulse_ramp_only: bool = False
    traveling_pulse_inter_loop_transfer: bool = False
    traveling_pulse_active_loop: int = 0
    # Burst + conditional inter-loop hops
    traveling_pulse_burst_mode: bool = False
    traveling_pulse_burst_length: int = 45
    traveling_pulse_burst_period: int = 550
    traveling_pulse_conditional_hop: bool = False
    traveling_pulse_drift_threshold: float = 0.75
    traveling_pulse_hop_prob: float = 0.018
    traveling_pulse_max_hops_per_run: int = 10
    traveling_pulse_hop_cooldown_frames: int = 180

    # ==================================================================
    # 11. Plasma flow / synchronization / mirror-balance (experiment)
    # ==================================================================
    # --- base flow ---
    plasma_enabled: bool = False
    plasma_flow_enabled: bool = False  # back-compat alias of plasma_enabled
    plasma_strength: float = 0.0
    plasma_tangential: float = 0.0
    plasma_omega: float = 0.15
    plasma_helix_angle: float = 55.0
    plasma_geometry: str = "helical"  # radial | tangential | helical
    plasma_k: int = 3
    # --- soft snap / quench ---
    plasma_snap_enabled: bool = False
    plasma_snap_threshold: float = 0.04
    plasma_snap_strength: float = 0.35
    plasma_snap_ramp_frames: int = 0
    plasma_snap_on_pulse_hop: bool = False
    plasma_snap_use_deviation: bool = False
    # --- energy gate ---
    plasma_energy_gate_enabled: bool = False
    plasma_energy_threshold: float = 0.02
    # --- synchronization / "hiding" ---
    plasma_synchronization_enabled: bool = False
    plasma_phase_lock_strength: float = 0.3
    plasma_helical_path_bias: float = 0.4
    plasma_sync_threshold: float = 0.02
    # --- always-on settle window (then energy gate) ---
    plasma_always_on_window_enabled: bool = False
    plasma_always_on_start_frame: int = 0
    plasma_always_on_end_frame: int = 2000
    plasma_always_on_engage: float = 1.0
    # --- mirror-balance (dual 55° helix + frequency feedback) ---
    plasma_mirror_balance_enabled: bool = False
    plasma_helical_mirror_bias: float = 0.45
    balance_feedback_strength: float = 0.2

    # ==================================================================
    # 12. GR gravity well (experiment)
    # ==================================================================
    gr_well_enabled: bool = False
    gr_strength: float = 0.0
    gr_well_center_x: float = 0.0
    gr_well_center_y: float = 0.0
    gr_well_softening: float = 0.15
    gr_well_min_radius: float = 0.25
    gr_force_cap: float = 2.0
    gr_gyro_barrier_enabled: bool = False
    gr_gyro_proximity_scale: float = 1.0
    gr_orbital_steering_enabled: bool = False
    gr_orbital_strength: float = 0.0
    gr_orbital_infall_threshold: float = 0.02

    # ==================================================================
    # 12b. Central attractive potential + linear radial gyro damp (experiment)
    # Weak 1/r² pull + multiplicative linear gyro damping. No torque injection.
    # Default OFF — only keep if sync improves while mode-3 stability holds.
    # ==================================================================
    enable_central_potential: bool = False
    # Force strength (very weak start). Uses gr_strength if this is 0 and flag on.
    central_potential_strength: float = 0.0008
    # Multiplicative velocity damping base (linear in R0/r boost)
    central_gyro_base: float = 0.12
    central_gyro_radial_boost: float = 0.35
    # Soft floor so force does not explode at r→0 (also gr_well_min_radius usable)
    central_potential_min_r: float = 0.15
    # Cap gyro_factor * dt so velocity scale stays in (0, 1]
    central_gyro_dt_cap: float = 0.25

    # ==================================================================
    # 13. Adaptive gyro memory (experiment)
    # ==================================================================
    adaptive_gyro_memory_enabled: bool = False
    adaptive_memory_activity_decay: float = 0.996
    adaptive_memory_impact_decay: float = 0.992
    adaptive_memory_learning_rate: float = 0.03
    adaptive_memory_activity_ref: float = 0.02
    adaptive_memory_gyro_scale: float = 0.5
    adaptive_memory_torque_scale: float = 0.4
    adaptive_memory_gain_min: float = 0.75
    adaptive_memory_gain_max: float = 2.25

    # ==================================================================
    # 13b. Predictive adaptive controller for gyro (experiment)
    # ==================================================================
    predictive_adaptive_controller_enabled: bool = False
    pac_activity_decay: float = 0.97
    pac_trend_decay: float = 0.90
    pac_baseline_decay: float = 0.999
    pac_learning_rate: float = 0.04
    pac_horizon_frames: float = 40.0
    pac_activity_ref: float = 0.02
    pac_envelope_margin: float = 1.15
    pac_boost_scale: float = 0.55
    pac_quiet_reduce: float = 0.06
    pac_gain_min: float = 0.85
    pac_gain_max: float = 2.0
    pac_risk_scale: float = 0.015

    # ==================================================================
    # 14. Radiation-proxy impacts (experiment)
    # ==================================================================
    radiation_impact_enabled: bool = False
    radiation_impact_prob: float = 0.004
    radiation_impact_strength: float = 0.10
    radiation_impact_tangential_fraction: float = 0.65
    radiation_impact_warmup_frames: int = 800

    # ==================================================================
    # 15. Plasma as fluid on the ring (experiment)
    # ==================================================================
    plasma_fluid_enabled: bool = False
    plasma_fluid_density_init: float = 0.01
    plasma_fluid_injection: float = 0.004
    plasma_fluid_tangential_injection: float = 0.0025
    plasma_fluid_viscosity: float = 0.06
    plasma_fluid_pressure_strength: float = 0.05
    plasma_fluid_advection_strength: float = 0.04
    plasma_fluid_gamma: float = 1.35
    plasma_fluid_activity_coupling: float = 0.02
    plasma_fluid_rho_max: float = 0.25

    # ==================================================================
    # 16. Time as fluid on the ring (experiment)
    # ==================================================================
    time_fluid_enabled: bool = False
    time_fluid_density: float = 1.0
    time_fluid_viscosity: float = 0.07
    time_fluid_advection: float = 0.12
    time_fluid_activity_coupling: float = 0.08
    time_fluid_injection: float = 0.002
    time_fluid_omega: float = 0.1
    time_fluid_force_coupling: float = 0.35
    time_fluid_tau_min: float = 0.5
    time_fluid_tau_max: float = 3.0

    # ==================================================================
    # 17. Gyro PLL memory (experiment)
    # ==================================================================
    gyro_pll_memory_enabled: bool = False
    gyro_pll_history_depth: int = 32
    gyro_pll_neighbor_blend: float = 0.88
    gyro_pll_phase_gain: float = 0.10
    gyro_pll_freq_gain: float = 0.006
    gyro_pll_freq_strength: float = 0.05
    gyro_pll_freq_offset_max: float = 0.35
    gyro_pll_gyro_track: float = 0.30

    # ==================================================================
    # 18. QSLT resonance drive (experiment)
    # ==================================================================
    qslt_resonance_enabled: bool = False
    qslt_resonance_frequency_hz: float = 553.0
    qslt_resonance_strength: float = 0.0
    qslt_resonance_mode: int = 3
    qslt_resonance_substeps: int = 32
    qslt_resonance_em_rpm: float = 0.0
    qslt_resonance_em_depth: float = 0.0

    # ==================================================================
    # 19. Known-frequency multi-tone drive (experiment)
    # ==================================================================
    known_frequencies_enabled: bool = False
    known_frequencies: List[float] = field(
        default_factory=lambda: [3.5e-3, 5.0e-3, 7.0e-3]
    )
    known_frequencies_amplitudes: List[float] = field(
        default_factory=lambda: [0.003, 0.002, 0.0015]
    )
    known_frequencies_phases: List[float] = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )
    known_frequencies_mode: int = 3
    known_frequencies_substeps: int = 32
    memory_frequency_switch_enabled: bool = False
    memory_frequency_threshold: float = 0.5
    memory_frequency_scale: float = 1.5

    # ==================================================================
    # 20. Corner / seed-53 fixes (experiment)
    # ==================================================================
    fix_seed_53_enabled: bool = False
    generalized_corner_boost_enabled: bool = False
    target_seed: int = 53
    target_corner_loop: int = 2
    memory_threshold: float = 0.35
    corner_coupling_boost: float = 1.4
    corner_freq_amplitude_boost: float = 1.25
    use_55_degree_helical_offset: bool = True
    helical_angle: float = 55.0
    helical_phase_shift: float = 0.35

    # ==================================================================
    # 21. Loop material properties (experiment)
    # ==================================================================
    material_properties_enabled: bool = False
    youngs_modulus: float = 1.0
    material_density: float = 1.0
    damping_ratio: float = 0.02
    poisson_ratio: float = 0.3
    cross_section_radius: float = 0.01
    cross_section_area: float = 0.0
    second_moment_area: float = 0.0
    material_calib_bending: float = 1.0
    material_calib_tension: float = 1.0
    material_calib_tension_curvature: float = 1.0
    material_calib_radial: float = 1.0
    material_calib_damping: float = 1.0
    material_legacy_blend: float = 0.0
    material_absolute_mode: bool = False
    youngs_modulus_reference: float = 1.0
    material_density_reference: float = 1.0
    material_damping_reference: float = 0.02

    # ==================================================================
    # 22. Compression-twist test (experiment)
    # ==================================================================
    compression_test_enabled: bool = False
    axial_compression_rate: float = 0.001
    max_axial_compression: float = 0.15
    measure_twist: bool = True
    twist_window: int = 1
    twist_measurement_window: int = 100
    compression_layer_thickness: float = 0.1
    dual_region_labeling: bool = False

    # ==================================================================
    # 23. Dual-loop & lattice topology
    # ==================================================================
    dual_loop_enabled: bool = False
    dual_loop_radius_scale: float = 1.05
    dual_loop_phase_offset: float = 0.0
    dual_loop_coupling: float = 0.08
    loop_lattice_enabled: bool = False
    loop_lattice_rows: int = 1
    loop_lattice_cols: int = 1
    loop_lattice_spacing: float = 2.2
    loop_lattice_coupling: float = 0.06
    loop_lattice_radius_jitter: float = 0.0
    loop_lattice_phase_jitter: float = 0.0
    loop_lattice_bond_width: float = 0.45
    loop_lattice_velocity_only: bool = True
    # Velocity-damping fraction of bond k in inter_loop_pair_coupling_forces.
    # Production default 0.15; raise (e.g. 0.22–0.30) to favor pump sync lock.
    loop_lattice_velocity_frac: float = 0.15

    # ==================================================================
    # 24. Run control & diagnostics
    # ==================================================================
    frames: int = 1500
    seed: Optional[int] = None
    initial_noise: float = 0.001
    mode_window: int = 20
    frozen_threshold: float = 0.05
    stability_rel_var_threshold: float = 0.015
    record_stride: int = 8
    reparam_interval: int = 8
    target_segment_length: Optional[float] = None
    integrator: str = "verlet"  # "verlet" | "euler"
    compute_emergent_mode: bool = False
    compute_lyapunov: bool = False
    lyapunov_perturbation: float = 1e-6
    lyapunov_rescale_every: int = 10
    lyapunov_frames: int = 600

    # ------------------------------------------------------------------
    # Lifecycle / helpers
    # ------------------------------------------------------------------
    def __post_init__(self) -> None:
        """Keep plasma enable aliases in sync; light validation."""
        # plasma_enabled <-> plasma_flow_enabled (historical dual name)
        if self.plasma_enabled and not self.plasma_flow_enabled:
            object.__setattr__(self, "plasma_flow_enabled", True)
        elif self.plasma_flow_enabled and not self.plasma_enabled:
            object.__setattr__(self, "plasma_enabled", True)

        if self.N < 4:
            raise ValueError(f"SimConfig.N must be >= 4, got {self.N}")
        if self.dt <= 0:
            raise ValueError(f"SimConfig.dt must be > 0, got {self.dt}")
        if self.frames < 1:
            raise ValueError(f"SimConfig.frames must be >= 1, got {self.frames}")
        if self.integrator not in ("verlet", "euler"):
            raise ValueError(
                f"SimConfig.integrator must be 'verlet' or 'euler', got {self.integrator!r}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all fields (safe for JSON after converting lists)."""
        return asdict(self)

    def updated(self, **overrides: Any) -> "SimConfig":
        """Return a copy with keyword overrides (wraps ``dataclasses.replace``)."""
        return replace(self, **overrides)

    def enabled_layers(self) -> List[str]:
        """Names of experiment / feature layers currently enabled."""
        out: List[str] = []
        for name, attr in _LAYER_ENABLE_FLAGS:
            if bool(getattr(self, attr, False)):
                out.append(name)
        return out

    def layer_summary(self) -> str:
        """Human-readable list of active layers (or 'production core only')."""
        layers = self.enabled_layers()
        if not layers:
            return "production core only (no experiment layers)"
        return "enabled: " + ", ".join(layers)

    @classmethod
    def field_names(cls) -> Tuple[str, ...]:
        return tuple(f.name for f in fields(cls))

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any], **extra: Any) -> "SimConfig":
        """Build from a dict, ignoring unknown keys (for forward-compat loads)."""
        known = {f.name for f in fields(cls)}
        merged = {k: v for k, v in data.items() if k in known}
        merged.update({k: v for k, v in extra.items() if k in known})
        return cls(**merged)

    def diff(self, other: "SimConfig") -> Dict[str, Tuple[Any, Any]]:
        """Fields that differ from ``other`` as {name: (self_val, other_val)}."""
        out: Dict[str, Tuple[Any, Any]] = {}
        for f in fields(self):
            a = getattr(self, f.name)
            b = getattr(other, f.name)
            if a != b:
                out[f.name] = (a, b)
        return out
