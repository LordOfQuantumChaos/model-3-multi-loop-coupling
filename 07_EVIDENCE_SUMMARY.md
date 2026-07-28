# Evidence summary

**Status:** Configuration-specific **simulation** observations.  
**Not:** hardware warranty or universal mode-3 guarantee.

## Where files live

| File | Role |
|------|------|
| `evidence/LATEST_CANONICAL_3X3_INTRINSIC.md` | Human-readable multi-seed summary |
| `evidence/LATEST_CANONICAL_3X3_INTRINSIC.json` | Machine-readable rates + config |
| `evidence/PHASE_ENERGY_DECOUPLING.md` | Phase vs energy metric separation |
| `PHASE_ENERGY_DECOUPLING.md` (root) | Package narrative |

## How to read results

Always note:

1. **Config** — rows, cols, k, frames, velocity-only, pulse flags, ρ gate  
2. **Seed set** — which seeds, how many  
3. **Metric column** — mode-3 rate ≠ phase-lock rate ≠ energy-lock rate  

## Typical campaign shape (historical package work)

- Lattice: 3×3 intrinsic  
- Frames: 6000 (production-style)  
- Seeds: 10 or 100  
- Coupling: k = 0.006 (constrained winner class)  
- Gate: ρ = 0.055  

Open the LATEST markdown/JSON in `evidence/` for the pinned numbers shipped with this snapshot.

## Reproducing evidence (advanced)

Full regeneration can take a long time (especially 100×6000f).  
This public GitHub package prioritizes:

1. Unit tests (seconds)  
2. Demo / smoke (seconds–minutes)  
3. Published LATEST evidence files (read-only snapshot)

Long campaign scripts may live in the inventor monorepo; not required for drop-in use.

## Scientific reporting template

> Under config C (3×3, k=…, frames=…, ρ=…), for seeds S₁…Sₙ,  
> mode-3 lattice success was **R/N**.  
> Phase and energy classes are reported separately (see table).  
> Results are simulation-only.
