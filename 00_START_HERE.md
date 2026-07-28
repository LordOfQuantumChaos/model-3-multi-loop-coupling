# Start here — Mode-3 Multi-Loop Coupling

**Scientific software package** for multi-loop lattice coupling of closed driven resonators, with **independent** mode-stability and synchronization metrics.

| Field | Value |
|-------|--------|
| **Package** | `mode3-multi-loop-coupling` |
| **Inventor** | Joe Louis Vanderpool |
| **Company** | Quantum Chaos Technologies L.L.C. |
| **Patent** | U.S. Provisional **64/119,833** — **patent pending** (not issued) |
| **Domain** | Simulation method + metrics (not a hardware warranty) |

---

## Read in this order (professional path)

| # | Document | Purpose |
|---|----------|---------|
| 0 | **This file** | Orientation |
| 1 | [`01_WHAT_IT_DOES.md`](01_WHAT_IT_DOES.md) | Capabilities |
| 2 | [`02_WHAT_IT_DOES_NOT.md`](02_WHAT_IT_DOES_NOT.md) | Honest limits |
| 3 | [`03_HOW_IT_WORKS.md`](03_HOW_IT_WORKS.md) | Method / algorithm |
| 4 | [`04_WHY_IT_WORKS.md`](04_WHY_IT_WORKS.md) | Rationale and gates |
| 5 | [`05_METHOD_AND_HISTORY.md`](05_METHOD_AND_HISTORY.md) | What we built and how |
| 6 | [`06_DROP_IN_AND_RUN.md`](06_DROP_IN_AND_RUN.md) | Install and run in minutes |
| 7 | [`07_EVIDENCE_SUMMARY.md`](07_EVIDENCE_SUMMARY.md) | Multi-seed results snapshot |
| 8 | [`08_PATENT_NOTICE.md`](08_PATENT_NOTICE.md) | Filing status language |
| 9 | [`09_API_REFERENCE.md`](09_API_REFERENCE.md) | Public Python API |

**Root README:** [`../README.md`](../README.md)  
**Math force specification:** [`../MATHEMATICAL_FORCE_SPECIFICATION.md`](../MATHEMATICAL_FORCE_SPECIFICATION.md)  
**Claim boundary:** [`../CLAIM_BOUNDARY.md`](../CLAIM_BOUNDARY.md)

---

## Information Center (browser)

Open the repo root file:

**[`../Mode3_Information_Center.html`](../Mode3_Information_Center.html)**

Single-page navigation: run · what / what-not · how · patent · evidence · docs map.

## 60-second run

```bash
cd mode3-multi-loop-coupling
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -e ".[dev]"
python -m mode3_coupling demo
```

---

## Repository map

```text
mode3-multi-loop-coupling/
  README.md                 ← public front door
  docs/                     ← scientific narrative (this folder)
  mode3_coupling/           ← public Python API + CLI
  simulation/driven_loop/   ← bundled dynamics + lattice coupling
  examples/                 ← copy-paste scripts
  tests/                    ← unit tests
  evidence/                 ← pinned multi-seed summaries
  figures/                  ← topology / force-flow diagrams
```

---

## One-sentence summary

**We couple many closed driven rings on a spatial lattice and score mode-3 stability, phase sync, energy sync, and energy balance as separate metrics — never as one vague “it locked” claim.**
