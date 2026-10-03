"""TS-04 stabilisation and TS-05 recovery architecture trades (directive §6B, §11, §27).

Uses the recovery physics (restraint capacity, target resistance), the mobility model (direct towing)
and the stability model (tipping under line pull). The *recovery envelope probability* p_env is the
fraction of sampled immobilisation cases (target mass, slope, embedding depth, brake state) that a given
architecture can recover with the required factor of safety, within the winch rating, and without
tipping. p_env feeds the value model.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import G_MOON, soil_nominal
from tsr1.mobility.terramechanics import Wheel
from tsr1.mobility.vehicle import Vehicle, max_tow_force
from tsr1.recovery.towing import (Restraint, Target, helical_anchor_capacity, max_recoverable_mass,
                                  restraint_capacity, spade_capacity, target_resistance)
import tsr1.stability.envelope  # noqa: F401  (registers fairlead/strap/tip-factor design parameters)

SUB = "recovery"
R.define("p_brake_release", "p_br", 0.7, "-", "ASSUMPTION",
         "A: probability TSR-1 can release a disabled vehicle's fail-safe brakes (emergency power to brake "
         "solenoids or manual release on L1+ assets)", SUB, "", low=0.4, high=0.9)

RESTRAINTS = {
    "R0 direct towing (drive)": None,
    "R1 winch + braked wheels": Restraint("braked"),
    "R2 winch + braked wheels + lowered skid": Restraint("skid", skid_area=1.4, skid_load_frac=0.5),
    "R3 winch + braked wheels + 2 rear spades": Restraint("spades", n_spades=2),
    "R4 winch + 2 spades + 2 helical anchors": Restraint("spades+2a", n_spades=2, n_anchors=2),
    "R5 winch + 2 spades + 4 helical anchors": Restraint("spades+4a", n_spades=2, n_anchors=4),
}
RESTRAINT_MASS = {   # added hardware CBE beyond winch [kg] (from configuration component estimates)
    "R0 direct towing (drive)": 3.0, "R1 winch + braked wheels": 0.0, "R2 winch + braked wheels + lowered skid": 9.4,
    "R3 winch + braked wheels + 2 rear spades": 17.6, "R4 winch + 2 spades + 2 helical anchors": 25.6,
    "R5 winch + 2 spades + 4 helical anchors": 29.6,
}


def tipping_limited_pull(mass_tsr: float, h_fl: float, x_restore: float, n_anchors: int, x_front: float,
                         anchor_q: float, strap_deg: float, tf_req: float) -> float:
    """Maximum line pull [N] with tipping factor ≥ tf_req about the rear restraint line.
    Restoring: weight × x_restore + anchor hold-down (vertical strap component × lever)."""
    W = mass_tsr * G_MOON
    hold = n_anchors * anchor_q * 0.8 * math.sin(math.radians(strap_deg)) * (x_front + x_restore)
    lever = h_fl + 0.15      # spade reaction centroid ≈ 0.15 m below ground
    return (W * x_restore + hold) / (tf_req * lever)


def sample_cases(n: int, rng: np.random.Generator) -> list[dict]:
    cases = []
    for _ in range(n):
        if rng.random() < 0.7:
            m = math.exp(rng.uniform(math.log(50), math.log(500)))
            wheel = Wheel(0.25, 0.20, 0.01)
        else:
            m = rng.uniform(1000, 2500)
            wheel = Wheel(0.40, 0.25, 0.01)
        slope = math.radians(rng.uniform(0, 20))
        u = rng.random()
        z = 0.0 if u < 0.4 else (rng.uniform(0.02, 0.10) if u < 0.8 else rng.uniform(0.10, 0.20))
        locked = rng.random() < 0.5 and rng.random() > R.v("p_brake_release")
        cases.append(dict(mass=m, wheel=wheel, slope=slope, sinkage=z, locked=locked))
    return cases


def envelope_probability(cfg, restraint_key: str, cases: list[dict], winch_kN: float | None = None,
                         bound: str = "mid", strength_factor: float = 1.0) -> float:
    soil = soil_nominal()
    veh = cfg.vehicle
    winch = cfg.opts.winch_pull_kN * 1e3 if winch_kN is None else winch_kN * 1e3
    fos = R.v("recovery_fos")
    ok = 0
    rcfg = RESTRAINTS[restraint_key]
    q = helical_anchor_capacity(0.15, 0.6, strength_factor)
    if rcfg is None:   # tabulate direct-tow capacity vs slope once (expensive), then interpolate
        grid = np.radians(np.arange(0.0, 21.0, 1.0))
        tow = np.array([max_tow_force(veh, soil, th) for th in grid])
    for c in cases:
        t = Target("case", c["mass"], wheel=c["wheel"], brakes_locked=c["locked"], sinkage=c["sinkage"])
        need = target_resistance(t, c["slope"], soil, bound)
        if rcfg is None:
            avail = float(np.interp(c["slope"], grid, tow)) / fos
        else:
            cap = restraint_capacity(veh.mass, c["slope"], rcfg, soil, veh.wheel, veh.n_wheels, strength_factor)
            tip = tipping_limited_pull(veh.mass, R.v("fairlead_height"), cfg.opts.wheelbase / 2 + 0.15,
                                       rcfg.n_anchors, cfg.opts.wheelbase / 2 + 0.1, q,
                                       R.v("anchor_strap_angle_deg"), R.v("tip_factor_req"))
            avail = min(cap / fos, winch, tip)
        ok += need <= avail
    return ok / len(cases)


def recovery_curves(cfg, slopes_deg=None, strength_factor: float = 1.0) -> dict:
    """Max recoverable mass vs slope for each restraint, target free-rolling / brakes locked."""
    soil = soil_nominal()
    veh = cfg.vehicle
    slopes_deg = np.arange(0, 26, 2.5) if slopes_deg is None else slopes_deg
    f_free = target_resistance(Target("f", 450.0), 0.0, soil) / (450.0 * G_MOON)
    f_lock = target_resistance(Target("l", 450.0, brakes_locked=True), 0.0, soil) / (450.0 * G_MOON)
    q = helical_anchor_capacity(0.15, 0.6, strength_factor)
    out = {}
    for key, rc in RESTRAINTS.items():
        free, lock = [], []
        for d in slopes_deg:
            th = math.radians(d)
            if rc is None:
                cap = max_tow_force(veh, soil, th)
                cap_net = cap
            else:
                cap = restraint_capacity(veh.mass, th, rc, soil, veh.wheel, veh.n_wheels, strength_factor)
                tip = tipping_limited_pull(veh.mass, R.v("fairlead_height"), cfg.opts.wheelbase / 2 + 0.15,
                                           rc.n_anchors, cfg.opts.wheelbase / 2 + 0.1, q,
                                           R.v("anchor_strap_angle_deg"), R.v("tip_factor_req"))
                cap_net = min(cap, cfg.opts.winch_pull_kN * 1e3 * R.v("recovery_fos"),
                              tip * R.v("recovery_fos"))
            free.append(max_recoverable_mass(cap_net, th, f_free))
            lock.append(max_recoverable_mass(cap_net, th, f_lock))
        out[key] = dict(slopes=list(map(float, slopes_deg)), free_kg=free, locked_kg=lock)
    return dict(curves=out, f_free=f_free, f_locked=f_lock)


def stabilisation_options(cfg) -> list[dict]:
    """TS-04: crane side-lift stability capacity and winch line-pull limit for stabilisation options."""
    from tsr1.stability.envelope import crane_capacity_curve
    W = cfg.vehicle.mass * G_MOON
    soil = soil_nominal()
    rows = []
    base = crane_capacity_curve(cfg, reaches=[cfg.derived["crane"].max_reach], slope_y=math.radians(-15))[0, 1]
    # body lowering: CoM lowered by ground-clearance reduction (0.45 -> 0.10 m)
    low_cfg_h = 0.35
    q = helical_anchor_capacity(0.15, 0.6)
    opts = [
        ("S0 locked wheels only", 0.0, 0.0, 0, 0, 0.0),
        ("S1 body lowering (skid on ground)", low_cfg_h, 0.0, 0, 0, 0.0),
        ("S2 deployable lateral outriggers (±0.8 m)", 0.0, 0.8, 0, 0, 24.0),
        ("S3 rear spades", 0.0, 0.0, 2, 0, 17.6),
        ("S4 rear spades + 2 helical anchors", 0.0, 0.0, 2, 2, 25.6),
        ("S5 body lowering + spades + 2 anchors", low_cfg_h, 0.0, 2, 2, 25.6),
    ]
    for name, dz, dy, nsp, nan, madd in opts:
        # crane side-lift stability capacity scales with restoring lever (track/2 + dy) and with lower CoM (slope)
        h = cfg.com()[2] - dz
        lever0 = cfg.opts.track / 2 - (cfg.com()[2]) * math.tan(math.radians(15))
        lever = cfg.opts.track / 2 + dy - h * math.tan(math.radians(15))
        side_cap = base * (lever / lever0) if lever0 > 0 else float("nan")
        cap_slide = soil.c * 0.3 + W * math.tan(soil.phi) + nsp * spade_capacity(0.6, 0.3) + nan * q
        tip = tipping_limited_pull(cfg.vehicle.mass, R.v("fairlead_height"), cfg.opts.wheelbase / 2 + 0.15, nan,
                                   cfg.opts.wheelbase / 2 + 0.1, q, R.v("anchor_strap_angle_deg"),
                                   R.v("tip_factor_req"))
        rows.append(dict(option=name, added_mass_kg=madd, crane_side_capacity_15deg_kg=side_cap,
                         winch_pull_limit_kN=min(cap_slide / R.v("recovery_fos"), tip) / 1e3,
                         deploy_time_min={0: 1, 1: 5}.get(int(dz > 0), 5) + 10 * (dy > 0) + 8 * nsp + 25 * nan))
    return rows
