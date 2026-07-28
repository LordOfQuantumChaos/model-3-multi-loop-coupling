# How it works

## Picture the system

Nine closed rings on a 3×3 grid. Neighbors push gently where they face each other.

```text
   L0 —— L1 —— L2
   |      |      |
   L3 —— L4 —— L5
   |      |      |
   L6 —— L7 —— L8

   12 nearest-neighbor bonds
```

## Method (steps)

1. **Build lattice** — rows, cols, spacing, neighbor list.  
2. **Integrate unit physics** — each loop’s internal forces (stiffness/damping/pump).  
3. **Apply contact coupling** per bond:
   - Direction from center A → B  
   - Soft arc mask on the facing region  
   - Pair facing nodes  
   - Force from relative velocity (and optional position spring)  
   - Equal and opposite on A and B  
4. **Add** coupling forces to totals; step time (many frames).  
5. **Score four independent metrics** (mode-3, phase sync, energy sync, energy ledger).

## Force path (conceptual)

```text
  per-loop internal forces
            │
            ▼
  + lattice coupling forces (arc-masked, action–reaction)
            │
            ▼
       time integrator
            │
            ▼
   metrics on analysis tail
```

## Production knobs (canonical 3×3)

| Knob | Typical value | Role |
|------|---------------|------|
| `loop_lattice_coupling` (k) | **0.006** | Bond strength |
| `loop_lattice_velocity_only` | **True** | Prefer velocity coupling |
| `loop_lattice_bond_width` | **0.4** | Contact mask width |
| `pump_mode` | **3** | Target spatial mode |
| `pump_stability_rel_var` (ρ) | **0.055** | Mode-3 variance gate |
| `frames` | **6000** | Production campaign length |

## Code map

| Concern | Location |
|---------|----------|
| Public API | `mode3_coupling/api.py` |
| Topology | `simulation/driven_loop/lattice_topology.py` |
| Coupling forces | `simulation/driven_loop/lattice_coupling.py` |
| Dynamics engine | `simulation/driven_loop/core.py` |
| Seed runner | `simulation/driven_loop/stress.py` |
| Mode / lock metrics | `simulation/driven_loop/validation_metrics.py`, `stability_gates.py` |
| 3×3 defaults | `simulation/driven_loop/defaults.py` |

Figures: `figures/fig01_topology_3x3.png`, `fig03_force_flow.png`, `fig05_runtime_flow.png`.

Deep math: [`../MATHEMATICAL_FORCE_SPECIFICATION.md`](../MATHEMATICAL_FORCE_SPECIFICATION.md).
