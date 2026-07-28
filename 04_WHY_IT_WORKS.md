# Why it works

This section explains the **design rationale**, not a universal physics proof.

## 1. Separate the unit oscillator from the lattice

Each loop can form a **limit-cycle-like** driven pattern on its own.  
Coupling is a **weak, local, reciprocal** perturbation — strong enough to coordinate modes, weak enough not to destroy the unit cycle (in the production k regime).

## 2. Contact masking (where rings face)

Forces act primarily on the facing arc, not the entire ring equally.  
That matches the geometric idea of **local contact** between closed loops and avoids over-coupling distant material on the same ring.

## 3. Velocity-only production coupling

Preferring velocity coupling (with k ≈ 0.006 on 3×3) was selected from constrained search / campaign work as a **stable coordination** setting for mode-3 under the intrinsic profile — not as the only possible k in nature.

## 4. Independent metrics prevent false “success”

If a system only reports “locked,” reviewers cannot tell whether:

- the **spatial mode** is correct (mode-3),  
- **phases** agree,  
- **energies** agree, or  
- the **integrator ledger** is healthy.

Decoupling these metrics is intentional. Campaigns show mode-3 rates and phase/energy classes can differ — that is a feature of honest evaluation.

## 5. Fixed gates enable comparison

The production relative-variance gate **ρ = 0.055** is a documented threshold for `mode3_stable`.  
Changing ρ changes rates; always publish **ρ with results**.

## 6. Why multi-seed evidence matters

A single lucky seed is anecdote.  
Multi-seed campaigns under a **config fingerprint** (frames, k, pulse off, seed list) support scientific reporting: rate R/N with stated conditions.

## What “works” means here

**Works** = under documented simulation configs, the coupling method produces measurable, reproducible multi-loop behavior that can be scored with the stated metrics.

**Does not mean** = hardware warranty, all-parameter universality, or issued patent rights.
