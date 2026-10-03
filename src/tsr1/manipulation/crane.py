"""Cable-stayed luffing crane boom (LSMS-type, S015) as the heavy-lift alternative to a heavy arm.

Geometry (vertical plane): boom pivot at the origin on the deck; boom length L_b at luff angle α;
hoist line hangs from the boom tip; a luff cable runs from the boom tip to the top of a short
A-frame mast at (−d_m, H_m). Statics about the pivot give the luff-cable tension; the boom carries
the axial compression. The boom is sized for Euler buckling and stress; winches and the slew drive are
sized with the motorisation factor and the actuator torque-density MER (same as arms).

The crane lifts, lowers and slews payloads but cannot orient them or apply pushing forces; precise
placement requires the dexterous arm to guide the suspended load (cooperative mode).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import G_MOON
from tsr1.manipulation.arm import _act_mass

SUB = "manipulation"
R.define("vectran_line_mass", "μ_line", 0.030, "kg/m", "ESTIMATE",
         "L: 5-6 mm Vectran braid with abrasion jacket (LITERATURE-RECALL)", SUB,
         "linear mass of synthetic line", low=0.020, high=0.045)
R.define("vectran_break_per_kg_m", "B_line", 1.0e6, "N/(kg/m)", "ESTIMATE",
         "L: liquid-crystal-polymer fibre braid breaking strength per linear density (~1 GN/(kg/m) fibre; jacket "
         "and braid efficiency included)", SUB, "breaking load / linear mass", low=0.6e6, high=1.5e6)
R.define("line_fos", "FoS_line", 5.0, "-", "ASSUMPTION", "A: rope/line practice for lifting gear (5:1)", SUB,
         "breaking load / working load", low=4.0, high=8.0)


@dataclass
class CraneSpec:
    boom_length: float = 2.6
    payload: float = 150.0          # [kg] rated hook load
    mast_height: float = 0.9        # A-frame height above pivot [m]
    mast_offset: float = 0.3        # A-frame top behind pivot [m]
    alpha_min: float = math.radians(10)
    drum_radius: float = 0.04
    side_load_frac: float = 0.10    # side load at tip as fraction of hook weight (slew design)
    hook_block_mass: float = 2.0
    hoist_length: float = 4.0


@dataclass
class CraneResult:
    spec: CraneSpec
    max_reach: float
    t_luff: float
    boom_comp: float
    boom_od: float
    boom_t: float
    mass: float
    breakdown: dict
    power_hoist: float


def size_crane(spec: CraneSpec, g: float = G_MOON, hoist_speed: float = 0.02) -> CraneResult:
    E, rho = R.v("cfrp_E"), R.v("cfrp_rho")
    fos = R.v("fos_ult")
    mf = R.v("motorisation_factor")
    P = (spec.payload + spec.hook_block_mass) * g
    boom_mass = 4.0
    for _ in range(40):
        worst_T, worst_C = 0.0, 0.0
        for a in np.linspace(spec.alpha_min, math.radians(75), 30):
            tip = np.array([spec.boom_length * math.cos(a), spec.boom_length * math.sin(a)])
            top = np.array([-spec.mast_offset, spec.mast_height])
            u = (top - tip) / np.linalg.norm(top - tip)          # unit vector tip -> mast top
            # moment about pivot: P*x_tip + w_b*x_tip/2 = T * |tip × u|
            arm_T = abs(tip[0] * u[1] - tip[1] * u[0])
            m_grav = P * tip[0] + boom_mass * g * tip[0] / 2
            T = m_grav / arm_T
            # axial compression in boom = projection of (T*u + gravity loads) onto boom axis
            ax = tip / np.linalg.norm(tip)
            C = -np.dot(T * u + np.array([0, -P]), ax) + boom_mass * g * math.sin(a) / 2
            worst_T, worst_C = max(worst_T, T), max(worst_C, C)
        # boom: Euler buckling pinned-pinned with FoS, plus minimum gauge
        best = None
        for od in np.linspace(0.05, 0.12, 29):
            for t in np.linspace(R.v("t_min_cfrp"), 0.006, 10):
                if 2 * t >= od:
                    continue
                I = math.pi / 64 * (od ** 4 - (od - 2 * t) ** 4)
                A = math.pi / 4 * (od ** 2 - (od - 2 * t) ** 2)
                Pcr = math.pi ** 2 * E * I / spec.boom_length ** 2
                # side-load bending at root (slew/side load) — stress check
                M_side = spec.side_load_frac * P * spec.boom_length
                stress = worst_C / A + M_side * (od / 2) / I
                # lateral stiffness: tip deflection under side load <= 1 % of boom length
                defl = spec.side_load_frac * P * spec.boom_length ** 3 / (3 * E * I)
                if Pcr < fos * 2.0 * worst_C or stress > R.v("cfrp_allow") / fos or defl > 0.01 * spec.boom_length:
                    continue
                m = rho * A * spec.boom_length * (1 + R.v("fitting_frac"))
                if best is None or m < best[2]:
                    best = (od, t, m)
        new_boom = best[2]
        if abs(new_boom - boom_mass) < 1e-3:
            boom_mass = new_boom
            break
        boom_mass = new_boom
    od, t, _ = best
    mast_mass = 0.6 * boom_mass                   # A-frame: two shorter compression legs (ESTIMATE ratio)
    luff_winch = _act_mass(worst_T * spec.drum_radius * mf) + 1.0     # + drum/brake
    hoist_winch = _act_mass(P * spec.drum_radius * mf) + 1.0
    slew = _act_mass(spec.side_load_frac * P * spec.boom_length * mf)
    line_lin = max(R.v("vectran_line_mass"), worst_T * R.v("line_fos") / R.v("vectran_break_per_kg_m"))
    lines = line_lin * (spec.hoist_length + 2 * spec.boom_length)
    sheaves_fittings = 2.0
    turntable = 3.0                               # slew bearing + base fitting (ESTIMATE)
    bd = dict(boom=boom_mass, mast=mast_mass, luff_winch=luff_winch, hoist_winch=hoist_winch, slew=slew,
              lines=lines, sheaves_fittings=sheaves_fittings, turntable=turntable,
              hook_block=spec.hook_block_mass)
    mass = sum(bd.values())
    power = P * hoist_speed / R.v("act_eff")
    return CraneResult(spec, spec.boom_length * math.cos(spec.alpha_min), worst_T, worst_C, od, t, mass, bd,
                       power)
