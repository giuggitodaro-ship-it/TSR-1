"""Primary-structure sizing: closed sandwich-panel torque box (directive §17).

The chassis is a closed box (L × W × H) of honeycomb-sandwich panels that also forms the Warm
Electronics Box. It is sized as an equivalent thin-walled beam for:
  LC1 launch/landing quasi-static load (A-05: 6 g axial + 3 g lateral, simultaneous), simply supported
      at launch locks spanning ``span``;
  LC2 first bending frequency f₁ ≥ f_req on the launch locks (A-05b);
  LC3 operational hard-point loads (winch, crane, arm) — local fittings sized from design load;
  LC4 thermal stress — checked for face/fitting CTE mismatch over the 40–390 K range.
Face-sheet equivalent thickness t_f is the larger of strength- and stiffness-driven values, bounded by
a minimum gauge. Mass = panels (faces + core + adhesive) + inserts/frames + hard-point fittings.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import G_EARTH

SUB = "structure"
R.define("launch_g_axial", "n_ax", 6.0, "g", "ASSUMPTION", "A-05", SUB, "quasi-static axial load factor", low=4.0, high=10.0)
R.define("launch_g_lateral", "n_lat", 3.0, "g", "ASSUMPTION", "A-05", SUB, "quasi-static lateral load factor", low=2.0, high=4.0)
R.define("f1_req", "f_1", 35.0, "Hz", "ASSUMPTION", "A-05b (typical lander payload stiffness requirement)", SUB,
         "minimum first-mode frequency on launch locks", low=25.0, high=50.0)
R.define("fos_yield", "FoS_y", 1.25, "-", "SOURCE", "S053 (A-22)", SUB, "yield factor of safety")
R.define("core_density", "ρ_core", 50.0, "kg/m^3", "SOURCE", "L007 (Al 5056 honeycomb 3.1 pcf, LITERATURE-RECALL)", SUB,
         "honeycomb core density")
R.define("core_thk", "t_core", 0.025, "m", "DESIGN", "TS-10", SUB, "core thickness")
R.define("adhesive_areal", "w_adh", 0.30, "kg/m^2", "ESTIMATE", "L007 (film adhesive 2 faces, LITERATURE-RECALL)", SUB,
         "adhesive areal mass")
R.define("insert_frac", "f_ins", 0.30, "-", "ESTIMATE", "L007 (inserts, edge closeouts, internal frames)", SUB,
         "inserts/frames as fraction of panel mass", low=0.2, high=0.45)
R.define("fitting_kg_per_kN", "k_fit", 0.35, "kg/kN", "ESTIMATE", "A: Ti-6Al-4V machined hard points sized at FoS 1.4",
         SUB, "hard-point fitting mass per kN of design load", low=0.2, high=0.6)
R.define("t_face_min", "t_f,min", 0.5e-3, "m", "ASSUMPTION", "A: handling/MMOD/insert pull-out minimum per face", SUB,
         "minimum face-sheet thickness (each face)")

# Candidate face materials (TS-10). E [Pa], density [kg/m3], allowable yield [Pa], CTE [1/K]
FACE_MATERIALS = {
    "Al 7075-T7351": dict(E=71.7e9, rho=2810.0, sy=390e6, cte=23.4e-6, src="L005"),
    "Al 2219-T87": dict(E=73.8e9, rho=2840.0, sy=345e6, cte=22.3e-6, src="L005 (LRV heritage S027)"),
    "Al-Li 2195-T8": dict(E=76.0e9, rho=2710.0, sy=500e6, cte=21.6e-6, src="L005 (LITERATURE-RECALL)"),
    "Ti-6Al-4V": dict(E=113.8e9, rho=4430.0, sy=880e6, cte=8.6e-6, src="L005"),
    "CFRP quasi-iso (M55J/cyanate)": dict(E=110e9, rho=1650.0, sy=450e6, cte=0.5e-6, src="L007 (LITERATURE-RECALL)"),
}


@dataclass
class ChassisResult:
    material: str
    t_face: float
    t_face_strength: float
    t_face_stiffness: float
    panel_mass: float
    fittings_mass: float
    mass: float
    f1: float
    margin_strength: float


def size_chassis(mass_supported: float, L: float = 2.4, W: float = 1.4, H: float = 0.45, span: float = 2.2,
                 material: str = "Al 7075-T7351", hardpoint_loads_kN: tuple = (6.0, 4.0, 3.0, 3.0)) -> ChassisResult:
    m = FACE_MATERIALS[material]
    E, rho, sy = m["E"], m["rho"], m["sy"]
    nax, nlat = R.v("launch_g_axial"), R.v("launch_g_lateral")
    fos = R.v("fos_yield")
    # equivalent thin-wall box: I = t * (2 W (H/2)^2 + 2 H^3/12) for bending about lateral axis
    c_I = 2 * W * (H / 2) ** 2 + 2 * H ** 3 / 12
    c_Ilat = 2 * H * (W / 2) ** 2 + 2 * W ** 3 / 12
    F_ax = mass_supported * G_EARTH * nax
    F_lat = mass_supported * G_EARTH * nlat
    M_ax = F_ax * span / 8
    M_lat = F_lat * span / 8
    # stress = M c / I with I = c_I t  ->  t = M (H/2) / (c_I σ_allow) ; combined linearly (conservative)
    s_allow = sy / fos
    t_str = M_ax * (H / 2) / (c_I * s_allow) + M_lat * (W / 2) / (c_Ilat * s_allow)
    # stiffness: f1 = (π/2) sqrt(EI / (m_L span^4)) >= f_req
    m_L = mass_supported / span
    EI_req = (R.v("f1_req") * 2 / math.pi) ** 2 * m_L * span ** 4
    t_stf = EI_req / (E * c_I)
    t_min = 2 * R.v("t_face_min")          # equivalent box wall = two faces of a sandwich wall
    t = max(t_str, t_stf, t_min)
    area = 2 * (L * W + L * H + W * H)
    areal = rho * t + R.v("core_density") * R.v("core_thk") + R.v("adhesive_areal")
    panels = area * areal * (1 + R.v("insert_frac"))
    fittings = R.v("fitting_kg_per_kN") * sum(hardpoint_loads_kN) * R.v("fos_ult")
    f1 = (math.pi / 2) * math.sqrt(E * c_I * t / (m_L * span ** 4))
    margin = (s_allow * c_I * t / (H / 2)) / M_ax - 1 if t_str > 0 else math.inf
    return ChassisResult(material, t, t_str, t_stf, panels, fittings, panels + fittings, f1, margin)


def thermal_mismatch_stress(material_a: str, material_b: str, dT: float = 250.0) -> float:
    """Free-thermal-strain mismatch stress estimate σ ≈ E_soft Δα ΔT (bolted joint, fully constrained)."""
    a, b = FACE_MATERIALS[material_a], FACE_MATERIALS[material_b]
    E = min(a["E"], b["E"])
    return E * abs(a["cte"] - b["cte"]) * dT
