"""
QSLT 553 Hz resonance experiment profiles (opt-in only).

  python scripts/run_qslt_resonance_test.py --seeds 10
"""

from __future__ import annotations

from typing import Any, Dict

QSLT_RESONANCE_DISABLED: Dict[str, Any] = dict(
    qslt_resonance_enabled=False,
    qslt_resonance_strength=0.0,
    qslt_resonance_frequency_hz=553.0,
    qslt_resonance_mode=3,
    qslt_resonance_substeps=32,
    qslt_resonance_em_rpm=0.0,
    qslt_resonance_em_depth=0.0,
)

_COMMON: Dict[str, Any] = dict(
    qslt_resonance_enabled=True,
    qslt_resonance_frequency_hz=553.0,
    qslt_resonance_mode=3,
    qslt_resonance_substeps=32,
)

RESONANCE_553_GENTLE: Dict[str, Any] = {
    **_COMMON,
    "qslt_resonance_strength": 0.003,
}

RESONANCE_553_MEDIUM: Dict[str, Any] = {
    **_COMMON,
    "qslt_resonance_strength": 0.008,
}

RESONANCE_553_STRONG: Dict[str, Any] = {
    **_COMMON,
    "qslt_resonance_strength": 0.015,
}

# Off-resonance controls (same strength as gentle)
RESONANCE_400_GENTLE: Dict[str, Any] = {
    **_COMMON,
    "qslt_resonance_strength": 0.003,
    "qslt_resonance_frequency_hz": 400.0,
}

RESONANCE_700_GENTLE: Dict[str, Any] = {
    **_COMMON,
    "qslt_resonance_strength": 0.003,
    "qslt_resonance_frequency_hz": 700.0,
}

# 553 Hz + 150 RPM EM envelope (paper §5.3)
RESONANCE_553_EM150: Dict[str, Any] = {
    **_COMMON,
    "qslt_resonance_strength": 0.003,
    "qslt_resonance_em_rpm": 150.0,
    "qslt_resonance_em_depth": 0.35,
}

PROFILES: Dict[str, Dict[str, Any]] = {
    "disabled": QSLT_RESONANCE_DISABLED,
    "553_gentle": RESONANCE_553_GENTLE,
    "553_medium": RESONANCE_553_MEDIUM,
    "553_strong": RESONANCE_553_STRONG,
    "400_gentle": RESONANCE_400_GENTLE,
    "700_gentle": RESONANCE_700_GENTLE,
    "553_em150": RESONANCE_553_EM150,
}

QSLT_RESONANCE_PROFILES: Dict[str, Dict[str, Any]] = {
    k: v for k, v in PROFILES.items() if k != "disabled"
}

DEFAULT_GENTLE_STRENGTH: float = RESONANCE_553_GENTLE["qslt_resonance_strength"]


def qslt_resonance_at_hz(
    frequency_hz: float,
    strength: float = DEFAULT_GENTLE_STRENGTH,
    *,
    mode: int = 3,
    substeps: int = 32,
    em_rpm: float = 0.0,
    em_depth: float = 0.0,
) -> Dict[str, Any]:
    """Return overlay dict for frequency-based forcing at ``frequency_hz``."""
    return {
        "qslt_resonance_enabled": True,
        "qslt_resonance_frequency_hz": float(frequency_hz),
        "qslt_resonance_strength": float(strength),
        "qslt_resonance_mode": int(mode),
        "qslt_resonance_substeps": int(substeps),
        "qslt_resonance_em_rpm": float(em_rpm),
        "qslt_resonance_em_depth": float(em_depth),
    }


def qslt_resonance_experiment(profile: str) -> Dict[str, Any]:
    """Named resonance profile overlay (does not copy base config)."""
    if profile not in QSLT_RESONANCE_PROFILES:
        raise KeyError(
            f"Unknown resonance profile {profile!r}; "
            f"choose from {list(QSLT_RESONANCE_PROFILES)}"
        )
    return dict(QSLT_RESONANCE_PROFILES[profile])


def apply_qslt_resonance(
    base: Dict[str, Any],
    *,
    frequency_hz: float | None = None,
    profile: str | None = None,
    strength: float | None = None,
    enabled: bool = True,
) -> Dict[str, Any]:
    """
    Merge base config with QSLT frequency forcing.

    Switch on via ``frequency_hz`` (e.g. 553) or ``profile`` (e.g. ``553_gentle``).
    Pass ``enabled=False`` or omit both to force off.
    """
    if not enabled:
        return {**base, **QSLT_RESONANCE_DISABLED}
    if profile is not None:
        overlay = qslt_resonance_experiment(profile)
        if frequency_hz is not None:
            overlay["qslt_resonance_frequency_hz"] = float(frequency_hz)
        if strength is not None:
            overlay["qslt_resonance_strength"] = float(strength)
        return {**base, **overlay}
    if frequency_hz is not None:
        return {
            **base,
            **qslt_resonance_at_hz(
                frequency_hz,
                strength if strength is not None else DEFAULT_GENTLE_STRENGTH,
            ),
        }
    return {**base, **QSLT_RESONANCE_DISABLED}