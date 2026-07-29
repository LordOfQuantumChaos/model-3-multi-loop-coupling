# Claim Boundary — Mode-3 Multi-Loop Coupling

**Package:** Mode-3 Multi-Loop Coupling (GitHub / upload hub)  
**Updated:** 2026-07-29  
**Owner:** Joe Louis Vanderpool · Quantum Chaos Technologies, L.L.C.

**PATENT PENDING** — U.S. Provisional Application **64/119,833**  
(Utility provisional under 35 U.S.C. § 111(b) · Confirmation **6339** · Patent Center **79378736**)  
See `PATENT_FILING_RECORD.md`.  
**A provisional is patent pending — not an issued patent.**

This file is the **honest technical claim boundary** for GitHub, partners, engineers, and diligence reviews.  
It is **not** a legal opinion and **not** a patent claim chart.

---

## 1. What this package **is**

A **software simulation method and metric set** for:

1. **Inter-loop coupling** of closed driven resonators on a spatial lattice (canonical demo: **3×3**).  
2. **Arc-masked / contact-region coupling forces** between neighboring loops (action–reaction).  
3. **Independent evaluation metrics**, including:
   - **mode-3 stability** (limit-cycle-like / dominant mode + variance gate),
   - **phase / pump synchronization**,
   - **energy synchronization**,
   - **energy-balance integrity** (ledger health check).

It is suitable for evaluation, research, technical review, and reproducible simulation under **documented configs**.

---

## 2. What this package **is not**

| Not this | Why it matters |
|----------|----------------|
| A hardware product warranty | Results are from **simulation** |
| Guaranteed mode-3 at all couplings, sizes, seeds, or times | Evidence is **config- and seed-set specific** |
| Proof that “locked” means one single thing | Metrics are **independent** |
| Proof that phase lock = energy lock | Campaigns show they often **decouple** |
| An issued patent | Status is **patent pending** (provisional) |
| A patent license | See `LICENSE` §5 — no patent rights granted by download |
| Full AetherMind product / Helix product catalog | Out of this package’s scope |
| Wormholes, vacuum energy, AGI, or exotic product claims | Out of scope |

---

## 3. What you **may** say (if you cite config + evidence)

| Allowed | Example wording |
|---------|-----------------|
| Describe the method | “Neighbor loops couple via arc-aligned contact forces on a lattice.” |
| Report observed rates | “Under intrinsic 3×3, k=0.006, 6000 frames, seeds 0–99, mode3_stable was 100/100.” |
| Define metrics | “mode3_stable uses stable oscillation, dominant mode = 3, and relative variance gate ρ = 0.055.” |
| Note independence | “Phase pump-lock and energy-lock are scored separately.” |
| Point to code | “Implemented in `simulation/driven_loop/` and exposed via `mode3_coupling`.” |
| Patent status | “U.S. provisional patent pending, App. 64/119,833.” |

---

## 4. What you must **not** claim from this package alone

| Forbidden / overclaim | Prefer instead |
|-----------------------|----------------|
| “Always mode-3” / “works at any rate” | “Observed rate R/N under config C.” |
| “Fully synced” without naming the metric | Name mode-3, phase lock, and/or energy lock |
| “Phase lock therefore energy lock” | Report both columns |
| “Hardware-validated” / “flight-proven” | “Simulation evidence only” |
| “Patented” / “patent granted” | “Patent pending (provisional)” |
| “Open source / free to relicense core” | See `LICENSE` — proprietary evaluation terms |
| Presenting a modified core as the original | Keep extensions separate; credit original |

---

## 5. Metric definitions (short)

| Metric | Meaning (package language) |
|--------|----------------------------|
| **mode3_stable** | Stable oscillation-like behavior, dominant spatial mode matches pump mode **3**, and pump-amplitude relative variance ≤ production gate **ρ = 0.055** (unless a different gate is stated). |
| **all_loops_mode3** | Every loop on the lattice meets mode3_stable (when reported). |
| **pump_locked / phase sync** | Agreement of pump-amplitude time series across loops — **not** the same as mode-3. |
| **energy sync** | Agreement of stored-energy time series — **not** the same as phase lock. |
| **energy balance** | Ledger residual near zero on the analysis window — integrator/accounting health, **not** a sync score. |

Full math/force detail: `MATHEMATICAL_FORCE_SPECIFICATION.md`.

---

## 6. Canonical evidence snapshot (when present)

See `evidence/LATEST_CANONICAL_3X3_INTRINSIC.md`.

Example published campaign shape (do not treat as universal):

- Lattice: intrinsic **3×3**
- Coupling **k = 0.006**, pulse **off**
- Frames **6000**, seeds **0…99**
- Gate **ρ = 0.055**

Illustrative rates under that config (confirm against LATEST file):

| Metric | Example rate |
|--------|----------------|
| mode3_stable | 100 / 100 |
| all_loops_mode3 | 95 / 100 |
| pump_locked (phase) | 19 / 100 |
| phase-locked AND energy-locked | 2 / 19 of phase-locked |

**Scope sentence (use this wording):**

> These results apply to the specific intrinsic 3×3 simulation configuration described above and should not be interpreted as universal behavior across all parameter choices.

Phase–energy decoupling write-up: `PHASE_ENERGY_DECOUPLING.md`.

---

## 7. Config fingerprint (always publish with rates)

When quoting results, include at least:

```text
rows, cols
loop_lattice_coupling (k)
loop_lattice_velocity_only (true/false)
frames
seed list or seed count
pump_mode
pump_stability_rel_var (ρ)
pulse / PAC / other modules ON or OFF
```

Production-style defaults are summarized by:

```python
from mode3_coupling import lattice_3x3_default_overrides
print(lattice_3x3_default_overrides())
```

---

## 8. IP / license boundary (one glance)

| Topic | Status in this package |
|-------|------------------------|
| Copyright | Joe Louis Vanderpool / Quantum Chaos Technologies, L.L.C. |
| Evaluation use | Allowed under `LICENSE` |
| Core modification / redistribution | Restricted — written permission required |
| Separate wrappers / extensions | Allowed if clearly separate + credit given |
| Patent license | **Not** granted by this package alone |
| Public patent language | “Patent pending” only — not “patented” |

Full legal text: **`LICENSE`**.

---

## 9. Contact

**Joe Vanderpool** — Owner / Founder  
Quantum Chaos Technologies, L.L.C.  
Email: [Vanderpool_Joe@hotmail.com](mailto:Vanderpool_Joe@hotmail.com)

For commercial licensing or written permission beyond evaluation use.

---

## 10. Related files

| File | Role |
|------|------|
| `LICENSE` | Evaluation / credit / no patent license |
| `PATENT_FILING_RECORD.md` | Application numbers |
| `docs/02_WHAT_IT_DOES_NOT.md` | Plain-language limits |
| `docs/08_PATENT_NOTICE.md` | Patent wording |
| `evidence/LATEST_CANONICAL_3X3_INTRINSIC.md` | Multi-seed rates |
| `CORE_CODE.md` | Source file map |
| `Mode3_Hub.html` | Browser information hub |

---

*End of claim boundary. Prefer under-claiming over over-claiming.*
