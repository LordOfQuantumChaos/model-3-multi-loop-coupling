# `mode3_coupling` — public Python package

This is the **import surface** for Mode-3 multi-loop coupling.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports + `__version__` |
| `api.py` | Coupling, topology, metrics, `package_info()` |
| `bootstrap.py` | Load bundled `simulation/` |
| `cli.py` | Interactive + CLI commands |
| `__main__.py` | Enables `python -m mode3_coupling` |

## Quick use

```python
from mode3_coupling import package_info, lattice_3x3_default_overrides
print(package_info()["patent_pending"])
print(lattice_3x3_default_overrides()["loop_lattice_coupling"])
```

```bash
python -m mode3_coupling demo
```

Core dynamics live under `../simulation/driven_loop/` — see [`../CORE_CODE.md`](../CORE_CODE.md).
