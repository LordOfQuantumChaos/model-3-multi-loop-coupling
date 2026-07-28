# What it does

## In one sentence

A **software simulation method** that couples closed driven resonators (“loops”) on a spatial lattice and evaluates their behavior with **named, independent metrics**.

## Capabilities

### 1. Multi-loop lattice topology
- Place loops on a grid (canonical: **3×3 = 9 loops**).
- Nearest-neighbor bonds only (canonical: **12 bonds**).

### 2. Inter-loop coupling forces
- Arc-masked contact regions where neighboring rings face each other.
- Spring and/or velocity coupling.
- Production preference: **velocity-only** coupling at strength **k = 0.006** (3×3 constrained regime).
- Forces are **equal and opposite** (action–reaction).

### 3. Intrinsic unit dynamics
- Each loop has its own driven limit-cycle style dynamics.
- Lattice forces are **added** after per-loop forces — coupling does not replace unit physics.

### 4. Mode-3 stability scoring
- Target pump mode = **3**.
- Stable oscillation + correct dominant mode + pump-amplitude relative variance gate  
  (**ρ = 0.055** production gate).
- Lattice-wide: `all_loops_mode3_stable` when every loop meets the criterion.

### 5. Independent synchronization metrics
| Metric | What it measures |
|--------|------------------|
| Phase / pump sync | Agreement of pump-amplitude time series across loops |
| Energy sync | Agreement of stored-energy time series across loops |
| Energy-balance integrity | Ledger residual (integrator / accounting health) |

These are **not** interchangeable with mode-3 stability.

### 6. Reproducible experiments
- Multi-seed campaigns under a fixed config fingerprint.
- Unit tests for topology and action–reaction.
- Drop-in CLI: `python -m mode3_coupling demo`.

### 7. Enablement package
- Bundled simulation sources under `simulation/driven_loop/`.
- Mathematical force specification.
- Evidence snapshots under `evidence/`.
