"""TS-01 mobility architecture and TS-02 wheel architecture/sizing.

Every candidate is built with ``design.configuration.build`` so that its mass, centre of mass, power
and mobility performance are computed with exactly the same models as the baseline.
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np

from tsr1.common.params import REGISTRY as R
from tsr1.design.configuration import Options, build
from tsr1.environment.lunar import G_MOON, soil_conservative, soil_nominal
from tsr1.mobility.terramechanics import Wheel, contact_pressure, solve
from tsr1.mobility.vehicle import max_slope, wheel_energy_per_m
import tsr1.reliability.tsr_reliability  # noqa: F401  (registers failure-rate parameters)

MOBILITY_CANDIDATES = {
    "M1 6-wheel rocker-bogie (passive)": dict(n_wheels=6, suspension="rocker_bogie"),
    "M2 6-wheel rocker-bogie + body lowering + differential lock": dict(n_wheels=6, suspension="rocker_bogie_lowering"),
    "M3 6-wheel independently articulated legs (active)": dict(n_wheels=6, suspension="active_6"),
    "M4 4-wheel independent active suspension": dict(n_wheels=4, suspension="active_4"),
}
WHEEL_D = (0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4)
WHEEL_B = (0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60)
R.define("dpw40_min", "DP/W_40,min", 0.36, "-", "DESIGN", "TS-02: ≈20° slope at 40 % slip (nominal soil)", "mobility",
         "minimum single-wheel drawbar coefficient at 40 % slip")


def size_wheel_for(n_wheels: int, mass_kg: float, grouser_h: float = 0.02):
    """Lightest wheel (D, b) meeting contact pressure ≤ limit and DP/W(40 %) ≥ dpw40_min."""
    from tsr1.design.configuration import _wheel_mass
    sn = soil_nominal()
    wl = mass_kg * G_MOON / n_wheels
    best, fallback = None, None
    for D in WHEEL_D:
        for b in WHEEL_B:
            w = Wheel(D / 2, b, grouser_h)
            s20 = solve(w, sn, wl, 0.2)
            p = contact_pressure(s20, w)
            dpw = solve(w, sn, wl, 0.4).dp_coeff
            m = _wheel_mass(w)
            viol = max(0.0, p / R.v("contact_pressure_limit") - 1) + max(0.0, 1 - dpw / R.v("dpw40_min"))
            if fallback is None or viol < fallback[3] - 1e-9 or (abs(viol - fallback[3]) < 1e-9 and m < fallback[2]):
                fallback = (D, b, m, viol)
            if viol > 0:
                continue
            if best is None or m < best[2]:
                best = (D, b, m)
    if best is None:   # no feasible wheel: return the least-violating one (flagged by the caller)
        return fallback[:3]
    return best
# Obstacle capability by suspension class (heritage-based rule, ratio to wheel diameter):
# rocker-bogie ≈ 1.0 D (MER/MSL heritage practice), active legs ≈ 1.25 D (leg stroke), 4-wheel active ≈ 0.75 D.
OBSTACLE_RATIO = {"rocker_bogie": 0.75, "rocker_bogie_lowering": 0.75, "active_6": 1.0, "active_4": 0.6}
R.define("obstacle_ratio_rb", "h_obs/D", 0.75, "-", "ESTIMATE",
         "L011 (rocker-bogie climbs obstacles of order one wheel diameter; 0.75 adopted for heavy, slow, "
         "quasi-static lunar operation)", "mobility", "step obstacle height / wheel diameter", low=0.5, high=1.0)


def evaluate_mobility(opts_base: Options | None = None) -> list[dict]:
    opts_base = opts_base or Options()
    sn, scn = soil_nominal(), soil_conservative()
    out = []
    for name, kw in MOBILITY_CANDIDATES.items():
        o = replace(opts_base, label=name, **kw)
        # size wheels at the candidate's own operational mass (two passes: mass depends on wheels)
        cfg = build(o)
        for _ in range(2):
            D, b, _m = size_wheel_for(o.n_wheels, cfg.operational_mass, o.grouser_h)
            o = replace(o, wheel_r=D / 2, wheel_b=b, wheelbase=max(opts_base.wheelbase, 3 * D * 0.9)
                        if o.n_wheels == 6 else max(opts_base.wheelbase, 2.2))
            cfg = build(o)
        v = cfg.vehicle
        wl = v.weight / v.n_wheels
        st = solve(v.wheel, sn, wl, 0.2)
        n_act = sum(1 for c in cfg.comps if c.subsystem in ("mobility",) and c.category == "mechanism"
                    and "wheel_" not in c.name)
        lam_drive = R.v("lambda_drive_unit")
        out.append(dict(
            candidate=name, n_wheels=o.n_wheels, suspension=o.suspension,
            wheel_D_m=2 * o.wheel_r, wheel_b_m=o.wheel_b,
            operational_mass_kg=cfg.operational_mass, delivered_mass_kg=cfg.delivered_mass,
            mobility_mass_pred_kg=cfg.predicted("mobility") + cfg.predicted("stabilisation"),
            wheel_load_N=wl, sinkage_m=st.sinkage, contact_pressure_kPa=contact_pressure(st, v.wheel) / 1e3,
            max_slope_nom_deg=math.degrees(max_slope(v, sn)), max_slope_cons_deg=math.degrees(max_slope(v, scn)),
            max_slope_one_wheel_out_deg=math.degrees(max_slope(v, sn, failed_wheels=1)),
            max_slope_two_wheels_out_deg=math.degrees(max_slope(v, sn, failed_wheels=2)),
            wheel_energy_Wh_per_km=wheel_energy_per_m(v, sn) / 3.6,
            obstacle_m=OBSTACLE_RATIO[o.suspension] * 2 * o.wheel_r,
            body_lowering=o.suspension != "rocker_bogie",
            mobility_actuators=n_act,
            p_no_drive_failure_10yr=math.exp(-lam_drive * 10 * o.n_wheels),
            # without repair: 6-wheel keeps (reduced-slope) mobility with 4 of 6 driven, 4-wheel with 3 of 4
            p_mobility_retained_10yr=_p_k_of_n(o.n_wheels, 4 if o.n_wheels == 6 else 3, lam_drive, 10.0),
        ))
    return out


def _p_k_of_n(n: int, k: int, lam: float, years: float) -> float:
    """P(at least k of n units survive) without repair (binomial, exponential lifetimes)."""
    p = math.exp(-lam * years)
    from math import comb
    return sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def wheel_sweep(mass_kg: float = 1150.0, n_wheels: int = 6) -> list[dict]:
    """TS-02 parametric wheel sizing sweep (single-wheel metrics at the nominal operational mass)."""
    from tsr1.design.configuration import _wheel_mass
    sn, scn = soil_nominal(), soil_conservative()
    wl = mass_kg * G_MOON / n_wheels
    rows = []
    for D in (0.6, 0.7, 0.8, 0.9, 1.0):
        for b in (0.2, 0.25, 0.3, 0.35, 0.4):
            for h in (0.0, 0.015, 0.03):
                w = Wheel(D / 2, b, h)
                s20 = solve(w, sn, wl, 0.2)
                s40 = solve(w, sn, wl, 0.4)
                c40 = solve(w, scn, wl, 0.4)
                rows.append(dict(D_m=D, b_m=b, grouser_m=h, sinkage_mm=s20.sinkage * 1e3,
                                 contact_pressure_kPa=contact_pressure(s20, w) / 1e3,
                                 dpw_20=s20.dp_coeff, dpw_40=s40.dp_coeff, dpw_40_cons=c40.dp_coeff,
                                 slope_proxy_deg=math.degrees(math.atan(max(s40.dp_coeff, 0))),
                                 resistance_coeff=s20.resistance / wl, wheel_mass_kg=_wheel_mass(w),
                                 torque_40_Nm=s40.torque))
    return rows


WHEEL_TYPES = [
    dict(type="Rigid Ti-6Al-4V rim with grousers", trl=6, heritage="VIPER/Yutu/Pragyan rigid wheels; MSL Al wheels",
         dust="no mesh to fill; grousers shed regolith", cold="Ti ductile to cryogenic T", fatigue="rim cracking risk (MSL) mitigated by thicker Ti, low speed",
         model_confidence="high (rigid-wheel terramechanics applies)", mass_note="computed by MER", selected=True),
    dict(type="Woven wire-mesh (LRV-type) with Ti chevrons", trl=6, heritage="Apollo LRV (S027, S029)",
         dust="mesh openings admit dust; abrasion of wire crossings", cold="steel/Ti wire OK",
         fatigue="low-cycle fatigue at wire crossings over 10-yr life and >1000 km unproven", model_confidence="low (flexible wheel)",
         mass_note="light (~5 kg class)", selected=False),
    dict(type="Superelastic NiTi spring tyre", trl=4, heritage="NASA GRC prototypes (no flight)",
         dust="open spring mesh admits dust", cold="NiTi transformation temperatures must be tuned for 40-390 K range",
         fatigue="superelastic fatigue promising but unqualified", model_confidence="low",
         mass_note="heavier than wire mesh", selected=False),
    dict(type="Rigid Al 7075 wheel", trl=7, heritage="MSL/M2020 wheels",
         dust="as rigid Ti", cold="OK", fatigue="MSL wheel punctures/cracks on sharp rocks (thin skin)",
         model_confidence="high", mass_note="~35 % lighter than Ti at equal thickness but needs thicker skin for 10-yr life",
         selected=False),
]
