"""
Compression-twist experiment profiles (opt-in only).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from driven_loop.experiments.plasma_flow import plasma_scenario

COMPRESSION_TWIST_DISABLED: Dict[str, Any] = dict(
    compression_test_enabled=False,
    axial_compression_rate=0.001,
    max_axial_compression=0.15,
    measure_twist=True,
    twist_window=1,
    twist_measurement_window=100,
    compression_layer_thickness=0.1,
)

COMPRESSION_TWIST_DEFAULT: Dict[str, Any] = {
    **COMPRESSION_TWIST_DISABLED,
    "compression_test_enabled": True,
}

# User stack: stronger mirror-balance plasma + compression-twist probe
# Plasma strength/bias raised so engaged spikes influence lattice metrics.
# Compression: force = min(rate * step/frames, max).
# 0.00125: 100/100 mode-3 validated. 0.0014: 99/100 (seed 90). 0.00145+: hard fails.
# Default 0.00125 prioritizes strict mode-3 stability over max compression.
MIRROR_BALANCE_COMPRESSION_TWIST: Dict[str, Any] = {
    **plasma_scenario("helical_55_mirror_balance"),
    **COMPRESSION_TWIST_DEFAULT,
    "plasma_mirror_balance_enabled": True,
    "plasma_strength": 0.04,
    "plasma_tangential": 0.025,
    "plasma_phase_lock_strength": 0.65,
    "plasma_helical_mirror_bias": 0.75,
    "balance_feedback_strength": 0.45,
    "plasma_sync_threshold": 0.01,
    "compression_test_enabled": True,
    "axial_compression_rate": 0.00125,
    "max_axial_compression": 0.20,
    "measure_twist": True,
}


def compression_twist_experiment(enabled: bool = True) -> Dict[str, Any]:
    return dict(COMPRESSION_TWIST_DEFAULT if enabled else COMPRESSION_TWIST_DISABLED)


def mirror_balance_compression_config(
    *,
    max_axial_compression: float = 0.20,
    axial_compression_rate: float = 0.00125,
    plasma_phase_lock_strength: float = 0.65,
    plasma_helical_mirror_bias: float = 0.75,
    balance_feedback_strength: Optional[float] = 0.45,
    plasma_strength: Optional[float] = 0.04,
    plasma_tangential: Optional[float] = 0.025,
    plasma_sync_threshold: Optional[float] = 0.01,
    diverge: bool = False,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build the mirror-balance + compression-twist overlay dict.

    Defaults use stronger plasma influence when energy exceeds sync threshold.
    ``diverge=True`` applies low threshold + always-on early window so plasma
    can move lattice metrics vs GR+KF baseline.
    """
    if diverge:
        out = {
            **plasma_scenario("helical_55_mirror_balance_diverge"),
            **COMPRESSION_TWIST_DEFAULT,
            "compression_test_enabled": True,
            "axial_compression_rate": float(axial_compression_rate),
            "max_axial_compression": float(max_axial_compression),
            "measure_twist": True,
        }
    else:
        out = dict(MIRROR_BALANCE_COMPRESSION_TWIST)
        out["max_axial_compression"] = float(max_axial_compression)
        out["axial_compression_rate"] = float(axial_compression_rate)
        out["plasma_phase_lock_strength"] = float(plasma_phase_lock_strength)
        out["plasma_helical_mirror_bias"] = float(plasma_helical_mirror_bias)
        if balance_feedback_strength is not None:
            out["balance_feedback_strength"] = float(balance_feedback_strength)
        if plasma_strength is not None:
            out["plasma_strength"] = float(plasma_strength)
        if plasma_tangential is not None:
            out["plasma_tangential"] = float(plasma_tangential)
        if plasma_sync_threshold is not None:
            out["plasma_sync_threshold"] = float(plasma_sync_threshold)
    if extra:
        out.update(extra)
    return out