"""
Public API for Mode-3 multi-loop coupling.

Simulation lives under ``simulation/driven_loop/``.
``bootstrap.ensure_package_simulation()`` puts that tree first on ``sys.path``.

See docs/ for what this system does, does not do, and how it works.
"""

from __future__ import annotations

from typing import Any, Dict

from mode3_coupling.bootstrap import (
    ensure_package_simulation,
    simulation_available,
    simulation_root,
)

ensure_package_simulation(prefer_package=True)

from driven_loop.lattice_coupling import (  # noqa: E402
    dual_loop_coupling_forces,
    inter_loop_pair_coupling_forces,
    loop_lattice_coupling_forces,
)
from driven_loop.lattice_topology import (  # noqa: E402
    lattice_bond_angle,
    loop_lattice_bond_arc_offset,
    loop_lattice_centers,
    loop_lattice_neighbor_pairs,
    loop_lattice_neighbors_of,
)
from driven_loop.multi_loop import (  # noqa: E402
    is_multi_loop_system,
    loop_state_slice,
    num_sim_loops,
    primary_loop_index,
)
from driven_loop.stress import lattice_overrides, mode3_stable  # noqa: E402
from driven_loop.validation_metrics import (  # noqa: E402
    is_fully_locked,
    is_pump_sync_locked,
    pump_lock_definition,
)
from driven_loop.stability_gates import (  # noqa: E402
    DEFAULT_PUMP_STABILITY_REL_VAR,
    MODE3_PUMP_STABILITY_REL_VAR,
    STRICT_PUMP_STABILITY_REL_VAR,
    describe_stability_gates,
)
from driven_loop.seed53_corner_fix import lattice_bond_coupling_scale  # noqa: E402

try:
    from driven_loop.defaults import (  # noqa: E402
        INTRINSIC_LATTICE_3X3_DEFAULT,
        PRODUCTION_FRAMES,
    )
except ImportError:  # pragma: no cover
    INTRINSIC_LATTICE_3X3_DEFAULT = {}
    PRODUCTION_FRAMES = 6000


def lattice_3x3_default_overrides() -> Dict[str, Any]:
    """
    Config overrides for the constrained 3×3 production lattice.

    Coupling 0.006 is the weaker constrained winner used for multi-seed
    mode-3 stability. ``pump_stability_rel_var`` is pinned to
    ``MODE3_PUMP_STABILITY_REL_VAR`` (0.055).
    """
    base = dict(INTRINSIC_LATTICE_3X3_DEFAULT) if INTRINSIC_LATTICE_3X3_DEFAULT else {}
    base.setdefault("loop_lattice_enabled", True)
    base.setdefault("loop_lattice_rows", 3)
    base.setdefault("loop_lattice_cols", 3)
    base.setdefault("loop_lattice_spacing", 2.4)
    base.setdefault("loop_lattice_coupling", 0.006)
    base.setdefault("loop_lattice_bond_width", 0.4)
    base.setdefault("loop_lattice_velocity_only", True)
    base.setdefault("loop_lattice_phase_jitter", 0.02)
    base.setdefault("pump_mode", 3)
    base.setdefault("frames", PRODUCTION_FRAMES)
    base.setdefault("pump_stability_rel_var", MODE3_PUMP_STABILITY_REL_VAR)
    return base


def describe_mode3_criteria() -> Dict[str, Any]:
    """Human-readable mode-3 / lock criteria (not a performance warranty)."""
    return {
        "mode3_stable": (
            "Loop in stable oscillation, dominant mode matches pump_mode (3), "
            f"and pump amplitude relative variance ≤ {MODE3_PUMP_STABILITY_REL_VAR}."
        ),
        "all_loops_mode3_stable": "Every loop on the lattice meets mode3_stable.",
        "pump_sync_lock": "Separate phase/pump-amplitude correlation metric — not mode-3.",
        "energy_sync": "Separate energy time-series agreement — not phase lock.",
        "energy_balance": "Ledger residual health check — not a sync metric.",
        "gate_rho": MODE3_PUMP_STABILITY_REL_VAR,
        "default_gate_rho": DEFAULT_PUMP_STABILITY_REL_VAR,
        "strict_gate_rho": STRICT_PUMP_STABILITY_REL_VAR,
        "stability_gates": describe_stability_gates(),
        "pump_lock_definition": pump_lock_definition(),
    }


def package_info() -> Dict[str, Any]:
    """Package identity, patent notice, and honest scope boundary."""
    core_path = None
    try:
        import driven_loop.core as core_mod

        core_path = getattr(core_mod, "__file__", None)
    except Exception:
        pass

    return {
        "name": "mode3-multi-loop-coupling",
        "scope": (
            "inter-loop coupling + mode-3 limit-cycle stability metrics "
            "+ bundled simulation"
        ),
        "patent_pending": {
            "application_number": "64/119,833",
            "type": "Utility provisional under 35 U.S.C. 111(b)",
            "status": "patent pending (provisional) — not an issued patent",
        },
        "simulation_bundled": simulation_available(),
        "simulation_root": str(simulation_root()),
        "simulation_core_path": core_path,
        "MODE3_PUMP_STABILITY_REL_VAR": MODE3_PUMP_STABILITY_REL_VAR,
        "runtime_dependency": "numpy (bundled driven_loop simulation)",
        "not_scope": [
            "AetherMind chat/HUD product",
            "Hardware performance warranty",
            "Universal mode-3 guarantee at all couplings/sizes",
            "Equating phase lock with energy lock",
            "Issued patent claims",
            "Wormholes / vacuum energy / AGI product claims",
        ],
        "docs": {
            "start": "docs/00_START_HERE.md",
            "what": "docs/01_WHAT_IT_DOES.md",
            "what_not": "docs/02_WHAT_IT_DOES_NOT.md",
            "how": "docs/03_HOW_IT_WORKS.md",
            "why": "docs/04_WHY_IT_WORKS.md",
            "method": "docs/05_METHOD_AND_HISTORY.md",
            "drop_in": "docs/06_DROP_IN_AND_RUN.md",
        },
    }


__all__ = [
    "ensure_package_simulation",
    "simulation_available",
    "simulation_root",
    "package_info",
    "lattice_3x3_default_overrides",
    "describe_mode3_criteria",
    "dual_loop_coupling_forces",
    "inter_loop_pair_coupling_forces",
    "loop_lattice_coupling_forces",
    "loop_lattice_neighbor_pairs",
    "loop_lattice_centers",
    "loop_lattice_neighbors_of",
    "lattice_bond_angle",
    "loop_lattice_bond_arc_offset",
    "is_multi_loop_system",
    "loop_state_slice",
    "num_sim_loops",
    "primary_loop_index",
    "lattice_overrides",
    "mode3_stable",
    "is_fully_locked",
    "is_pump_sync_locked",
    "pump_lock_definition",
    "DEFAULT_PUMP_STABILITY_REL_VAR",
    "MODE3_PUMP_STABILITY_REL_VAR",
    "STRICT_PUMP_STABILITY_REL_VAR",
    "describe_stability_gates",
    "lattice_bond_coupling_scale",
    "INTRINSIC_LATTICE_3X3_DEFAULT",
    "PRODUCTION_FRAMES",
]
