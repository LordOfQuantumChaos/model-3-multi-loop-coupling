# Mode-3 Multi-Loop Coupling

**What this is:** A standalone **simulation package** for multi-loop lattice coupling of closed driven resonators, with **independent** metrics for mode-3 stability, phase sync, energy sync, and energy-balance integrity.

**What this is not:** A hardware warranty, an issued patent, or a claim of universal mode-3 at all settings.  
**Status:** **Patent pending** — U.S. Provisional Application **64/119,833** (not issued).  
**Inventor:** Joe Louis Vanderpool · Quantum Chaos Technologies, L.L.C. · Goodman, Missouri, USA

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

**Expected:** topology check (12 bonds on 3x3), action-reaction forces, short lattice integrate, `Demo OK`.

| Command | Result |
|---------|--------|
| `python -m mode3_coupling demo` | Minimal outsider demo |
| `python -m mode3_coupling info` | Package paths + patent notice |
| `python -m mode3_coupling test` | Unit tests |
| `python -m mode3_coupling smoke` | Short 3x3 integrate |
| Double-click `START_HERE.bat` | Windows menu (stays open) |

**Dependency:** `numpy` only (plus `pytest` if you run tests).

---

## License (read this)

> **License:** (c) 2024-2026 Joe Louis Vanderpool / Quantum Chaos Technologies, L.L.C. Proprietary evaluation terms; core may not be modified or redistributed without written permission. See [`LICENSE`](LICENSE).  
> **Patent:** Pending App. **64/119,833** only. **No patent license** is granted by cloning this repo.  
> **Claims:** Allowed vs forbidden technical wording: [`CLAIM_BOUNDARY.md`](CLAIM_BOUNDARY.md). Credit required for any use or reference.

---

## Where everything is

| Piece | Path |
|-------|------|
| Simulation engine (all core files) | [`driven_loop/`](driven_loop/) |
| Public Python API + CLI | [`mode3_coupling/`](mode3_coupling/) |
| Docs (what / how / why / limits) | [`docs/`](docs/) start at [`docs/00_START_HERE.md`](docs/00_START_HERE.md) |
| Browser hub | [`Mode3_Information_Center.html`](Mode3_Information_Center.html) or site root `index.html` |
| Legal | [`LICENSE`](LICENSE) · [`CLAIM_BOUNDARY.md`](CLAIM_BOUNDARY.md) |

Open **`driven_loop/`** in File Explorer for the full core (`core.py`, `lattice_coupling.py`, `lattice_topology.py`, `stress.py`, …).

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

Lower-level runner:

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

Full card: keep confirmation against USPTO Patent Center.

---

## More reading

1. [`docs/00_START_HERE.md`](docs/00_START_HERE.md)  
2. [`docs/01_WHAT_IT_DOES.md`](docs/01_WHAT_IT_DOES.md)  
3. [`docs/03_HOW_IT_WORKS.md`](docs/03_HOW_IT_WORKS.md)  
4. [`docs/06_DROP_IN_AND_RUN.md`](docs/06_DROP_IN_AND_RUN.md)  
5. [`docs/STANDALONE_CHANGES.md`](docs/STANDALONE_CHANGES.md) · [`REPO_MAP.md`](REPO_MAP.md)

---

*Standalone package. No parent monorepo required.*
