"""Multi-loop indexing: lattice grid, dual loop, state slices."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from driven_loop.core import SimConfig


def num_sim_loops(config: SimConfig) -> int:
    if config.loop_lattice_enabled:
        return max(1, config.loop_lattice_rows * config.loop_lattice_cols)
    if config.dual_loop_enabled:
        return 2
    return 1


def is_multi_loop_system(config: SimConfig) -> bool:
    return num_sim_loops(config) > 1


def loop_state_slice(config: SimConfig, loop_index: int) -> slice:
    n = config.N
    start = loop_index * n
    return slice(start, start + n)


def primary_loop_index(config: SimConfig) -> int:
    if config.loop_lattice_enabled:
        return (config.loop_lattice_rows // 2) * config.loop_lattice_cols + (
            config.loop_lattice_cols // 2
        )
    return 0