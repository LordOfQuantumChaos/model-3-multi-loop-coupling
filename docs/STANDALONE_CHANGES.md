# Standalone conversion — change log

**Date:** 2026-07-29  
**Repo:** https://github.com/LordOfQuantumChaos/model-3-multi-loop-coupling  

## Goals met

1. Removed need for monorepo / missing packages  
2. Core Mode-3 path works with **numpy only**  
3. Public API via `mode3_coupling`  
4. Scientific method / coupling code **not redesigned** — packaged complete  
5. Everything engine-related lives under **`driven_loop/`** for File Explorer  

## What was broken before

Root-level `core.py`, `defaults.py`, etc. imported:

- `driven_loop.sim_config` (missing)
- `driven_loop.multi_loop`, `gravity_well`, `loop_material`, `intrinsic_profile` (missing)
- `driven_loop.experiments.*` (missing)

So the public flat files could not run without the full monorepo.

## What we did

| Action | Detail |
|--------|--------|
| Added full package | `driven_loop/` with all required modules + `experiments/` OFF flags |
| Public API | `mode3_coupling/` with bootstrap pointing at **repo root** |
| Removed flat duplicates | Root `core.py`, `defaults.py`, `lattice_*.py`, `stress.py`, `stability_gates.py`, `validation_metrics.py` (now only inside `driven_loop/`) |
| Packaging | `pyproject.toml`, `requirements.txt`, `tests/`, `run_demo.py`, `START_HERE.bat` |
| Legal | `LICENSE` + `CLAIM_BOUNDARY.md` at root **and** inside `driven_loop/` |

## Files added (package)

### `driven_loop/` (complete engine)

- `core.py`, `sim_config.py`, `defaults.py`
- `lattice_coupling.py`, `lattice_topology.py`, `multi_loop.py`
- `stress.py`, `validation_metrics.py`, `stability_gates.py`
- `gravity_well.py`, `loop_material.py`, `intrinsic_profile.py`, `seed53_corner_fix.py`
- `experiments/*` (disable flags used by intrinsic defaults)
- `__init__.py`, `README.md`, `LICENSE`, `CLAIM_BOUNDARY.md`, `README_LICENSE.txt`

### `mode3_coupling/`

- `__init__.py`, `__main__.py`, `api.py`, `bootstrap.py` (**fixed** for standalone layout), `cli.py`

### Root tooling

- `pyproject.toml`, `requirements.txt`, `tests/`, `run_demo.py`, `START_HERE.bat`
- `STANDALONE_CHANGES.md` (this file)
- Updated `README.md`

## Files removed from repo root (moved into `driven_loop/`)

- `core.py`
- `defaults.py`
- `lattice_coupling.py`
- `lattice_topology.py`
- `stress.py`
- `stability_gates.py`
- `validation_metrics.py`

## Files modified

| File | Fix |
|------|-----|
| `mode3_coupling/bootstrap.py` | `simulation_root()` = repo root (contains `driven_loop/`), not `simulation/` |
| `README.md` | Standalone layout + install + API |
| `CLAIM_BOUNDARY.md` / `LICENSE` | Kept / refreshed from upload hub |

## Scientific method

**Unchanged.** Coupling forces, topology, mode-3 gate (ρ=0.055), and metric definitions are the same modules used in the enablement package — not a new algorithm.

## Verify

```bash
pip install -e ".[dev]"
python -m mode3_coupling demo   # OK
python -m mode3_coupling test   # 9 passed
```

## 2026-07-29 follow-up (visitor polish)

- README rewritten: what this is + run in 60s at the top
- Removed `README_LICENSE.txt` (redundant with LICENSE + README blurb)
- Slimmed `driven_loop/__init__.py` to Mode-3-only exports (no AetherMind imports)
- Added `index.html` redirect for GitHub Pages root URL
- Added `.github/workflows/pages.yml` for automatic Pages deploy
- Fresh venv: `pip install -e .[dev]` + demo + tests **pass**
