"""Serial-manipulator sizing in lunar gravity (directive §6A, §12).

A planar worst-case model is used: the arm fully extended horizontally with the payload at the tip
maximises gravity torque at every pitch joint. Link tubes are sized for (i) tip deflection under the
payload and (ii) bending stress with the structural factor of safety; pitch actuators are sized for the
gravity torque × motorisation factor; actuator mass follows a torque-density MER. Because link and
actuator masses feed back into joint torques, the sizing is iterated to a fixed point.

Outputs per arm: link dimensions, joint torques, actuator and link masses, total mass, reaction
force/moment at the base, power for a reference joint speed, and first-mode stiffness indicator.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import G_MOON

SUB = "manipulation"

R.define("motorisation_factor", "MF", 2.0, "-", "SOURCE", "L024 (ECSS-E-ST-33-01C, LITERATURE-RECALL); A-22", SUB,
         "actuator torque capability / required resistive torque", low=1.5, high=3.0)
R.define("act_torque_density", "τ_ρ", 25.0, "N m/kg", "ESTIMATE",
         "A: space-rated strain-wave actuator units incl. motor, brake, encoder, housing, heater", SUB,
         "peak output torque per unit actuator mass; terrestrial robot joints 30-80 N m/kg", low=15.0, high=40.0)
R.define("act_min_mass", "m_act,min", 1.2, "kg", "ESTIMATE", "A: smallest practical space joint module", SUB,
         "floor on actuator module mass", low=0.8, high=2.0)
R.define("act_eff", "η_act", 0.60, "-", "ASSUMPTION", "A-17 (strain-wave gear at low speed/cold)", SUB,
         "joint mechanical/electrical efficiency", low=0.4, high=0.75)
R.define("cfrp_E", "E_CFRP", 120e9, "Pa", "SOURCE", "L006/L007 (quasi-iso. high-modulus tube, LITERATURE-RECALL)", SUB,
         "axial modulus of filament-wound high-modulus CFRP tube", low=90e9, high=180e9)
R.define("cfrp_rho", "ρ_CFRP", 1600.0, "kg/m^3", "SOURCE", "L007 (LITERATURE-RECALL)", SUB, "CFRP density",
         low=1550.0, high=1650.0)
R.define("cfrp_allow", "σ_CFRP", 400e6, "Pa", "ESTIMATE", "L007 (LITERATURE-RECALL) with knock-downs", SUB,
         "design allowable bending stress after environmental/thermal-cycling knock-down", low=250e6, high=600e6)
R.define("fos_ult", "FoS_u", 1.4, "-", "SOURCE", "S053 (A-22)", SUB, "ultimate factor of safety")
R.define("t_min_cfrp", "t_min", 1.5e-3, "m", "ASSUMPTION", "A: minimum robust wall for handling/impact", SUB,
         "minimum CFRP wall thickness", low=1.0e-3, high=2.5e-3)
R.define("fitting_frac", "f_fit", 0.25, "-", "ESTIMATE", "A: Ti end fittings + cable routing per link", SUB,
         "link fittings/harness mass as fraction of tube mass", low=0.15, high=0.4)


@dataclass
class ArmSpec:
    name: str
    link_lengths: tuple          # pitch-plane link lengths shoulder->tip [m]
    payload: float               # rated tip payload [kg]
    tip_deflection: float        # allowed static tip deflection under payload [m]
    n_dof: int                   # total DOF
    n_pitch: int                 # pitch joints carrying gravity moment (shoulder, elbow, wrist pitch)
    end_effector_mass: float     # end effector + F/T sensor + tool changer [kg]
    tool_mass: float = 0.0       # heaviest tool carried during rated-payload lift [kg]
    joint_speed: float = math.radians(3.0)   # reference joint speed for power [rad/s]
    roll_joint_torque_frac: float = 0.25     # roll/yaw joint torque as fraction of adjacent pitch joint
    dynamic_factor: float = 1.15             # quasi-static acceleration allowance
    link_material: str = "CFRP"              # "CFRP" | "Ti-6Al-4V" | "Al 7075-T7351"


@dataclass
class ArmResult:
    spec: ArmSpec
    reach: float
    tube_od: list
    tube_t: list
    link_mass: list
    joint_torque: list               # required (static × dynamic) pitch torques [N m], shoulder first
    joint_rating: list               # actuator ratings (× motorisation factor) [N m]
    actuator_mass: list              # all actuators incl. roll/yaw [kg]
    mass: float
    base_force: float                # vertical reaction at base [N]
    base_moment: float               # reaction moment at base [N m]
    power_move: float                # electrical power, all pitch joints moving at joint_speed [W]
    tip_deflection: float
    iterations: int = 0

    def summary(self) -> dict:
        return dict(name=self.spec.name, reach_m=self.reach, payload_kg=self.spec.payload, mass_kg=self.mass,
                    shoulder_torque_Nm=self.joint_torque[0], shoulder_rating_Nm=self.joint_rating[0],
                    base_moment_Nm=self.base_moment, power_move_W=self.power_move,
                    tip_deflection_mm=self.tip_deflection * 1e3, dof=self.spec.n_dof)


def _act_mass(torque_rating: float) -> float:
    return max(R.v("act_min_mass"), torque_rating / R.v("act_torque_density"))


def _tube_for(moment: float, length: float, stiffness_share: float, E: float, rho: float, sigma: float,
              tmin: float, d_max: float = 0.20):
    """Lightest thin-wall tube (OD, t) meeting stress and a stiffness target EI ≥ stiffness_share."""
    best = None
    for od in np.linspace(0.04, d_max, 33):
        for t in np.linspace(tmin, 0.012, 22):
            if 2 * t >= od:
                continue
            I = math.pi / 64 * (od ** 4 - (od - 2 * t) ** 4)
            A = math.pi / 4 * (od ** 2 - (od - 2 * t) ** 2)
            stress = moment * (od / 2) / I
            if stress > sigma or E * I < stiffness_share:
                continue
            m = rho * A * length
            if best is None or m < best[2]:
                best = (od, t, m, I)
    if best is None:
        raise RuntimeError("no tube satisfies constraints; increase d_max")
    return best


LINK_MATERIALS = {   # E [Pa], rho [kg/m3], design allowable (yield-based for metals) [Pa], min wall [m]
    "Ti-6Al-4V": (113.8e9, 4430.0, 880e6 / 1.25 * 1.4, 1.0e-3),
    "Al 7075-T7351": (71.7e9, 2810.0, 390e6 / 1.25 * 1.4, 1.2e-3),
}


def size_arm(spec: ArmSpec, g: float = G_MOON) -> ArmResult:
    if spec.link_material == "CFRP":
        E, rho, allow, tmin_m = R.v("cfrp_E"), R.v("cfrp_rho"), R.v("cfrp_allow"), R.v("t_min_cfrp")
    else:
        E, rho, allow, tmin_m = LINK_MATERIALS[spec.link_material]
    sigma = allow / R.v("fos_ult")
    tmin, ff = tmin_m, R.v("fitting_frac")
    mf, eta = R.v("motorisation_factor"), R.v("act_eff")
    L = np.asarray(spec.link_lengths, float)
    n = len(L)
    if spec.n_pitch != n:
        raise ValueError("model assumes one pitch joint at the root of each pitch-plane link")
    # joints at the root of each link (pitch); end effector at tip
    m_link = np.full(n, 3.0)
    m_act = np.full(n, 5.0)
    tip_mass = spec.payload + spec.end_effector_mass + spec.tool_mass
    for it in range(60):
        x_joint = np.concatenate([[0.0], np.cumsum(L)[:-1]])   # joint positions from shoulder
        x_tip = L.sum()
        torques = []
        for k in range(n):
            xk = x_joint[k]
            mom = tip_mass * g * (x_tip - xk)
            for j in range(k, n):
                mom += m_link[j] * g * (x_joint[j] + L[j] / 2 - xk)
                if j > k:
                    mom += m_act[j] * g * (x_joint[j] - xk)
            torques.append(mom * spec.dynamic_factor)
        torques = np.array(torques)
        ratings = torques * mf
        # tube sizing: bending moment at link root = torque of the joint at its root (static part);
        # stiffness: allocate allowed tip deflection equally among links (cantilever superposition)
        new_m_link, ods, ts = [], [], []
        Fp = spec.payload * g
        for k in range(n):
            lever = x_tip - x_joint[k]
            # contribution of link k bending to tip deflection under tip force: δ_k ≈ F L_k (lever^2 - ...)/EI;
            # conservative: δ_k = F·L_k·lever² / (E I)
            share = spec.tip_deflection / n
            EI_req = Fp * L[k] * lever ** 2 / share
            od, t, mt, _ = _tube_for(torques[k], L[k], EI_req, E, rho, sigma, tmin)
            new_m_link.append(mt * (1 + ff))
            ods.append(od)
            ts.append(t)
        new_m_act = np.array([_act_mass(r) for r in ratings])
        conv = np.allclose(new_m_link, m_link, rtol=1e-4) and np.allclose(new_m_act, m_act, rtol=1e-4)
        m_link, m_act = np.array(new_m_link), new_m_act
        if conv:
            break
    # non-pitch joints (roll/yaw) sized as fraction of adjacent pitch joint rating
    n_other = spec.n_dof - spec.n_pitch
    other_ratings = [ratings[min(i, n - 1)] * spec.roll_joint_torque_frac for i in range(n_other)]
    other_mass = [_act_mass(r) for r in other_ratings]
    act_all = list(m_act[: spec.n_pitch]) + other_mass
    mass = float(sum(m_link) + sum(act_all) + spec.end_effector_mass)
    base_force = (mass + spec.payload + spec.tool_mass) * g
    base_moment = float(torques[0])
    power = float(sum(torques[: spec.n_pitch]) / spec.dynamic_factor * spec.joint_speed / eta)
    # achieved tip deflection estimate
    x_joint = np.concatenate([[0.0], np.cumsum(L)[:-1]])
    defl = 0.0
    for k in range(n):
        od, t = ods[k], ts[k]
        I = math.pi / 64 * (od ** 4 - (od - 2 * t) ** 4)
        defl += spec.payload * g * L[k] * (L.sum() - x_joint[k]) ** 2 / (E * I)
    return ArmResult(spec, float(L.sum()), ods, ts, list(m_link), list(torques), list(ratings), act_all, mass,
                     base_force, base_moment, power, defl, it)


def workspace_samples(spec: ArmSpec, base=(0.0, 0.0), n=40):
    """Planar reachable-point cloud (for figures) from joint-limit sweeps of the first two links."""
    L = spec.link_lengths
    pts = []
    for q1 in np.linspace(math.radians(-30), math.radians(150), n):
        for q2 in np.linspace(math.radians(-150), math.radians(0), n):
            x = base[0] + L[0] * math.cos(q1) + sum(L[1:]) * math.cos(q1 + q2)
            z = base[1] + L[0] * math.sin(q1) + sum(L[1:]) * math.sin(q1 + q2)
            pts.append((x, z))
    return np.array(pts)
