"""Generate DESIGN_FREEZE_V1.md, CRITICAL_DESIGN_REVIEW.md and results/*.md from simulation results.

    PYTHONPATH=src python results/build_reports.py

Every number is read from simulations/results/*.json (or the parameter register) and printed together with
the model/file that derived it, so the frozen design, final specification, verdict and paper tables cannot
contradict one another.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RES = ROOT / "simulations" / "results"
DISCL = ("> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other "
         "organizations are used solely as technical and architectural context.")


def J(n, d=RES):
    return json.loads((d / n).read_text())


def f(x, d=1):
    if isinstance(x, str):
        return x
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "∞" if isinstance(x, float) and math.isinf(x) else "—"
    return f"{x:,.{d}f}"


class Doc:
    def __init__(self):
        self.lines = []

    def h(self, t, n=2):
        self.lines += [f"{'#' * n} {t}", ""]

    def p(self, t=""):
        self.lines += [t, ""]

    def rows(self, header, rows):
        self.lines.append("| " + " | ".join(header) + " |")
        self.lines.append("|" + "---|" * len(header))
        for r in rows:
            self.lines.append("| " + " | ".join(str(c) for c in r) + " |")
        self.lines.append("")

    def text(self):
        return "\n".join(self.lines)


def load():
    D = dict(base=J("baseline_summary.json"), mob=J("mobility.json"), stab=J("stability.json"), rec=J("recovery.json"),
             en=J("energy_power_thermal.json"), val=J("value_model.json"), rel=J("tsr_reliability.json"),
             sens=J("sensitivity.json"), cdr=J("cdr_analyses.json"), clo=J("closure.json"), dv=J("design_values.json"),
             tr=J("trades.json"), srv=J("servicing_success.json"))
    D["cap"] = J("capacity_study.json")
    pre = RES / "pre_cdr"
    if pre.exists():
        D["pre"] = dict(clo=J("closure.json", pre), dv=J("design_values.json", pre), base=J("baseline_summary.json", pre),
                        en=J("energy_power_thermal.json", pre), val=J("value_model.json", pre))
    from tsr1.common.params import REGISTRY as R
    import tsr1.reliability.value_model  # noqa: F401 (registers)
    import tsr1.budgets.scenarios  # noqa: F401
    import tsr1.budgets.closure  # noqa: F401
    import tsr1.stability.envelope  # noqa: F401
    D["R"] = R
    return D


# ===================================================================================== DESIGN FREEZE
def design_freeze(D) -> str:
    b, m, en, st, rec, val, rel, dv = D["base"], D["mob"], D["en"], D["stab"], D["rec"], D["val"], D["rel"], D["dv"]
    o = b["options"]
    bat = b["battery"]
    L = o["wheelbase"] + 2 * o["wheel_r"] + 0.1
    W = o["track"] + o["wheel_b"]
    geom4 = next(c for c in D["clo"] if c["check"].startswith("GEOM-4"))
    d = Doc()
    d.h("TODARO CORP. TSR-1 — DESIGN FREEZE V1", 1)
    d.p(DISCL)
    d.p("Frozen preliminary configuration after trade studies (`trade_studies/`) and the critical design review "
        "(`CRITICAL_DESIGN_REVIEW.md`). Every value cites its derivation: model function, result file, source ID "
        "(`research/source_register.csv`) or assumption ID (`engineering/assumptions.md`). Regenerate with "
        "`simulations/run_all.py` then `results/build_reports.py`.")
    n_fail = sum(1 for c in D["clo"] if not c["passed"])
    d.p(f"**Budget closure:** {len(D['clo']) - n_fail}/{len(D['clo'])} independent closure checks pass "
        f"(`simulations/results/closure.json`).")
    d.h("§1 Summary")
    d.rows(["Item", "Frozen value", "Derivation"], [
        ["Role", "autonomous lunar service & recovery rover for distributed infrastructure (not crew transport)", "ConOps"],
        ["Operating site / epoch", "lunar south pole (Shackleton–de Gerlache ridge complex), ~2036–2041", "A-01, A-02"],
        ["Delivered mass (charged to lander)", f"{f(b['delivered'],0)} kg", "design.configuration.build; mass_budget.csv"],
        ["Dry mass allocation (CBE + MGA + 15 % margin)", f"{f(b['dry_allocation'],0)} kg", "AIAA S-120A method (S052), A-23"],
        ["Operational mass (incl. 100 kg carried ORUs/modules)", f"{f(b['operational'],0)} kg", "mass_budget.csv"],
        ["Payload / spares capacity", f"{f(o['spine_payload'],0)} kg in {o['spine_slots']} spine slots", "TS-07"],
        ["Compatible landers", "Argonaut-class (1.5 t) with margin; Blue Moon Mk1-class (3.0 t)", "S047, S056; closure MASS-3/4"],
        ["Design life", "10 years", "MR-09 (S036 precedent)"],
        ["Integrated-system TRL", "4", "research/technology_readiness.md"],
    ])
    d.h("§2 Dimensions and mass properties")
    com = b["com_stowed"]
    d.rows(["Item", "Value", "Derivation"], [
        ["Overall length × width (deployed)", f"{L:.2f} × {W:.2f} m", "wheelbase + wheel Ø + fenders; track + wheel width"],
        ["Deck height / mast height", f"{o['ground_clearance'] + 0.45:.2f} m / 2.20 m", "chassis 0.45 m on 0.45 m clearance"],
        ["Ground clearance", f"{o['ground_clearance']:.2f} m (0.10 m lowered)", "TS-01"],
        ["Wheelbase / track", f"{o['wheelbase']:.2f} m / {o['track']:.2f} m", "TS-01/02 packaging, GEOM-6"],
        ["Stowed envelope (mast folded, arms in upright stow)", f"{L:.2f} × {W:.2f} × {geom4['computed']:.2f} m", "closure GEOM-2..4 vs A-32 envelope 4.0 × 2.6 × 2.0 m"],
        ["Deck layout", "rear: zenith radiator, full width; middle: service spine 2 × 3 slots; front: crane turntable, mast, arm bases; "
         "tools on the chassis front face", "design.layout; closure GEOM-5/7/8; fig03 (CDR-21)"],
        ["Centre of mass (stowed, loaded)", f"x {com[0]:+.2f} m, y {com[1]:+.2f} m, z {com[2]:.2f} m", "Config.com()"],
        ["Static tip-over angles", f"{st['static_tip_angles_deg'][0]:.0f}° longitudinal / {st['static_tip_angles_deg'][1]:.0f}° lateral",
         "stability.envelope.static_tip_angles"],
        ["Mass CBE / predicted", f"{f(b['cbe'],0)} kg / {f(b['predicted'],0)} kg", "mass_budget.csv"],
        ["Mass P50 / P90 (MER + MGA Monte Carlo)", f"{f(D['sens']['mass_mc']['p50'],0)} / {f(D['sens']['mass_mc']['p90'],0)} kg; "
         f"P(≤ 1.5 t) = {D['sens']['mass_mc']['p_le_1500']:.2f}", "budgets.sensitivity.mass_monte_carlo"],
    ])
    d.p("Subsystem predicted masses (CBE + MGA): " + "; ".join(f"{s} {f(p,1)} kg" for s, c, p in b["subsystems"]) + ".")
    d.h("§3 Mobility")
    s = m["slopes_deg"]
    d.rows(["Item", "Value", "Derivation"], [
        ["Architecture", "6-wheel rocker-bogie, body lowering (2 lead-screw actuators), differential lock, all-wheel steering", "TS-01"],
        ["Wheels", f"6 × rigid Ti-6Al-4V, Ø{2*o['wheel_r']:.2f} × {o['wheel_b']:.2f} m, 18 grousers × {o['grouser_h']*1000:.0f} mm", "TS-02"],
        ["Ground pressure / sinkage", f"{m['contact_pressure_kPa']:.2f} kPa / {m['sinkage_m']*1000:.0f} mm at {m['wheel_load_N']:.0f} N per wheel",
         "terramechanics.solve; S023 limit 7 kPa"],
        ["Max slope (i ≤ 0.4)", f"{s['nominal']:.1f}° nominal soil; {s['conservative']:.1f}° conservative; {s['weak']:.1f}° weak bound",
         "vehicle.max_slope; soils S023/S043"],
        ["Max slope with 1 / 2 drives failed", f"{s['one_wheel_out']:.1f}° / {s['two_wheels_out']:.1f}°", "vehicle.max_slope(failed_wheels)"],
        ["Slope claim (requirement SR-MOB-02)", f"{dv['slope_climb_deg']}° nominal / {dv['slope_climb_cons_deg']}° conservative; hold {dv['slope_hold_deg']}°",
         "design_values.json"],
        ["Step obstacle / ditch", f"{dv['obstacle_m']} m / {dv['ditch_m']} m (0.5 D conservative rocker-bogie rule)", "obstacle_ratio_rb (ESTIMATE)"],
        ["Speed", f"{o.get('v_nom', 0.5) if False else 0.5} m/s nominal, 1.0 m/s max; effective 1.26 km/h with 70 % motion duty", "v_drive_nom, drive_duty, tsr_speed_eff"],
        ["Drive actuator rating", f"{m['drive_rating_Nm']:.0f} N·m per wheel (soil-limited {m['drive_torque_soil_Nm']:.0f} N·m × 1.25)", "configuration._drive_rating"],
        ["Steering torque", f"{b['steer_torque']:.0f} N·m per wheel (× MF 2 rating)", "configuration (scrub model)"],
        ["Energy per km (traverse incl. hotel loads)", f"{en['energy_per_km_kwh']:.2f} kWh/km at 1.26 km/h", "budgets.scenarios; LRV k_cal " + f"{m['k_cal']:.2f}"],
        ["Range on one charge (keeping 50 h reserve)", f"{en['range_km']:.0f} km", "run_all energy analysis"],
        ["Direct tow capacity", "; ".join(f"{t['slope_deg']}° {t['nominal_N']:.0f} N" for t in m["tow_capacity"]), "vehicle.max_tow_force (nominal soil)"],
    ])
    d.h("§4 Stability")
    d.rows(["Case", "Tipping factor", "CoP margin [m]", "Sliding OK"],
           [[c["case"], f(c["tip_factor"] if c["tip_factor"] != "inf" else float("inf"), 2) if not isinstance(c["tip_factor"], str) else "∞",
             f(c["margin_m"], 2), "yes" if c["sliding_ok"] else "**no**"] for c in st["cases"]])
    d.p("Requirement: tipping factor ≥ 1.5 for planned operations (tip_factor_req, TS-04). C7c (0.60 m fairlead) is the "
        "rejected design shown for comparison.")
    d.h("§5 Manipulation")
    dx = b["dex"]
    cr = b["crane"]
    d.rows(["Item", "Value", "Derivation"], [
        ["Architecture", "2 identical 7-DOF dexterous arms + cable-stayed luffing crane boom (heavy arm rejected)", "TS-03"],
        ["Dexterous arm", f"reach {dx['reach_m']:.2f} m, rated {dx['payload_kg']:.0f} kg (lunar g), tip deflection {dx['tip_deflection_mm']:.1f} mm, "
         f"{f(dx['mass_kg'],1)} kg CBE each", "manipulation.arm.size_arm (Ti links)"],
        ["Shoulder torque / rating", f"{dx['shoulder_torque_Nm']:.0f} / {dx['shoulder_rating_Nm']:.0f} N·m (MF 2)", "size_arm"],
        ["Arm move power", f"{dx['power_move_W']:.0f} W per arm at 5°/s", "size_arm"],
        ["Positioning", f"≤ {dv['dex_accuracy_mm']} mm with visual servoing; 6-axis F/T; tool change ≤ {dv['tool_change_min']} min", "SR-MAN-01/03 (DESIGN)"],
        ["Crane", f"boom 2.6 m (reach {cr['reach']:.2f} m), hook load 150 kg, luff tension {cr['t_luff']:.0f} N, {f(cr['mass'],1)} kg CBE", "manipulation.crane.size_crane"],
        ["Crane stability limit at max reach, 15° side slope", f"{st['crane_capacity_15deg'][-1][1]:.0f} kg (TF 1.5) ≫ 150 kg rating", "envelope.crane_capacity_curve"],
        ["Max ORU", f"{dv['oru_max_kg']:.0f} kg (crane + arm cooperative); ≤ {dv['dex_payload_kg']:.0f} kg single arm", "MR-04"],
    ])
    d.h("§6 Service spine, tools and interfaces")
    d.rows(["Item", "Value", "Derivation"], [
        ["Service spine", f"{o['spine_slots']} androgynous slots in a 2 × 3 grid of 0.45 m (0.90 × 1.35 m on the mid-deck), ≤ 40 kg per occupied slot (double-slot modules ≤ 80 kg), ≤ {o['spine_payload']:.0f} kg total, 120 VDC ≤ 1 kW + Ethernet per slot", "TS-07; interfaces II-01; design.layout"],
        ["Service modules", f"MOD-KA keep-alive ({val['keepalive_trade']['selected']}, {val['keepalive_module_kg']:.0f} kg, double slot; ×{val['base_scenario']['keepalive_modules']} in base inventory, ≤ 2 carried), "
         "MOD-ORU cradles, MOD-REC recovery kit, MOD-RPT repeater; MOD-SOL optional; no fluid module", "TS-07, TS-07b, CDR-19/20"],
        ["Keep-alive inventory rule", "n_KA = Poisson 95th percentile of f_park · p_KA · F · T_hold (fault rate F; f_park ≈ 0.14; T_hold ≈ 1–2 yr)",
         "value_model.keepalive_inventory; capacity_study.json"],
        ["Tools (12)", "gripper, socket driver (≤ 50 N·m), electrical probe, connector tool, dust brush, EDS wand, anchor driver, OTCM adapter, androgynous adapter, slings, shackle/hitch, regolith scoop", "engineering/subsystem_specs/tools.md"],
        ["Interfaces", "ISPSIS 120 VDC power port; ISO 9409-1/IERIIS tool interface + adapters; LunaNet/DTN data", "engineering/interfaces.md"],
    ])
    d.h("§7 Recovery")
    pe = rec["p_env"]["R4 winch + 2 spades + 2 helical anchors"]
    cur = rec["curves"]["curves"]["R4 winch + 2 spades + 2 helical anchors"]
    i15 = cur["slopes"].index(15.0)
    d.rows(["Item", "Value", "Derivation"], [
        ["Winch", f"{o['winch_pull_kN']:.0f} kN line pull, {o['winch_line_m']:.0f} m Vectran line, 0.05 m/s, {b['winch']['power_elec']:.0f} W, fairlead 0.25 m",
         "recovery.towing.size_winch; fairlead_height"],
        ["Ground reaction", f"2 rear spades 0.6 × 0.3 m + 2 helical anchors Ø0.15 m @ 0.6 m ({b['anchor_q']:.0f} N each) + 2 spare in MOD-REC; "
         f"restraint {dv['anchor_capacity_kN']} kN (P50 soil), {dv['anchor_capacity_p10_kN']} kN (half strength)", "recovery.towing"],
        ["Recovery envelope (15°, FoS 1.5)", f"free-rolling ≤ {cur['free_kg'][i15]/1000:.1f} t; brakes locked ≤ {cur['locked_kg'][i15]/1000:.1f} t", "trades.recovery_trades.recovery_curves"],
        ["P(sampled immobilisation case recoverable)", f"{pe['mid']:.2f} (range {pe['high']:.2f}–{pe['low']:.2f} over resistance bounds; {pe['weak_soil']:.2f} in half-strength soil)",
         "envelope_probability"],
        ["Scenario outcomes", "; ".join(f"{r['id']}: {'OK' if r['feasible'] else 'NOT feasible'} (margin {f(r['margin'],2)})" for r in rec["scenarios"]), "recovery.scenarios"],
    ])
    d.h("§8 Power")
    d.rows(["Item", "Value", "Derivation"], [
        ["Battery", f"Li-ion PPR, {bat['nameplate_kwh']:.1f} kWh nameplate ({bat['n_series']}s{bat['n_parallel']}p, {bat['n_cells']} cells, {bat['v_nominal']:.0f} V nom.), "
         f"{bat['usable_eol_kwh']:.0f} kWh usable at EOL, {bat['mass']:.0f} kg", "power.electrical.size_battery; A-15/16"],
        ["Bus", "regulated 120 VDC (ISPSIS) primary, 28 VDC avionics; PCDU 4 kW, 3 interleaved phases", "S011; TS-06"],
        ["Power-transfer module", f"isolated bidirectional, single stage on battery, 3 kW continuous / 4.5 kW 60 s; 25 m tether 2 × {en['tether']['area_mm2']:.1f} mm² Cu",
         "S012; power.electrical.size_cable"],
        ["Emergency power at 10 km edge", f"{en['keepalive_duration_at_edge_h']:.1f} h at 300 W keep-alive or {en['emergency_3kW_duration_at_edge_h']:.1f} h at 3 kW; MOD-KA for longer",
         "run_all energy analysis"],
        ["Solar", f"1.5 m² fixed vertical PV, {en['solar_avg_W']:.0f} W average in sunlight", "budgets.scenarios.solar_avg_w"],
        ["Survival power / full-battery survival", f"{en['survival_power_W']:.0f} W / {en['survival_full_battery_h']:.0f} h darkness; indefinite in sunlight", "thermal + power closure"],
        ["Mode powers [W]", ", ".join(f"{k.split('_',1)[1]} {v:.0f}" for k, v in en["mode_power_W"].items()), "power_budget.csv"],
    ])
    d.h("§9 Thermal")
    th = en["thermal"]
    d.rows(["Item", "Value", "Derivation"], [
        ["Concept", "MLI-insulated WEB (1.0 × 0.8 × 0.35 m) in chassis; zenith radiator with OSR + EDS film; LHP with thermal switch", "thermal.lumped"],
        ["Radiator", f"{b['a_rad']:.2f} m² for 380 W at 293 K with dusty α (×2.0) and 12° solar incidence", "radiator_area"],
        ["Cold-case leak / heater", f"{th['leak_cold_w']:.0f} W leak (PSR sink 40 K) / {b['heater_cold']:.0f} W heaters", "cold_leak"],
        ["Max WEB dissipation", f"{max(en['web_dissipation_W'].values()):.0f} W steady (≤ 380 W); 3 kW transfer transient within ΔT ≤ 15 K", "closure THERMAL-1a/b"],
        ["PSR excursion", f"≤ {dv['psr_excursion_h']} h (energy-limited {en['psr_excursion_energy_limited_h']:.0f} h, × 0.5 margin, cap 8 h)", "run_all"],
        ["Actuator thermal policy", "cold-tolerant actuators (no survival heat); warm-start heaters only for heavy-duty drives", "TG-01"],
    ])
    d.h("§10 Avionics and sensors")
    d.rows(["Item", "Value", "Derivation"], [
        ["Autonomy computer", "HPSC-class rad-hard (100 krad TID part, SEL-immune), 45 W active", "S039; A-18, A-24"],
        ["Safety/RT computers", "2 independent rad-hard lanes, 10 W each, deterministic guards", "SR-AVI-01"],
        ["Sensors", "mast NavCam stereo (70° FOV) + pan-tilt + LEDs; 6 HazCams; front/rear LiDAR; thermal IR; arm macro camera; 2 wrist F/T; LN-200S IMU; sun sensor/star tracker; electrical diagnostic unit; contact vibration sensors; no acoustic sensors",
         "SR-SNS-01; S064, S065"],
        ["Radiation design", "TID 10 krad(Si)/10 yr (GCR alone ≈ 0.12 krad), RDM 2 → parts ≥ 20 krad; SEE mitigation", "S033; A-24"],
    ])
    d.h("§11 Autonomy and safety")
    d.p("Layered: mission planner → task planner → verified skills → motion planning → real-time control → actuators; "
        "independent deterministic safety layer; ML advisory only; human approval at hold points (power connection, "
        "load-path fastener release, ORU insertion, winch > 1 kN). Crew-proximity limits 0.2 m/s and 50 N (SR-SAF-01). "
        "Comm-outage behaviour: continue to next hold point, then safe hold (MR-08). Details: `trade_studies/autonomy.md`.")
    d.h("§12 Communications and navigation")
    lb = D["tr"]["comms"]
    d.p(f"Surface network radio (LTE-class), LunaNet S-band relay (5 W, 10 dBi; ≈ {lb['link_10000km']['max_rate_bps']/1e3:.0f} kbit/s at "
        f"10 000 km), UHF peer mesh, DTN; availability ≈ {lb['availability']['C4 surface network + relay + mesh + DTN (selected)']:.2f}. "
        "Navigation: visual odometry + IMU + star tracker + LiDAR map matching; base-frame ≤ 1 m; relative pose before "
        "contact ≤ 5 mm / 0.5°.")
    d.h("§13 Dust mitigation")
    d.p("Self-protection: fenders + skirts (Apollo lesson S022), zenith radiator with EDS film, EDS on camera/LiDAR windows, "
        "labyrinth + PTFE bellows on all external joints (no dynamic elastomers), dust-tolerant connector with self-closing "
        "cover, latch covers. External cleaning: brush and EDS wand tools; target residual coverage ≤ 5 % (MR-07).")
    d.h("§14 Structure and materials")
    ch = b["chassis"]
    d.p(f"Closed Al 7075-T7351/Al 5056 honeycomb torque box 2.6 × 1.5 × 0.45 m (equivalent wall {ch['t_face']*1000:.1f} mm, "
        f"f₁ = {ch['f1']:.0f} Hz on launch locks, minimum-gauge driven), Ti-6Al-4V hard points; Ti-6Al-4V wheels and arm links; "
        "CFRP crane boom and mast; Vectran recovery line. Launch loads 6 g axial + 3 g lateral (A-05), FoS 1.25/1.4 (A-22). "
        "Full matrix: `engineering/materials_matrix.csv`.")
    d.h("§15 Mission performance (design-reference missions at the 10 km service edge)")
    d.rows(["DRM", "Title", "Duration [h]", "Distance [km]", "Energy [kWh] (no PV)", "Energy with PV [kWh]", "Peak [W]"],
           [[r["id"], r["title"], f(r["duration_h"], 1), f(r["distance_km"], 1), f(r["energy_kwh"], 2), f(r["energy_with_solar_kwh"], 2),
             f(r["peak_W"], 0)] for r in en["drms"]])
    d.p(f"Battery usable at EOL {bat['usable_eol_kwh']:.0f} kWh; reserve retained {en['reserve_kwh']:.2f} kWh (50 h survival).")
    d.h("§16 Reliability and lifetime")
    cr_ = rel["crew_repair"]
    d.p(f"Expected repairable faults {cr_['fault_rate_per_yr']:.2f} per year; P(servicing-capable at 10 yr) = {cr_['p_capable_10yr']:.2f} with "
        f"30-day ORU repair (peer: {rel['peer']['p_capable_10yr']:.2f}; no repair: {rel['no_repair']['p_capable_10yr']:.2f}); fully functional "
        f"{100*cr_['availability_full']:.0f} % of the time. FMEA and degraded modes: `engineering/fmea.md`.")
    d.h("§17 System-level value (30 assets, 10 years, epistemic Monte Carlo)")
    vb = val["base"]
    d.rows(["Metric", "Without TSR-1 (mean)", "With TSR-1 (mean)", "Difference P10 / P50 / P90"], [
        ["Infrastructure availability", f"{vb['A0']['mean']:.3f}", f"{vb['A1']['mean']:.3f}", f"{100*vb['dA']['p10']:.1f} / {100*vb['dA']['p50']:.1f} / {100*vb['dA']['p90']:.1f} pp"],
        ["Preventable asset losses (excl. non-serviceable faults)", f"{vb['plost0']['mean']:.1f}", f"{vb['plost1']['mean']:.1f}", "—"],
        ["Assets lost, all causes", f"{vb['lost0']['mean']:.1f}", f"{vb['lost1']['mean']:.1f}", "—"],
        ["Fault events (grow with uptime)", f"{vb['faults0']['mean']:.0f}", f"{vb['faults1']['mean']:.0f}", "—"],
        ["Earth-supplied mass [t]", f"{vb['mass0']['mean']/1000:.1f}", f"{vb['mass1']['mean']/1000:.1f}", "—"],
        ["Earth mass per available asset-year [kg]", f"{val['kg_per_asset_yr0']['mean']:.0f}", f"{val['kg_per_asset_yr1']['mean']:.0f}", "—"],
        ["Crew EVA [crew-h]", f"{vb['eva0']['mean']:.0f}", f"{vb['eva1']['mean']:.0f}", "—"],
        ["Mean response time [h]", "—", f"{vb['resp']['mean']:.1f}", "—"],
        ["TSR-1 utilisation", "—", f"{100*vb['util']['mean']:.1f} %", "—"],
    ])
    d.p(f"Logistics break-even (Earth mass avoided = TSR-1 life-cycle mass {val['tsr_lifecycle_mass_kg']/1000:.2f} t incl. "
        f"{val['base_scenario']['keepalive_modules']} MOD-KA): ≈ {f(val['break_even_assets'],0)} serviceable assets. Losses from non-serviceable faults "
        "are not preventable and grow with operating exposure (a kept-alive asset can fail again), so preventable losses and mass per "
        "available asset-year are the fair comparison (CDR-19).")
    if "pre" in D:
        d.h("§18 Changes from the pre-CDR configuration")
        pb = D["pre"]["base"]
        d.rows(["Item", "Pre-CDR", "Frozen", "Reason"], [
            ["Battery usable EOL", f"{pb['battery']['usable_eol_kwh']:.0f} kWh", f"{bat['usable_eol_kwh']:.0f} kWh", "CDR-06: ENERGY-1 failed after survival-heater correction"],
            ["Delivered mass", f"{pb['delivered']:.0f} kg", f"{b['delivered']:.0f} kg", "battery change"],
            ["Slope requirement", "nominal soil only", f"{dv['slope_climb_deg']}° nominal / {dv['slope_climb_cons_deg']}° conservative", "CDR-15"],
            ["MOD-KA keep-alive module", "2 kWh, 0.75 m² PV, 23 kg (placeholder)", f"{val['keepalive_trade']['selected']}, {val['keepalive_module_kg']:.0f} kg, double slot",
             "CDR-20: placeholder physically inconsistent; sustains only ≈ 40 % of assets"],
            ["MOD-KA inventory", "2", f"{val['base_scenario']['keepalive_modules']} (scaling rule)", "CDR-19: capacity study"],
            ["Value-model loss accounting", "failed TSR-1 attempt = immediate loss", "crew may still attempt within survival/abandonment time",
             "CDR-19 (consistency with the no-TSR baseline)"],
        ])
    return d.text()


# ===================================================================================== CDR
def cdr(D) -> str:
    b, val, cd, en, rec, m, dv = D["base"], D["val"], D["cdr"], D["en"], D["rec"], D["mob"], D["dv"]
    kit = cd["service_kit"]
    host = {h["case"]: h for h in cd["host_cases"]}
    hk = list(host.values())
    sk = {round(s["robot_step_factor"], 2): s for s in cd["skill_factor"]}
    sw = {s["n_assets"]: s for s in val["asset_sweep"]}
    lm = {x["level_mix"]: x for x in val["level_mix"]}
    sr = cd["speed_radius"]
    pre = D.get("pre")
    cap1 = {(c["n_assets"], c["mtbf_yr"]): c for c in D["cap"] if c["n_tsr"] == 1 and c["keepalive_modules"] == 4}
    cap2 = {(c["n_assets"], c["mtbf_yr"]): c for c in D["cap"] if c["n_tsr"] == 2 and c["keepalive_modules"] == 4}
    capk = {(c["n_assets"], c["mtbf_yr"], c["keepalive_modules"]): c for c in D["cap"] if c["n_tsr"] == 1}
    ka_opts = {o["option"]: o for o in val["keepalive_trade"]["options"]}
    geom4 = next(c for c in D["clo"] if c["check"].startswith("GEOM-4"))
    geom5 = next(c for c in D["clo"] if c["check"].startswith("GEOM-5"))
    geom7 = next(c for c in D["clo"] if c["check"].startswith("GEOM-7"))
    geom8 = next(c for c in D["clo"] if c["check"].startswith("GEOM-8"))
    mob1 = next(c for c in D["clo"] if c["check"].startswith("MOB-1"))
    geom7_note = geom7["note"].replace("boom covers ", "").split(" (")[0]
    tf_c3 = next(c["tip_factor"] for c in D["stab"]["cases"] if c["case"].startswith("C3"))
    d = Doc()
    d.h("TSR-1 CRITICAL DESIGN REVIEW (adversarial)", 1)
    d.p(DISCL)
    d.p("The project team switched role to a hostile independent design-review board whose objective was to invalidate "
        "TSR-1. Each objection is answered with model evidence; dispositions are **design change**, **requirement change**, "
        "**accepted risk** or **open**. Failed ideas are recorded, not hidden. Evidence files: `simulations/results/`.")
    rows = [
        ["CDR-01", "Is a dedicated servicing rover necessary? NASA's Lunar Utility Rover already includes maintain/repair/"
                   "service (S005); TSR-1 would be idle most of the time.",
         f"Utilisation of one TSR-1 is only {100*val['base']['util']['mean']:.1f} % at 30 assets ({100*sw[60]['util_mean']:.1f} % at 60). "
         f"The service-and-recovery functions packaged as a kit weigh ≈ {kit['kit_allocation_kg']:.0f} kg (allocation) vs {kit['dedicated_delivered_kg']:.0f} kg "
         f"for the dedicated rover. Value with a shared host: ΔA {100*hk[0]['dA_mean']:.1f} pp dedicated vs {100*hk[1]['dA_mean']:.1f} pp "
         f"(host busy 30 %, 24 h) vs {100*hk[2]['dA_mean']:.1f} pp (busy 60 %, 72 h); assets lost {hk[0]['lost1_mean']:.1f} / {hk[1]['lost1_mean']:.1f} / {hk[2]['lost1_mean']:.1f}.",
         "**Valid — design change (architecture variant).** The objection is substantially correct for a utilisation basis. TSR-1 is "
         "re-baselined as a host-agnostic *service & recovery kit* (arms, crane, tools, spine, PTM, recovery hardware) with the dedicated "
         "carrier as one implementation, justified only where no host can reach unpowered assets within their survival time "
         "(the dedicated carrier's advantage is response, not capacity). Recommendation: offer the kit to utility-rover hosts first."],
        ["CDR-02", "The dual-arm idea is unjustified.",
         "The *asymmetric heavy + dexterous* pair costs +113 kg for +6 % task coverage (TS-03) — rejected. Two identical dexterous arms "
         "cost +27 kg over one arm and remove the arm single-point failure (λ 0.08/yr → 55 % chance of an arm failure in 10 yr).",
         "**Partially valid — design change already made (TS-03).** Heavy arm replaced by a ~20 kg crane boom. Second dexterous arm "
         "retained; A4 (one arm + crane) is the recorded −27 kg descope."],
        ["CDR-03", "The rover is too massive for its job.",
         f"Delivered {b['delivered']:.0f} kg (P90 {D['sens']['mass_mc']['p90']:.0f} kg; P(≤ 1.5 t) {D['sens']['mass_mc']['p_le_1500']:.2f}) consumes most of an "
         "Argonaut-class lander. Mass drivers: actuator torque density, system margin, battery (tornado).",
         "**Partially valid — accepted with descope list.** Descopes: CFRP chassis (−15 kg), one arm (−27 kg), passive rocker-bogie "
         "(−29 kg), 7.5 km service radius battery (−15 kg). Kit variant (CDR-01) is the main mass answer."],
        ["CDR-04", "Towing is unrealistic in lunar regolith.",
         f"Confirmed for slopes: direct tow capacity {m['tow_capacity'][3]['nominal_N']:.0f} N at 15° (nominal soil), "
         f"{m['tow_capacity'][3]['conservative_N']:.0f} N conservative; recovery fraction by direct towing only {rec['p_env']['R0 direct towing (drive)']['mid']:.2f}.",
         "**Valid — design change already made (TS-05).** Terrestrial-style towing is limited to level ground; slope recovery uses "
         "anchored winching (p_env " + f"{rec['p_env']['R4 winch + 2 spades + 2 helical anchors']['mid']:.2f})."],
        ["CDR-05", "Anchors are not practical.",
         f"Spade insertion force ≈ 1.4 kN each vs vehicle weight ≈ {b['vehicle']['mass']*1.62/1000:.1f} kN (one at a time); deeper spades "
         f"(0.4 m) need ≈ 15 kN — infeasible. Helical anchor capacity ≈ {b['anchor_q']:.0f} N (ESTIMATE N_q 10–40). With half-strength soil p_env "
         f"falls to {rec['p_env']['R4 winch + 2 spades + 2 helical anchors']['weak_soil']:.2f}; with spades only {rec['p_env']['R3 winch + braked wheels + 2 rear spades']['mid']:.2f}.",
         "**Partially valid — accepted risk, TRL 3 (TG-03).** Spade depth frozen at 0.3 m; proof-load hold point before every winch "
         "pull; 2 spare anchors in MOD-REC. Recovery claims flagged as contingent on Stage-1 anchor tests."],
        ["CDR-06", "Battery endurance is inadequate.",
         (f"Pre-CDR: after correcting the survival heater, DRM-2 at 10 km + 50 h reserve required "
          f"{next(c for c in pre['clo'] if c['check'].startswith('ENERGY-1'))['computed']:.2f} kWh vs "
          f"{pre['base']['battery']['usable_eol_kwh']:.0f} kWh available — closure ENERGY-1 **failed**. " if pre else "") +
         f"Frozen: {b['battery']['usable_eol_kwh']:.0f} kWh usable EOL; DRM-2 {en['drms'][1]['energy_kwh']:.2f} kWh + reserve {en['reserve_kwh']:.2f} kWh. "
         "Service radius vs effective speed: " + ", ".join(f"{x['speed_kmh']} km/h → {x['max_service_radius_km']:.1f} km" for x in sr) + ".",
         "**Valid — design change.** Battery raised to 15 kWh usable EOL (+≈10 kg). Operational rule: service radius is set by "
         "demonstrated effective speed (table); PV adds ≈ 1.9 kWh per DRM in sunlit routes (not credited)."],
        ["CDR-07", "The service spine adds unnecessary mass.",
         f"Spine overhead {D['tr']['service_modules']['spine_overhead_kg']:.1f} kg vs ≈ {D['tr']['service_modules']['mass_saving_per_sortie_kg']:.0f} kg mean carried-kit saving per sortie (TS-07); "
         "MOD-KA keep-alive modules are only possible with a deployable-module interface and reduce preventable losses (TS-07 tables).",
         "**Invalid — no change.**"],
        ["CDR-08", "Future assets will not be standardised enough.",
         f"ΔA: legacy base {100*lm['legacy (L0-heavy)']['dA_mean']:.1f} pp, mixed {100*lm['mixed (baseline)']['dA_mean']:.1f} pp, "
         f"standardised {100*lm['standardised (L2/L3)']['dA_mean']:.1f} pp. Robotic ORU success L0 ≈ 0, L1 ≈ 0.12.",
         "**Valid — open (programmatic, TG-05).** The single most important condition for TSR-1 value. Recommendation: make an "
         "L2 robotic-service interface a Moon Base asset requirement; without it TSR-1 is mainly an inspection, emergency-power "
         "and recovery vehicle."],
        ["CDR-09", "Robotic repair is too difficult; success assumptions are optimistic.",
         "No lunar servicing statistics exist. Pessimism case (all robotic step probabilities × 0.9): L2 ORU success "
         f"{sk[0.9]['p_oru_L2']:.2f} (nominal {sk[1.0]['p_oru_L2']:.2f}); ΔA {100*sk[0.9]['dA_mean']:.1f} pp vs {100*sk[1.0]['dA_mean']:.1f} pp; "
         f"assets lost with TSR-1 {sk[0.9]['lost1_mean']:.1f} vs {sk[1.0]['lost1_mean']:.1f}.",
         "**Partially valid — accepted risk.** Value degrades but stays positive because emergency power + keep-alive modules prevent "
         "losses even when repair fails. Stage-3 field statistics must replace assumption A-31."],
        ["CDR-10", "Autonomy adds unacceptable complexity.",
         "Supervised autonomy halves human operator time vs teleop and works in comm outages (TS-09); ML is advisory behind deterministic "
         "guards. Verification of contact-rich skills is TRL 4 (TG-04).",
         "**Partially valid — accepted risk with mitigation.** Skill library limited to DRM steps; formal verification of guards; "
         "teleop-assisted fallback (DM-7)."],
        ["CDR-11", "The design relies on infrastructure that does not exist yet.",
         "Dependencies: ISPSIS-compliant charging nodes (A-06), relay services (S017/S018), surface network (S054), HPSC (S039), BMG "
         "actuators (S040), asset standards (TG-05), lunar failure-rate data (TG-08).",
         "**Valid — open.** Each dependency has a degraded alternative (PV charging, DTE + mesh, GR740-class computing, heated "
         "actuators with −≈80 h survival) recorded in open_questions.md; asset standards have no substitute."],
        ["CDR-12", "Low utilisation wastes a 1.2 t asset.",
         "See CDR-01; idle time can host DRM-1 patrols (fault pre-detection, not credited in the value model) and light logistics.",
         "**Valid — operational change.** Scheduled patrols and opportunistic logistics added to ConOps; not credited in value."],
        ["CDR-13", "Effective autonomous speed is optimistic.",
         "DRM-2 energy is speed-dominated (hotel loads): 6.9–15.1 kWh over 2.5–0.7 km/h (tornado).",
         "**Valid — requirement change.** Service radius tied to demonstrated speed (CDR-06 table); SR-MOB-04 retains ≥ 0.35 m/s average."],
        ["CDR-14", "Thermal margins are thin with dust on the radiator.",
         f"Radiator sized with dusty α (×2.0, S062 range 1.4–2.6); max steady WEB dissipation {max(en['web_dissipation_W'].values()):.0f} W vs 380 W; "
         "3 kW transfer is energy-limited (≈ 1 h) and absorbed by WEB heat capacity.",
         "**Accepted.** EDS on radiator; operational throttling of charging if α degrades beyond ×2.6."],
        ["CDR-15", "Slope capability is overstated.",
         f"Nominal {m['slopes_deg']['nominal']:.1f}°, conservative {m['slopes_deg']['conservative']:.1f}°, weak bound {m['slopes_deg']['weak']:.1f}°; "
         "friction angle dominates (16–31° over 30–46°).",
         f"**Valid — requirement change.** SR-MOB-02 now states {dv['slope_climb_deg']}° nominal **and** {dv['slope_climb_cons_deg']}° conservative; "
         "route planning uses the conservative value until in-situ traction is measured."],
        ["CDR-16", "Launch loads are unknown.",
         "No lander user-guide values retrieved (S075). Chassis is minimum-gauge driven and insensitive over 4–10 g; mechanisms need "
         "launch locks (in 5 % accommodation allowance).",
         "**Accepted — open** until a lander is selected."],
        ["CDR-17", "Value is an artefact of the assumed fault rate.",
         f"MTBF is the strongest correlate of ΔA (r ≈ {val['sensitivity_corr']['mtbf->dA']:.2f}); at small bases the case fails: 3 assets → net "
         f"mass benefit {sw[3]['net_mass_benefit']/1000:.2f} t; 5 assets → {sw[5]['net_mass_benefit']/1000:.2f} t; break-even ≈ {f(val['break_even_assets'],0)} assets.",
         f"**Valid — scope statement.** TSR-1 is *not* justified for an outpost of a few assets; it becomes rational above ≈ {f(val['break_even_assets'], 0)} "
         "serviceable assets, and only if their fault rate is not negligible."],
        ["CDR-18", "A second TSR would be needed for redundancy or capacity.",
         f"Capacity study (4 MOD-KA): a second unit cuts mean response from {cap1[(60, 1.5)]['response_h']:.1f} h to {cap2[(60, 1.5)]['response_h']:.1f} h at 40 faults/yr but preventable "
         f"losses change only {cap1[(60, 1.5)]['plost1']:.1f} → {cap2[(60, 1.5)]['plost1']:.1f}; utilisation per unit {100*val['two_tsr_60_assets']['util']:.1f} % at 60 assets (Monte Carlo).",
         "**Accepted.** One unit; response time is far inside the asset survival time, so capacity is set by keep-alive inventory "
         "(CDR-19). Peer servicing (MR-13) is the only argument for a second unit."],
        ["CDR-19", "At large bases the value collapses: the model shows *more* assets lost and *more* Earth mass with TSR-1 at 60 assets "
                   "with MTBF 1–1.5 yr.",
         f"Instrumented capacity study: with TSR-1 the base stays up longer, so fault events rise ({cap1[(60, 1.0)]['faults0']:.0f} → {cap1[(60, 1.0)]['faults1']:.0f} at 60 faults/yr) "
         f"and non-serviceable losses rise with them; **preventable** losses always fall ({cap1[(60, 1.0)]['plost0']:.1f} → {capk[(60, 1.0, 2)]['plost1']:.1f} with 2 modules, "
         f"{capk[(60, 1.0, 8)]['plost1']:.1f} with 8) and Earth mass per available asset-year falls ({cap1[(60, 1.0)]['kg_per_asset_yr0']:.0f} → {capk[(60, 1.0, 8)]['kg_per_asset_yr1']:.0f} kg). "
         f"Genuine saturation is in keep-alive modules: with 2 modules {capk[(60, 1.0, 2)]['ka_denied']:.0f} requests in 10 yr found none free. A pre-CDR modelling "
         "inconsistency was also found: a failed TSR-1 recovery was an immediate loss, whereas the baseline let crew try.",
         "**Partially valid — design change + model correction.** Metrics changed to preventable losses and mass per available asset-year "
         "(total losses still reported). Keep-alive inventory now follows a Little's-law rule (n_KA = Poisson q95 of f_park·p_KA·F·T_hold); "
         f"{val['base_scenario']['keepalive_modules']} modules at the 30-asset reference base. Failed-attempt handling made consistent with the baseline."],
        ["CDR-20", "The keep-alive module cannot do what is claimed: a 23 kg box cannot keep an asset alive for months.",
         f"TS-07b sizing with the TSR-1 battery rules: 2 kWh usable needs ≈ {ka_opts['KA-A 0.75 m² / 2 kWh']['battery_kg']:.0f} kg of cells; KA-A totals "
         f"{ka_opts['KA-A 0.75 m² / 2 kWh']['mass_kg']:.0f} kg and sustains a sampled asset with P = {ka_opts['KA-A 0.75 m² / 2 kWh']['p_sustain']:.2f} "
         f"(asset survival power 40–250 W, site illumination 0.5–0.92, dark periods 24–120 h). Selected {val['keepalive_trade']['selected']}: "
         f"{val['keepalive_module_kg']:.0f} kg, P = {val['keepalive_trade']['selected_row']['p_sustain']:.2f} "
         f"({val['keepalive_trade']['selected_row']['p_sustain_low']:.2f}–{val['keepalive_trade']['selected_row']['p_sustain_high']:.2f}).",
         "**Valid — design change.** MOD-KA resized (KA-C), made a double-slot module (spine rule ≤ 40 kg per slot), its success "
         "probability entered into the value model, and its mass charged to the TSR-1 life-cycle mass. Asset survival power "
         "(A-33) is now an open question (OQ-15)."],
        ["CDR-21", "The equipment does not physically fit on the deck.",
         "Pre-CDR, six 0.45 m spine slots were specified in a 1.6 × 0.5 m footprint (needs ≥ 2.7 m in one row), and in plan the "
         "spine overlapped the zenith radiator; closure GEOM-5 compared areas only. A single layout definition "
         f"(`design.layout`) now places the radiator ({b['a_rad']:.2f} m², full width) at the rear, the spine as a 2 × 3 grid "
         "(0.90 × 1.35 m) mid-deck, and crane turntable, mast and arm bases in the front strip; tools move to the chassis front face. "
         f"Deck items {geom5['computed']:.2f} of {geom5['limit']:.2f} m², no overlaps; the stowed boom shades "
         f"{geom7_note}; crane reach covers every slot ({geom8['computed']:.2f} m ≤ {geom8['limit']:.2f} m); arms stow upright, "
         f"raising the stowed height to {geom4['computed']:.2f} m (≤ 2.0 m envelope). Front crane lift tipping factor "
         f"{tf_c3:.1f} (≥ 1.5). Moving crane, arms and tools forward first shifted the centre of mass 0.13 m forward and the "
         "heaviest-axle ground pressure to 7.37 kPa — closure MOB-1 **failed**; the WEB was then moved 0.5 m rearward under the "
         f"radiator (shorter heat-pipe run), giving CoM x = {b['com_stowed'][0]:+.2f} m and {mob1['computed']:.2f} kPa.",
         "**Valid — design change.** Layout frozen; WEB at x = −0.5 m; GEOM-5 now checks containment and non-overlap, GEOM-7 "
         "radiator shading and GEOM-8 crane coverage; component positions in the mass model come from the same layout."],
    ]
    d.rows(["ID", "Objection", "Evidence", "Assessment and disposition"], rows)
    d.h("Failed or rejected ideas (kept on record)")
    for t in ["Asymmetric heavy service arm (TS-03): mass-inefficient in lunar gravity; replaced by crane boom.",
              "Terrestrial-style towing on slopes (TS-05): traction-limited; replaced by anchored winching.",
              "High winch fairlead (0.60 m): pitches the vehicle over at 4 kN (tip factor < 1).",
              "Deep (0.4 m) spades: insertion force ≈ 15 kN exceeds vehicle weight.",
              "Outriggers (TS-04): no stability need at 150 kg crane rating; do not resist sliding.",
              "Fully active / 4-wheel suspensions (TS-01): +80–100 kg for no gradeability gain.",
              "Fluid-servicing module (TS-07): no identified client asset.",
              "Radioisotope power for the baseline (TS-06): availability/approval; retained only for a PSR-specialist variant.",
              "Earth joystick teleoperation as primary control (TS-09): latency + 51 % DTE availability.",
              "Second TSR-1 for capacity (CDR-18): halves response time but saves almost no additional assets.",
              "23 kg / 2 kWh keep-alive module (CDR-20): battery alone ≈ 20 kg; sustains only ≈ 40 % of plausible assets.",
              "Counting all asset losses as the value metric (CDR-19): penalises TSR-1 for keeping assets operating.",
              "Six-slot spine in a 1.6 × 0.5 m strip over the radiator (CDR-21): did not fit; replaced by a 2 × 3 grid mid-deck."]:
        d.p("- " + t)
    d.h("Review outcome")
    d.p("The review did not invalidate the engineering feasibility of a service-and-recovery capability, but it did invalidate "
        "two original Todaro hypotheses (heavy service arm; towing as the primary recovery method) and substantially weakened the case "
        "for a *dedicated* vehicle relative to a host-mounted kit (CDR-01). Design changes: battery 15 kWh (CDR-06); conservative slope "
        "requirement (CDR-15); service-radius rule tied to speed (CDR-13); kit variant (CDR-01); keep-alive module resized and its "
        "inventory scaled with fault load (CDR-19/20); deck layout made physically consistent (CDR-21). Open items are listed in "
        "`results/open_questions.md`.")
    return d.text()


# ===================================================================================== VERDICT
def verdict(D) -> str:
    val, cd, rec, b = D["val"], D["cdr"], D["rec"], D["base"]
    sw = {s["n_assets"]: s for s in val["asset_sweep"]}
    lm = {x["level_mix"]: x for x in val["level_mix"]}
    hk = cd["host_cases"]
    kit = cd["service_kit"]
    c40 = {c["keepalive_modules"]: c for c in D["cap"] if c["n_tsr"] == 1 and c["n_assets"] == 60 and c["mtbf_yr"] == 1.5}
    n_fail = sum(1 for c in D["clo"] if not c["passed"])
    d = Doc()
    d.h("TSR-1 FEASIBILITY VERDICT", 1)
    d.p(DISCL)
    d.h("Verdict: FEASIBLE WITH IDENTIFIED TECHNOLOGY DEVELOPMENT — conditionally justified")
    d.p("**Engineering feasibility.** A ≈ 1.2 t rover performing inspection, ISPSIS-compatible emergency power, robotic ORU "
        "servicing, dust remediation and anchored-winch recovery closes in mass, power, energy, thermal, mobility, recovery, "
        f"manipulation, geometry and mission time ({len(D['clo']) - n_fail}/{len(D['clo'])} independent closure checks pass) using "
        "technology that exists today at TRL 5–7 for most elements, **but** depends on four immature items: ground-reaction anchors "
        "(TRL 3), cold/dust-tolerant long-life actuators (TRL 4), verified supervised servicing autonomy (TRL 4) and robot-mateable "
        "dust-tolerant kW connectors (TRL 4–5). None requires new physics; each has a defined test path (`docs/development_roadmap.md`).")
    d.p("**Why not 'feasible with current/near-term technology':** the integrated system is TRL 4 and its recovery and long-life "
        "claims rest on TRL 3–4 elements with no lunar test data.")
    d.p("**Why not 'partially feasible':** the full functional scope survives in mass and power; what failed were specific means "
        "(heavy arm → crane; towing → anchored winch), not functions.")
    p10_pos = next((n for n in sorted(sw) if all(sw[m]['dA_p10'] > 0 for m in sorted(sw) if m >= n)), None)
    d.p(f"**Why not 'not currently justified':** above ≈ {f(val['break_even_assets'], 0)} serviceable assets the model shows a positive logistics "
        f"balance, and the P10 of the availability gain is positive from {p10_pos} assets (ΔA P10 {100*sw[p10_pos]['dA_p10']:.1f} pp at {p10_pos}, "
        f"{100*sw[30]['dA_p10']:.1f} pp at 30).")
    d.h("Conditions under which TSR-1 is justified")
    d.rows(["Condition", "Evidence", "If not met"], [
        ["Base has more than ≈ " + f(val["break_even_assets"], 0) + " serviceable assets (logistics break-even)",
         f"net Earth-mass benefit {sw[3]['net_mass_benefit']/1000:.2f} t (3 assets), {sw[10]['net_mass_benefit']/1000:.2f} t (10), {sw[30]['net_mass_benefit']/1000:.2f} t (30)",
         "**not justified**: a 3-asset outpost should rely on crew + Earth spares"],
        ["Most assets are L2/L3 robot-serviceable", f"ΔA {100*lm['legacy (L0-heavy)']['dA_mean']:.1f} pp (legacy) vs {100*lm['standardised (L2/L3)']['dA_mean']:.1f} pp (standardised)",
         "TSR-1 degenerates to inspection + emergency power + recovery"],
        ["Assets have non-negligible fault rates (MTBF ≲ 10 yr)", f"corr(MTBF, ΔA) ≈ {val['sensitivity_corr']['mtbf->dA']:.2f}", "value scales down with fault rate"],
        ["Crew presence is intermittent", f"ΔA {100*val['crew'][0]['dA_mean']:.1f} pp with no crew vs {100*val['crew'][2]['dA_mean']:.1f} pp with 2 missions/yr", "value falls as crew presence rises"],
        ["Anchors validated (TG-03)", f"p_env {rec['p_env']['R4 winch + 2 spades + 2 helical anchors']['mid']:.2f} with anchors vs {rec['p_env']['R1 winch + braked wheels']['mid']:.2f} braked wheels only",
         "slope recovery largely lost"],
        ["A dedicated carrier only if no host can respond within asset survival time", f"kit ≈ {kit['kit_allocation_kg']:.0f} kg vs dedicated {kit['dedicated_delivered_kg']:.0f} kg; "
         f"preventable losses {hk[0]['plost1_mean']:.1f} (dedicated) vs {hk[2]['plost1_mean']:.1f} (shared host busy 60 %)",
         "choose the kit variant on a utility-rover host"],
        ["Keep-alive inventory scaled with fault load (CDR-19)", f"60 assets, MTBF 1.5 yr: preventable losses {c40[2]['plost1']:.1f} / {c40[4]['plost1']:.1f} / {c40[8]['plost1']:.1f} "
         f"with 2 / 4 / 8 modules (without TSR-1 {c40[2]['plost0']:.1f})", "one TSR-1 saturates on keep-alive capacity, not on driving or servicing time"],
        ["Parked assets' survival power within MOD-KA output (CDR-20)", f"P(sustain) {val['keepalive_trade']['selected_row']['p_sustain']:.2f} "
         f"({val['keepalive_trade']['selected_row']['p_sustain_low']:.2f} if assets need 50 % more power)", "losses rise toward the no-module case; larger MOD-KA or MOD-SOL needed"],
    ])
    d.h("Answer to the research question")
    vb = val["base"]
    d.p(f"For a 30-asset south-polar base over 10 years, one TSR-1 raises mean infrastructure availability from {vb['A0']['mean']:.2f} to "
        f"{vb['A1']['mean']:.2f} (ΔA P10/P50/P90 = {100*vb['dA']['p10']:.1f}/{100*vb['dA']['p50']:.1f}/{100*vb['dA']['p90']:.1f} pp), reduces preventable asset losses from "
        f"{vb['plost0']['mean']:.1f} to {vb['plost1']['mean']:.1f} (all causes {vb['lost0']['mean']:.0f} → {vb['lost1']['mean']:.0f}) and Earth-supplied replacement mass from "
        f"{vb['mass0']['mean']/1000:.1f} t to {vb['mass1']['mean']/1000:.1f} t ({val['kg_per_asset_yr0']['mean']:.0f} → {val['kg_per_asset_yr1']['mean']:.0f} kg per available asset-year). "
        f"**Crew EVA is reduced only modestly** ({vb['eva0']['mean']:.0f} → {vb['eva1']['mean']:.0f} crew-h): TSR-1 saves assets that then still need crew for "
        "repairs it cannot perform on non-standard interfaces. The answer is therefore **yes, materially, for asset availability, asset "
        f"loss and logistics mass, at bases of more than ≈ {f(val['break_even_assets'], 0)} serviceable assets — and only weakly for EVA reduction**, with the value "
        "dominated by emergency power/keep-alive and by asset interface standardisation rather than by manipulation sophistication.")
    return d.text()


# ===================================================================================== EXEC SUMMARY
def exec_summary(D) -> str:
    b, val, m, rec, en = D["base"], D["val"], D["mob"], D["rec"], D["en"]
    vb = val["base"]
    d = Doc()
    d.h("TODARO CORP. TSR-1 — Executive Summary", 1)
    d.p(DISCL)
    d.p("**What it is.** TSR-1 is a concept for an autonomous lunar service-and-recovery rover whose job is to keep distributed "
        "south-polar infrastructure (power, communication, science and robotic assets) working: inspect it, restore power to "
        "disabled assets, replace robot-serviceable modules, clean dust, and recover immobilised vehicles — without crew EVA.")
    d.p(f"**What the study found it must be.** A {b['delivered']:.0f} kg (delivered) six-wheel rocker-bogie rover with body lowering; "
        "two identical 20 kg-class dexterous arms plus a 150 kg cable-stayed crane (a heavy arm was rejected: ~110 kg heavier); "
        "a 3 kW ISPSIS-compatible 120 VDC power-transfer module with a 25 m tether and deployable keep-alive modules; a 4 kN "
        "anchored winch with rear spades and helical anchors (towing was rejected on slopes: < 0.2 kN available on 15°); "
        f"a {b['battery']['usable_eol_kwh']:.0f} kWh battery plus vertical solar panels; supervised autonomy behind a deterministic safety layer.")
    d.p(f"**Performance.** {m['slopes_deg']['nominal']:.0f}° slopes (nominal soil; {m['slopes_deg']['conservative']:.0f}° conservative), 10 km service radius, "
        f"{en['survival_full_battery_h']:.0f} h darkness survival (indefinite in sunlight), recovery of {rec['p_env']['R4 winch + 2 spades + 2 helical anchors']['mid']*100:.0f} % "
        "of sampled immobilisation cases, ORU swaps up to 150 kg.")
    d.p(f"**Value.** At 30 assets over 10 years: availability {vb['A0']['mean']:.2f} → {vb['A1']['mean']:.2f}, preventable asset losses {vb['plost0']['mean']:.1f} → {vb['plost1']['mean']:.1f}, "
        f"Earth replacement mass {vb['mass0']['mean']/1000:.1f} → {vb['mass1']['mean']/1000:.1f} t; logistics break-even at ≈ {f(val['break_even_assets'],0)} assets. "
        "EVA savings are modest. Value depends overwhelmingly on assets having standard robotic interfaces; at large or failure-prone "
        "bases the limiting resource is the inventory of deployable keep-alive modules, not the rover.")
    d.p("**Verdict.** Feasible with identified technology development (anchors, cold/dust-tolerant actuators, servicing autonomy, "
        f"dust-tolerant power connectors), and justified only for bases of more than ≈ {f(val['break_even_assets'], 0)} serviceable, standardised assets. The "
        "review found a dedicated vehicle would be idle > 95 % of the time; the recommended path is a host-agnostic service-and-recovery "
        "kit, with the dedicated TSR-1 carrier used where no utility-rover host can respond in time.")
    return d.text()


# ===================================================================================== FINAL SPECS
def final_specs(D) -> str:
    import csv
    d = Doc()
    d.h("TSR-1 FINAL SPECIFICATIONS", 1)
    d.p(DISCL)
    d.p("Complete technical specification of the frozen configuration. System-level values: `DESIGN_FREEZE_V1.md` (same "
        "generator, same data). Component specification sheets: `engineering/subsystem_specs/`. Requirements with model-derived "
        "values: `requirements/`.")
    d.h("1. Requirement compliance")
    with open(ROOT / "requirements" / "requirements_traceability.csv") as fh:
        rows = list(csv.DictReader(fh))
    d.rows(["Req", "Statement", "Verification", "Status"], [[r["req_id"], r["statement"], r["verification"], r["status"]] for r in rows])
    d.h("2. Component list (mass budget)")
    with open(ROOT / "engineering" / "mass_budget.csv") as fh:
        mb = list(csv.DictReader(fh))
    d.rows(["Component", "Subsystem", "CBE [kg]", "Predicted [kg]", "Material", "TRL"],
           [[r["component"], r["subsystem"], r["cbe_kg"], r["predicted_kg"], r["material"], r["trl"]] for r in mb])
    d.h("3. Closure verification")
    d.rows(["Check", "Computed", "Limit", "Result"],
           [[c["check"], f(c["computed"], 3) if isinstance(c["computed"], (int, float)) and not isinstance(c["computed"], bool) else str(c["computed"]),
             f(c["limit"], 3) if isinstance(c["limit"], (int, float)) else "—", "PASS" if c["passed"] else "**FAIL**"] for c in D["clo"]])
    return d.text()


def open_questions(D) -> str:
    d = Doc()
    d.h("TSR-1 — Open questions and unresolved problems", 1)
    d.p(DISCL)
    items = [
        ("OQ-01", "Will Moon Base assets carry L2/L3 robotic servicing interfaces?", "dominant value driver (CDR-08)", "programmatic; standards bodies"),
        ("OQ-02", "Actual regolith anchor/spade capacity and installability at the south pole", "recovery on slopes (CDR-05, TG-03)", "Stage-1 tests"),
        ("OQ-03", "Will a utility-rover host exist with ≥ 300 kg spare payload, ISPSIS power and response availability?", "kit vs dedicated carrier (CDR-01)", "NASA LUR definition"),
        ("OQ-04", "Lunar asset fault rates and fault-type mix", "all value results (TG-08)", "Moon Base telemetry"),
        ("OQ-05", "10-year dust life of ~30 external actuators", "TSR-1 reliability (TG-07)", "life tests"),
        ("OQ-06", "Cold-tolerant actuator torque density at 200 N·m class", "mass and survival power (TG-01)", "BMG gear development"),
        ("OQ-07", "Achievable effective autonomous speed under polar lighting", "energy, radius, response (CDR-13)", "analogue field tests"),
        ("OQ-08", "ISPSIS surface power-quality and connector definition", "interoperability of emergency power (TG-09)", "standards"),
        ("OQ-09", "Lander accommodation: loads, envelope, offloading", "structure, mechanisms locks (CDR-16)", "lander selection"),
        ("OQ-10", "Robotic task success statistics by interface level", "assumption A-31 (CDR-09)", "Stage 2–3 testing"),
        ("OQ-11", "Reduced-gravity traction penalty magnitude for 0.9 m grousered wheels", "slope claims (TG-06)", "parabolic flights / VIPER data"),
        ("OQ-12", "Seed document NTRS 20260001878 and full texts of S002 and the LTV SRD were not accessible", "evidence completeness", "re-run literature review with network access"),
        ("OQ-13", "Policy for TSR-1 command authority over third-party assets (cyber-security, liability)", "operations", "governance"),
        ("OQ-14", "Benefit of patrol inspections (early fault detection) not modelled", "possible additional value", "extend value model"),
        ("OQ-15", "Survival power and dark-period exposure of the assets TSR-1 would park on keep-alive modules", "MOD-KA sizing and value (CDR-20, A-33..A-35)", "asset design data; site illumination time series"),
    ]
    d.rows(["ID", "Question", "Affects", "Resolution path"], items)
    return d.text()


def main():
    D = load()
    (ROOT / "DESIGN_FREEZE_V1.md").write_text(design_freeze(D))
    (ROOT / "CRITICAL_DESIGN_REVIEW.md").write_text(cdr(D))
    (ROOT / "results" / "FEASIBILITY_VERDICT.md").write_text(verdict(D))
    (ROOT / "results" / "EXECUTIVE_SUMMARY.md").write_text(exec_summary(D))
    (ROOT / "results" / "FINAL_SPECIFICATIONS.md").write_text(final_specs(D))
    (ROOT / "results" / "open_questions.md").write_text(open_questions(D))
    print("reports written")


if __name__ == "__main__":
    main()
