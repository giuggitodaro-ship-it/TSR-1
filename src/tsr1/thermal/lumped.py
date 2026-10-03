"""First-order thermal model of TSR-1 (directive §19).

Nodes: (1) Warm Electronics Box (WEB: avionics, battery, power electronics), MLI-insulated, coupled to
(2) a zenith-facing radiator through a variable-conductance link (loop heat pipe with a thermal
switch / VCHP; louvers as alternative). External actuators are treated separately (heaters or
cold-tolerant design, TS thermal sub-trade).

Hot case:  Q_int + Q_env,abs = ε σ A_rad (T_rad⁴ − T_sink⁴)
Cold case: heater power = leak(WEB) − Q_int,survival, with leak = σ ε* A_MLI (T⁴ − T_s⁴)
           + ε_off σ A_rad (T⁴ − T_s⁴) + G_cond (T − T_struct)
Survival time = usable energy / (heater + survival electronics), and a transient cool-down estimate
from the WEB heat capacity for PSR excursions.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import SIGMA_SB, SOLAR_CONST

SUB = "thermal"
R.define("mli_eps_eff", "ε*", 0.03, "-", "SOURCE", "L006 (Gilmore: practical blankets 0.01-0.05, LITERATURE-RECALL)", SUB,
         "effective emittance of flight MLI incl. seams/penetrations", low=0.015, high=0.05)
R.define("rad_eps", "ε_rad", 0.85, "-", "SOURCE", "L006 (white paint / OSR BOL, LITERATURE-RECALL)", SUB,
         "radiator IR emittance (BOL)", low=0.75, high=0.90)
R.define("rad_alpha_bol", "α_rad", 0.15, "-", "SOURCE", "L006 (LITERATURE-RECALL)", SUB, "radiator solar absorptance BOL",
         low=0.08, high=0.25)
R.define("rad_alpha_dust_factor", "f_α,dust", 2.0, "-", "SOURCE", "S062", SUB,
         "absorptance multiplication at ~25 % dust coverage (1.4-2.6)", low=1.4, high=2.6)
R.define("rad_off_eps", "ε_off", 0.04, "-", "ESTIMATE", "L006 (closed louver / LHP shut-off effective, LITERATURE-RECALL)",
         SUB, "effective radiator emittance with heat rejection switched off", low=0.02, high=0.10)
R.define("web_cond_leak", "G_leak", 0.25, "W/K", "ESTIMATE", "A: titanium/GFRP standoffs + harness feed-throughs", SUB,
         "conductive coupling WEB->structure", low=0.10, high=0.50)
R.define("T_rad_max", "T_rad,max", 293.0, "K", "DESIGN", "TS thermal: battery <= 30 C charging with 10 K gradient", SUB,
         "maximum radiator operating temperature in hot case")
R.define("T_web_survival", "T_surv", 263.0, "K", "DESIGN", "S071 (battery discharge >= -20 C) + 10 K margin", SUB,
         "minimum WEB/battery temperature held in survival")
R.define("sun_inc_worst_deg", "β_inc", 12.0, "deg", "ASSUMPTION",
         "A: 1.54 deg max solar elevation (L009) + 10 deg vehicle tilt toward sun on slopes", SUB,
         "worst-case solar incidence angle above radiator plane", low=2.0, high=20.0)
R.define("terrain_vf_rad", "F_terr", 0.10, "-", "ASSUMPTION", "A: zenith radiator near sloped terrain", SUB,
         "radiator view factor to sunlit terrain", low=0.0, high=0.25)
R.define("cp_battery", "c_p,bat", 1000.0, "J/(kg K)", "SOURCE", "L006 (Li-ion cells ~0.9-1.1 kJ/kgK, LITERATURE-RECALL)",
         SUB, "specific heat of Li-ion pack")
R.define("cp_al", "c_p,Al", 900.0, "J/(kg K)", "SOURCE", "L005", SUB, "specific heat aluminium")


@dataclass
class ThermalResult:
    a_rad: float
    q_env_abs: float
    heater_cold_w: float
    leak_cold_w: float
    survival_h: float
    cooldown_h: float


def radiator_area(q_int_w: float, t_rad: float | None = None, dusty: bool = True) -> tuple[float, float]:
    """Radiator area [m²] to reject ``q_int_w`` in the hot case; returns (area, absorbed env. flux W/m²)."""
    t_rad = R.v("T_rad_max") if t_rad is None else t_rad
    eps = R.v("rad_eps")
    alpha = R.v("rad_alpha_bol") * (R.v("rad_alpha_dust_factor") if dusty else 1.0)
    q_sun = alpha * SOLAR_CONST * math.sin(math.radians(R.v("sun_inc_worst_deg")))
    q_terr = eps * R.v("terrain_vf_rad") * SIGMA_SB * R.v("T_sunlit_rim_max") ** 4
    # zenith-facing radiator: deep-space background (~3 K) plus the terrain view handled by q_terr
    q_net = eps * SIGMA_SB * t_rad ** 4 - q_sun - q_terr
    if q_net <= 0:
        raise RuntimeError("radiator cannot reject heat at this temperature")
    return q_int_w / q_net, q_sun + q_terr


def cold_leak(a_mli: float, a_rad: float, t_in: float | None = None, t_sink: float | None = None,
              t_struct: float | None = None) -> float:
    t_in = R.v("T_web_survival") if t_in is None else t_in
    t_sink = R.v("T_psr") if t_sink is None else t_sink
    t_struct = t_sink + 60.0 if t_struct is None else t_struct
    q_mli = SIGMA_SB * R.v("mli_eps_eff") * a_mli * (t_in ** 4 - t_sink ** 4)
    q_rad = SIGMA_SB * R.v("rad_off_eps") * a_rad * (t_in ** 4 - t_sink ** 4)
    q_cond = R.v("web_cond_leak") * (t_in - t_struct)
    return q_mli + q_rad + q_cond


def survival(a_mli: float, a_rad: float, p_survival_elec: float, usable_kwh: float,
             web_heat_capacity_j_k: float, p_ops_internal: float = 0.0) -> ThermalResult:
    leak = cold_leak(a_mli, a_rad)
    heater = max(0.0, leak - p_survival_elec)
    total = p_survival_elec + heater
    t_surv = usable_kwh * 1000.0 / total
    # PSR excursion: time for WEB to cool from 293 K to T_survival with operating dissipation p_ops
    t_hi = 293.0
    q_leak_mean = cold_leak(a_mli, a_rad, t_in=0.5 * (t_hi + R.v("T_web_survival")))
    net = q_leak_mean - p_ops_internal
    cool = math.inf if net <= 0 else web_heat_capacity_j_k * (t_hi - R.v("T_web_survival")) / net / 3600.0
    a_r, q_env = radiator_area(1.0)
    return ThermalResult(a_rad, q_env, heater, leak, t_surv, cool)


def actuator_heater_power(n_actuators: int, area_each: float = 0.06, t_hold: float = 218.0,
                          t_sink: float | None = None, eps_cover: float | None = None) -> float:
    """Survival heater demand of external actuators held at ``t_hold`` (−55 °C AFT) under MLI covers."""
    t_sink = R.v("T_psr") if t_sink is None else t_sink
    eps_cover = 2 * R.v("mli_eps_eff") if eps_cover is None else eps_cover   # small blankets: 2x edge losses
    q_rad = SIGMA_SB * eps_cover * area_each * (t_hold ** 4 - t_sink ** 4)
    q_cond = 0.02 * (t_hold - (t_sink + 60.0))   # shaft/structure path ~0.02 W/K each (ESTIMATE)
    return n_actuators * (q_rad + max(q_cond, 0.0))
