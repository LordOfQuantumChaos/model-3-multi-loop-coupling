# Mode-3 Multi-Loop Coupling Package

> **License:** © 2024–2026 Joe Louis Vanderpool / Quantum Chaos Technologies, L.L.C. — proprietary evaluation terms; core may not be modified or redistributed without written permission. See [`LICENSE`](LICENSE).  
> **Patent:** Pending — U.S. Provisional Application **64/119,833** (not an issued patent). No patent license is granted by this package.  
> **Claims:** Honest technical limits and allowed wording are in [`CLAIM_BOUNDARY.md`](CLAIM_BOUNDARY.md). Credit required for any use or reference.

**PATENT PENDING** — U.S. Provisional Application **64/119,833**  
Confirmation No. **6339** · Patent Center No. **79378736**

**Inventor:** Joe Louis Vanderpool · **Company:** Quantum Chaos Technologies, L.L.C. · Goodman, Missouri, USA

---

## Standalone package

This repository is **fully standalone**. You do **not** need the larger monorepo.

| Piece | Location |
|-------|----------|
| **Simulation core** | [`driven_loop/`](driven_loop/) (File Explorer: all engine files live here) |
| **Public Python API** | [`mode3_coupling/`](mode3_coupling/) |
| **Legal** | [`LICENSE`](LICENSE) · [`CLAIM_BOUNDARY.md`](CLAIM_BOUNDARY.md) · also inside `driven_loop/` |
| **Docs** | `00_START_HERE.md` … `09_API_REFERENCE.md` |
| **Hub page** | [`Mode3_Information_Center.html`](Mode3_Information_Center.html) |

**Only external dependency:** `numpy` (optional `pytest` for tests).

---

## Quick start

```bash
git clone https://github.com/LordOfQuantumChaos/model-3-multi-loop-coupling.git
cd model-3-multi-loop-coupling
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

pip install -e ".[dev]"
python -m mode3_coupling demo
python -m mode3_coupling test
```

Windows: double-click **`START_HERE.bat`**.

---

## Public API

```python
from mode3_coupling import (
    package_info,
    lattice_3x3_default_overrides,
    loop_lattice_neighbor_pairs,
    inter_loop_pair_coupling_forces,
    MODE3_PUMP_STABILITY_REL_VAR,
)

print(package_info()["patent_pending"])
print(lattice_3x3_default_overrides()["loop_lattice_coupling"])  # 0.006
```

Lower-level:

```python
from driven_loop.stress import run_seed
from driven_loop.stability_gates import MODE3_PUMP_STABILITY_REL_VAR

stats = run_seed(0, lattice=True, frames=200, rows=3, cols=3, coupling=0.006)
```

---

## What this is / is not

**Is:** Multi-loop lattice coupling + independent mode-3 / phase / energy metrics (simulation).  
**Is not:** Hardware warranty · universal mode-3 · issued patent · AetherMind full product.

See [`CLAIM_BOUNDARY.md`](CLAIM_BOUNDARY.md) and [`02_WHAT_IT_DOES_NOT.md`](02_WHAT_IT_DOES_NOT.md).

---

## Folder map

```text
model-3-multi-loop-coupling/
  driven_loop/           ← complete simulation package (open in File Explorer)
    core.py
    lattice_coupling.py
    lattice_topology.py
    defaults.py
    stress.py
    stability_gates.py
    validation_metrics.py
    sim_config.py
    multi_loop.py
    gravity_well.py
    loop_material.py
    intrinsic_profile.py
    experiments/         ← OFF flags for intrinsic profile
    LICENSE
    CLAIM_BOUNDARY.md
  mode3_coupling/        ← clean public API + CLI
  tests/
  LICENSE
  CLAIM_BOUNDARY.md
  README.md
  START_HERE.bat
  run_demo.py
  pyproject.toml
  00_…09_*.md            ← documentation
  Mode3_Information_Center.html
```

---

## License & patent

See [`LICENSE`](LICENSE). Evaluation use allowed; core redistribution/modification requires written permission. **No patent license** is granted by cloning this repo.
