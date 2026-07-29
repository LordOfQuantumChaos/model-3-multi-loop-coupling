"""
Known-frequency experiment profiles (opt-in only).
"""

from __future__ import annotations

from typing import Any, Dict, List

KNOWN_FREQUENCIES_DISABLED: Dict[str, Any] = dict(
    known_frequencies_enabled=False,
    known_frequencies=[],
    known_frequencies_amplitudes=[],
    known_frequencies_phases=[],
    known_frequencies_mode=3,
    known_frequencies_substeps=32,
    memory_frequency_switch_enabled=False,
    memory_frequency_threshold=0.5,
    memory_frequency_scale=1.5,
)

_EXAMPLE_FREQS: List[float] = [3.5e-3, 5.0e-3, 7.0e-3]
_EXAMPLE_AMPS: List[float] = [0.003, 0.002, 0.0015]
_EXAMPLE_PHASES: List[float] = [0.0, 0.0, 0.0]

KNOWN_FREQUENCIES_GENTLE: Dict[str, Any] = {
    "known_frequencies_enabled": True,
    "known_frequencies": list(_EXAMPLE_FREQS),
    "known_frequencies_amplitudes": list(_EXAMPLE_AMPS),
    "known_frequencies_phases": list(_EXAMPLE_PHASES),
    "known_frequencies_mode": 3,
    "known_frequencies_substeps": 32,
    "memory_frequency_switch_enabled": False,
}

# One-third of gentle amplitudes — first lattice panel default
KNOWN_FREQUENCIES_VERY_GENTLE: Dict[str, Any] = {
    **KNOWN_FREQUENCIES_GENTLE,
    "known_frequencies_amplitudes": [0.001, 0.0007, 0.0005],
}

KNOWN_FREQUENCIES_MEMORY: Dict[str, Any] = {
    **KNOWN_FREQUENCIES_GENTLE,
    "memory_frequency_switch_enabled": True,
    "memory_frequency_threshold": 0.5,
    "memory_frequency_scale": 1.5,
}

PROFILES: Dict[str, Dict[str, Any]] = {
    "disabled": KNOWN_FREQUENCIES_DISABLED,
    "very_gentle": KNOWN_FREQUENCIES_VERY_GENTLE,
    "gentle": KNOWN_FREQUENCIES_GENTLE,
    "gentle_memory": KNOWN_FREQUENCIES_MEMORY,
}

KNOWN_FREQUENCY_PROFILES: Dict[str, Dict[str, Any]] = {
    k: v for k, v in PROFILES.items() if k != "disabled"
}


def known_frequencies_experiment(profile: str) -> Dict[str, Any]:
    if profile not in KNOWN_FREQUENCY_PROFILES:
        raise KeyError(
            f"Unknown known-frequency profile {profile!r}; "
            f"choose from {list(KNOWN_FREQUENCY_PROFILES)}"
        )
    return dict(KNOWN_FREQUENCY_PROFILES[profile])


def apply_known_frequencies(
    base: Dict[str, Any],
    profile: str | None = None,
    *,
    enabled: bool = True,
    frequencies: List[float] | None = None,
    amplitudes: List[float] | None = None,
    phases: List[float] | None = None,
) -> Dict[str, Any]:
    if not enabled:
        return {**base, **KNOWN_FREQUENCIES_DISABLED}
    if profile is not None:
        overlay = known_frequencies_experiment(profile)
    else:
        overlay = dict(KNOWN_FREQUENCIES_GENTLE)
    if frequencies is not None:
        overlay["known_frequencies"] = list(frequencies)
    if amplitudes is not None:
        overlay["known_frequencies_amplitudes"] = list(amplitudes)
    if phases is not None:
        overlay["known_frequencies_phases"] = list(phases)
    return {**base, **overlay}