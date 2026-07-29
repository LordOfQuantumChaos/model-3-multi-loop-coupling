"""
Pump-variance stability gates — single source of truth.

Two thresholds exist for historical / role reasons. Do **not** mix them
when reporting mode-3 vs fully_locked:

  MODE3_PUMP_STABILITY_REL_VAR (0.055)
      Production mode3_stable gate (INTRINSIC_V6 / lattice 3×3 evidence).
      Used by driven_loop.stress.mode3_stable when the stats row does not
      carry pump_stability_rel_var, and by INTRINSIC_* defaults.

  DEFAULT_PUMP_STABILITY_REL_VAR (0.02)
      SimConfig field default and the stricter fully_locked parameter default
      in validation_metrics.is_fully_locked.

Canonical package evidence (INTRINSIC_LATTICE_3X3_DEFAULT) uses **0.055**.
"""

from __future__ import annotations

# Production mode-3 limit-cycle variance gate (relative pump amplitude variance)
MODE3_PUMP_STABILITY_REL_VAR: float = 0.055

# Stricter / legacy SimConfig + fully_locked default
DEFAULT_PUMP_STABILITY_REL_VAR: float = 0.02

# Alias kept for readable package API
STRICT_PUMP_STABILITY_REL_VAR: float = DEFAULT_PUMP_STABILITY_REL_VAR


def describe_stability_gates() -> dict:
    return {
        "MODE3_PUMP_STABILITY_REL_VAR": MODE3_PUMP_STABILITY_REL_VAR,
        "DEFAULT_PUMP_STABILITY_REL_VAR": DEFAULT_PUMP_STABILITY_REL_VAR,
        "STRICT_PUMP_STABILITY_REL_VAR": STRICT_PUMP_STABILITY_REL_VAR,
        "mode3_stable_uses": "config/stats pump_stability_rel_var, else MODE3_PUMP_STABILITY_REL_VAR",
        "fully_locked_uses": "parameter default DEFAULT_PUMP_STABILITY_REL_VAR unless overridden",
        "production_intrinsic_config": MODE3_PUMP_STABILITY_REL_VAR,
        "note": (
            "mode3_stable and fully_locked are different metrics; "
            "do not report fully_locked rates as mode-3 success."
        ),
    }
