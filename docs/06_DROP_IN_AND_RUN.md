# Drop-in and run (standalone)

This repository is fully standalone. No monorepo required.

**Publicly viewable for evaluation; this repository is not open-source software.**  
See root [`LICENSE`](../LICENSE) and [`CLAIM_BOUNDARY.md`](../CLAIM_BOUNDARY.md).

## Install

```bash
cd model-3-multi-loop-coupling
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate

pip install -e ".[dev]"
python -m mode3_coupling demo
python -m mode3_coupling test
```

Or double-click `START_HERE.bat` on Windows.

## Reproducibility

| Item | Value |
|------|--------|
| Python | 3.10+ (tested on 3.14) |
| OS | Windows 10/11 primary; pure Python + NumPy elsewhere |
| Dependencies | `numpy>=1.24,<3` |
| Demo runtime | ~1–5 seconds |
| Tests | 9 unit tests |

## Where the code is

All simulation sources are under `driven_loop/` (open that folder in File Explorer).

Public API: `mode3_coupling/`.

See root `README.md` and `docs/STANDALONE_CHANGES.md`.
