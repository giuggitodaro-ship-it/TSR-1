"""TS-06 energy, TS-07 service-module, TS-08 communications, TS-09 autonomy, TS-10 structural materials."""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import SOLAR_CONST

# ============================================================================== TS-06 energy
R.define("mmrtg_mass", "m_MMRTG", 45.0, "kg", "SOURCE", "L028 (NASA MMRTG fact sheet, LITERATURE-RECALL)", "power",
         "MMRTG mass")
R.define("mmrtg_power", "P_MMRTG", 110.0, "W", "SOURCE", "L028 (BOL electrical, LITERATURE-RECALL)", "power",
         "MMRTG BOL electrical output")
R.define("rfc_spec_energy", "e_RFC", 350.0, "Wh/kg", "ESTIMATE", "L007 (regenerative fuel cell system incl. tanks, "
         "long-duration storage; LITERATURE-RECALL)", "power", "", low=200.0, high=600.0)


def battery_vs_radius(cfg_builder, radii_km=(5, 7.5, 10, 12.5, 15, 20, 25)) -> list[dict]:
    """Usable EOL energy required for DRM-2 at the service edge + survival reserve, and resulting pack mass."""
    from tsr1.budgets.scenarios import drm_library, evaluate
    from tsr1.power.electrical import size_battery
    cfg = cfg_builder()
    rows = []
    res_kwh = R.v("reserve_survival_h") * cfg.mode_power("M10_survival") / 1000
    for d in radii_km:
        drm2 = [x for x in drm_library(cfg, d) if x.id == "DRM-2"][0]
        r = evaluate(cfg, drm2)
        need = r.energy_kwh + res_kwh
        need_sol = r.energy_solar_kwh + res_kwh
        rows.append(dict(radius_km=d, drm2_kwh=r.energy_kwh, drm2_with_solar_kwh=r.energy_solar_kwh,
                         reserve_kwh=res_kwh, usable_eol_required_kwh=need,
                         pack_mass_kg=size_battery(need).mass, pack_mass_with_solar_kg=size_battery(need_sol).mass))
    return rows


def energy_alternatives(cfg) -> list[dict]:
    """Direct comparison of energy architectures for the same mission set."""
    from tsr1.budgets.scenarios import solar_avg_w
    surv = cfg.mode_power("M10_survival")
    bat = cfg.derived["battery"]
    e_use = cfg.opts.battery_usable_eol_kwh
    sol = solar_avg_w(cfg)
    rows = [
        dict(option="E1 Li-ion battery only, grid charging at nodes", added_mass_kg=0.0,
             survival_dark_h=e_use * 1000 / surv, survival_sunlit="limited by battery",
             indefinite_survival_in_sun=False, trl=6, issues="stranded TSR in darkness dies after battery exhaustion",
             selected=False),
        dict(option="E2 Li-ion battery + fixed vertical solar arrays (1.5 m²)", added_mass_kg=4.2 + 1.5,
             survival_dark_h=e_use * 1000 / surv, survival_sunlit=f"indefinite ({sol:.0f} W avg > {surv:.0f} W)",
             indefinite_survival_in_sun=sol > surv, trl=7, issues="dust on arrays (vertical: low deposition)",
             selected=True),
        dict(option="E3 battery + MMRTG-class radioisotope power", added_mass_kg=R.v("mmrtg_mass"),
             survival_dark_h=float("inf"), survival_sunlit="indefinite", indefinite_survival_in_sun=True, trl=9,
             issues="Pu-238 supply and launch approval; ~2 kW waste heat helps PSR ops; not available to an "
                    "independent commercial programme with confidence", selected=False),
        dict(option="E4 battery + regenerative fuel cell", added_mass_kg=5.0 / R.v("rfc_spec_energy") * 1000 + 25.0,
             survival_dark_h=(e_use + 5.0) * 1000 / surv, survival_sunlit="needs electrolysis power",
             indefinite_survival_in_sun=False, trl=4,
             issues="mobile H2/O2 storage, cryo/pressure hazards near crew, low TRL on surface", selected=False),
        dict(option="E5 battery + wireless/beamed power", added_mass_kg=8.0, survival_dark_h=e_use * 1000 / surv,
             survival_sunlit="n/a", indefinite_survival_in_sun=False, trl=3,
             issues="requires transmitter infrastructure and line of sight; low TRL", selected=False),
    ]
    return rows


# ============================================================================== TS-07 keep-alive module sizing
R.define("asset_survival_w", "P_surv,a", 100.0, "W", "ASSUMPTION", "A-33 (no survival-power data retrieved for "
         "candidate assets; small rover / infrastructure-box class)", "power",
         "survival (heater + minimal avionics) power of a parked client asset, log-uniform", low=40.0, high=250.0)
R.define("site_illum_frac", "f_ill,site", 0.75, "-", "ASSUMPTION", "A-34 (upper bound S030 best ridge 0.92 at 2 m; "
         "lower bound for infrastructure off the ridges)", "power", "time-averaged illumination at a parked asset",
         low=0.5, high=0.92)
R.define("dark_period_h", "t_dark", 72.0, "h", "ASSUMPTION", "A-35 (S030: longest darkness 3-5 days at the best sites; "
         "no site-specific data used)", "power", "", low=24.0, high=120.0)
R.define("pv_areal_density", "ρ_A,PV", 2.5, "kg/m^2", "ESTIMATE", "L007 (rigid space panel incl. substrate and hinge, "
         "LITERATURE-RECALL 2-3.5)", "power", "", low=2.0, high=3.5)
R.define("ka_self_w", "P_self,KA", 5.0, "W", "ESTIMATE", "A: MPPT/controller standby + battery heater average", "power",
         "", low=3.0, high=10.0)

KA_OPTIONS = {"KA-A 0.75 m² / 2 kWh": (0.75, 2.0), "KA-B 1.0 m² / 3 kWh": (1.0, 3.0),
              "KA-C 1.5 m² / 4 kWh": (1.5, 4.0), "KA-D 1.5 m² / 6 kWh": (1.5, 6.0)}
KA_SELECTED = "KA-C 1.5 m² / 4 kWh"   # DESIGN DECISION (TS-07b, CDR-20)


def keepalive_module_sizing(face_m2: float, usable_kwh: float, n_mc: int = 20000, seed: int = 31) -> dict:
    """MOD-KA keep-alive module: mass, sustained output and probability of sustaining a parked asset (CDR-20).

    PV: two back-to-back vertical panels of ``face_m2`` each (one face lit at a time, as on TSR-1, geometric factor
    2/π). Battery: ISPSIS 120 V string sized like the TSR-1 pack (usable EOL energy). Sustain criterion per sample:
    sunlit-average output ≥ asset survival power AND battery bridging + asset thermal inertia ≥ longest dark period.
    """
    import tsr1.budgets.scenarios  # noqa: F401  (registers PV and keep-alive parameters)
    from tsr1.power.electrical import converter_mass, size_battery
    bat = size_battery(usable_kwh)
    p_sun = (R.v("solar_cell_eff") * SOLAR_CONST * face_m2 * R.v("solar_geom_factor") * R.v("solar_eol_factor")
             * R.v("conv_eff"))
    m_pv = 2 * face_m2 * R.v("pv_areal_density")
    m_elec = converter_mass(p_sun + R.v("p_keepalive_w")) + 1.0          # MPPT + 120 V output stage + controller
    m_conn = 1.5                                                          # ISPSIS connector + 10 m cable (ESTIMATE)
    m_struct = 0.15 * (bat.mass + m_pv + m_elec + m_conn) + 1.0        # frame, hinge, feet, MLI (ESTIMATE)
    cbe = bat.mass + m_pv + m_elec + m_conn + m_struct
    mass = cbe * 1.20                                                     # MGA, new design (AIAA S-120A class)
    rng = np.random.default_rng(seed)
    lo, hi = R.rng("asset_survival_w")
    p_asset = np.exp(rng.uniform(math.log(lo), math.log(hi), n_mc))
    f_ill = rng.uniform(*R.rng("site_illum_frac"), n_mc)
    t_dark = rng.uniform(*R.rng("dark_period_h"), n_mc)
    t_surv = rng.uniform(*R.rng("t_survive_h"), n_mc)
    p_avg = p_sun * f_ill - R.v("ka_self_w")

    def sustained(scale):
        pa = p_asset * scale
        return (p_avg >= pa) & (usable_kwh * 1000 / (pa + R.v("ka_self_w")) + t_surv >= t_dark)

    ok = sustained(1.0)
    p_nom = p_sun * R.v("site_illum_frac") - R.v("ka_self_w")
    return dict(face_m2=face_m2, usable_kwh=usable_kwh, battery_kg=bat.mass, pv_kg=m_pv, electronics_kg=m_elec,
                structure_kg=m_struct, mass_cbe_kg=cbe, mass_kg=mass, p_sunlit_w=p_sun, p_sustained_nominal_w=p_nom,
                bridge_nominal_h=usable_kwh * 1000 / (R.v("asset_survival_w") + R.v("ka_self_w")),
                p_sustain=float(ok.mean()),
                p_sustain_low=float(sustained(1.5).mean()),      # asset survival powers 50 % higher than assumed
                p_sustain_high=float(sustained(1 / 1.5).mean()),  # ... one third lower
                p_sustain_power_only=float((p_avg >= p_asset).mean()))


def keepalive_module_trade() -> dict:
    rows = [dict(option=k, **keepalive_module_sizing(*v)) for k, v in KA_OPTIONS.items()]
    sel = next(r for r in rows if r["option"] == KA_SELECTED)
    return dict(options=rows, selected=KA_SELECTED, selected_row=sel)


def ka_mass() -> float:
    return keepalive_module_sizing(*KA_OPTIONS[KA_SELECTED])["mass_kg"]


# ============================================================================== TS-07 service modules
SERVICE_MODULES = [
    # name, mass kg, function, per-sortie carry probability (fraction of sorties needing it)
    ("MOD-KA keep-alive power module (KA-C: 4 kWh, 2 × 1.5 m² back-to-back vertical PV, ISPSIS port)", None,
     "left connected to a disabled asset until spare/crew arrives", 0.25),
    ("MOD-ORU generic ORU cradle (passive standard interface)", 4.0, "carry ORUs/spares", 0.6),
    ("MOD-REC recovery kit (anchors, slings, shackles)", 9.0, "immobilised-vehicle recovery", 0.15),
    ("MOD-RPT deployable comm repeater (UHF/LTE, 8 h battery + PV)", 6.0, "link into PSRs/shadowed terrain", 0.1),
    ("MOD-SOL solar mast module (4 m² vertical, tracking)", 15.0, "no-grid charging scenario", 0.0),
    ("MOD-FLD fluid servicing coupling + 10 kg tank", 15.0, "not baselined: no fluid-serviceable asset identified", 0.0),
]


def service_modules() -> list[tuple]:
    import tsr1.reliability.value_model  # noqa: F401  (registers t_survive_h used by the MOD-KA sizing)
    m_ka = ka_mass()
    return [(m[0], m_ka if m[1] is None else m[1], m[2], m[3]) for m in SERVICE_MODULES]


def service_module_trade(n_slots: int = 6) -> dict:
    spine_overhead = 8.0 + 1.1 * n_slots
    mods = service_modules()
    lib = [m for m in mods if "not baselined" not in m[2]]
    # integrated alternative: every module with non-zero carry fraction permanently aboard, MOD-KA counted once
    # (an integrated vehicle cannot leave a module behind, so it carries one keep-alive unit as a fixed function)
    integrated_always = sum(m[1] for m in lib if m[1] and m[3] > 0)
    modular_mean_sortie = sum(m[1] * m[3] for m in lib) + spine_overhead
    return dict(spine_overhead_kg=spine_overhead, integrated_carried_kg=integrated_always,
                modular_mean_carried_kg=modular_mean_sortie,
                mass_saving_per_sortie_kg=integrated_always - modular_mean_sortie,
                modules=[dict(name=m[0], mass_kg=m[1], function=m[2], carry_fraction=m[3]) for m in mods])


# ============================================================================== TS-08 communications
R.define("relay_range_max_km", "d_rel", 10000.0, "km", "ASSUMPTION", "A: elliptical lunar relay orbit slant range (no "
         "orbit data retrieved for LCRNS/Moonlight)", "comms", "", low=3000.0, high=20000.0)
R.define("relay_gt_dbk", "G/T_rel", 0.0, "dB/K", "ASSUMPTION", "A: small relay satellite S-band receive", "comms", "",
         low=-5.0, high=5.0)


def link_budget(p_tx_w: float = 5.0, g_tx_dbi: float = 10.0, f_hz: float = 2.25e9, d_km: float | None = None,
                gt_dbk: float | None = None, losses_db: float = 3.0, ebn0_req_db: float = 4.0,
                margin_db: float = 3.0) -> dict:
    d = (R.v("relay_range_max_km") if d_km is None else d_km) * 1e3
    gt = R.v("relay_gt_dbk") if gt_dbk is None else gt_dbk
    lam = 2.998e8 / f_hz
    eirp = 10 * math.log10(p_tx_w) + g_tx_dbi
    fspl = 20 * math.log10(4 * math.pi * d / lam)
    cn0 = eirp - fspl + gt + 228.6 - losses_db
    rate_db = cn0 - ebn0_req_db - margin_db
    return dict(eirp_dbw=eirp, fspl_db=fspl, cn0_dbhz=cn0, max_rate_bps=10 ** (rate_db / 10))


def comm_availability(a_surface=0.90, a_relay=0.80, a_dte=None) -> dict:
    a_dte = R.v("dte_availability") if a_dte is None else a_dte
    rows = {
        "C1 DTE only": a_dte,
        "C2 relay only": a_relay,
        "C3 surface network only": a_surface,
        "C4 surface network + relay + mesh + DTN (selected)": 1 - (1 - a_surface) * (1 - a_relay),
        "C5 C4 + DTE backup": 1 - (1 - a_surface) * (1 - a_relay) * (1 - a_dte),
    }
    return rows


# ============================================================================== TS-09 autonomy
def autonomy_task_time(n_motions: int = 300, rtt_s: float = 8.0, think_s: float = 10.0, move_s: float = 15.0,
                       n_holds: int = 8, approval_wait_min: float = 10.0, exec_h: float = 2.0,
                       link_avail_teleop: float = 0.51) -> list[dict]:
    """Time to complete a representative ORU swap under different control architectures."""
    teleop_h = n_motions * (rtt_s + think_s + move_s) / 3600 / link_avail_teleop
    supervised_h = exec_h + n_holds * approval_wait_min / 60
    return [
        dict(option="AU1 Earth joystick teleoperation", task_h=teleop_h, works_in_outage=False,
             contact_safety="poor: force loops through 8 s latency", operator_h=teleop_h, selected=False),
        dict(option="AU2 local crew teleoperation (crew present only)", task_h=n_motions * (0.2 + think_s + move_s) / 3600,
             works_in_outage=True, contact_safety="good", operator_h=n_motions * (think_s + move_s) / 3600,
             selected=False),
        dict(option="AU3 supervised autonomy: verified skills + hold-point approvals (selected)", task_h=supervised_h,
             works_in_outage=True, contact_safety="good: local F/T loops, deterministic guards",
             operator_h=n_holds * 0.1, selected=True),
        dict(option="AU4 full autonomy (no human approval)", task_h=exec_h, works_in_outage=True,
             contact_safety="unverifiable for novel faults", operator_h=0.0, selected=False),
    ]


# ============================================================================== TS-10 structural materials
ARM_LINK_MATERIALS = {
    "CFRP high-modulus tube": dict(E=120e9, rho=1600.0, allow=400e6, cte=0.5e-6),
    "Al 7075-T7351 tube": dict(E=71.7e9, rho=2810.0, allow=390e6 / 1.25 * 1.4, cte=23.4e-6),
    "Ti-6Al-4V tube": dict(E=113.8e9, rho=4430.0, allow=880e6 / 1.25 * 1.4, cte=8.6e-6),
}


def arm_material_comparison() -> list[dict]:
    from tsr1.manipulation.arm import ArmSpec, size_arm
    out = []
    for name, m in ARM_LINK_MATERIALS.items():
        reg_backup = {k: R.params[k] for k in ("cfrp_E", "cfrp_rho", "cfrp_allow")}
        try:
            R.params["cfrp_E"] = replace(reg_backup["cfrp_E"], value=m["E"], low=None, high=None)
            R.params["cfrp_rho"] = replace(reg_backup["cfrp_rho"], value=m["rho"], low=None, high=None)
            R.params["cfrp_allow"] = replace(reg_backup["cfrp_allow"], value=m["allow"], low=None, high=None)
            r = size_arm(ArmSpec("dex", (0.75, 0.70, 0.15), 20.0, 0.003, 7, 3, 6.0, 3.0, math.radians(5)))
            out.append(dict(material=name, arm_mass_kg=r.mass, link_mass_kg=sum(r.link_mass),
                            specific_stiffness_MNm_per_kg=m["E"] / m["rho"] / 1e6, cte_per_K=m["cte"],
                            thermal_growth_mm_1p5m_250K=m["cte"] * 1.5 * 250 * 1e3))
        finally:
            R.params.update(reg_backup)
    return out


def chassis_material_comparison(mass_supported: float) -> list[dict]:
    from tsr1.structures.chassis import FACE_MATERIALS, size_chassis
    out = []
    for mat in FACE_MATERIALS:
        r = size_chassis(mass_supported, material=mat)
        out.append(dict(material=mat, chassis_mass_kg=r.mass, t_face_mm=r.t_face * 1e3, f1_Hz=r.f1,
                        cte_per_K=FACE_MATERIALS[mat]["cte"], source=FACE_MATERIALS[mat]["src"]))
    return out


# ============================================================================== CDR-01 service kit
KIT_SUBSYSTEMS = ("manipulation", "tools", "recovery", "service_spine")
KIT_COMPONENTS = ("power_transfer_module", "power_tether_and_reel", "dust_tolerant_connector_head",
                  "thermal_ir_imager", "macro_inspection_camera", "electrical_diagnostic_unit", "contact_vibration_sensors",
                  "lidar_front", "autonomy_computer_hpsc", "safety_rt_computer_A", "optics_eds_and_covers")


def service_kit(cfg) -> dict:
    """Mass of the TSR-1 service-and-recovery functions packaged as a kit for a host utility rover.
    Adds a kit motor-control share (0.4 kg/actuator), kit harness (8 % of kit CBE) and a 6 kg mounting/
    adapter frame; MGA by category + same system margin. Spades/winch need a host of ≥ ~1 t lunar-surface
    mass to develop the same restraint (restraint scales with host weight)."""
    from tsr1.common.params import REGISTRY as R
    items = [c for c in cfg.comps if c.subsystem in KIT_SUBSYSTEMS or c.name in KIT_COMPONENTS]
    n_act = sum(1 for c in items if c.category == "mechanism")
    cbe = sum(c.cbe for c in items) + 0.4 * n_act + 6.0
    cbe += 0.08 * cbe
    pred = sum(c.predicted for c in items) + (0.4 * n_act) * 1.25 + 6.0 * 1.2 + 0.08 * cbe * 1.6
    alloc = pred * (1 + R.v("system_margin"))
    return dict(kit_cbe_kg=cbe, kit_predicted_kg=pred, kit_allocation_kg=alloc,
                dedicated_delivered_kg=cfg.delivered_mass, chassis_and_rest_kg=cfg.delivered_mass - alloc,
                host_requirements=dict(payload_kg=alloc, power_continuous_W=max(cfg.mode_power("M5_manipulation"), 500.0),
                                       power_transfer_W=3000.0, bus="ISPSIS 120 VDC", min_host_mass_for_recovery_kg=1000.0,
                                       deck_interface="service-spine slot standard + 2 arm bases + crane turntable"))
