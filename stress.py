"""Unified stress-test helpers for lattice and single-loop runs."""

from __future__ import annotations

import csv
import json
import os
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .core import SimConfig, run_simulation
from .defaults import INTRINSIC_DEFAULT, INTRINSIC_LATTICE_DEFAULT, LATTICE_FRAMES, PRODUCTION_FRAMES
from .experiments.pulse import PULSE_DISABLED
from .experiments.qslt_resonance import QSLT_RESONANCE_DISABLED
from .experiments.known_frequencies import KNOWN_FREQUENCIES_DISABLED
from .stability_gates import MODE3_PUMP_STABILITY_REL_VAR

FOCUS_SEEDS: Tuple[int, ...] = (53, 90)


def mode3_stable(stats: Dict[str, Any]) -> bool:
    """Stable oscillation + dominant mode 3 + pump variance gate.

    Variance threshold: stats['pump_stability_rel_var'] if present, else
    MODE3_PUMP_STABILITY_REL_VAR (0.055 production / package constant).
    """
    return (
        stats.get("equilibrium_type") == "stable_oscillation"
        and stats.get("dominant_mode") == 3
        and float(stats.get("pump_mode_rel_var", 1.0))
        <= float(stats.get("pump_stability_rel_var", MODE3_PUMP_STABILITY_REL_VAR))
    )


def lattice_overrides(
    rows: int = 2,
    cols: int = 2,
    coupling: float = 0.012,
    spacing: float = 2.4,
) -> Dict[str, Any]:
    return {
        "loop_lattice_enabled": True,
        "loop_lattice_rows": rows,
        "loop_lattice_cols": cols,
        "loop_lattice_spacing": spacing,
        "loop_lattice_coupling": coupling,
    }


def summarize_row(seed: int, stats: Dict[str, Any], system: str) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "seed": seed,
        "system": system,
        "equilibrium_type": stats.get("equilibrium_type"),
        "dominant_mode": stats.get("dominant_mode"),
        "pump_mode_rel_var": stats.get("pump_mode_rel_var"),
        "mode3_stable": mode3_stable(stats),
    }
    if system == "lattice":
        n_loops = stats.get("loop_lattice_rows", 2) * stats.get("loop_lattice_cols", 2)
        row.update(
            {
                "n_loops": n_loops,
                "all_loops_mode3_stable": stats.get("all_loops_mode3_stable"),
                "mean_pairwise_corr": stats.get("mean_pairwise_corr"),
                "sync_class": stats.get("sync_class"),
                "mean_per_loop_stored_energy": stats.get("mean_per_loop_stored_energy"),
                "energy_mean_pairwise_corr": stats.get("energy_mean_pairwise_corr"),
                "energy_sync_class": stats.get("energy_sync_class"),
                "energy_balance": stats.get("energy_balance"),
                "pump_mode_rel_var": stats.get("pump_mode_rel_var"),
            }
        )
        pll = stats.get("gyro_pll_memory")
        if isinstance(pll, dict):
            row["pll_mean_lock_quality"] = pll.get("mean_lock_quality")
            row["pll_mean_phase_error_rad"] = pll.get("mean_phase_error_rad")
            row["pll_mean_freq_offset"] = pll.get("mean_freq_offset")
    return row


def _worker(
    args: Tuple[int, bool, Optional[int], int, int, float, float, Optional[Dict[str, Any]]],
) -> Dict[str, Any]:
    seed, lattice, frames, rows, cols, coupling, spacing, extra = args
    return run_seed(
        seed,
        lattice=lattice,
        frames=frames,
        rows=rows,
        cols=cols,
        coupling=coupling,
        spacing=spacing,
        extra=extra if lattice else None,
    )


def run_seed(
    seed: int,
    *,
    lattice: bool = False,
    frames: Optional[int] = None,
    rows: int = 2,
    cols: int = 2,
    coupling: float = 0.012,
    spacing: float = 2.4,
    base: Optional[Dict[str, Any]] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if lattice:
        merged = {
            **(base or INTRINSIC_LATTICE_DEFAULT),
            **lattice_overrides(rows, cols, coupling, spacing),
            **PULSE_DISABLED,
            **QSLT_RESONANCE_DISABLED,
            **KNOWN_FREQUENCIES_DISABLED,
            **(extra or {}),
        }
        if frames is not None:
            merged["frames"] = frames
        system = "lattice"
    else:
        merged = {
            **(base or INTRINSIC_DEFAULT),
            "loop_lattice_enabled": False,
            **(extra or {}),
        }
        if frames is not None:
            merged["frames"] = frames
        system = "single"

    stats = run_simulation(SimConfig(**merged, seed=seed))
    return summarize_row(seed, stats, system)


def run_batch(
    seeds: Sequence[int],
    *,
    lattice: bool = False,
    frames: Optional[int] = None,
    rows: int = 2,
    cols: int = 2,
    coupling: float = 0.012,
    spacing: float = 2.4,
    parallel: bool = False,
    workers: Optional[int] = None,
    verbose: bool = False,
    focus_seeds: Sequence[int] = FOCUS_SEEDS,
    extra: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    if not parallel:
        rows_out: List[Dict[str, Any]] = []
        for seed in seeds:
            row = run_seed(
                seed,
                lattice=lattice,
                frames=frames,
                rows=rows,
                cols=cols,
                coupling=coupling,
                spacing=spacing,
                extra=extra if lattice else None,
            )
            rows_out.append(row)
            if verbose and (seed in focus_seeds or seed % 20 == 0):
                _print_row(row)
        return rows_out

    n_workers = workers or max(1, (os.cpu_count() or 4) - 1)
    tasks = [
        (seed, lattice, frames, rows, cols, coupling, spacing, extra) for seed in seeds
    ]
    rows_out = []
    with ProcessPoolExecutor(max_workers=n_workers) as pool:
        futures = {pool.submit(_worker, t): t[0] for t in tasks}
        for fut in as_completed(futures):
            seed = futures[fut]
            row = fut.result()
            rows_out.append(row)
            if verbose and (seed in focus_seeds or seed % 20 == 0):
                _print_row(row)
    rows_out.sort(key=lambda r: r["seed"])
    return rows_out


def _print_row(row: Dict[str, Any]) -> None:
    sync = f"  sync {row.get('sync_class', '-')}" if row["system"] == "lattice" else ""
    print(
        f"  seed {row['seed']:3d}  {row.get('equilibrium_type'):18s}  "
        f"mode {row.get('dominant_mode')}  pump_var {row.get('pump_mode_rel_var', 0):.4f}"
        f"{sync}"
    )


def _batch_summary(rows: List[Dict[str, Any]], frames: int) -> Dict[str, Any]:
    stable = sum(r["mode3_stable"] for r in rows)
    n = len(rows)
    summary: Dict[str, Any] = {
        "n_seeds": n,
        "frames": frames,
        "mode3_stable_count": stable,
        "mode3_stable_pct": round(100 * stable / max(1, n), 1),
        "phase_counts": dict(Counter(r["equilibrium_type"] for r in rows)),
    }
    if rows and rows[0]["system"] == "lattice":
        summary["sync_class_counts"] = dict(
            Counter(r.get("sync_class", "n/a") for r in rows)
        )
        summary["energy_sync_class_counts"] = dict(
            Counter(r.get("energy_sync_class", "n/a") for r in rows)
        )
        energies = [
            r["mean_per_loop_stored_energy"]
            for r in rows
            if r.get("mean_per_loop_stored_energy") is not None
        ]
        if energies:
            summary["mean_stored_energy"] = round(float(sum(energies) / len(energies)), 6)
    return summary


def compare_stress(
    seeds: Sequence[int],
    *,
    rows: int = 2,
    cols: int = 2,
    coupling: float = 0.012,
    spacing: float = 2.4,
    lattice_frames: int = LATTICE_FRAMES,
    single_frames: int = PRODUCTION_FRAMES,
    include_single: bool = True,
    parallel: bool = True,
    verbose: bool = True,
    focus_seeds: Sequence[int] = FOCUS_SEEDS,
    lattice_extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    t0 = time.time()
    if verbose:
        label = f"{rows}x{cols} lattice @ {lattice_frames}f"
        print(f"\n=== LATTICE STRESS ({len(seeds)} seeds, {label}) ===")

    lattice_rows = run_batch(
        seeds,
        lattice=True,
        frames=lattice_frames,
        rows=rows,
        cols=cols,
        coupling=coupling,
        spacing=spacing,
        parallel=parallel,
        verbose=verbose,
        focus_seeds=focus_seeds,
        extra=lattice_extra,
    )
    lattice_summary = _batch_summary(lattice_rows, lattice_frames)
    if verbose:
        print(
            f"\n  lattice mode-3 stable: {lattice_summary['mode3_stable_count']}/"
            f"{lattice_summary['n_seeds']} ({lattice_summary['mode3_stable_pct']}%)"
        )
        if "sync_class_counts" in lattice_summary:
            print(f"  sync classes: {lattice_summary['sync_class_counts']}")

    single_rows: List[Dict[str, Any]] = []
    single_summary: Dict[str, Any] = {}
    single_focus: Dict[str, Any] = {}
    if include_single:
        if verbose:
            print(f"\n=== SINGLE-LOOP BASELINE ({len(seeds)} seeds @ {single_frames}f) ===")

        single_rows = run_batch(
            seeds,
            lattice=False,
            frames=single_frames,
            parallel=parallel,
            verbose=verbose,
            focus_seeds=focus_seeds,
        )
        single_summary = _batch_summary(single_rows, single_frames)
        if verbose:
            print(
                f"\n  single mode-3 stable: {single_summary['mode3_stable_count']}/"
                f"{single_summary['n_seeds']} ({single_summary['mode3_stable_pct']}%)"
            )
        single_focus = {
            str(s): next(r for r in single_rows if r["seed"] == s) for s in focus_seeds
        }

    focus = {str(s): next(r for r in lattice_rows if r["seed"] == s) for s in focus_seeds}

    return {
        "elapsed_seconds": round(time.time() - t0, 1),
        "lattice": lattice_summary,
        "single": single_summary,
        "lattice_rows": lattice_rows,
        "single_rows": single_rows,
        "focus_seeds": focus,
        "single_focus": single_focus,
        "grid": {
            "rows": rows,
            "cols": cols,
            "coupling": coupling,
            "spacing": spacing,
            "lattice_frames": lattice_frames,
        },
    }


def write_compare_artifacts(
    out_dir: Path,
    report: Dict[str, Any],
    *,
    prefix: str = "stress",
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    n = report["lattice"]["n_seeds"]

    csv_path = out_dir / f"{prefix}_{n}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(report["lattice_rows"][0].keys()))
        w.writeheader()
        w.writerows(report["lattice_rows"])

    json_report = {
        k: v
        for k, v in report.items()
        if k not in ("lattice_rows", "single_rows")
    }
    json_path = out_dir / f"{prefix}_{n}_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_report, f, indent=2)

    print(f"  wrote {csv_path}")
    print(f"  wrote {json_path}")