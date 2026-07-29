# API reference (public surface)

```python
import mode3_coupling
from mode3_coupling import (
    package_info,
    describe_mode3_criteria,
    lattice_3x3_default_overrides,
    ensure_package_simulation,
    simulation_available,
    loop_lattice_neighbor_pairs,
    inter_loop_pair_coupling_forces,
    MODE3_PUMP_STABILITY_REL_VAR,
)
```

## Identity

| Function | Description |
|----------|-------------|
| `package_info()` | Name, scope, patent notice, not-scope list, paths |
| `describe_mode3_criteria()` | Text definitions of metrics / gates |
| `lattice_3x3_default_overrides()` | Dict of production-style 3×3 config keys |
| `simulation_available()` | True if bundled `core.py` is present |
| `ensure_package_simulation()` | Puts `simulation/` on `sys.path` |

## Topology & coupling

| Symbol | Description |
|--------|-------------|
| `loop_lattice_neighbor_pairs` | Neighbor bond list |
| `loop_lattice_centers` | Loop center coordinates |
| `inter_loop_pair_coupling_forces` | Pair forces (action–reaction) |
| `loop_lattice_coupling_forces` | Full lattice force assembly |
| `MODE3_PUMP_STABILITY_REL_VAR` | Production ρ = 0.055 |

## CLI

```bash
python -m mode3_coupling           # menu
python -m mode3_coupling info
python -m mode3_coupling demo
python -m mode3_coupling smoke
python -m mode3_coupling test
```

## Lower-level simulation

After bootstrap:

```python
from mode3_coupling.bootstrap import ensure_package_simulation
ensure_package_simulation()

from driven_loop.stress import run_seed
stats = run_seed(0, lattice=True, frames=200, rows=3, cols=3, coupling=0.006)
```

See `simulation/driven_loop/` for full dynamics modules.
