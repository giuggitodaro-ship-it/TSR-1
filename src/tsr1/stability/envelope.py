"""Configuration-level stability cases and manipulation envelope (directive §11, §26).

Uses the configuration's component positions (predicted masses) to compute CoM for each operating
configuration and evaluates tip-over (centre-of-pressure margin, tipping factor) and sliding.

A key lunar-specific result: TSR-1's weight is only ~1.75 kN, so winch line pulls of several kN can
pitch the vehicle over unless the fairlead is low and the vehicle is held down by anchors. The
winching case therefore includes front hold-down straps to helical anchors and rear spades.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import G_MOON, soil_nominal
from tsr1.recovery.towing import helical_anchor_capacity, spade_capacity
from tsr1.stability.static_stability import Load, evaluate, gravity_vector, weight

SUB = "stability"
R.define("tip_factor_req", "TF_req", 1.5, "-", "DESIGN", "TS-04 (static tipping safety factor)", SUB,
         "minimum restoring/overturning moment ratio for planned operations")
R.define("fairlead_height", "h_fl", 0.25, "m", "DESIGN", "TS-05 (pitch stability under line pull)", SUB,
         "winch fairlead height above ground")
R.define("anchor_strap_angle_deg", "ε_strap", 35.0, "deg", "DESIGN", "TS-05", SUB,
         "front hold-down strap angle below horizontal (toward anchors)")


@dataclass
class CaseResult:
    case: str
    com: tuple
    margin_m: float
    tip_factor: float
    sliding_ok: bool
    note: str = ""


def wheel_contacts(cfg) -> np.ndarray:
    pts = []
    for x in cfg.vehicle.axle_x:
        for s in (1, -1):
            pts.append((x, s * cfg.opts.track / 2))
    return np.array(pts)


def _vehicle_loads(cfg, th_x=0.0, th_y=0.0, overrides=None, exclude=(), extra=()):
    """Loads from all components (predicted mass) + system margin + carried payload."""
    loads = []
    overrides = overrides or {}
    tot = 0.0
    mom = np.zeros(3)
    for c in cfg.comps:
        if c.name in exclude:
            continue
        p = np.asarray(overrides.get(c.name, c.pos), float)
        m = c.predicted * c.qty
        loads.append(weight(m, p, th_x, th_y, c.name))
        tot += m
        mom += m * p
    sm = cfg.predicted() * R.v("system_margin")
    loads.append(weight(sm, mom / tot, th_x, th_y, "system_margin"))
    loads.append(weight(cfg.opts.payload_carried, cfg.derived["spine_payload_pos"], th_x, th_y, "payload"))
    loads += list(extra)
    return loads


def crane_tip(cfg, azimuth_deg: float, reach: float | None = None):
    base = np.array([0.3, 0.0, 1.05])
    reach = cfg.derived["crane"].max_reach if reach is None else reach
    a = math.radians(azimuth_deg)
    tip = base + np.array([reach * math.cos(a), reach * math.sin(a), 0.4])
    boom_mid = 0.5 * (base + tip)
    return base, tip, boom_mid


def case_results(cfg) -> list[CaseResult]:
    out = []
    sup = wheel_contacts(cfg)
    tfr = R.v("tip_factor_req")
    soil = soil_nominal()

    def run(name, loads, support=sup, slide_cap=None, note=""):
        res = evaluate(loads, support)
        ok = True if slide_cap is None else res.f_horizontal <= slide_cap
        F = np.sum([l.force for l in loads], axis=0)
        M = np.sum([l.force for l in loads if "system_margin" != l.label], axis=0)
        com = cfg.com()
        out.append(CaseResult(name, tuple(np.round(com, 3)), res.margin, res.tip_factor, ok, note))
        return res

    # C1: stowed, level and slopes
    run("C1 stowed, level", _vehicle_loads(cfg))
    for deg in (20, 25):
        run(f"C1 stowed, {deg}° longitudinal", _vehicle_loads(cfg, th_x=math.radians(deg)))
        run(f"C1 stowed, {deg}° lateral", _vehicle_loads(cfg, th_y=math.radians(deg)))
    # C2: crane side lift at max reach with rated payload, level and 10° lateral (load downhill side)
    crane = cfg.derived.get("crane")
    if crane is not None:
        P = cfg.opts.heavy_payload
        # load at +y (left); "load downhill" means left side down, i.e. θy < 0
        for th_y, lab in ((0.0, "level"), (math.radians(-10), "10° lateral, load downhill")):
            base, tip, mid = crane_tip(cfg, 90.0)
            ov = {"crane_boom": tuple(mid)}
            extra = [weight(P + crane.spec.hook_block_mass, (tip[0], tip[1], 0.3), 0.0, th_y, "crane_payload")]
            run(f"C2 crane side lift {P:.0f} kg @ {crane.max_reach:.2f} m, {lab}",
                _vehicle_loads(cfg, 0.0, th_y, ov, exclude=(), extra=extra))
        base, tip, mid = crane_tip(cfg, 0.0)
        extra = [weight(P + crane.spec.hook_block_mass, (tip[0], tip[1], 0.3), 0.0, 0.0, "crane_payload")]
        run(f"C3 crane front lift {P:.0f} kg", _vehicle_loads(cfg, overrides={"crane_boom": tuple(mid)}, extra=extra))
    # C4: dexterous arm extended forward-side with rated payload + crane extended side (both)
    dex = cfg.derived["dex"]
    xa = cfg.opts.wheelbase / 2 - 0.15
    arm_tip = (xa + dex.reach * 0.7, -0.45 - dex.reach * 0.7, 0.8)
    extra = [weight(cfg.opts.dex_payload, arm_tip, label="dex_payload")]
    run("C4 dexterous arm extended (front-right) with rated payload",
        _vehicle_loads(cfg, overrides={"dexterous_arm": ((xa + arm_tip[0]) / 2, (-0.45 + arm_tip[1]) / 2, 0.95)},
                       extra=extra))
    if crane is not None:
        base, tip, mid = crane_tip(cfg, -90.0)
        extra2 = extra + [weight(cfg.opts.heavy_payload + 2.0, (tip[0], tip[1], 0.3), label="crane_payload")]
        run("C5 both extended same side (worst)", _vehicle_loads(
            cfg, overrides={"dexterous_arm": ((xa + arm_tip[0]) / 2, (-0.45 + arm_tip[1]) / 2, 0.95),
                            "crane_boom": tuple(mid)}, extra=extra2))
    # C6: towing on 10° slope (drawbar force at rear hitch, height 0.3 m)
    W = cfg.operational_mass * G_MOON
    f_tow = 200.0
    extra = [Load(np.array([-f_tow, 0, 0]), np.array([-cfg.opts.wheelbase / 2 - 0.3, 0, 0.3]), "tow")]
    run("C6 towing 200 N on 10° slope", _vehicle_loads(cfg, th_x=math.radians(10), extra=extra))
    # C7: winching at rated pull, fairlead low, with and without front hold-down anchors
    if cfg.opts.recovery:
        F = cfg.opts.winch_pull_kN * 1e3
        h = R.v("fairlead_height")
        x_fl = -cfg.opts.wheelbase / 2 - 0.1
        line = Load(np.array([-F, 0, 0]), np.array([x_fl, 0, h]), "winch_line")
        # spade passive reaction acts below ground: model as support point region extension
        sup_sp = np.vstack([sup, [[-cfg.opts.wheelbase / 2 - 0.15, 0.5], [-cfg.opts.wheelbase / 2 - 0.15, -0.5]]])
        cap = (R.v("soil_c") * 0.2 + W * math.tan(soil.phi)) + cfg.opts.n_spades * spade_capacity(0.6, 0.3)
        r1 = run(f"C7a winch {F/1e3:.1f} kN, fairlead {h:.2f} m, spades only", _vehicle_loads(cfg, extra=[line]),
                 support=sup_sp, slide_cap=cap)
        # front hold-down straps to helical anchors (axial capacity Q each, strap angle ε below horizontal)
        Q = helical_anchor_capacity(0.15, 0.6)
        eps = math.radians(R.v("anchor_strap_angle_deg"))
        straps = [Load(np.array([Q * math.cos(eps) * 0.8, 0.0, -Q * math.sin(eps) * 0.8]),
                       np.array([cfg.opts.wheelbase / 2 + 0.1, s * 0.6, 0.35]), "anchor_strap")
                  for s in (1, -1)[: cfg.opts.n_anchors]]
        run(f"C7b winch {F/1e3:.1f} kN + spades + {cfg.opts.n_anchors} front hold-down anchors (80 % preload)",
            _vehicle_loads(cfg, extra=[line] + straps), support=sup_sp, slide_cap=cap + cfg.opts.n_anchors * Q)
        # high fairlead (rejected design) for comparison
        line_hi = Load(np.array([-F, 0, 0]), np.array([x_fl, 0, 0.6]), "winch_line_high")
        run(f"C7c winch {F/1e3:.1f} kN, fairlead 0.60 m, spades only (rejected)",
            _vehicle_loads(cfg, extra=[line_hi]), support=sup_sp, slide_cap=cap)
    return out


def static_tip_angles(cfg) -> tuple[float, float]:
    """Static tip-over slope angles (deg), longitudinal and lateral, stowed."""
    com = cfg.com()
    xs = [x for x in cfg.vehicle.axle_x]
    lon = math.degrees(math.atan(min(max(xs) - com[0], com[0] - min(xs)) / com[2]))
    lat = math.degrees(math.atan((cfg.opts.track / 2 - abs(com[1])) / com[2]))
    return lon, lat


def crane_capacity_curve(cfg, reaches=None, azimuth_deg=90.0, slope_y=0.0):
    """Max hook load [kg] vs reach limited by tipping factor requirement (stability-only)."""
    reaches = np.linspace(0.5, 2.6, 15) if reaches is None else reaches
    tfr = R.v("tip_factor_req")
    sup = wheel_contacts(cfg)
    out = []
    for rch in reaches:
        lo, hi = 0.0, 3000.0
        for _ in range(30):
            mid_m = 0.5 * (lo + hi)
            base, tip, mid = crane_tip(cfg, azimuth_deg, rch)
            extra = [weight(mid_m, (tip[0], tip[1], 0.3), 0.0, slope_y, "hook")]
            res = evaluate(_vehicle_loads(cfg, 0.0, slope_y, {"crane_boom": tuple(mid)}, extra=extra), sup)
            if res.tip_factor >= tfr and res.margin > 0:
                lo = mid_m
            else:
                hi = mid_m
        out.append((rch, lo))
    return np.array(out)
