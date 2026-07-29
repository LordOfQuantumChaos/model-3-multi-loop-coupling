# Mode-3 Multi-Loop Coupling

**What this is:** A standalone **simulation package** for multi-loop lattice coupling of closed driven resonators, with **independent** metrics for mode-3 stability, phase sync, energy sync, and energy-balance integrity.

**What this is not:** A hardware warranty, an issued patent, or a claim of universal mode-3 at all settings.  
**Status:** **Patent pending** — U.S. Provisional Application **64/119,833** (not issued).  
**Inventor:** Joe Louis Vanderpool · Quantum Chaos Technologies, L.L.C. · Goodman, Missouri, USA

**Publicly viewable for evaluation; this repository is not open-source software.**

---

## Run it (60 seconds)

```bash
git clone https://github.com/LordOfQuantumChaos/model-3-multi-loop-coupling.git
cd model-3-multi-loop-coupling
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate

pip install -e ".[dev]"
python -m mode3_coupling demo
```

**Expected:** 3x3 topology (12 bonds), action-reaction check, short lattice integrate, ends with `=== Demo OK ===`.

| Command | Result |
|---------|--------|
| `python -m mode3_coupling demo` | Minimal outsider demo |
| `python -m mode3_coupling info` | Package paths + patent notice |
| `python -m mode3_coupling test` | Unit tests (9) |
| `python -m mode3_coupling smoke` | Short 3x3 integrate |
| Double-click `START_HERE.bat` | Windows menu (stays open) |

### License near install

> Evaluation and technical review are allowed under [`LICENSE`](LICENSE).  
> **Publicly viewable for evaluation; this repository is not open-source software.**  
> Core modification or redistribution requires written permission.  
> **No patent license** is granted by cloning this repo. See also [`CLAIM_BOUNDARY.md`](CLAIM_BOUNDARY.md).

---

## Reproducibility

| Item | Value |
|------|--------|
| **Python** | 3.10, 3.11, 3.12, 3.13, **3.14** (tested on 3.14) |
| **OS tested** | Windows 10/11 (primary). Linux/macOS expected via pure Python + NumPy. |
| **Dependencies** | `numpy>=1.24,<3` (see [`requirements.txt`](requirements.txt)) |
| **Dev / tests** | `pytest>=7.0` via `pip install -e ".[dev]"` |
| **Demo runtime** | Typically **~1–5 seconds** on a modern laptop (short integrate path) |
| **Unit tests** | **9 passed** (`python -m mode3_coupling test`) |
| **Scientific method** | Unchanged Mode-3 multi-loop coupling + independent metrics |

### Example terminal output (demo)

```text
=== Mode-3 minimal demo ===

1) Package: mode3-multi-loop-coupling
   Simulation bundled: True
   Patent: {'application_number': '64/119,833', ...}

2) Topology: 3x3 bonds = 12 (expect 12)

3) Pair coupling action-reaction residual max ~ 0.000e+00

4) Mode-3 criteria (summary):
   ... Gate rho: 0.055

5) Production 3x3 defaults (subset):
   loop_lattice_coupling: 0.006
   loop_lattice_velocity_only: True
   pump_mode: 3
   frames: 6000
   pump_stability_rel_var: 0.055

6) Short integrate path (optional; a few seconds)...
   Short run completed. Sample keys: ['seed', 'system', 'equilibrium_type', ...]

=== Demo OK ===
```

---

## License (summary)

> **License:** (c) **2026** Joe Louis Vanderpool / Quantum Chaos Technologies, L.L.C. Proprietary evaluation terms; core may not be modified or redistributed without written permission. See [`LICENSE`](LICENSE).  
> **Patent:** Pending App. **64/119,833** only. **No patent license** is granted by this package.  
> **Claims:** Allowed vs forbidden wording: [`CLAIM_BOUNDARY.md`](CLAIM_BOUNDARY.md). Credit required for any use or reference.

---

## Where everything is

| Piece | Path |
|-------|------|
| Simulation engine (all core files) | [`driven_loop/`](driven_loop/) |
| Public Python API + CLI | [`mode3_coupling/`](mode3_coupling/) |
| Docs (what / how / why / limits) | [`docs/`](docs/) — start [`docs/00_START_HERE.md`](docs/00_START_HERE.md) |
| Browser hub / social preview | [`Mode3_Information_Center.html`](Mode3_Information_Center.html) · [`assets/mode3-overview.jpg`](assets/mode3-overview.jpg) |
| Legal | [`LICENSE`](LICENSE) · [`CLAIM_BOUNDARY.md`](CLAIM_BOUNDARY.md) |

---

## Public API (short)

```python
from mode3_coupling import (
    package_info,
    lattice_3x3_default_overrides,
    loop_lattice_neighbor_pairs,
    inter_loop_pair_coupling_forces,
    MODE3_PUMP_STABILITY_REL_VAR,
)

print(package_info()["name"])
print(lattice_3x3_default_overrides()["loop_lattice_coupling"])  # 0.006
```

```python
from driven_loop.stress import run_seed

stats = run_seed(0, lattice=True, frames=200, rows=3, cols=3, coupling=0.006)
print(stats.get("mode3_stable"), stats.get("all_loops_mode3_stable"))
```

---

## Honest limits (one screen)

| You may say | You should not say |
|-------------|-------------------|
| Config-specific multi-seed simulation rates | "Always mode-3" / hardware warranty |
| Coupling method + independent metrics | Phase lock = energy lock |
| "Patent pending" App. 64/119,833 | "Patented" / patent granted |

Details: [`CLAIM_BOUNDARY.md`](CLAIM_BOUNDARY.md) · [`docs/02_WHAT_IT_DOES_NOT.md`](docs/02_WHAT_IT_DOES_NOT.md)

---

## Filing snapshot

| Field | Value |
|-------|--------|
| Application | **64/119,833** |
| Type | U.S. utility provisional (35 U.S.C. 111(b)) |
| Confirmation | 6339 |
| Patent Center | 79378736 |
| Filed | July 27, 2026 |

Confirm numbers against USPTO Patent Center.

---

## More reading

1. [`docs/00_START_HERE.md`](docs/00_START_HERE.md)  
2. [`docs/01_WHAT_IT_DOES.md`](docs/01_WHAT_IT_DOES.md)  
3. [`docs/03_HOW_IT_WORKS.md`](docs/03_HOW_IT_WORKS.md)  
4. [`docs/06_DROP_IN_AND_RUN.md`](docs/06_DROP_IN_AND_RUN.md)  
5. [`docs/STANDALONE_CHANGES.md`](docs/STANDALONE_CHANGES.md) · [`REPO_MAP.md`](REPO_MAP.md)

---

*Standalone package. No parent monorepo required. Not open-source software.*
