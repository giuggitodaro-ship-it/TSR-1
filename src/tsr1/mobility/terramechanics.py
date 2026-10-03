"""Rigid-wheel terramechanics (directive §10).

Model: Wong–Reece stress distribution around a driven rigid wheel (L003) with Bekker
pressure–sinkage (L002) and Janosi–Hanamoto shear stress–displacement (L004):

    σ(θ) = k_eq · [r (cos θ − cos θ1)]^n                       (front region θm ≤ θ ≤ θ1)
    σ(θ) = k_eq · [r (cos θ* − cos θ1)]^n, θ* = θ1 − (θ−θ2)/(θm−θ2)·(θ1−θm)   (rear region)
    k_eq = (k_c / b + k_φ) · k_factor
    θm   = (c1 + c2·i) θ1
    j(θ) = r_s [(θ1 − θ) − (1 − i)(sin θ1 − sin θ)]
    τ(θ) = (c + σ tan φ)(1 − exp(−j/K)) · dp_factor

    W  = b ∫ (r σ cos θ + r_s τ sin θ) dθ
    DP = b ∫ (r_s τ cos θ − r σ sin θ) dθ
    T  = b r_s² ∫ τ dθ

Grousers are represented by shearing at the grouser-tip radius r_s = r + h (a common
simplification, L010); normal stress acts on the rim radius r. Slip i = 1 − v/(ω r_s).

Limitations: rigid wheel; quasi-static; no bulldozing or side-wall effects; grouser model is
first-order. The reduced-gravity penalty (S043) enters through ``Soil.k_factor``/``dp_factor``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import Soil

SUB = "mobility"
C1 = R.define("wr_c1", "c_1", 0.43, "-", "SOURCE", "L003", SUB,
              "Wong-Reece max-stress angle coefficient (theta_m=(c1+c2 i) theta1)", low=0.35, high=0.50)
C2 = R.define("wr_c2", "c_2", 0.32, "-", "SOURCE", "L003", SUB, "Wong-Reece coefficient", low=0.15, high=0.40)
_NPTS = 121


@dataclass(frozen=True)
class Wheel:
    radius: float          # rim radius r [m]
    width: float           # b [m]
    grouser_h: float = 0.0  # grouser height h [m]

    @property
    def r_shear(self) -> float:
        return self.radius + self.grouser_h


@dataclass(frozen=True)
class WheelState:
    load: float        # vertical load W [N]
    slip: float
    theta1: float      # entry angle [rad]
    sinkage: float     # z [m]
    dp: float          # drawbar pull [N]
    torque: float      # wheel torque [N m]
    resistance: float  # compaction resistance R = b r ∫σ sinθ [N]
    thrust: float      # gross thrust H [N]
    contact_len: float  # chord length of contact patch [m]

    @property
    def dp_coeff(self) -> float:
        return self.dp / self.load

    @property
    def efficiency(self) -> float:
        """Tractive efficiency DP·v / (T·ω) with v = ω r_s (1 − i)."""
        return float("nan")


def _integrals(wheel: Wheel, soil: Soil, theta1: float, slip: float, theta2: float = 0.0):
    r, b, rs = wheel.radius, wheel.width, wheel.r_shear
    keq = (soil.kc / b + soil.kphi) * soil.k_factor
    thm = (C1 + C2 * slip) * theta1
    th = np.linspace(theta2, theta1, _NPTS)
    # equivalent angle mapping for rear region
    front = th >= thm
    th_eq = np.where(front, th, theta1 - (th - theta2) / max(thm - theta2, 1e-12) * (theta1 - thm))
    base = np.clip(r * (np.cos(th_eq) - math.cos(theta1)), 0.0, None)
    sigma = keq * base ** soil.n
    j = rs * ((theta1 - th) - (1.0 - slip) * (math.sin(theta1) - np.sin(th)))
    j = np.clip(j, 0.0, None)
    tau = (soil.c + sigma * math.tan(soil.phi)) * (1.0 - np.exp(-j / soil.K)) * soil.dp_factor
    trap = np.trapezoid
    Wv = b * (r * trap(sigma * np.cos(th), th) + rs * trap(tau * np.sin(th), th))
    Rr = b * r * trap(sigma * np.sin(th), th)
    H = b * rs * trap(tau * np.cos(th), th)
    T = b * rs ** 2 * trap(tau, th)
    return Wv, H, Rr, T


def solve(wheel: Wheel, soil: Soil, load: float, slip: float) -> WheelState:
    """Find entry angle θ1 that supports ``load`` at the given slip and return wheel forces."""
    if load <= 0:
        raise ValueError("load must be positive")
    f = lambda t1: _integrals(wheel, soil, t1, slip)[0] - load
    lo, hi = 1e-4, 1.2
    if f(hi) < 0:
        raise RuntimeError("wheel cannot support load: sinkage exceeds model validity (theta1 > 1.2 rad)")
    t1 = brentq(f, lo, hi, xtol=1e-9)
    Wv, H, Rr, T = _integrals(wheel, soil, t1, slip)
    z = wheel.radius * (1.0 - math.cos(t1))
    return WheelState(load=load, slip=slip, theta1=t1, sinkage=z, dp=H - Rr, torque=T, resistance=Rr,
                      thrust=H, contact_len=wheel.radius * math.sin(t1))


def bekker_sinkage_closed_form(wheel: Wheel, soil: Soil, load: float) -> float:
    """Classical Bekker closed-form rigid-wheel sinkage (towed wheel, small-sinkage approx.):
        z = [3W / ((3 − n)(k_c + b k_φ) √D)]^(2/(2n+1))
    Used as a verification check of the numerical model (tests)."""
    n = soil.n
    D = 2 * wheel.radius
    k = (soil.kc + wheel.width * soil.kphi) * soil.k_factor
    return (3 * load / ((3 - n) * k * math.sqrt(D))) ** (2 / (2 * n + 1))


def dp_curve(wheel: Wheel, soil: Soil, load: float, slips=None):
    slips = np.linspace(0.02, 0.8, 40) if slips is None else np.asarray(slips)
    return slips, np.array([solve(wheel, soil, load, s).dp for s in slips])


def contact_pressure(state: WheelState, wheel: Wheel) -> float:
    """Mean ground pressure over the contact patch (chord length × width)."""
    return state.load / (wheel.width * max(state.contact_len, 1e-6))
