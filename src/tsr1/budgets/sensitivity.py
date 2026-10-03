"""Sensitivity and uncertainty analysis (directive §36).

One-at-a-time (tornado) sweeps evaluate an output at the low and high end of each registered parameter
range with everything else nominal; Monte Carlo propagates all MER/MGA uncertainties jointly for mass.
Parameters are swapped in the central register temporarily (restored afterwards).
"""
from __future__ import annotations

import math
from contextlib import contextmanager
from dataclasses import replace

import numpy as np

from tsr1.common.params import REGISTRY as R


@contextmanager
def override(values: dict):
    saved = {k: R.params[k] for k in values}
    try:
        for k, v in values.items():
            R.params[k] = replace(R.params[k], value=float(v), low=None, high=None)
        yield
    finally:
        R.params.update(saved)


def tornado(fn, names: list[str], label: str = "") -> list[dict]:
    """fn() -> float evaluated at nominal, at each parameter's low and high bound."""
    base = fn()
    rows = []
    for n in names:
        lo, hi = R.rng(n)
        with override({n: lo}):
            f_lo = fn()
        with override({n: hi}):
            f_hi = fn()
        rows.append(dict(output=label, parameter=n, low=lo, high=hi, f_nominal=base, f_low=f_lo, f_high=f_hi,
                         swing=abs(f_hi - f_lo)))
    rows.sort(key=lambda r: -r["swing"])
    return rows


MASS_UNCERTAIN = ["act_torque_density", "batt_spec_energy", "harness_frac", "system_margin", "wheel_rim_t",
                  "insert_frac", "conv_spec_power", "batt_dod", "batt_eol_fade", "fitting_frac",
                  "lander_accommodation_frac"] + [f"mga_{k}" for k in ("structure", "mechanism", "electronics",
                                                                        "harness", "battery", "thermal", "tool")]


def mass_monte_carlo(build_fn, n: int = 200, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        vals = {}
        for k in MASS_UNCERTAIN:
            lo, hi = R.rng(k)
            # triangular with mode at nominal
            vals[k] = rng.triangular(lo, R.v(k), hi) if lo < hi else R.v(k)
        with override(vals):
            out.append(build_fn().delivered_mass)
    return np.array(out)
