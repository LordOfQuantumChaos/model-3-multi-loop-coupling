# Method and history — what we built and how

Professional record of the work packaged in this repository.

## Goal

Isolate a **packageable invention surface**:

> Multi-loop lattice coupling of closed driven resonators with **independent** mode-stability and synchronization metrics.

## What we did (ordered)

### Phase A — Dynamics and lattice
1. Built / refined a driven closed-loop simulator (`driven_loop` core).  
2. Added multi-loop indexing and **nearest-neighbor lattice topology**.  
3. Implemented **arc-masked inter-loop coupling** with action–reaction.  
4. Established an **intrinsic** profile (optional modules off) for clean mode-3 study.

### Phase B — Metrics and honesty
5. Defined **mode3_stable** with pump-mode match + variance gate (ρ).  
6. Separated **phase/pump sync**, **energy sync**, and **energy-balance** metrics.  
7. Documented claim boundary language (what may / may not be said).

### Phase C — Evidence campaigns
8. Ran multi-seed campaigns (including **10×** and **100×** seeds at **6000** frames) under pinned 3×3 configs.  
9. Analyzed **phase–energy decoupling** (metrics do not collapse).  
10. Micro-benchmarks and unit tests for coupling / topology.

### Phase D — Packaging and patent enablement
11. Bundled simulation snapshot inside the package for offline enablement.  
12. Wrote mathematical force specification and provisional disclosure set.  
13. Filed U.S. provisional **64/119,833** (patent pending).  
14. Built drop-in API + CLI for outsiders (`mode3_coupling`).

## How we did it (engineering practices)

| Practice | Implementation |
|----------|----------------|
| Config fingerprinting | Fixed rows/cols/k/frames/pulse-off for campaigns |
| Seed aggregation | Report rates R/N, not single-run anecdotes |
| Unit tests | Action–reaction, 12 bonds on 3×3, profile flags |
| Include/exclude profile | Explicit “off” flags for intrinsic claims |
| Reproducible runners | `python -m mode3_coupling demo|smoke|test` |
| Honest docs | What / what-not / how / why / evidence |

## Canonical production-style config (summary)

- Lattice: 3×3, spacing 2.4  
- Coupling: k = 0.006, velocity-only  
- Pump mode: 3  
- Gate: ρ = 0.055  
- Frames (campaign): 6000  
- Profile: intrinsic (optional pulse / PAC / etc. off)

Exact keys: `mode3_coupling.lattice_3x3_default_overrides()` and `simulation/driven_loop/defaults.py`.

## Artifacts in this repo

| Artifact | Path |
|----------|------|
| Simulation code | `simulation/driven_loop/` |
| Public API | `mode3_coupling/` |
| Evidence snapshot | `evidence/` |
| Figures | `figures/` |
| Math spec | `MATHEMATICAL_FORCE_SPECIFICATION.md` |
| Patent filing card | `PATENT_FILING_RECORD.md` |

## What we deliberately left out of this GitHub package

- Full monorepo (AetherMind, radiation packs, other products)  
- Multi-gigabyte campaign dumps (keep LATEST summaries)  
- Personal contact email on public pages  
- Over-claims beyond simulation evidence  
