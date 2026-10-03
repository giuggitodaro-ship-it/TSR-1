"""Vehicle-level mobility: slope capability, drawbar pull for towing, drive power and energy.

Static longitudinal model on a slope of angle θ (uphill = +x). Axle normal loads N_j satisfy
    Σ N_j = W cos θ
    Σ (x_j − x_cg) N_j = −W sin θ · h_cg − F_tow · h_tow
For more than two axles (statically indeterminate) the minimum-norm linear distribution is used,
representing a compliant/equalising suspension. All wheels operate at a common slip (rigid ground
speed coupling). A failed (unpowered, free-rolling) wheel contributes −R (its compaction resistance).

Energy is calibrated against the only measured lunar-vehicle datum, the Apollo LRV
(1.58–1.67 A·h/km at 36 V, S060), see :func:`lrv_calibration`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import brentq

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import G_MOON, Soil, soil_nominal
from tsr1.mobility.terramechanics import Wheel, solve

SUB = "mobility"
R.define("lrv_mass_loaded", "m_LRV", 680.0, "kg", "ASSUMPTION", "S027,A (210 kg + 2 suited crew + gear)", SUB,
         "Apollo 15/17 traverse mass: 210 kg empty, <= 700 kg max loaded (S027)", low=600.0, high=700.0)
R.define("lrv_energy_per_km", "e_LRV", 1.625 * 36.0, "Wh/km", "SOURCE", "S060", SUB,
         "mean of 1.58 (A17) and 1.67 (A15) A h/km at 36 V nominal", low=1.58 * 36.0, high=1.67 * 36.0)
R.define("lrv_drive_eff", "η_LRV", 0.55, "-", "ASSUMPTION", "A-17 (series DC motor x 80:1 harmonic drive)", SUB,
         "battery-to-wheel efficiency of LRV drive", low=0.45, high=0.65)
R.define("drive_eff", "η_drv", 0.70, "-", "ASSUMPTION", "A-17", SUB,
         "TSR-1 battery-to-wheel efficiency (BLDC + strain-wave gear + controller)", low=0.55, high=0.80)
R.define("slip_design_limit", "i_max", 0.40, "-", "DESIGN", "TS-01", SUB,
         "maximum sustained slip used for slope capability claims", low=0.2, high=0.6)


@dataclass
class Vehicle:
    mass: float                    # operational mass [kg]
    wheel: Wheel
    axle_x: tuple                  # axle positions along wheelbase [m] (x_cg reference frame)
    wheels_per_axle: int = 2
    x_cg: float = 0.0
    h_cg: float = 0.6
    track: float = 1.8             # lateral wheel spacing [m]
    drive_eff: float = field(default_factory=lambda: R.v("drive_eff"))

    @property
    def n_wheels(self) -> int:
        return len(self.axle_x) * self.wheels_per_axle

    @property
    def weight(self) -> float:
        return self.mass * G_MOON


def axle_loads(veh: Vehicle, slope: float, f_tow: float = 0.0, h_tow: float = 0.0) -> np.ndarray:
    W = veh.weight
    x = np.asarray(veh.axle_x, float) - veh.x_cg
    n = len(x)
    wn = W * math.cos(slope)
    m_req = -W * math.sin(slope) * veh.h_cg - f_tow * h_tow
    A = np.array([[n, x.sum()], [x.sum(), (x ** 2).sum()]])
    a, b = np.linalg.solve(A, [wn, m_req])
    loads = a + b * x
    return loads


@dataclass
class DriveState:
    slip: float
    wheel_states: list
    dp_total: float
    torque_total: float
    feasible: bool
    loads: np.ndarray


def _total_dp(veh: Vehicle, soil: Soil, slip: float, loads: np.ndarray, failed: int = 0):
    states, dp, tq = [], 0.0, 0.0
    k = 0
    for N in loads:
        for _ in range(veh.wheels_per_axle):
            wl = max(N / veh.wheels_per_axle, 1.0)
            st = solve(veh.wheel, soil, wl, slip)
            if k < failed:      # unpowered free-rolling wheel: resistance only
                dp -= st.resistance
                states.append(None)
            else:
                dp += st.dp
                tq += st.torque
                states.append(st)
            k += 1
    return dp, tq, states


def drive_state(veh: Vehicle, soil: Soil, slope: float, f_tow: float = 0.0, h_tow: float = 0.3,
                failed_wheels: int = 0, slip_max: float = 0.8) -> DriveState:
    """Slip and torques needed to move at constant speed up ``slope`` while towing ``f_tow``."""
    loads = axle_loads(veh, slope, f_tow, h_tow)
    if (loads <= 0).any():
        return DriveState(float("nan"), [], 0.0, 0.0, False, loads)
    need = veh.weight * math.sin(slope) + f_tow
    g = lambda s: _total_dp(veh, soil, s, loads, failed_wheels)[0] - need
    lo, hi = 0.005, slip_max
    if g(hi) < 0:
        dp, tq, st = _total_dp(veh, soil, hi, loads, failed_wheels)
        return DriveState(hi, st, dp, tq, False, loads)
    if g(lo) > 0:
        s = lo
    else:
        s = brentq(g, lo, hi, xtol=1e-4)
    dp, tq, st = _total_dp(veh, soil, s, loads, failed_wheels)
    return DriveState(s, st, dp, tq, True, loads)


def max_slope(veh: Vehicle, soil: Soil, slip_limit: float | None = None, f_tow: float = 0.0,
              failed_wheels: int = 0) -> float:
    """Largest slope [rad] climbable at constant speed with slip ≤ slip_limit."""
    slip_limit = R.v("slip_design_limit") if slip_limit is None else slip_limit

    def ok(th):
        return drive_state(veh, soil, th, f_tow, failed_wheels=failed_wheels, slip_max=slip_limit).feasible

    if not ok(0.0):
        return 0.0
    lo, hi = 0.0, math.radians(45)
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if ok(mid):
            lo = mid
        else:
            hi = mid
    return lo


def max_tow_force(veh: Vehicle, soil: Soil, slope: float, slip_limit: float | None = None,
                  h_tow: float = 0.3) -> float:
    """Largest towing force [N] (along slope) the vehicle can sustain while climbing ``slope``."""
    slip_limit = R.v("slip_design_limit") if slip_limit is None else slip_limit
    loads = axle_loads(veh, slope)
    dp, _, _ = _total_dp(veh, soil, slip_limit, loads)
    f0 = dp - veh.weight * math.sin(slope)
    if f0 <= 0:
        return 0.0
    # refine including load transfer from the tow moment
    f = f0
    for _ in range(20):
        loads = axle_loads(veh, slope, f, h_tow)
        if (loads <= 0).any():
            f *= 0.9
            continue
        dp, _, _ = _total_dp(veh, soil, slip_limit, loads)
        fn = dp - veh.weight * math.sin(slope)
        if abs(fn - f) < 1.0:
            f = fn
            break
        f = 0.5 * (f + fn)
    return max(f, 0.0)


def wheel_power(veh: Vehicle, ds: DriveState, v: float) -> float:
    """Mechanical power at the wheels [W] for speed v [m/s]."""
    omega = v / (veh.wheel.r_shear * (1.0 - ds.slip))
    return ds.torque_total * omega


def electrical_drive_power(veh: Vehicle, soil: Soil, slope: float, v: float, f_tow: float = 0.0,
                           k_cal: float = 1.0, failed_wheels: int = 0) -> float:
    ds = drive_state(veh, soil, slope, f_tow, failed_wheels=failed_wheels)
    if not ds.feasible:
        return float("nan")
    return k_cal * wheel_power(veh, ds, v) / veh.drive_eff


def wheel_energy_per_m(veh: Vehicle, soil: Soil, slope: float = 0.0, f_tow: float = 0.0) -> float:
    """Wheel mechanical energy per metre travelled [J/m] (= Σ T / (r_s (1 − i)))."""
    ds = drive_state(veh, soil, slope, f_tow)
    if not ds.feasible:
        return float("nan")
    return ds.torque_total / (veh.wheel.r_shear * (1.0 - ds.slip))


def lrv_vehicle() -> Vehicle:
    """Apollo LRV approximated as rigid 0.818 m × 0.23 m wheels, 2.29 m wheelbase (S027)."""
    return Vehicle(mass=R.v("lrv_mass_loaded"), wheel=Wheel(0.409, 0.23, 0.0), axle_x=(1.145, -1.145),
                   x_cg=0.0, h_cg=0.6, track=1.83, drive_eff=R.v("lrv_drive_eff"))


def lrv_calibration(soil: Soil | None = None) -> float:
    """k_cal = (measured LRV battery energy × η_LRV) / (model wheel energy on level ground).

    k_cal < 1 means the Table 9.14 soil + rigid-wheel model over-predicts real lunar driving
    resistance (LRV wire-mesh wheels deflect; in-situ soil is stronger than the trafficability set);
    k_cal > 1 would mean real traverses cost more than level-ground model predictions.
    """
    soil = soil_nominal() if soil is None else soil
    lrv = lrv_vehicle()
    e_model = wheel_energy_per_m(lrv, soil) * 1000.0 / 3600.0  # Wh/km at wheels
    e_meas_wheel = R.v("lrv_energy_per_km") * R.v("lrv_drive_eff")
    k = e_meas_wheel / e_model
    R.calc("lrv_model_wheel_energy", "e_LRV,model", e_model, "Wh/km",
           "mobility.vehicle.lrv_calibration: Wong-Reece, nominal soil, level", SUB)
    R.calc("k_cal_lrv", "k_cal", k, "-", "mobility.vehicle.lrv_calibration: measured(S060)*η/model", SUB)
    return k
