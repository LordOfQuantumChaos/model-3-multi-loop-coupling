"""
Seed-53 corner-loop fix experiment overlay (opt-in only).
"""

from __future__ import annotations

from typing import Any, Dict

_CORNER_BOOST_BASE: Dict[str, Any] = dict(
    memory_threshold=0.35,
    corner_coupling_boost=1.4,
    corner_freq_amplitude_boost=1.25,
    use_55_degree_helical_offset=True,
    helical_angle=55.0,
    helical_phase_shift=0.35,
)

SEED53_FIX_DISABLED: Dict[str, Any] = dict(
    fix_seed_53_enabled=False,
    generalized_corner_boost_enabled=False,
    target_seed=53,
    target_corner_loop=2,
    **_CORNER_BOOST_BASE,
)

SEED53_CORNER_FIX: Dict[str, Any] = {
    **SEED53_FIX_DISABLED,
    "fix_seed_53_enabled": True,
}


def seed53_corner_fix_experiment(enabled: bool = True) -> Dict[str, Any]:
    return dict(SEED53_CORNER_FIX if enabled else SEED53_FIX_DISABLED)


GENERALIZED_55_CORNER_BOOST: Dict[str, Any] = {
    **SEED53_FIX_DISABLED,
    "generalized_corner_boost_enabled": True,
}


def generalized_55_corner_boost_experiment(enabled: bool = True) -> Dict[str, Any]:
    return dict(GENERALIZED_55_CORNER_BOOST if enabled else SEED53_FIX_DISABLED)