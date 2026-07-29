"""
PLL gyro memory experiment overlays (opt-in only).
"""

from __future__ import annotations

from typing import Any, Dict

GYRO_PLL_DISABLED: Dict[str, Any] = dict(
    gyro_pll_memory_enabled=False,
)

# Phase-locked gyro: neighbor phase history + frequency pull toward collective rhythm
GYRO_PLL_GENTLE: Dict[str, Any] = {
    "gyro_pll_memory_enabled": True,
    "gyro_pll_history_depth": 32,
    "gyro_pll_neighbor_blend": 0.88,
    "gyro_pll_phase_gain": 0.08,
    "gyro_pll_freq_gain": 0.005,
    "gyro_pll_freq_strength": 0.04,
    "gyro_pll_freq_offset_max": 0.30,
    "gyro_pll_gyro_track": 0.28,
}

# Stronger neighbor interlock pull (interlock strength tests)
GYRO_PLL_MEDIUM: Dict[str, Any] = {
    **GYRO_PLL_GENTLE,
    "gyro_pll_phase_gain": 0.12,
    "gyro_pll_freq_gain": 0.008,
    "gyro_pll_freq_strength": 0.06,
    "gyro_pll_gyro_track": 0.42,
}

GYRO_PLL_STRONG: Dict[str, Any] = {
    **GYRO_PLL_GENTLE,
    "gyro_pll_phase_gain": 0.18,
    "gyro_pll_freq_gain": 0.012,
    "gyro_pll_freq_strength": 0.08,
    "gyro_pll_gyro_track": 0.55,
    "gyro_pll_neighbor_blend": 0.92,
}

GYRO_PLL_EXPERIMENT_PROFILES: Dict[str, Dict[str, Any]] = {
    "disabled": GYRO_PLL_DISABLED,
    "gentle": GYRO_PLL_GENTLE,
    "medium": GYRO_PLL_MEDIUM,
    "strong": GYRO_PLL_STRONG,
}


def gyro_pll_experiment(profile: str) -> Dict[str, Any]:
    if profile not in GYRO_PLL_EXPERIMENT_PROFILES:
        raise KeyError(
            f"Unknown gyro PLL profile {profile!r}; "
            f"choose from {list(GYRO_PLL_EXPERIMENT_PROFILES)}"
        )
    return dict(GYRO_PLL_EXPERIMENT_PROFILES[profile])