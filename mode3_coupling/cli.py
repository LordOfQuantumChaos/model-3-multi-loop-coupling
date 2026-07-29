"""
Command-line interface for Mode-3 multi-loop coupling.

Extremely simple entry points for drop-in use:

  python -m mode3_coupling           # interactive menu
  python -m mode3_coupling info
  python -m mode3_coupling demo
  python -m mode3_coupling smoke
  python -m mode3_coupling test
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import traceback
from pathlib import Path

from mode3_coupling.bootstrap import package_root


def _pause(msg: str = "Press Enter to continue...") -> None:
    try:
        input(msg)
    except (EOFError, KeyboardInterrupt):
        print()


def cmd_info() -> int:
    from mode3_coupling.api import package_info
    from mode3_coupling.bootstrap import simulation_available, simulation_root

    info = package_info()
    print("=" * 60)
    print("MODE-3 MULTI-LOOP COUPLING")
    print("=" * 60)
    print("Name:     ", info.get("name"))
    print("Version:  ", __import__("mode3_coupling").__version__)
    print("Scope:    ", info.get("scope"))
    print("Patent:   ", info.get("patent_pending"))
    print("Sim code: ", info.get("simulation_bundled"), simulation_available())
    print("Sim root: ", simulation_root())
    print("Core:     ", info.get("simulation_core_path"))
    print("Gate rho: ", info.get("MODE3_PUMP_STABILITY_REL_VAR"))
    print("Repo:     ", package_root())
    print("=" * 60)
    print("Docs: docs/00_START_HERE.md")
    print("Next: python -m mode3_coupling demo")
    print("=" * 60)
    return 0


def cmd_demo() -> int:
    """Topology + action-reaction + optional short integrate path."""
    print("=== Mode-3 minimal demo ===\n")
    from mode3_coupling.api import (
        describe_mode3_criteria,
        inter_loop_pair_coupling_forces,
        lattice_3x3_default_overrides,
        loop_lattice_neighbor_pairs,
        package_info,
        simulation_available,
    )
    import numpy as np

    info = package_info()
    print("1) Package:", info["name"])
    print("   Simulation bundled:", simulation_available())
    print("   Patent:", info["patent_pending"])
    print("   Not scope:", "; ".join(info["not_scope"][:3]), "...")

    class _Cfg:
        loop_lattice_rows = 3
        loop_lattice_cols = 3

    pairs = loop_lattice_neighbor_pairs(_Cfg())  # type: ignore[arg-type]
    print(f"\n2) Topology: 3×3 bonds = {len(pairs)} (expect 12)")
    assert len(pairs) == 12, f"expected 12 bonds, got {len(pairs)}"

    n = 8
    rng = np.random.default_rng(0)
    xa, ya = rng.normal(size=n), rng.normal(size=n)
    xb, yb = xa + 0.2, ya - 0.1
    vxa, vya = rng.normal(size=n) * 0.01, rng.normal(size=n) * 0.01
    vxb, vyb = vxa + 0.05, vya - 0.03
    fa_x, fa_y, fb_x, fb_y = inter_loop_pair_coupling_forces(
        xa, ya, vxa, vya, xb, yb, vxb, vyb, coupling=0.05, position_coupling=True
    )
    max_sum = float(np.max(np.abs(fa_x + fb_x)) + np.max(np.abs(fa_y + fb_y)))
    print(f"\n3) Pair coupling action–reaction residual max ≈ {max_sum:.3e}")
    assert max_sum < 1e-9, "forces not equal-and-opposite"

    crit = describe_mode3_criteria()
    print("\n4) Mode-3 criteria (summary):")
    print("  ", crit["mode3_stable"][:90], "...")
    print("   Gate rho:", crit["gate_rho"])

    ov = lattice_3x3_default_overrides()
    print("\n5) Production 3×3 defaults (subset):")
    for k in (
        "loop_lattice_coupling",
        "loop_lattice_velocity_only",
        "pump_mode",
        "frames",
        "pump_stability_rel_var",
    ):
        print(f"   {k}: {ov.get(k)}")

    # Optional short multi-loop integrate
    if simulation_available():
        print("\n6) Short integrate path (optional; a few seconds)...")
        try:
            from driven_loop.stress import run_seed

            stats = run_seed(
                0,
                lattice=True,
                frames=60,
                rows=3,
                cols=3,
                coupling=float(ov.get("loop_lattice_coupling", 0.006)),
                spacing=float(ov.get("loop_lattice_spacing", 2.4)),
                extra={
                    "loop_lattice_velocity_only": ov.get(
                        "loop_lattice_velocity_only", True
                    ),
                    "pump_mode": 3,
                    "pump_stability_rel_var": 0.055,
                },
            )
            if isinstance(stats, dict):
                print("   Short run completed. Sample keys:", list(stats.keys())[:8])
            else:
                print("   Short run completed:", type(stats))
        except Exception as e:
            print("   (Short integrate skipped — coupling demo still OK)")
            print("   reason:", type(e).__name__, str(e)[:120])
    else:
        print("\n6) Simulation core missing — topology/coupling demo only.")

    print("\n=== Demo OK ===")
    print("This does NOT claim 100-seed production rates.")
    print("See evidence/ and docs/07_EVIDENCE_SUMMARY.md for multi-seed results.")
    return 0


def cmd_smoke() -> int:
    print("=== Mode-3 smoke (short 3×3) ===\n")
    try:
        from driven_loop.stress import run_seed
        from mode3_coupling.api import lattice_3x3_default_overrides

        ov = lattice_3x3_default_overrides()
        stats = run_seed(
            1,
            lattice=True,
            frames=200,
            rows=int(ov.get("loop_lattice_rows", 3)),
            cols=int(ov.get("loop_lattice_cols", 3)),
            coupling=float(ov.get("loop_lattice_coupling", 0.006)),
            spacing=float(ov.get("loop_lattice_spacing", 2.4)),
            extra={
                "loop_lattice_velocity_only": ov.get("loop_lattice_velocity_only", True),
                "loop_lattice_bond_width": ov.get("loop_lattice_bond_width", 0.4),
                "pump_mode": ov.get("pump_mode", 3),
                "pump_stability_rel_var": ov.get("pump_stability_rel_var", 0.055),
            },
        )
        print("Smoke run_seed completed.")
        if isinstance(stats, dict):
            for k in (
                "mode3_stable",
                "all_loops_mode3_stable",
                "dominant_mode",
                "equilibrium_type",
            ):
                if k in stats:
                    print(f"  {k}: {stats[k]}")
        return 0
    except Exception:
        traceback.print_exc()
        print("\nSmoke failed. Try: python -m mode3_coupling demo")
        return 1


def cmd_test() -> int:
    root = package_root()
    tests = root / "tests"
    print("Running tests in", tests)
    return subprocess.call(
        [sys.executable, "-m", "pytest", str(tests), "-q", "--tb=line"],
        cwd=str(root),
    )


def interactive() -> int:
    last = 0
    while True:
        print()
        print("=" * 60)
        print("  MODE-3 MULTI-LOOP COUPLING")
        print("  PATENT PENDING  App. 64/119,833")
        print("=" * 60)
        print("  [1] Package info")
        print("  [2] Minimal demo (topology + coupling + short path)")
        print("  [3] Smoke 3×3 (short integrate)")
        print("  [4] Unit tests")
        print("  [D] Open docs folder")
        print("  [Q] Quit")
        print("=" * 60)
        try:
            choice = input("Select: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return last

        if choice in ("q", "quit"):
            print("Goodbye.")
            return last
        if choice == "1":
            last = cmd_info()
            _pause()
        elif choice == "2":
            try:
                last = cmd_demo()
            except Exception:
                traceback.print_exc()
                last = 1
            _pause()
        elif choice == "3":
            last = cmd_smoke()
            _pause()
        elif choice == "4":
            last = cmd_test()
            _pause()
        elif choice == "d":
            import os

            docs = package_root() / "docs"
            try:
                os.startfile(str(docs))  # type: ignore[attr-defined]
            except Exception:
                print("Docs path:", docs)
            _pause()
        else:
            print("Unknown choice. Use 1-4, D, or Q.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="mode3_coupling",
        description="Mode-3 multi-loop coupling — drop-in runner",
    )
    ap.add_argument(
        "command",
        nargs="?",
        default="",
        choices=["", "info", "demo", "smoke", "test"],
        help="Command (default: interactive menu)",
    )
    args = ap.parse_args(argv)
    try:
        if not args.command:
            return interactive()
        return {
            "info": cmd_info,
            "demo": cmd_demo,
            "smoke": cmd_smoke,
            "test": cmd_test,
        }[args.command]()
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
