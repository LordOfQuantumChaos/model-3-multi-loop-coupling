"""
Predictive adaptive controller (PAC) experiment overlays for the gyro term.
"""

from __future__ import annotations

from typing import Any, Dict

from driven_loop.experiments.gravity_well import GR_WELL_STABILIZED

PAC_DISABLED: Dict[str, Any] = dict(
    predictive_adaptive_controller_enabled=False,
)

# Gentle PAC tuned for GR well + gyro barrier stack
PAC_GENTLE: Dict[str, Any] = dict(
    predictive_adaptive_controller_enabled=True,
    pac_activity_decay=0.97,
    pac_trend_decay=0.90,
    pac_baseline_decay=0.999,
    pac_learning_rate=0.04,
    pac_horizon_frames=40.0,
    pac_activity_ref=0.02,
    pac_envelope_margin=1.15,
    pac_boost_scale=0.55,
    pac_quiet_reduce=0.06,
    pac_gain_min=0.85,
    pac_gain_max=2.0,
    pac_risk_scale=0.015,
)

# Stronger preemptive boost (more aggressive)
PAC_STRONG: Dict[str, Any] = dict(
    predictive_adaptive_controller_enabled=True,
    pac_activity_decay=0.95,
    pac_trend_decay=0.88,
    pac_baseline_decay=0.998,
    pac_learning_rate=0.06,
    pac_horizon_frames=60.0,
    pac_activity_ref=0.02,
    pac_envelope_margin=1.08,
    pac_boost_scale=0.85,
    pac_quiet_reduce=0.04,
    pac_gain_min=0.80,
    pac_gain_max=2.4,
    pac_risk_scale=0.012,
)

# GR stabilized + gentle PAC
GR_PAC_GENTLE: Dict[str, Any] = {
    **GR_WELL_STABILIZED,
    **PAC_GENTLE,
}

PAC_EXPERIMENT_PROFILES: Dict[str, Dict[str, Any]] = {
    "disabled": PAC_DISABLED,
    "gentle": PAC_GENTLE,
    "strong": PAC_STRONG,
    "gr_pac_gentle": GR_PAC_GENTLE,
}


def pac_experiment(profile: str = "gentle") -> Dict[str, Any]:
    if profile not in PAC_EXPERIMENT_PROFILES:
        raise KeyError(
            f"Unknown PAC profile {profile!r}; "
            f"choose from {list(PAC_EXPERIMENT_PROFILES)}"
        )
    return dict(PAC_EXPERIMENT_PROFILES[profile])


def apply_pac_experiment(
    base: Dict[str, Any], profile: str = "gentle",
) -> Dict[str, Any]:
    return {**base, **pac_experiment(profile)}
