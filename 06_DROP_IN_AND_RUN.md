# Drop-in and run

**Goal:** anyone with Python 3.10+ can clone, install, and run Mode-3 coupling in minutes.

## Requirements

- Python **3.10+** (3.11–3.14 fine)
- `pip`
- ~50 MB disk for the package

## Option A — fastest (recommended)

```bash
git clone https://github.com/<YOUR_ORG>/mode3-multi-loop-coupling.git
cd mode3-multi-loop-coupling

python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate

pip install -U pip
pip install -e ".[dev]"

python -m mode3_coupling info
python -m mode3_coupling demo
python -m mode3_coupling smoke
python -m mode3_coupling test
```

### Interactive menu (Windows-friendly)

```bash
python -m mode3_coupling
```

Then:

| Key | Action |
|-----|--------|
| 1 | Package info |
| 2 | Minimal demo |
| 3 | Short 3×3 smoke integrate |
| 4 | Unit tests |
| Q | Quit |

Windows double-click helper:

```text
RUN.bat
```

## Option B — no install (path only)

```bash
cd mode3-multi-loop-coupling
pip install numpy pytest
set PYTHONPATH=%CD%          # Windows cmd
# export PYTHONPATH=$PWD     # bash
python -m mode3_coupling demo
```

## Option C — use as a library in your project

```python
from mode3_coupling import (
    package_info,
    lattice_3x3_default_overrides,
    loop_lattice_neighbor_pairs,
    inter_loop_pair_coupling_forces,
)

print(package_info()["patent_pending"])
print(lattice_3x3_default_overrides()["loop_lattice_coupling"])
```

Copy the whole repository (or install editable) so `simulation/driven_loop` stays next to `mode3_coupling`.

## Drop-in into another monorepo

1. Copy folder `mode3-multi-loop-coupling/` into your repo (or add as git submodule).  
2. `pip install -e path/to/mode3-multi-loop-coupling`  
3. `import mode3_coupling`  

Do **not** strip `simulation/` — the API loads dynamics from there.

## Expected demo output (shape)

- Package name + patent pending notice  
- 3×3 bonds = 12  
- Action–reaction residual near 0  
- Production defaults (k=0.006, ρ=0.055)  
- Optional short integrate path  

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `No module named mode3_coupling` | `pip install -e .` from repo root |
| `No module named driven_loop` | Ensure `simulation/driven_loop/core.py` exists; re-clone |
| Window closes on Windows | Use `RUN.bat` or `python -m mode3_coupling` (menu pauses) |
| Tests fail on import path | Run from repo root with editable install |
| Slow smoke | Normal — even short lattice integrates take a few seconds |

## What “demo” is not

The minimal demo is **not** the 100×6000-frame campaign.  
For multi-seed rates see `evidence/` and `docs/07_EVIDENCE_SUMMARY.md`.
