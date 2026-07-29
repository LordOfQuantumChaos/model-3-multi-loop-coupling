# driven_loop — standalone Mode-3 core

This folder is the **complete simulation package** for public GitHub.
No parent monorepo is required.

## Core files (patent-pending multi-loop coupling path)

| File | Role |
|------|------|
| core.py | Dynamics engine |
| sim_config.py | SimConfig |
| defaults.py | Intrinsic / 3x3 defaults |
| lattice_coupling.py | Inter-loop forces |
| lattice_topology.py | Bonds / centers |
| multi_loop.py | Multi-loop indexing |
| stress.py | run_seed / mode3_stable |
| validation_metrics.py | Lock metrics |
| stability_gates.py | rho gates (0.055) |
| gravity_well.py | Helpers used by core |
| loop_material.py | Material helpers |
| intrinsic_profile.py | Optional plugin loader |
| experiments/ | OFF flags for intrinsic profile |

## Legal

- LICENSE
- CLAIM_BOUNDARY.md

## Run from package root (parent of this folder)

```text
pip install -e ".[dev]"
python -m mode3_coupling demo
```
