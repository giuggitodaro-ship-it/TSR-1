"""Recovery / towing / winching physics in lunar gravity (directive §6B, §27).

Two recovery modes are compared:
  (1) direct towing — TSR-1 drives and pulls; capacity limited by its drawbar pull (mobility model);
  (2) stationary winching — TSR-1 is restrained by ground reaction and its winch pulls the target.

Ground-reaction elements (restraint of TSR-1 against the line pull):
  • braked wheels: Mohr–Coulomb shear of soil under the locked wheels, Σ(c·A) + N·tan φ
  • lowered skid/belly plate: adds cohesion area (body lowering via active suspension)
  • spades (artillery-trail / recovery-vehicle blade principle): Rankine passive earth pressure with
    a 3-D shape factor, integrated over the layered in-situ profile (S023)
  • helical anchors: plate-anchor breakout, Q = A_h (σ_v N_q* + c N_c*), installation torque via the
    Hoyt–Clemence torque factor

Target resistance:
  • free-rolling wheels: compaction resistance from the terramechanics model
  • locked wheels (fail-safe brakes engaged, no power): sliding shear Σ(c A + N tan φ) + bulldozing
  • embedded wheels at depth z: step-climb lower bound (F = N tan β, cos β = 1 − z/r) and Bekker
    compaction upper bound (R = k_eq b z^(n+1)/(n+1)), plus bulldozing passive term

Lunar soil unit weight is γ = ρ g with g = 1.62 m/s², i.e. one sixth of terrestrial — gravity-driven
anchor terms are small and cohesion-driven terms dominate at shallow depth.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import (G_MOON, Soil, insitu_profile, layer_at, overburden_stress, soil_nominal)
from tsr1.mobility.terramechanics import Wheel, solve

SUB = "recovery"
R.define("spade_shape_factor", "S_3D", 1.3, "-", "ESTIMATE", "L025 (Das, Earth Anchors; 3-D plate effect, LITERATURE-RECALL)",
         SUB, "passive resistance enhancement of finite-width plate vs plane strain", low=1.0, high=1.8)
R.define("helix_Nq", "N_q*", 20.0, "-", "ESTIMATE", "L025 (breakout factor for phi 45-54 deg, H/D 4-5)", SUB,
         "plate-anchor breakout factor", low=10.0, high=40.0)
R.define("helix_Kt", "K_t", 33.0, "1/m", "SOURCE", "L026 (Hoyt & Clemence 1989, LITERATURE-RECALL)", SUB,
         "capacity-to-installation-torque factor", low=20.0, high=50.0)
R.define("winch_eff", "η_w", 0.65, "-", "ASSUMPTION", "A-17 (motor x gear x drum/level-wind)", SUB,
         "winch electrical-to-line efficiency", low=0.5, high=0.75)
R.define("recovery_fos", "FoS_rec", 1.5, "-", "DESIGN", "TS-05", SUB,
         "required ratio restraint capacity / line pull for planned recovery", low=1.25, high=2.0)


def kp(phi: float) -> float:
    return math.tan(math.pi / 4 + phi / 2) ** 2


# ------------------------------------------------------------------------------------- restraint
def spade_capacity(width: float, depth: float, strength_factor: float = 1.0, shape: float | None = None,
                   g: float = G_MOON, nz: int = 60) -> float:
    """Horizontal passive capacity [N] of a vertical spade plate of ``width`` × ``depth``."""
    shape = R.v("spade_shape_factor") if shape is None else shape
    prof = insitu_profile(strength_factor)
    zs = np.linspace(0.0, depth, nz)
    pp = []
    for z in zs:
        lay = layer_at(min(z, depth - 1e-9), prof)
        K = kp(lay.phi)
        pp.append(overburden_stress(z, prof, g) * K + 2 * lay.c * math.sqrt(K))
    return float(np.trapezoid(pp, zs) * width * shape)


def spade_insertion_force(width: float, depth: float, edge_thk: float = 0.008, strength_factor: float = 1.0,
                          g: float = G_MOON) -> float:
    """Vertical force [N] to push a spade to ``depth``: tip bearing + two-face adhesion/friction.
    Tip bearing uses q = c N_c + σ_v N_q with N_q = e^{π tanφ} tan²(45+φ/2), N_c = (N_q − 1) cot φ."""
    prof = insitu_profile(strength_factor)
    lay = layer_at(depth - 1e-9, prof)
    Nq = math.exp(math.pi * math.tan(lay.phi)) * kp(lay.phi)
    Nc = (Nq - 1) / math.tan(lay.phi)
    q = lay.c * Nc + overburden_stress(depth, prof, g) * Nq
    tip = q * edge_thk * width
    # side friction (at-rest K0 = 1 − sin φ) + adhesion on both faces, depth-averaged
    zs = np.linspace(0, depth, 30)
    side = 0.0
    for z0, z1 in zip(zs[:-1], zs[1:]):
        l2 = layer_at(0.5 * (z0 + z1), prof)
        sv = overburden_stress(0.5 * (z0 + z1), prof, g)
        side += 2 * width * (z1 - z0) * (l2.c * 0.5 + sv * (1 - math.sin(l2.phi)) * math.tan(2 / 3 * l2.phi))
    return tip + side


def helical_anchor_capacity(d_helix: float, depth_v: float, strength_factor: float = 1.0,
                            nq: float | None = None, g: float = G_MOON) -> float:
    """Axial pull-out capacity [N] of a single-helix anchor with vertical embedment ``depth_v``."""
    nq = R.v("helix_Nq") if nq is None else nq
    prof = insitu_profile(strength_factor)
    lay = layer_at(depth_v - 1e-9, prof)
    nc = min(1.2 * depth_v / d_helix + 2.0, 9.0)
    A = math.pi * d_helix ** 2 / 4
    return A * (overburden_stress(depth_v, prof, g) * nq + lay.c * nc)


def helical_install_torque(capacity: float) -> float:
    return capacity / R.v("helix_Kt")


@dataclass
class Restraint:
    label: str
    braked_wheels: bool = True
    skid_area: float = 0.0          # lowered belly/skid contact area [m^2]
    skid_load_frac: float = 0.0     # fraction of weight transferred to skid
    n_spades: int = 0
    spade_w: float = 0.6
    spade_d: float = 0.30
    n_anchors: int = 0
    helix_d: float = 0.15
    anchor_depth: float = 0.6


def restraint_capacity(mass_tsr: float, slope: float, cfg: Restraint, soil: Soil, wheel: Wheel, n_wheels: int,
                       strength_factor: float = 1.0, g: float = G_MOON) -> float:
    """Net horizontal (along-slope, downhill-directed line) resistance [N] available to TSR-1 parked
    upslope of the target: shear + passive + anchors − own downslope weight component."""
    W = mass_tsr * g
    Wn = W * math.cos(slope)
    cap = 0.0
    if cfg.braked_wheels:
        n_wheel = Wn * (1 - cfg.skid_load_frac) / n_wheels
        st = solve(wheel, soil, max(n_wheel, 1.0), 0.05)
        A = wheel.width * st.contact_len * n_wheels
        # locked grousered wheel shears soil at the grouser tips: Mohr-Coulomb with soil φ
        cap += soil.c * A + Wn * (1 - cfg.skid_load_frac) * math.tan(soil.phi)
    if cfg.skid_area > 0:
        cap += soil.c * cfg.skid_area + Wn * cfg.skid_load_frac * math.tan(2 / 3 * soil.phi)
    if cfg.n_spades:
        cap += cfg.n_spades * spade_capacity(cfg.spade_w, cfg.spade_d, strength_factor)
    if cfg.n_anchors:
        cap += cfg.n_anchors * helical_anchor_capacity(cfg.helix_d, cfg.anchor_depth, strength_factor)
    return cap - W * math.sin(slope)


# ------------------------------------------------------------------------------------- targets
@dataclass
class Target:
    label: str
    mass: float
    n_wheels: int = 4
    wheel: Wheel = field(default_factory=lambda: Wheel(0.25, 0.20, 0.01))
    brakes_locked: bool = False
    sinkage: float = 0.0            # embedding depth of all wheels [m]
    belly_drag: float = 0.0         # additional drag if high-centred [N]


def target_resistance(t: Target, slope: float, soil: Soil | None = None, bound: str = "mid",
                      g: float = G_MOON) -> float:
    """Along-slope force [N] needed to move target ``t`` uphill at quasi-static speed."""
    soil = soil_nominal() if soil is None else soil
    W = t.mass * g
    Wn = W * math.cos(slope)
    Nw = Wn / t.n_wheels
    st = solve(t.wheel, soil, Nw, 0.02)
    if t.brakes_locked:
        A = t.wheel.width * st.contact_len * t.n_wheels
        res = soil.c * A + Wn * math.tan(soil.phi)
    else:
        res = st.resistance * t.n_wheels
    if t.sinkage > 0:
        r = t.wheel.radius
        z = min(t.sinkage, 0.95 * r)
        tan_beta = math.sqrt(2 * r * z - z * z) / (r - z) if z < r else 10.0
        lower = Nw * tan_beta * t.n_wheels                      # rigid-edge step climb
        keq = soil.kc / t.wheel.width + soil.kphi
        upper = keq * t.wheel.width * z ** (soil.n + 1) / (soil.n + 1) * t.n_wheels   # Bekker compaction
        K = kp(soil.phi)
        gamma = 1500.0 * g
        bulldoze = t.wheel.width * (0.5 * gamma * z * z * K + 2 * soil.c * z * math.sqrt(K)) * t.n_wheels
        emb = {"low": lower, "mid": math.sqrt(lower * upper), "high": upper}[bound] + bulldoze
        res = max(res, emb)
    return W * math.sin(slope) + res + t.belly_drag


def max_recoverable_mass(capacity_net: float, slope: float, f_coeff: float, g: float = G_MOON,
                         fos: float | None = None) -> float:
    """Largest target mass for a given net restraint and target resistance coefficient f (= R/(W cosθ))."""
    fos = R.v("recovery_fos") if fos is None else fos
    denom = g * (math.sin(slope) + f_coeff * math.cos(slope))
    return max(capacity_net / fos, 0.0) / denom


def target_coeff(t: Target, soil: Soil | None = None, bound: str = "mid") -> float:
    """Resistance coefficient f = (F_required on level ground) / W."""
    return target_resistance(t, 0.0, soil, bound) / (t.mass * G_MOON)


@dataclass
class WinchSizing:
    line_pull: float
    line_speed: float
    power_elec: float
    drum_torque: float
    mass: float
    line_mass: float


def size_winch(line_pull: float, line_length: float, line_speed: float = 0.05, drum_r: float = 0.06) -> WinchSizing:
    from tsr1.manipulation.arm import _act_mass
    from tsr1.manipulation.crane import R as _R  # noqa: F401  (ensures line params registered)
    mf = R.v("motorisation_factor")
    lin = max(R.v("vectran_line_mass"), line_pull * R.v("line_fos") / R.v("vectran_break_per_kg_m"))
    line_mass = lin * line_length
    drum_torque = line_pull * drum_r
    drive = _act_mass(drum_torque * mf)
    structure = 4.0 + 0.02 * line_length       # drum, level-wind, fairlead, frame, load cell (ESTIMATE)
    mass = drive + structure + line_mass
    power = line_pull * line_speed / R.v("winch_eff")
    return WinchSizing(line_pull, line_speed, power, drum_torque, mass, line_mass)
