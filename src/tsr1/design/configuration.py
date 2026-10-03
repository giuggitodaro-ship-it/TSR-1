"""TSR-1 configuration builder: component list, mass properties, power by mode (directive §25, §26, §44).

``build(Options)`` assembles a full vehicle from architecture options, sizing each component with the
physics models (mobility, manipulation, recovery, power, thermal, structures) and MERs registered in
the parameter register. Mass feeds back into drive, suspension and structure sizing, so the build is
iterated to a fixed point. The same builder is used for trade-study alternatives and for the frozen
baseline, guaranteeing that trades and budgets are computed consistently.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Optional

import numpy as np

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import G_MOON, soil_conservative, soil_nominal
from tsr1.manipulation.arm import ArmSpec, _act_mass, size_arm
from tsr1.manipulation.crane import CraneSpec, size_crane
from tsr1.mobility.terramechanics import Wheel, solve
from tsr1.mobility.vehicle import Vehicle, drive_state, lrv_calibration
from tsr1.power.electrical import converter_mass, size_battery, size_cable
from tsr1.recovery.towing import size_winch
from tsr1.structures.chassis import size_chassis
from tsr1.thermal.lumped import actuator_heater_power, cold_leak, radiator_area
from tsr1.design.layout import crane_base, deck_layout

SUB = "configuration"

# ------------------------------------------------------------------------------------- MGA (A-23)
MGA = {"structure": 0.20, "mechanism": 0.25, "electronics": 0.25, "harness": 0.60, "battery": 0.10,
       "thermal": 0.25, "heritage": 0.10, "tool": 0.25, "solar": 0.20, "line": 0.20}
for k, v in MGA.items():
    R.define(f"mga_{k}", f"MGA_{k}", v, "-", "ASSUMPTION", "A-23 / S052 (AIAA S-120A method)", "budgets",
             f"mass growth allowance, {k} category, conceptual maturity", low=v * 0.5, high=min(v * 1.5, 1.0))
R.define("system_margin", "M_sys", 0.15, "-", "ASSUMPTION", "A-23", "budgets",
         "system-level margin on top of MGA-inclusive predicted mass", low=0.10, high=0.25)
R.define("harness_frac", "f_harn", 0.06, "-", "ESTIMATE", "L007 (harness 5-8 % of dry mass)", "budgets",
         "harness CBE as fraction of other dry CBE", low=0.04, high=0.09)
R.define("wheel_rim_t", "t_rim", 1.2e-3, "m", "ESTIMATE", "A: Ti-6Al-4V rim skin with internal stiffeners", "mobility",
         "wheel rim skin thickness", low=0.8e-3, high=2.0e-3)
R.define("ti_density", "ρ_Ti", 4430.0, "kg/m^3", "SOURCE", "L005", "materials", "Ti-6Al-4V density")
R.define("drive_torque_margin", "k_T,drv", 1.25, "-", "DESIGN", "TS-01: torque beyond soil-limited thrust is unusable",
         "mobility", "drive actuator rating / soil-limited wheel torque at i=0.6 on max-load wheel")
R.define("v_drive_nom", "v_nom", 0.5, "m/s", "DESIGN", "TS-01/autonomy: hazard detection 10 cm @ 15 m (S064)", "mobility",
         "nominal autonomous driving speed", low=0.3, high=1.0)
R.define("v_drive_max", "v_max", 1.0, "m/s", "DESIGN", "TS-01", "mobility", "maximum speed on benign terrain")
R.define("payload_carried_nom", "m_pl", 100.0, "kg", "DESIGN", "TS-07 (ORUs, spares, modules per sortie)", "budgets",
         "nominal carried payload in operational mass")
R.define("web_L", "L_WEB", 1.0, "m", "DESIGN", "TS thermal (packaging of ~120 L of WEB equipment)", "thermal",
         "warm electronics box length")
R.define("web_W", "W_WEB", 0.8, "m", "DESIGN", "TS thermal", "thermal", "warm electronics box width")
R.define("web_H", "H_WEB", 0.35, "m", "DESIGN", "TS thermal", "thermal", "warm electronics box height")
R.define("web_x", "x_WEB", -0.5, "m", "DESIGN", "CDR-21: WEB centred under the radiator (short heat-pipe run) and "
         "rearward to balance axle loads after the front strip took the crane, mast and arm bases", "structure",
         "longitudinal position of the warm electronics box centre (chassis frame)")
R.define("q_web_hot", "Q_hot", 380.0, "W", "DESIGN", "budgets.closure (max WEB dissipation over modes, verified)",
         "thermal", "hot-case WEB dissipation used to size the radiator")
R.define("lander_accommodation_frac", "f_acc", 0.05, "-", "ESTIMATE",
         "A: launch locks, deployment ramp/offload interface (~5 % of payload)", "budgets",
         "lander accommodation hardware as fraction of rover wet mass", low=0.03, high=0.10)

MODES = ("M1_dormant", "M2_comm_standby", "M3_driving", "M4_inspection", "M5_manipulation",
         "M6_heavy_manip", "M7_recovery_winch", "M8_emergency_power", "M9_charging", "M10_survival", "M11_safe")


@dataclass
class Component:
    name: str
    subsystem: str
    category: str
    cbe: float                       # current best estimate [kg]
    pos: tuple                       # stowed CoM position (x, y, z) [m]
    basis: str                       # CALCULATED / ESTIMATE / SOURCE + reference
    material: str = ""
    trl: int = 0
    power: dict = field(default_factory=dict)   # mode -> average W
    peak: float = 0.0                # peak W
    qty: int = 1

    @property
    def mga(self) -> float:
        return R.v(f"mga_{self.category}")

    @property
    def predicted(self) -> float:
        return self.cbe * (1 + self.mga)


@dataclass
class Options:
    label: str = "baseline"
    # mobility
    n_wheels: int = 6
    suspension: str = "rocker_bogie_lowering"      # rocker_bogie | rocker_bogie_lowering | active_6 | active_4
    wheel_r: float = 0.45
    wheel_b: float = 0.40
    grouser_h: float = 0.02
    wheelbase: float = 2.6
    track: float = 2.0
    ground_clearance: float = 0.45
    # manipulation
    manip: str = "dual_dex+crane"                    # general | dual_identical | heavy+dex | dex+crane | dex+fixtures | dual_dex+crane
    dex_link_material: str = "Ti-6Al-4V"
    dex_payload: float = 20.0
    dex_links: tuple = (0.75, 0.70, 0.15)
    heavy_payload: float = 150.0
    heavy_links: tuple = (1.1, 1.0, 0.2)
    crane_boom: float = 2.6
    # stabilisation / recovery
    winch_pull_kN: float = 4.0
    winch_line_m: float = 50.0
    n_spades: int = 2
    n_anchors: int = 2
    recovery: bool = True
    # power
    battery_usable_eol_kwh: float = 14.0
    ptm_kw: float = 3.0
    tether_m: float = 25.0
    solar_area: float = 1.5
    # service spine
    spine: str = "modular"                            # modular | integrated
    spine_slots: int = 6
    spine_payload: float = 150.0
    # thermal
    cold_tolerant_actuators: bool = True
    # payload carried in operational mass
    payload_carried: float = field(default_factory=lambda: R.v("payload_carried_nom"))


@dataclass
class Config:
    opts: Options
    comps: list
    vehicle: Vehicle
    derived: dict

    # ------------------------------------------------------------------ mass properties
    def cbe(self, subsystem: Optional[str] = None) -> float:
        return sum(c.cbe * c.qty for c in self.comps if subsystem in (None, c.subsystem))

    def predicted(self, subsystem: Optional[str] = None) -> float:
        return sum(c.predicted * c.qty for c in self.comps if subsystem in (None, c.subsystem))

    @property
    def dry_mass_allocation(self) -> float:
        return self.predicted() * (1 + R.v("system_margin"))

    @property
    def operational_mass(self) -> float:
        """Mass used for performance sizing: predicted dry + system margin + carried payload."""
        return self.dry_mass_allocation + self.opts.payload_carried

    @property
    def delivered_mass(self) -> float:
        """Mass charged to the lander: dry allocation + accommodation (payload not included)."""
        return self.dry_mass_allocation * (1 + R.v("lander_accommodation_frac"))

    def com(self, overrides: Optional[dict] = None, extra: Optional[list] = None) -> np.ndarray:
        """Centre of mass with optional position overrides {name: pos} and extra (mass, pos) items.
        Uses predicted masses; system margin and payload are added at their own positions."""
        overrides = overrides or {}
        tot, mom = 0.0, np.zeros(3)
        for c in self.comps:
            p = np.asarray(overrides.get(c.name, c.pos), float)
            m = c.predicted * c.qty
            tot += m
            mom += m * p
        # system margin distributed like the vehicle; payload at the service spine
        sm = self.predicted() * R.v("system_margin")
        mom += sm * (mom / tot)
        tot += sm
        pl = self.opts.payload_carried
        mom += pl * np.array(self.derived["spine_payload_pos"])
        tot += pl
        for m, p in (extra or []):
            tot += m
            mom += m * np.asarray(p, float)
        return mom / tot

    def subsystem_table(self):
        subs = sorted({c.subsystem for c in self.comps})
        return [(s, self.cbe(s), self.predicted(s)) for s in subs]

    def mode_power(self, mode: str) -> float:
        return sum(c.power.get(mode, 0.0) * c.qty for c in self.comps)

    def peak_power(self) -> float:
        return sum(c.peak * c.qty for c in self.comps)


# ------------------------------------------------------------------------------ helper sizing
def _wheel_mass(w: Wheel) -> float:
    rim = R.v("ti_density") * math.pi * 2 * w.radius * w.width * R.v("wheel_rim_t")
    spokes = 0.35 * rim
    hub = 1.0
    grousers = 18 * w.width * w.grouser_h * 0.002 * R.v("ti_density")
    return rim + spokes + hub + grousers


def _drive_rating(veh: Vehicle) -> tuple[float, float]:
    """Soil-limited max wheel torque (heaviest wheel on 20° climb at slip 0.6) and rating."""
    s = soil_nominal().scaled(phi=math.radians(R.rng("soil_phi_deg")[1]))   # strongest soil -> highest torque
    th = math.radians(20)
    from tsr1.mobility.vehicle import axle_loads
    loads = axle_loads(veh, th)
    nmax = max(loads) / veh.wheels_per_axle
    tq = solve(veh.wheel, s, nmax, 0.6).torque
    return tq, tq * R.v("drive_torque_margin")


def build(opts: Options, iterate: int = 25) -> Config:
    soil = soil_nominal()
    wheel = Wheel(opts.wheel_r, opts.wheel_b, opts.grouser_h)
    n_ax = opts.n_wheels // 2
    if n_ax == 3:
        axle_x = (opts.wheelbase / 2, 0.0, -opts.wheelbase / 2)
    elif n_ax == 2:
        axle_x = (opts.wheelbase / 2, -opts.wheelbase / 2)
    else:
        raise ValueError("4 or 6 wheels supported")
    m_guess = 1400.0
    k_cal = lrv_calibration()
    comps: list[Component] = []
    derived: dict = {}
    zc = opts.ground_clearance + 0.225                 # chassis box centroid height (H = 0.45 m)
    deck_top = opts.ground_clearance + 0.45
    deck_w = min(opts.track - 0.5, 1.5)
    lay = deck_layout(opts.wheelbase, deck_w, radiator_area(R.v("q_web_hot"))[0], opts.dex_links[0])   # CDR-21
    derived["layout"] = lay
    derived["deck_top"] = deck_top
    derived["crane_base"] = crane_base(lay)
    for _ in range(iterate):
        comps = []
        veh = Vehicle(m_guess, wheel, axle_x, x_cg=0.0, h_cg=0.85, track=opts.track)
        A = comps.append

        # ---------------- mobility
        wm = _wheel_mass(wheel)
        tq, rating = _drive_rating(veh)
        drive_m = _act_mass(rating) + 0.6        # + motor controller share/housing seal (ESTIMATE)
        ds = drive_state(veh, soil, math.radians(5))
        p_drive_nom = k_cal * ds.torque_total * R.v("v_drive_nom") / (wheel.r_shear * (1 - ds.slip)) / veh.drive_eff
        ds15 = drive_state(veh, soil, math.radians(15))
        p_drive_15 = (ds15.torque_total * R.v("v_drive_nom") / (wheel.r_shear * (1 - ds15.slip)) / veh.drive_eff
                      if ds15.feasible else float("nan"))
        derived.update(drive_torque_soil=tq, drive_rating=rating, p_drive_nom=p_drive_nom, p_drive_15=p_drive_15,
                       k_cal=k_cal)
        for i in range(opts.n_wheels):
            x = axle_x[i // 2]
            y = (opts.track / 2) * (1 if i % 2 == 0 else -1)
            A(Component(f"wheel_{i+1}", "mobility", "mechanism", wm, (x, y, wheel.radius),
                        "CALCULATED configuration._wheel_mass (Ti-6Al-4V rim+spokes+grousers)", "Ti-6Al-4V", 5))
            A(Component(f"drive_actuator_{i+1}", "mobility", "mechanism", drive_m, (x, y, wheel.radius),
                        "CALCULATED: soil-limited torque × margin / torque density (act_torque_density)",
                        "Ti housing, BLDC, strain-wave gear, BMG/MoS2", 5,
                        power={"M3_driving": p_drive_nom / opts.n_wheels,
                               "M7_recovery_winch": 0.0},
                        peak=(p_drive_15 if p_drive_15 == p_drive_15 else p_drive_nom * 3) * 2 / opts.n_wheels))
        # steering: all wheels steerable (point turn capability)
        n_mu = 0.7 * (m_guess * G_MOON / opts.n_wheels)
        steer_tq = n_mu * math.hypot(0.12, opts.wheel_b) / 3 * 1.5        # scrub + bulldozing allowance
        steer_m = _act_mass(steer_tq * R.v("motorisation_factor")) + 0.3
        for i in range(opts.n_wheels):
            x = axle_x[i // 2]
            y = (opts.track / 2 - 0.05) * (1 if i % 2 == 0 else -1)
            A(Component(f"steer_actuator_{i+1}", "mobility", "mechanism", steer_m, (x, y, 2 * wheel.radius + 0.05),
                        "CALCULATED: scrub torque μN·√(l²+b²)/3 ×1.5 × MF / torque density", "Ti/Al housing", 5,
                        power={"M3_driving": 3.0}, peak=steer_tq * math.radians(15) / R.v("act_eff") + 5))
        derived["steer_torque"] = steer_tq
        # suspension
        if opts.suspension.startswith("rocker_bogie"):
            susp = 0.045 * m_guess + 6 * 0.8
            A(Component("suspension_rocker_bogie", "mobility", "structure", susp, (0, 0, 0.55),
                        "ESTIMATE: 4.5 % of operational mass (links Al 7075 / Ti pivots) + 6 pivot bearings",
                        "Al 7075-T7351 tubes, Ti-6Al-4V pivots", 6))
            A(Component("differential_lock", "mobility", "mechanism", 2.5, (0, 0, 0.95),
                        "ESTIMATE: brake on rocker differential (body attitude lock for manipulation)", "steel/Ti", 5,
                        power={"M5_manipulation": 0.0}, peak=20))
            if opts.suspension == "rocker_bogie_lowering":
                # two lead-screw actuators at rocker pivots carrying half the weight each, ×1.5 dynamic × MF
                f_act = 0.5 * m_guess * G_MOON * 1.5 * R.v("motorisation_factor")
                low_m = 1.0 + f_act / 1500.0       # linear actuator force density ~1.5 kN/kg (ESTIMATE)
                for s_ in (1, -1):
                    A(Component(f"body_lowering_actuator_{'L' if s_>0 else 'R'}", "mobility", "mechanism", low_m,
                                (0, s_ * 0.75, 0.8), "CALCULATED: 0.5 W ×1.5 × MF / 1.5 kN/kg (ESTIMATE)",
                                "Ti ball-screw, BMG nut", 4, peak=60))
                A(Component("belly_skid_plate", "stabilisation", "structure", 1.4 * 1.0 * 1.5e-3 * 2810 * 1.6,
                            (0, 0, opts.ground_clearance - 0.02),
                            "CALCULATED: 1.4 m² Al 7075 1.5 mm with cleats (×1.6)", "Al 7075-T7351 + Ti cleats", 6))
        elif opts.suspension in ("active_6", "active_4"):
            leg_tq = (m_guess * G_MOON / opts.n_wheels) * 1.5 * 0.4 * R.v("motorisation_factor")
            leg_m = _act_mass(leg_tq) + 2.5          # + leg link
            for i in range(opts.n_wheels):
                x = axle_x[i // 2]
                y = (opts.track / 2 - 0.2) * (1 if i % 2 == 0 else -1)
                A(Component(f"leg_actuator_{i+1}", "mobility", "mechanism", leg_m, (x, y, 0.7),
                            "CALCULATED: N_wheel×1.5×0.4 m lever × MF / torque density + link", "Ti/Al", 4,
                            power={"M3_driving": 4.0}, peak=80))
            A(Component("belly_skid_plate", "stabilisation", "structure", 1.4 * 1.0 * 1.5e-3 * 2810 * 1.6,
                        (0, 0, opts.ground_clearance - 0.02), "CALCULATED (as above)", "Al 7075-T7351", 6))
        for i in range(opts.n_wheels):
            x = axle_x[i // 2]
            y = (opts.track / 2) * (1 if i % 2 == 0 else -1)
            A(Component(f"fender_{i+1}", "dust", "structure", 0.9 + 1.2 * opts.wheel_b, (x, y, 2 * wheel.radius + 0.08),
                        "ESTIMATE: CFRP fender + flexible skirt (Apollo fender lesson S022)", "CFRP + PTFE-coated fabric", 7))

        # ---------------- structure
        ch = size_chassis(m_guess, L=opts.wheelbase, W=min(opts.track - 0.5, 1.5), H=0.45,
                          span=opts.wheelbase - 0.2,
                          hardpoint_loads_kN=(opts.winch_pull_kN * 1.5, opts.winch_pull_kN, 3.0, 3.0))
        A(Component("chassis_torque_box", "structure", "structure", ch.mass, (0, 0, zc),
                    f"CALCULATED structures.chassis (t_face={ch.t_face*1e3:.2f} mm, f1={ch.f1:.0f} Hz)",
                    "Al 7075-T7351 faces / Al 5056 honeycomb; Ti-6Al-4V hard points", 7))
        derived["chassis"] = ch
        A(Component("secondary_structure", "structure", "structure", 0.25 * ch.mass, (0, 0, zc + 0.2),
                    "ESTIMATE: brackets, mounts, mast base, deck rails = 25 % of primary (L007)", "Al 6061/7075", 7))
        A(Component("sensor_mast", "structure", "structure", 6.0, (*lay["sensor_mast_base"].centre, 1.6),
                    "ESTIMATE: 1.2 m CFRP mast with deploy hinge", "CFRP tube, Ti hinge", 6))

        # ---------------- manipulation
        dex = size_arm(ArmSpec("dexterous", opts.dex_links, opts.dex_payload, 0.003, 7, 3, 6.0, 3.0,
                               math.radians(5), link_material=opts.dex_link_material))
        derived["dex"] = dex
        x_arm, y_arm = lay["dex_arm_R_base"].centre[0], -lay["dex_arm_R_base"].centre[1]
        z_arm = deck_top + 0.5 * opts.dex_links[0]          # upright (candle) stow, CDR-21
        derived["arm_base"] = (x_arm, y_arm)
        manip_items = [("dexterous_arm", dex.mass, (x_arm, -y_arm, z_arm), dex)]
        crane = heavy = None
        if opts.manip == "dual_dex+crane":
            manip_items.append(("dexterous_arm_2", dex.mass, (x_arm, y_arm, z_arm), dex))
        if opts.manip in ("dex+crane", "dual_dex+crane"):
            crane = size_crane(CraneSpec(boom_length=opts.crane_boom, payload=opts.heavy_payload))
            xb = derived["crane_base"][0]
            # half the mass in turntable/A-frame/hoist at the base, half in the boom stowed rearward over the spine
            manip_items.append(("crane_boom", crane.mass, (xb - opts.crane_boom / 4, 0.0, deck_top + 0.38), crane))
        if opts.manip in ("heavy+dex",):
            heavy = size_arm(ArmSpec("heavy", opts.heavy_links, opts.heavy_payload, 0.010, 6, 3, 10.0, 0.0,
                                     math.radians(2)))
            manip_items.append(("heavy_arm", heavy.mass, (0.0, 0.45, 1.1), heavy))
        if opts.manip == "dual_identical":
            dex2 = size_arm(ArmSpec("dexterous2", opts.dex_links, opts.dex_payload, 0.003, 7, 3, 6.0, 3.0,
                                    math.radians(5)))
            manip_items.append(("dexterous_arm_2", dex2.mass, (x_arm, y_arm, z_arm), dex2))
        if opts.manip == "general":
            gen = size_arm(ArmSpec("general", opts.heavy_links, opts.heavy_payload, 0.003, 7, 3, 10.0, 3.0,
                                   math.radians(3)))
            manip_items = [("general_arm", gen.mass, (0.0, -0.45, 1.1), gen)]
            derived["dex"] = gen
        if opts.manip == "dex+fixtures":
            manip_items.append(("passive_fixtures", 8.0, (0.4, 0.4, 1.1), None))
        derived["crane"], derived["heavy"] = crane, heavy
        for name, m, pos, obj in manip_items:
            pw = getattr(obj, "power_move", None)
            if obj is not None and hasattr(obj, "power_hoist"):
                pw = obj.power_hoist + 25.0
            A(Component(name, "manipulation", "mechanism", m, pos,
                        "CALCULATED manipulation.arm/crane sizing (torque density, CFRP tubes, MF)",
                        "CFRP links, Ti-6Al-4V joints, strain-wave gears, BMG/MoS2", 4 if "crane" in name else 5,
                        power={"M5_manipulation": (pw or 10.0) * 0.6 + 15.0,
                               "M6_heavy_manip": (pw or 10.0) + 20.0, "M4_inspection": 8.0},
                        peak=(pw or 10.0) * 2.5 + 30))
        A(Component("ft_sensor_and_tool_changer", "manipulation", "mechanism", 0.0, (x_arm, -y_arm, deck_top + 0.15),
                    "included in dexterous arm end-effector mass (6 kg)", "Ti-6Al-4V", 6))

        # ---------------- tools (directive §13)
        tools = [
            ("tool_parallel_gripper", 2.0, "Ti/PEEK fingers, Vespel pads", 6, 8),
            ("tool_socket_driver", 2.5, "Ti body, tool-steel socket set", 6, 40),
            ("tool_electrical_probe", 1.5, "PEEK/Ti, Au-plated probes", 5, 5),
            ("tool_connector_mate", 2.0, "Ti/PEEK", 5, 10),
            ("tool_dust_brush", 1.5, "Ti frame, PTFE-coated aramid bristles", 5, 15),
            ("tool_eds_wand", 2.5, "CFRP frame, ITO/PI electrode film, HV supply", 4, 10),
            ("tool_anchor_driver", 4.0, "Ti body, steel bit", 4, 120),
            ("tool_oru_adapter_otcm", 3.0, "Ti-6Al-4V", 5, 10),
            ("tool_oru_adapter_androgynous", 2.5, "Ti-6Al-4V/Al 7075", 5, 10),
            ("tool_lifting_fixture_slings", 2.0, "Vectran slings, Ti hooks", 6, 0),
            ("tool_recovery_shackle_hitch", 2.0, "Ti-6Al-4V", 6, 0),
            ("tool_regolith_scoop", 2.0, "Ti-6Al-4V blade, PTFE-coated", 6, 30),
            ("tool_rack_holsters", 6.0, "Al 7075, Ti latches", 6, 5),
        ]
        for nm, m, mat, trl, pk in tools:
            A(Component(nm, "tools", "tool", m, (opts.wheelbase / 2 + 0.05, 0.0, zc), "ESTIMATE per tool spec sheet; holstered on chassis front face (CDR-21)", mat, trl,
                        power={"M5_manipulation": pk * 0.3}, peak=pk))

        # ---------------- service spine
        if opts.spine == "modular":
            spine_m = 8.0 + 1.1 * opts.spine_slots
            A(Component("service_spine", "service_spine", "structure", spine_m, (lay["service_spine"].centre[0], 0, deck_top + 0.05),
                        "ESTIMATE: Al 7075 rail + slots × (1.1 kg latch+connector)", "Al 7075, Ti latches", 5,
                        power={"M1_dormant": 1.0, "M5_manipulation": 5.0}, peak=30))
        else:
            A(Component("integrated_mounts", "service_spine", "structure", 5.0, (lay["service_spine"].centre[0], 0, deck_top + 0.05),
                        "ESTIMATE: fixed brackets", "Al 7075", 7))
        derived["spine_payload_pos"] = (lay["service_spine"].centre[0], 0.0, deck_top + 0.225)

        # ---------------- recovery & stabilisation
        if opts.recovery:
            win = size_winch(opts.winch_pull_kN * 1e3, opts.winch_line_m)
            derived["winch"] = win
            A(Component("recovery_winch", "recovery", "mechanism", win.mass - win.line_mass,
                        (-opts.wheelbase / 2 - 0.05, 0, 0.6), "CALCULATED recovery.towing.size_winch",
                        "Ti drum, steel gear, BMG level-wind", 5,
                        power={"M7_recovery_winch": win.power_elec * 0.6, "M1_dormant": 0.5},
                        peak=win.power_elec * 1.3))
            A(Component("recovery_line", "recovery", "line", win.line_mass, (-opts.wheelbase / 2 - 0.05, 0, 0.6),
                        "CALCULATED: Vectran braid, FoS 5", "Vectran with PTFE/aramid jacket", 6))
            for k in range(opts.n_spades):
                A(Component(f"spade_{k+1}", "recovery", "mechanism", 0.6 * 0.30 * 0.006 * R.v("ti_density") + 4.0,
                            (-opts.wheelbase / 2 - 0.15, 0.5 * (1 if k % 2 == 0 else -1), 0.5),
                            "CALCULATED: Ti plate 0.6×0.3×6 mm + deploy actuator/hinge 4 kg (ESTIMATE)",
                            "Ti-6Al-4V", 4, peak=60))
            for k in range(opts.n_anchors):
                A(Component(f"helical_anchor_{k+1}", "recovery", "mechanism", 2.0, (-0.6, 0.65, 0.9),
                            "ESTIMATE: Ti shaft 0.7 m Ø25 mm + Ø150 mm helix", "Ti-6Al-4V", 4))
            A(Component("tow_hardpoints_front_rear", "recovery", "structure", 3.0, (0, 0, 0.6),
                        "ESTIMATE: Ti-6Al-4V lugs, pins", "Ti-6Al-4V", 7))

        # ---------------- power
        bat = size_battery(opts.battery_usable_eol_kwh)
        derived["battery"] = bat
        wx = R.v("web_x")
        A(Component("battery_pack", "power", "battery", bat.mass, (wx, 0.0, opts.ground_clearance + 0.12),
                    f"CALCULATED power.electrical.size_battery ({bat.nameplate_kwh:.1f} kWh nameplate, "
                    f"{bat.n_series}s{bat.n_parallel}p)", "Li-ion 18650 PPR pack (Al interstitials, mica)", 6,
                    power={m: 0.0 for m in MODES}))
        p_bus = 4000.0
        A(Component("pcdu_bus_regulator", "power", "electronics", converter_mass(p_bus) + 3.0, (wx + 0.3, 0.25, zc),
                    "CALCULATED: 4 kW bidirectional buck-boost /300 W/kg + 3 kg distribution/SSPCs",
                    "Al housing, SiC FETs", 5, power={m: 6.0 for m in MODES}, peak=0))
        A(Component("power_transfer_module", "power", "electronics", converter_mass(opts.ptm_kw * 1000) + 2.0,
                    (wx + 0.4, -0.25, zc), "CALCULATED: isolated bidirectional DC-DC /300 W/kg + diagnostics",
                    "Al housing, SiC, planar transformer", 4,
                    power={"M8_emergency_power": opts.ptm_kw * 1000 * 0.0, "M9_charging": 0.0}, peak=0))
        cab = size_cable(opts.ptm_kw * 1000, opts.tether_m)
        derived["tether"] = cab
        A(Component("power_tether_and_reel", "power", "mechanism", cab.mass + 4.0, (1.0, 0.45, zc),
                    f"CALCULATED: {cab.area_mm2:.1f} mm² Cu ×2 × {opts.tether_m:.0f} m, 3 % drop + 4 kg reel",
                    "Cu/PTFE/aramid jacket; Al reel", 5, power={"M8_emergency_power": 3.0}, peak=40))
        A(Component("dust_tolerant_connector_head", "power", "mechanism", 2.5, (x_arm, -0.45, 1.05),
                    "ESTIMATE: S042 DTC class with clamshell cover", "Ti shell, Au contacts, PEEK", 4))
        if opts.solar_area > 0:
            A(Component("solar_arrays_vertical", "power", "solar", opts.solar_area * 2.8,
                        (-0.3, 0.0, 1.35), "ESTIMATE: 2.8 kg/m² incl. CFRP panel, hinge (L007)",
                        "IMM/triple-junction GaAs on CFRP", 7))
            A(Component("solar_array_regulator", "power", "electronics", 1.5, (wx + 0.3, -0.3, zc),
                        "ESTIMATE: MPPT 600 W", "Al", 6, power={"M9_charging": 2.0}))

        # ---------------- avionics
        av = [
            ("autonomy_computer_hpsc", 6.0, 6, dict(M3_driving=45, M4_inspection=45, M5_manipulation=45,
                                                   M6_heavy_manip=45, M7_recovery_winch=40, M8_emergency_power=25,
                                                   M9_charging=15, M2_comm_standby=0, M1_dormant=0, M10_survival=0,
                                                   M11_safe=10), 60),
            ("safety_rt_computer_A", 3.0, 7, {m: 10.0 for m in MODES}, 12),
            ("safety_rt_computer_B", 3.0, 7, {m: (10.0 if m not in ("M1_dormant", "M10_survival") else 0.0)
                                            for m in MODES}, 12),
            ("motor_control_units", 0.4 * (opts.n_wheels * 2 + 16), 5,
             dict(M3_driving=40, M4_inspection=10, M5_manipulation=30, M6_heavy_manip=40, M7_recovery_winch=25,
                  M8_emergency_power=5, M9_charging=5, M11_safe=5), 120),
            ("mass_memory_and_timing", 1.3, 7, {m: 5.0 for m in MODES if m != "M10_survival"}, 8),
        ]
        for nm, m, trl, pw, pk in av:
            A(Component(nm, "avionics", "electronics", m, (wx + 0.35, -0.2, zc), "ESTIMATE per avionics spec", "Al chassis",
                        trl, power=pw, peak=pk))
        # ---------------- sensors
        sens = [
            ("navcam_stereo_pair", 0.8, (x_arm - 0.05, 0.5, 2.15), 6, dict(M3_driving=6, M4_inspection=6, M5_manipulation=6, M6_heavy_manip=6, M7_recovery_winch=6, M8_emergency_power=6), 8),
            ("mast_pan_tilt", 5.0, (x_arm - 0.05, 0.5, 2.0), 6, dict(M3_driving=5, M4_inspection=8), 25),
            ("led_illuminators", 1.0, (x_arm - 0.05, 0.5, 2.1), 7, dict(M3_driving=20, M4_inspection=20, M5_manipulation=20, M6_heavy_manip=20, M7_recovery_winch=20), 45),
            ("hazcams_x6", 1.5, (0, 0, 0.9), 7, dict(M3_driving=9, M7_recovery_winch=6), 10),
            ("lidar_front", 2.5, (opts.wheelbase / 2 + 0.2, 0, 1.0), 5, dict(M3_driving=25, M4_inspection=25, M5_manipulation=10), 35),
            ("lidar_rear", 2.5, (-opts.wheelbase / 2 - 0.2, 0, 1.0), 5, dict(M3_driving=25, M7_recovery_winch=25), 35),
            ("thermal_ir_imager", 0.6, (x_arm - 0.05, 0.5, 2.15), 6, dict(M4_inspection=4, M5_manipulation=4), 6),
            ("macro_inspection_camera", 0.4, (x_arm, -0.45, 1.05), 6, dict(M4_inspection=3, M5_manipulation=3), 5),
            ("imu_ln200s", 0.75, (0, 0, zc), 9, dict(M3_driving=12, M4_inspection=12, M5_manipulation=12, M6_heavy_manip=12, M7_recovery_winch=12, M11_safe=12), 16),
            ("sun_sensor_star_tracker", 0.5, (x_arm, 0.5, 2.2), 8, dict(M3_driving=2, M11_safe=2), 3),
            ("electrical_diagnostic_unit", 1.5, (wx + 0.4, 0.25, zc), 5, dict(M5_manipulation=5, M8_emergency_power=5), 10),
            ("contact_vibration_sensors", 0.2, (x_arm, -0.45, 1.05), 6, dict(M4_inspection=1, M5_manipulation=1), 2),
        ]
        for nm, m, pos, trl, pw, pk in sens:
            A(Component(nm, "sensors", "electronics", m, pos, "ESTIMATE per sensor spec (S064/S065 analogues)",
                        "", trl, power=pw, peak=pk))
        # ---------------- communications
        comm = [
            ("surface_network_radio", 1.5, 6, dict(M2_comm_standby=4, M3_driving=12, M4_inspection=15, M5_manipulation=15, M6_heavy_manip=12, M7_recovery_winch=12, M8_emergency_power=12, M9_charging=8, M11_safe=8), 25),
            ("lunanet_relay_transceiver", 2.5, 6, dict(M2_comm_standby=6, M4_inspection=30, M5_manipulation=30, M8_emergency_power=20, M11_safe=30, M9_charging=10), 55),
            ("relay_antenna_gimballed", 2.2, 6, dict(M4_inspection=4, M5_manipulation=4, M11_safe=4), 15),
            ("mesh_uhf_radio", 0.5, 7, {m: 3.0 for m in MODES if m != "M1_dormant"}, 6),
        ]
        for nm, m, trl, pw, pk in comm:
            A(Component(nm, "communications", "electronics", m, (x_arm - 0.05, 0.5, 1.9), "ESTIMATE per comms spec",
                        "", trl, power=pw, peak=pk))

        # ---------------- thermal
        # Warm Electronics Box inside the chassis: battery (~60 L), avionics (~30 L), PCDU/PTM (~25 L)
        web = (R.v("web_L"), R.v("web_W"), R.v("web_H"))
        a_mli = 2 * (web[0] * web[1] + web[0] * web[2] + web[1] * web[2])
        q_hot = R.v("q_web_hot")
        a_rad, _ = radiator_area(q_hot)
        derived.update(a_mli=a_mli, a_rad=a_rad, q_hot=q_hot)
        leak = cold_leak(a_mli, a_rad)
        n_act_ext = sum(1 for c in comps if c.subsystem in ("mobility", "manipulation", "recovery")
                        and c.category == "mechanism")
        act_heat = 0.0 if opts.cold_tolerant_actuators else actuator_heater_power(n_act_ext)
        derived.update(web_leak_cold=leak, actuator_heaters=act_heat, n_external_actuators=n_act_ext)
        A(Component("mli_blankets", "thermal", "thermal", a_mli * 0.8, (R.v("web_x"), 0, zc), "CALCULATED: area × 0.8 kg/m²",
                    "Kapton/Mylar/Dacron netting, Beta-cloth outer", 8))
        A(Component("radiator_panel_eds", "thermal", "thermal", a_rad * 6.0, (lay["radiator"].centre[0], 0, deck_top + 0.01),
                    f"CALCULATED: {a_rad:.2f} m² × 6 kg/m² (Al panel, heat pipes, OSR, EDS film)",
                    "Al 6063 heat-pipe panel, OSR/AgFEP, ITO EDS film", 5))
        A(Component("loop_heat_pipe_switch", "thermal", "thermal", 3.5, (R.v("web_x"), 0, zc + 0.15), "ESTIMATE: LHP with thermal switch",
                    "SS/Al, ammonia", 6))
        web_names = ("pcdu_bus_regulator", "power_transfer_module", "autonomy_computer_hpsc", "safety_rt_computer_A",
                     "safety_rt_computer_B", "motor_control_units", "mass_memory_and_timing", "imu_ln200s",
                     "electrical_diagnostic_unit", "surface_network_radio", "lunanet_relay_transceiver", "mesh_uhf_radio",
                     "solar_array_regulator")
        p_elec_surv = sum(c.power.get("M10_survival", 0.0) for c in comps if c.name in web_names)
        heater_cold = max(0.0, leak - p_elec_surv) + act_heat
        derived["p_elec_survival"] = p_elec_surv
        A(Component("heaters_thermostats", "thermal", "thermal", 2.0 + 0.1 * n_act_ext, (0, 0, zc),
                    "ESTIMATE: Kapton heaters, PRTs, thermostats", "Kapton/Inconel", 8,
                    power={"M10_survival": heater_cold, "M1_dormant": heater_cold * 0.6,
                           "M2_comm_standby": heater_cold * 0.5, "M11_safe": heater_cold * 0.5,
                           "M3_driving": act_heat * 0.2, "M5_manipulation": act_heat * 0.3}))
        derived["heater_cold"] = heater_cold
        # dust self-protection extras
        A(Component("optics_eds_and_covers", "dust", "electronics", 1.2, (x_arm, 0.5, 2.1),
                    "ESTIMATE: EDS films on camera/LiDAR windows + HV supply + covers", "ITO/PI, Ti covers", 5,
                    power={"M4_inspection": 0.5, "M3_driving": 0.5}, peak=5))
        A(Component("joint_boots_seals", "dust", "mechanism", 0.15 * n_act_ext, (0, 0, 0.9),
                    "ESTIMATE: 0.15 kg per external actuator (labyrinth + PTFE/Ti bellows)", "PTFE-coated fabric, Ti", 5))

        # ---------------- harness
        cbe_other = sum(c.cbe * c.qty for c in comps)
        A(Component("harness", "harness", "harness", R.v("harness_frac") * cbe_other, (0, 0, zc),
                    "ESTIMATE: 6 % of other dry CBE (L007)", "Cu/PTFE, connectors", 7))

        cfg = Config(opts, comps, veh, derived)
        m_new = cfg.operational_mass
        if abs(m_new - m_guess) < 0.5:
            m_guess = m_new
            break
        m_guess = 0.5 * (m_guess + m_new)
    veh = Vehicle(m_guess, wheel, axle_x, x_cg=0.0, h_cg=0.85, track=opts.track)
    cfg = Config(opts, comps, veh, derived)
    c = cfg.com()
    cfg.vehicle = Vehicle(cfg.operational_mass, wheel, axle_x, x_cg=float(c[0]), h_cg=float(c[2]), track=opts.track)
    return cfg
