# Drop-in and run (standalone)

This repository is fully standalone. No monorepo required.

## Install

```bash
cd model-3-multi-loop-coupling
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m mode3_coupling demo
python -m mode3_coupling test
```

Or double-click `START_HERE.bat`.

## Where the code is

All simulation sources are under `driven_loop/` (open that folder in File Explorer).

Public API: `mode3_coupling/`.

See `README.md` and `STANDALONE_CHANGES.md`.
