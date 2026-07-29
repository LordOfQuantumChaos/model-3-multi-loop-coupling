"""
Mode-3 multi-loop coupling — public package.

Quick start::

    from mode3_coupling import package_info, lattice_3x3_default_overrides
    print(package_info()["name"])

CLI::

    python -m mode3_coupling
    python -m mode3_coupling demo
"""

from mode3_coupling.api import (  # noqa: F401
    MODE3_PUMP_STABILITY_REL_VAR,
    describe_mode3_criteria,
    ensure_package_simulation,
    inter_loop_pair_coupling_forces,
    lattice_3x3_default_overrides,
    loop_lattice_neighbor_pairs,
    package_info,
    simulation_available,
    simulation_root,
)

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "package_info",
    "describe_mode3_criteria",
    "lattice_3x3_default_overrides",
    "ensure_package_simulation",
    "simulation_available",
    "simulation_root",
    "loop_lattice_neighbor_pairs",
    "inter_loop_pair_coupling_forces",
    "MODE3_PUMP_STABILITY_REL_VAR",
]
