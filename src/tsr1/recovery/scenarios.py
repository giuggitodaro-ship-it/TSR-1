"""Quantitative recovery scenarios A–D (directive §27).

For each scenario: required along-slope force, chosen method (direct tow vs anchored winch), winch line
tension, restraint/anchor reaction, TSR-1 wheel traction use, drive-motor torque, energy, thermal load,
structural load at hard points and factor of safety, plus feasibility verdict.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import G_MOON, soil_nominal
from tsr1.mobility.terramechanics import Wheel
from tsr1.mobility.vehicle import drive_state, max_tow_force
from tsr1.recovery.towing import (Restraint, Target, helical_anchor_capacity, restraint_capacity,
                                  spade_capacity, target_resistance)
import tsr1.stability.envelope  # noqa: F401
from tsr1.trades.recovery_trades import tipping_limited_pull


@dataclass
class ScenarioSpec:
    id: str
    title: str
    target: Target
    slope_deg: float
    move_m: float
    bound: str = "mid"


SCENARIOS = [
    ScenarioSpec("A", "Disabled 300 kg science rover on flat regolith (brakes released), tow 100 m",
                 Target("A", 300.0), 0.0, 100.0),
    ScenarioSpec("B", "Disabled 450 kg rover on 15° slope (brakes released), winch 30 m upslope",
                 Target("B", 450.0), 15.0, 30.0),
    ScenarioSpec("B2", "As B but fail-safe brakes locked (no release)", Target("B2", 450.0, brakes_locked=True),
                 15.0, 30.0),
    ScenarioSpec("C", "450 kg rover with all wheels embedded 0.15 m on flat (mid estimate)",
                 Target("C", 450.0, sinkage=0.15), 0.0, 5.0, "mid"),
    ScenarioSpec("C-hi", "As C, upper-bound (Bekker compaction) extraction resistance",
                 Target("C", 450.0, sinkage=0.15), 0.0, 5.0, "high"),
    ScenarioSpec("C-dig", "As C after excavating ramps to 0.05 m effective sinkage (scoop tool) + upper bound",
                 Target("C", 450.0, sinkage=0.05), 0.0, 5.0, "high"),
    ScenarioSpec("D", "1.5 t LTV-class vehicle (free-rolling) repositioned 200 m on flat",
                 Target("D", 1500.0, wheel=Wheel(0.40, 0.25, 0.01)), 0.0, 200.0),
    ScenarioSpec("D2", "1.5 t LTV-class vehicle on 10° slope, winch 30 m",
                 Target("D", 1500.0, wheel=Wheel(0.40, 0.25, 0.01)), 10.0, 30.0),
    ScenarioSpec("D3", "1.0 t infrastructure element on skids (sliding), drag 20 m on flat",
                 Target("D3", 1000.0, brakes_locked=True, wheel=Wheel(0.6, 0.6, 0.0)), 0.0, 20.0),
]


def analyse(cfg) -> list[dict]:
    soil = soil_nominal()
    veh = cfg.vehicle
    fos = R.v("recovery_fos")
    winch = cfg.opts.winch_pull_kN * 1e3
    rc = Restraint("baseline", n_spades=cfg.opts.n_spades, n_anchors=cfg.opts.n_anchors)
    q = helical_anchor_capacity(0.15, 0.6)
    out = []
    for sc in SCENARIOS:
        th = math.radians(sc.slope_deg)
        F = target_resistance(sc.target, th, soil, sc.bound)
        tow_cap = max_tow_force(veh, soil, th)
        row = dict(id=sc.id, title=sc.title, target_mass_kg=sc.target.mass, slope_deg=sc.slope_deg,
                   required_force_N=F, direct_tow_capacity_N=tow_cap)
        if F * fos <= tow_cap:
            ds = drive_state(veh, soil, th, F)
            omega_t = ds.torque_total / veh.n_wheels
            v = 0.2
            p_mech = ds.torque_total * v / (veh.wheel.r_shear * (1 - ds.slip))
            p_el = p_mech / veh.drive_eff
            t_s = sc.move_m / v
            row.update(method="direct tow (drive)", line_tension_N=0.0, restraint_reaction_N=0.0,
                       wheel_slip=ds.slip, drive_torque_per_wheel_Nm=omega_t,
                       drive_power_W=p_el, energy_Wh=p_el * t_s / 3600, heat_W=p_el * (1 - veh.drive_eff),
                       hardpoint_load_N=F, margin=tow_cap / F, feasible=True)
        else:
            cap = restraint_capacity(veh.mass, th, rc, soil, veh.wheel, veh.n_wheels)
            tip = tipping_limited_pull(veh.mass, R.v("fairlead_height"), cfg.opts.wheelbase / 2 + 0.15,
                                       rc.n_anchors, cfg.opts.wheelbase / 2 + 0.1, q,
                                       R.v("anchor_strap_angle_deg"), R.v("tip_factor_req"))
            limit = min(cap / fos, winch, tip)
            v = 0.05
            p_el = F * v / R.v("winch_eff")
            t_s = sc.move_m / v
            feas = F <= limit
            row.update(method="anchored winch (braked wheels + spades + helical anchors)", line_tension_N=F,
                       restraint_reaction_N=F, restraint_capacity_N=cap, tipping_limit_N=tip, winch_rating_N=winch,
                       spade_share_N=min(F, cfg.opts.n_spades * spade_capacity(0.6, 0.3)),
                       anchor_share_N=max(0.0, F - cfg.opts.n_spades * spade_capacity(0.6, 0.3)),
                       drive_power_W=0.0, winch_power_W=p_el, energy_Wh=p_el * t_s / 3600,
                       heat_W=p_el * (1 - R.v("winch_eff")), hardpoint_load_N=F * R.v("fos_ult"),
                       margin=limit / F if F > 0 else float("inf"), feasible=bool(feas))
        out.append(row)
    return out
