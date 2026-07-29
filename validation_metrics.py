"""
Canonical validation metrics and pump-lock definitions.

Single source of truth for sync class thresholds, reproducibility keys,
energy drift analysis, and locked-seed counting used by stress tests
and scripts/run_core_validation.py.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, TypedDict

import numpy as np

from driven_loop.core import classify_pairwise_sync, tail_window_for
from driven_loop.stability_gates import (
    DEFAULT_PUMP_STABILITY_REL_VAR,
    MODE3_PUMP_STABILITY_REL_VAR,
    STRICT_PUMP_STABILITY_REL_VAR,
    describe_stability_gates,
)

# Must stay aligned with classify_pairwise_sync() in core.py
PUMP_SYNC_LOCKED_CORR_MIN = 0.85
PUMP_SYNC_PARTIAL_CORR_MIN = 0.55

# Re-export gates (single source: driven_loop.stability_gates)
# DEFAULT_PUMP_STABILITY_REL_VAR = 0.02  → fully_locked / SimConfig default
# MODE3_PUMP_STABILITY_REL_VAR = 0.055 → production mode3_stable / INTRINSIC_V6
# Hard pass: final ledger residual (limit-cycle steady state)
ENERGY_BALANCE_PASS_MAX = 0.01
FULLY_LOCKED_ENERGY_BALANCE_MAX = ENERGY_BALANCE_PASS_MAX
# Hard pass: tail-local running balance (reference reset at tail start)
TAIL_RUNNING_BALANCE_PASS_MAX = 0.02
FULLY_LOCKED_TAIL_RUNNING_BALANCE_MAX = TAIL_RUNNING_BALANCE_PASS_MAX
# Informational warn only: full-run peak (startup transient / limit-cycle swing)
FULL_RUN_RUNNING_BALANCE_WARN = 0.05
FULLY_LOCKED_STORED_SLOPE_MAX = 1e-5  # per frame, tail window


class ReproScalarKey(TypedDict, total=False):
    success: bool
    equilibrium_type: str
    dominant_mode: int
    pump_mode_rel_var: float
    pump_mode_stable: bool
    avg_activity: float
    avg_deformation: float
    drift_percent: float
    energy_balance: float
    total_injected: float
    total_dissipated: float
    delta_stored: float
    all_loops_mode3_stable: bool
    mean_pairwise_corr: float
    sync_class: str


REPRO_SCALAR_KEYS: tuple[str, ...] = (
    "success",
    "equilibrium_type",
    "dominant_mode",
    "pump_mode_rel_var",
    "pump_mode_stable",
    "avg_activity",
    "avg_deformation",
    "drift_percent",
    "energy_balance",
    "total_injected",
    "total_dissipated",
    "delta_stored",
    "all_loops_mode3_stable",
    "mean_pairwise_corr",
    "sync_class",
)


def pump_lock_definition() -> Dict[str, Any]:
    """
    Documented criteria for pump lock reporting.

    ``pump_locked`` (legacy headline metric):
      Per seed, ``sync_class == "locked"`` on pump-amplitude pairwise correlation
      over the analysis tail window (see tail_window_for).

    ``fully_locked`` (strict metric):
      All of: lattice mode-3 stable, sync locked, pump variance gate, energy gate,
      and no large running-balance drift when ledger histories are available.
    """
    return {
        "pump_locked": {
            "description": "Seed counted when lattice pump sync_class is locked.",
            "sync_class_locked": (
                f"mean_pairwise_corr >= {PUMP_SYNC_LOCKED_CORR_MIN} "
                f"(Pearson corr of per-loop pump amplitude tail series)"
            ),
            "sync_class_partial": (
                f"{PUMP_SYNC_PARTIAL_CORR_MIN} <= mean_pairwise_corr < {PUMP_SYNC_LOCKED_CORR_MIN}"
            ),
            "sync_class_desync": f"mean_pairwise_corr < {PUMP_SYNC_PARTIAL_CORR_MIN}",
            "tail_window": "max(200, min(500, frames // 8)) final frames",
            "signal": "Per-loop pump mode FFT amplitude time series",
            "implementation": "driven_loop.core.classify_pairwise_sync / analyze_lattice_sync",
        },
        "fully_locked": {
            "description": "Stricter seed-level lock: stability + sync + pump variance + energy.",
            "requires": {
                "all_loops_mode3_stable": True,
                "sync_class": "locked",
                "mean_pairwise_corr": f">= {PUMP_SYNC_LOCKED_CORR_MIN}",
                "pump_mode_rel_var": (
                    f"< pump_stability_rel_var "
                    f"(fully_locked default {DEFAULT_PUMP_STABILITY_REL_VAR}; "
                    f"production mode3_stable uses {MODE3_PUMP_STABILITY_REL_VAR})"
                ),
                "energy_balance_abs": f"<= {FULLY_LOCKED_ENERGY_BALANCE_MAX}",
                "max_tail_local_running_balance_abs": (
                    f"<= {FULLY_LOCKED_TAIL_RUNNING_BALANCE_MAX} "
                    "(tail window, reference reset at tail start)"
                ),
                "max_full_run_running_balance_warn": (
                    f">{FULL_RUN_RUNNING_BALANCE_WARN} logged as warn only (startup transient)"
                ),
                "stored_energy_tail_slope_abs": (
                    f"<= {FULLY_LOCKED_STORED_SLOPE_MAX} per frame when histories present"
                ),
            },
        },
        "note": (
            "Headline '19 pump locked' uses pump_locked (sync_class only), not fully_locked. "
            "mode3_stable is reported separately (100/100 on production strength)."
        ),
    }


def is_pump_sync_locked(stats: Dict[str, Any]) -> bool:
    """Legacy pump_locked criterion: sync_class == 'locked'."""
    return stats.get("sync_class") == "locked"


def is_fully_locked(
    stats: Dict[str, Any],
    *,
    pump_stability_rel_var: float = DEFAULT_PUMP_STABILITY_REL_VAR,
    energy_balance_max: float = FULLY_LOCKED_ENERGY_BALANCE_MAX,
) -> bool:
    """Strict fully-locked criterion for a single simulation stats dict."""
    if not stats.get("success"):
        return False
    if not stats.get("all_loops_mode3_stable", True):
        return False
    if stats.get("sync_class") != "locked":
        return False
    corr = stats.get("mean_pairwise_corr")
    if corr is None or float(corr) < PUMP_SYNC_LOCKED_CORR_MIN:
        return False
    if float(stats.get("pump_mode_rel_var", 1.0)) >= pump_stability_rel_var:
        return False
    eb = stats.get("energy_balance")
    if eb is not None and abs(float(eb)) > energy_balance_max:
        return False
    drift = analyze_energy_drift(stats)
    tail_local = drift.get("max_tail_local_running_balance")
    if tail_local is not None and tail_local > FULLY_LOCKED_TAIL_RUNNING_BALANCE_MAX:
        return False
    if drift.get("stored_energy_tail_slope") is not None:
        if abs(drift["stored_energy_tail_slope"]) > FULLY_LOCKED_STORED_SLOPE_MAX:
            return False
    return True


def count_lock_metrics(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count pump_locked (sync) and fully_locked from stress/lattice rows."""
    pump_locked = sum(1 for r in rows if r.get("sync_class") == "locked")
    fully = 0
    for r in rows:
        merged = dict(r)
        if merged.get("mode3_stable") and not merged.get("all_loops_mode3_stable"):
            merged["all_loops_mode3_stable"] = merged.get("mode3_stable")
        if is_fully_locked(merged):
            fully += 1
    return {"pump_locked": pump_locked, "fully_locked": fully, "n_seeds": len(rows)}


def scalar_snapshot(stats: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k in REPRO_SCALAR_KEYS:
        if k in stats:
            v = stats[k]
            if isinstance(v, (bool, int, float, str)) or v is None:
                out[k] = v
    return out


def array_snapshot(stats: Dict[str, Any]) -> Dict[str, Any]:
    """Secondary reproducibility vectors (dominant modes, mode energy shape)."""
    snap: Dict[str, Any] = {}
    per_loop = stats.get("per_loop")
    if isinstance(per_loop, list):
        snap["per_loop_dominant_modes"] = [int(r["dominant_mode"]) for r in per_loop]
        snap["per_loop_pump_stable"] = [bool(r.get("stable", False)) for r in per_loop]

    mode_energies = stats.get("mode_energies")
    frames = int(stats.get("frames", 0) or 0)
    if mode_energies is not None and frames > 0:
        arr = np.asarray(mode_energies, dtype=float)
        if arr.ndim == 2 and arr.shape[0] >= 1:
            tail_n = tail_window_for(frames)
            tail_mean = arr[-tail_n:].mean(axis=0)
            snap["mode_energies_tail_mean"] = [round(float(x), 8) for x in tail_mean]
    return snap


def compare_reproducibility(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    sa, sb = scalar_snapshot(a), scalar_snapshot(b)
    aa, ab = array_snapshot(a), array_snapshot(b)
    scalar_mismatch = {k: {"run_a": sa.get(k), "run_b": sb.get(k)} for k in REPRO_SCALAR_KEYS if sa.get(k) != sb.get(k)}
    array_mismatch: Dict[str, Any] = {}
    for k in set(aa) | set(ab):
        if aa.get(k) != ab.get(k):
            array_mismatch[k] = {"run_a": aa.get(k), "run_b": ab.get(k)}
    return {
        "scalar_mismatches": scalar_mismatch,
        "array_mismatches": array_mismatch,
        "pass": len(scalar_mismatch) == 0 and len(array_mismatch) == 0,
        "scalar_snapshot": sa,
        "array_snapshot": aa,
    }


def _tail_local_running_balance(
    inj_a: np.ndarray,
    diss_a: np.ndarray,
    stored_a: np.ndarray,
    dt: float,
    tail_n: int,
) -> np.ndarray:
    """Running balance within tail only (reference stored at tail start)."""
    inj_tail = inj_a[-tail_n:]
    diss_tail = diss_a[-tail_n:]
    stored_tail = stored_a[-tail_n:]
    cum_in = np.cumsum(inj_tail) * dt
    cum_out = np.cumsum(-diss_tail) * dt
    return cum_in - cum_out - (stored_tail - stored_tail[0])


def analyze_energy_drift(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Final balance (hard pass), tail-local running balance (hard pass),
    full-run peak (warn only), and stored-energy tail slope.

    Requires underscore ledger histories when track_energy_ledger=True.
    """
    dt = float(stats.get("dt", 0.01))
    eb = stats.get("energy_balance")
    out: Dict[str, Any] = {
        "energy_balance": eb,
        "drift_percent": stats.get("drift_percent"),
        "threshold_final_abs": ENERGY_BALANCE_PASS_MAX,
        "threshold_tail_local_abs": TAIL_RUNNING_BALANCE_PASS_MAX,
        "threshold_full_run_warn": FULL_RUN_RUNNING_BALANCE_WARN,
        "threshold_tail_slope_abs": FULLY_LOCKED_STORED_SLOPE_MAX,
    }

    stored = stats.get("_stored_energy_history")
    inj = stats.get("_inject_power_history")
    diss = stats.get("_diss_power_history")
    if stored and inj and diss and len(stored) == len(inj) == len(diss):
        stored_a = np.asarray(stored, dtype=float)
        inj_a = np.asarray(inj, dtype=float)
        diss_a = np.asarray(diss, dtype=float)
        cum_in = np.cumsum(inj_a) * dt
        cum_out = np.cumsum(-diss_a) * dt
        running_balance = cum_in - cum_out - (stored_a - stored_a[0])
        tail_n = tail_window_for(len(stored_a))
        tail_local = _tail_local_running_balance(inj_a, diss_a, stored_a, dt, tail_n)
        tail_stored = stored_a[-tail_n:]
        frames_idx = np.arange(tail_n, dtype=float)
        slope = float(np.polyfit(frames_idx, tail_stored, 1)[0]) if tail_n >= 2 else 0.0
        max_full = float(np.max(np.abs(running_balance)))
        max_tail_local = float(np.max(np.abs(tail_local)))
        out.update({
            "tail_window_frames": tail_n,
            "max_running_balance_full_run": round(max_full, 8),
            "max_tail_local_running_balance": round(max_tail_local, 8),
            "stored_energy_tail_slope": round(slope, 10),
            "full_run_transient_warn": max_full > FULL_RUN_RUNNING_BALANCE_WARN,
        })
    return out


def energy_drift_pass(stats: Dict[str, Any]) -> bool:
    """Hard pass: final balance + tail-local running balance + tail slope."""
    drift = analyze_energy_drift(stats)
    if not stats.get("success"):
        return False
    eb = drift.get("energy_balance")
    if eb is None or not math.isfinite(float(eb)):
        return False
    if abs(float(eb)) > ENERGY_BALANCE_PASS_MAX:
        return False
    tail_local = drift.get("max_tail_local_running_balance")
    if tail_local is not None and tail_local > TAIL_RUNNING_BALANCE_PASS_MAX:
        return False
    slope = drift.get("stored_energy_tail_slope")
    if slope is not None and abs(slope) > FULLY_LOCKED_STORED_SLOPE_MAX:
        return False
    return True