"""Single source of truth for TSR-1 requirements.

Generates:
  requirements/mission_requirements.md
  requirements/system_requirements.md
  requirements/requirements_traceability.csv

Numerical values that are produced by analysis are written as ``{key}`` placeholders and are
resolved from ``simulations/results/design_values.json`` (written by ``simulations/run_all.py``).
Unresolved placeholders render as ``[TBD:key]`` so that no requirement value is ever invented
before the corresponding model has run.

Run:  python requirements/build_requirements.py
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DV_PATH = ROOT / "simulations" / "results" / "design_values.json"

# Verification methods: A=Analysis, T=Test, I=Inspection, D=Demonstration
# Source conventions: S0xx/L0xx = source_register.csv; DESIGN-DERIVED(<model>) = internal analysis;
# DIRECTIVE = study charter; ASSUMPTION A-xx = engineering/assumptions.md
MISSION = [
    dict(id="MR-01", cat="Availability",
         text="TSR-1 shall increase the time-averaged availability of serviceable surface assets in its "
              "service area relative to an otherwise identical base without TSR-1, by at least "
              "{mr01_avail_gain_pp} percentage points for the reference base of {ref_assets} assets.",
         rat="Primary research question; infrastructure availability is the stated purpose (S051 objective).",
         src="DIRECTIVE §4; S051; DESIGN-DERIVED(reliability.value_model)", ver="A"),
    dict(id="MR-02", cat="Crew",
         text="TSR-1 shall perform all nominal inspection, servicing, emergency-power and recovery functions "
              "without crew EVA support.",
         rat="Reduce EVA demand and crew dependence (S001 gap: reduce reliance on humans; S049 ISS EVA burden).",
         src="S001; S049; S051", ver="D"),
    dict(id="MR-03", cat="Inspection",
         text="TSR-1 shall inspect assets of classes AC-1 to AC-9 at compatibility levels L0–L3 using visible, "
              "thermal-infrared and 3-D imaging, and report anomalies with location and severity.",
         rat="Inspection is the only function available for L0 assets and precedes every intervention.",
         src="S001 (autonomous inspection gap); DIRECTIVE §5", ver="D"),
    dict(id="MR-04", cat="Servicing",
         text="TSR-1 shall remove and replace robot-compatible ORUs of mass up to {oru_max_kg} kg on L2 and L3 "
              "assets.",
         rat="ORU-level repair is the established supportability strategy (S049); mass from manipulator and "
             "stability analysis.",
         src="S049; ASSUMPTION A-13; DESIGN-DERIVED(manipulation.arm, stability)", ver="T"),
    dict(id="MR-05", cat="Emergency power",
         text="TSR-1 shall deliver temporary electrical power to a disabled asset through an ISPSIS 120 VDC "
              "compatible interface at up to {p_emer_cont_kw} kW continuous for at least {t_emer_keepalive_h} h "
              "at keep-alive load ({p_keepalive_w} W).",
         rat="Prevents thermal death of unpowered assets (A-14) and enables diagnosis; 120 VDC is the "
             "international interoperability standard (S011, S012).",
         src="S011; S012; ASSUMPTION A-14; DESIGN-DERIVED(power.budget)", ver="T"),
    dict(id="MR-06", cat="Recovery",
         text="TSR-1 shall recover or reposition immobilized vehicles within the envelope: {rec_envelope_text}.",
         rat="Immobilization is a demonstrated rover loss mode (S046); envelope from recovery model.",
         src="S046; DESIGN-DERIVED(recovery.towing)", ver="A,T"),
    dict(id="MR-07", cat="Dust",
         text="TSR-1 shall remove regolith dust from asset solar-array, radiator and optical surfaces such that "
              "the residual area coverage is ≤ {dust_residual_pct} %.",
         rat="Sub-monolayer dust degrades thermal surfaces (S062); Apollo dust effects (S022).",
         src="S022; S062; DESIGN-DERIVED(dust trade)", ver="T"),
    dict(id="MR-08", cat="Autonomy",
         text="TSR-1 shall execute service tasks under task-level human supervision only (no continuous "
              "teleoperation) and shall safely continue to the next hold point or abort predefined tasks during "
              "Earth-link outages up to 72 h and local-network outages up to 24 h.",
         rat="DTE availability ≈ 51 % at the pole (S073); communication delay (S001).",
         src="S001; S073; ASSUMPTION A-19; DIRECTIVE §22", ver="D"),
    dict(id="MR-09", cat="Lifetime",
         text="TSR-1 shall have an operational design life of 10 years on the lunar surface.",
         rat="Matches infrastructure-element life class (LTV 10-yr requirement precedent, S036).",
         src="S036 (precedent); DESIGN-DERIVED", ver="A"),
    dict(id="MR-10", cat="Environment",
         text="TSR-1 shall operate in the south-polar environment (sunlit ridges, shadowed terrain) including "
              "PSR excursions of up to {psr_excursion_h} h, and shall survive {survival_h} h without external "
              "power or sunlight.",
         rat="Longest darkness at best sites 3–5 days (S030); PSR < 40 K (S032); lunar-night survival is the #1 "
             "NASA shortfall (S010).",
         src="S010; S030; S032; DESIGN-DERIVED(thermal, power)", ver="A,T"),
    dict(id="MR-11", cat="Delivery",
         text="TSR-1 shall be deliverable as a single payload on a commercial lander with ≤ 3.0 t surface payload "
              "capacity (threshold) and ≤ 1.5 t (goal), including accommodation hardware.",
         rat="Blue Moon Mk1 3.0 t (S056); Argonaut 1.5 t (S047).",
         src="S047; S056", ver="A,I"),
    dict(id="MR-12", cat="Interoperability",
         text="TSR-1 shall use open interface standards: ISPSIS for power, LunaNet/CCSDS for communications and "
              "PNT, and ISO 9409-1/IERIIS-derived mechanical tool interfaces with adapters; it shall not require "
              "proprietary-only interfaces on serviced assets.",
         rat="Interoperability gap (S001); international standards (S011, S013, S017); NASA surface robotic "
             "interface best practices (S002).",
         src="S001; S002; S011; S013; S017", ver="I"),
    dict(id="MR-13", cat="Maintainability",
         text="TSR-1's life-limited and failure-prone items shall be replaceable at ORU level by another TSR-class "
              "vehicle or by crew without special tools.",
         rat="A servicing robot must itself be serviceable (DIRECTIVE §23); ISS ORU strategy (S049).",
         src="DIRECTIVE §23; S049", ver="D"),
    dict(id="MR-14", cat="Safety",
         text="TSR-1 shall not create a catastrophic hazard to crew or to other assets; all motion shall be "
              "bounded by a deterministic safety layer independent of high-level autonomy.",
         rat="Crew coexistence; AI verification limits (DIRECTIVE §20–21).",
         src="DIRECTIVE §20–21", ver="A,T"),
    dict(id="MR-15", cat="Service area",
         text="TSR-1 shall serve assets within a service radius of {service_radius_km} km of its home charging "
              "node and reach any such asset within {response_time_h} h of task approval.",
         rat="Comm-tower cell ≈ 10 km (S054); response time from availability model.",
         src="S054; ASSUMPTION A-20; DESIGN-DERIVED(reliability.value_model, mobility)", ver="A,D"),
]

SYSTEM = [
    # Mobility
    dict(id="SR-MOB-01", parent="MR-10", cat="Mobility",
         text="Mean static ground contact pressure shall not exceed 7 kPa at maximum operational mass on level "
              "ground (computed: {contact_pressure_kpa} kPa).",
         rat="Lunar Sourcebook: satisfactory mobility if contact pressure ≤ 7–10 kPa (S023).",
         src="S023", ver="A,T"),
    dict(id="SR-MOB-02", parent="MR-15", cat="Mobility",
         text="TSR-1 shall climb and descend {slope_climb_deg}° slopes at maximum operational mass with wheel "
              "slip ≤ 40 % under nominal soil, and shall hold position (brakes) on {slope_hold_deg}°.",
         rat="Route slopes A-04; traction limit from terramechanics model.",
         src="ASSUMPTION A-04; DESIGN-DERIVED(mobility.vehicle)", ver="A,T"),
    dict(id="SR-MOB-03", parent="MR-15", cat="Mobility",
         text="TSR-1 shall negotiate step obstacles of {obstacle_m} m and ditches of {ditch_m} m width.",
         rat="LRV heritage 0.30 m obstacles (S027); suspension geometry.",
         src="S027; DESIGN-DERIVED(mobility trade)", ver="T"),
    dict(id="SR-MOB-04", parent="MR-15", cat="Mobility",
         text="Autonomous average traverse speed shall be ≥ {v_avg_ms} m/s on ≤ 10° terrain; maximum speed "
              "{v_max_ms} m/s.",
         rat="Response time MR-15; hazard-detection range (S064 10 cm at 15 m).",
         src="S064; DESIGN-DERIVED(mobility, autonomy)", ver="T"),
    dict(id="SR-MOB-05", parent="MR-15", cat="Mobility",
         text="Range on one charge shall be ≥ {range_km} km on nominal terrain at maximum operational mass "
              "while retaining the survival energy reserve.",
         rat="Round trip 2·R_s plus work energy and reserve.",
         src="DESIGN-DERIVED(power.budget)", ver="A,T"),
    dict(id="SR-MOB-06", parent="MR-13", cat="Mobility",
         text="Loss of any single wheel drive shall not prevent mobility on slopes ≤ {slope_one_wheel_out_deg}°.",
         rat="Spirit was lost after one wheel failure (S046); redundancy.",
         src="S046; DESIGN-DERIVED(mobility.vehicle)", ver="A,T"),
    # Manipulation
    dict(id="SR-MAN-01", parent="MR-04", cat="Manipulation",
         text="The dexterous arm shall handle {dex_payload_kg} kg at {dex_reach_m} m reach in lunar gravity with "
              "end-effector positioning accuracy ≤ {dex_accuracy_mm} mm (visual-servo closed loop) and 6-axis "
              "force/torque sensing.",
         rat="Connector/fastener work on L2/L3 ORUs; ISS OTCM practice (S067).",
         src="S067; DESIGN-DERIVED(manipulation.arm)", ver="T"),
    dict(id="SR-MAN-02", parent="MR-04", cat="Manipulation",
         text="The heavy-handling system shall lift and place {heavy_payload_kg} kg at {heavy_reach_m} m "
              "horizontal reach in lunar gravity within the stability envelope.",
         rat="Heavy ORUs and recovery support (A-13).",
         src="ASSUMPTION A-13; DESIGN-DERIVED(manipulation.arm, stability)", ver="T"),
    dict(id="SR-MAN-03", parent="MR-04", cat="Manipulation",
         text="Tools shall be exchanged autonomously via a tool changer; tool change time ≤ {tool_change_min} min.",
         rat="Tool variety (DIRECTIVE §13).",
         src="DESIGN-DERIVED(tools)", ver="D"),
    # Servicing
    dict(id="SR-SRV-01", parent="MR-04", cat="Servicing",
         text="The service spine shall carry ≥ {spine_payload_kg} kg of ORUs, tools and modules in ≥ "
              "{spine_slots} standard slots.",
         rat="Carry spares for DRM-2/DRM-5 in one sortie.",
         src="DESIGN-DERIVED(service-module trade)", ver="I,T"),
    dict(id="SR-SRV-02", parent="MR-04", cat="Servicing",
         text="The fastener tool shall deliver up to {fastener_torque_nm} N·m with reaction taken through the "
              "arm/fixture and torque measurement accuracy ±5 %.",
         rat="Captive robotic fasteners (S067 OTCM socket drive heritage).",
         src="S067; DESIGN-DERIVED", ver="T"),
    # Power
    dict(id="SR-PWR-01", parent="MR-12", cat="Power",
         text="The primary power bus shall be 120 VDC with power quality and grounding compatible with ISPSIS; "
              "28 VDC secondary bus for avionics.",
         rat="International interoperability standard (S011).",
         src="S011", ver="I,T"),
    dict(id="SR-PWR-02", parent="MR-05", cat="Power",
         text="A bidirectional, galvanically isolated power-transfer port shall accept ≥ {p_charge_kw} kW for "
              "charging and deliver ≥ {p_emer_cont_kw} kW continuous / {p_emer_peak_kw} kW peak (60 s) at 120 VDC "
              "through a tether ≤ {tether_m} m.",
         rat="120 VDC exchange limited to < 100 m (S012); emergency power analysis.",
         src="S012; DESIGN-DERIVED(power.budget)", ver="T"),
    dict(id="SR-PWR-03", parent="MR-10", cat="Power",
         text="Battery usable energy shall be ≥ {battery_usable_kwh} kWh at end of life, sufficient for the "
              "design-reference sortie plus {survival_h} h survival reserve.",
         rat="Energy closure (DIRECTIVE §44).",
         src="DESIGN-DERIVED(power.budget)", ver="A,T"),
    # Thermal
    dict(id="SR-THM-01", parent="MR-10", cat="Thermal",
         text="Battery temperature shall be held within 0 to +30 °C while charging and −20 to +40 °C while "
              "discharging.",
         rat="Li-ion limits (S071).", src="S071", ver="A,T"),
    dict(id="SR-THM-02", parent="MR-10", cat="Thermal",
         text="The thermal system shall reject {q_reject_max_w} W peak internal dissipation in the hot case and "
              "limit survival heater demand to ≤ {p_survival_w} W in the cold case.",
         rat="Thermal closure; survival energy.",
         src="DESIGN-DERIVED(thermal.lumped)", ver="A,T"),
    # Autonomy / avionics
    dict(id="SR-AUT-01", parent="MR-14", cat="Autonomy",
         text="Autonomy shall be layered (mission planner → task planner → verified skills → motion planning → "
              "real-time control); no learned or generative component shall command actuator torques or currents "
              "directly.",
         rat="Verification boundary (DIRECTIVE §20–21).", src="DIRECTIVE §20–21", ver="I,A"),
    dict(id="SR-AUT-02", parent="MR-08", cat="Autonomy",
         text="Every irreversible step (power connection, release of load-bearing fasteners, winch tension above "
              "{winch_hold_kN} kN, cutting) shall be preceded by a hold point requiring human approval or a "
              "pre-authorised rule.",
         rat="Safety and supervisability.", src="DESIGN-DERIVED(autonomy trade)", ver="D"),
    dict(id="SR-AVI-01", parent="MR-14", cat="Avionics",
         text="Avionics shall separate a high-performance autonomy computer from a dual-redundant deterministic "
              "safety/real-time computer; parts shall tolerate ≥ 20 krad(Si) TID and be SEL-immune or protected.",
         rat="A-24 radiation; directive §20.", src="S039; ASSUMPTION A-24", ver="A,T"),
    # Communications / navigation
    dict(id="SR-COM-01", parent="MR-12", cat="Communications",
         text="TSR-1 shall communicate via (a) the base surface network, (b) a LunaNet-compliant relay link and "
              "(c) a peer mesh link, using DTN store-and-forward for non-real-time data.",
         rat="S017, S054, S073, L020.", src="S017; S054; S073; L020", ver="T"),
    dict(id="SR-NAV-01", parent="MR-15", cat="Navigation",
         text="TSR-1 shall localise to ≤ {loc_global_m} m in the base frame and determine relative pose to a "
              "servicing interface to ≤ {loc_rel_mm} mm / {loc_rel_deg}° before contact.",
         rat="Docking/tool alignment tolerances.", src="DESIGN-DERIVED(sensor suite)", ver="T"),
    # Dust
    dict(id="SR-DST-01", parent="MR-09", cat="Dust",
         text="All external mechanisms shall use labyrinth + seal protection; optics and radiators shall have "
              "dust removal (EDS) or covers; wheels shall have fenders limiting ejecta onto the vehicle; connectors "
              "shall have self-closing dust covers.",
         rat="Apollo dust lessons (S022/S074); EDS (S019, S063); DTC (S042).",
         src="S019; S022; S042; S063", ver="I,T"),
    # Structure
    dict(id="SR-STR-01", parent="MR-11", cat="Structure",
         text="Primary structure shall withstand launch/landing quasi-static loads of 6 g axial + 3 g lateral with "
              "factors of safety 1.25 (yield) and 1.4 (ultimate).",
         rat="A-05, A-22.", src="ASSUMPTION A-05; S053 (A-22)", ver="A,T"),
    dict(id="SR-STR-02", parent="MR-06", cat="Structure",
         text="Recovery hard points and the winch load path shall withstand {winch_line_pull_kN} kN line pull "
              "at any angle within the recovery cone with FoS 1.4 (ultimate).",
         rat="Recovery loads.", src="DESIGN-DERIVED(recovery.towing)", ver="A,T"),
    # Recovery
    dict(id="SR-REC-01", parent="MR-06", cat="Recovery",
         text="The winch shall provide {winch_line_pull_kN} kN line pull, {winch_line_m} m usable line, with "
              "continuous tension measurement and automatic limiting.",
         rat="Recovery scenarios A–D.", src="DESIGN-DERIVED(recovery.towing)", ver="T"),
    dict(id="SR-REC-02", parent="MR-06", cat="Recovery",
         text="The ground-reaction system shall resist ≥ {anchor_capacity_kN} kN horizontal load (P50 soil) and "
              "≥ {anchor_capacity_p10_kN} kN (P10 soil).",
         rat="Traction-limited towing in lunar gravity.", src="DESIGN-DERIVED(recovery.towing)", ver="A,T"),
    # Reliability
    dict(id="SR-REL-01", parent="MR-09", cat="Reliability",
         text="No single failure other than primary-structure failure shall cause loss of mobility on terrain "
              "≤ {slope_one_wheel_out_deg}°, or loss of the ability to communicate and safe the vehicle.",
         rat="FMEA single-point-failure policy (DIRECTIVE §24).", src="DIRECTIVE §24", ver="A"),
    dict(id="SR-REL-02", parent="MR-09", cat="Reliability",
         text="Probability that TSR-1 retains at least degraded-mode servicing capability after 10 years shall be "
              "≥ {p_mission_10yr} (with peer/crew ORU replacement).",
         rat="Life (MR-09).", src="DESIGN-DERIVED(reliability.tsr_reliability)", ver="A"),
    # Maintainability
    dict(id="SR-MNT-01", parent="MR-13", cat="Maintainability",
         text="Wheel drive units, battery modules, avionics modules, cameras, tools, power electronics and arms "
              "(at the arm base) shall be ORUs with grapple handles, captive fasteners and blind-mate connectors.",
         rat="Self-serviceability (DIRECTIVE §23).", src="DIRECTIVE §23; S049", ver="I,D"),
    dict(id="SR-MNT-02", parent="MR-13", cat="Maintainability",
         text="TSR-1 shall carry ≥ 2 grapple fixtures, fiducial markers on each ORU and a service port for peer "
              "diagnostics.",
         rat="TSR-to-TSR servicing (DIRECTIVE §23).", src="DIRECTIVE §23", ver="I"),
    # Interfaces
    dict(id="SR-INT-01", parent="MR-12", cat="Interfaces",
         text="The arm tool interface shall follow an ISO 9409-1 bolt pattern and carry adapters for OTCM-type "
              "grapple/socket interfaces, HOTDOCK-type androgynous interfaces and payload-deck-type interfaces.",
         rat="S013, S048, S067, S037.", src="S013; S037; S048; S067", ver="I,T"),
    # Safety
    dict(id="SR-SAF-01", parent="MR-14", cat="Safety",
         text="Within 10 m of crew, vehicle speed shall be limited to {v_crew_ms} m/s and manipulator "
              "end-effector force to {f_crew_n} N by the deterministic safety layer.",
         rat="Crew coexistence.", src="DESIGN-DERIVED(safety)", ver="T"),
    # Sensors
    dict(id="SR-SNS-01", parent="MR-03", cat="Sensors",
         text="The sensor suite shall comprise at minimum: mast stereo navigation cameras with illumination, "
              "hazard cameras, LiDAR, macro inspection camera, thermal-IR imager, wrist F/T sensors, IMU, wheel "
              "and joint encoders, and electrical diagnostic instrumentation; no airborne acoustic sensors.",
         rat="Inspection and navigation needs; vacuum (no acoustic propagation).",
         src="S064; S065; DIRECTIVE §14", ver="I"),
]


def _load_values() -> dict:
    if DV_PATH.exists():
        return json.loads(DV_PATH.read_text())
    return {}


def _resolve(text: str, values: dict) -> tuple[str, list[str]]:
    missing: list[str] = []

    def rep(m: re.Match) -> str:
        key = m.group(1)
        if key in values:
            v = values[key]
            if isinstance(v, float):
                return f"{v:.3g}" if abs(v) < 1000 else f"{v:.0f}"
            return str(v)
        missing.append(key)
        return f"[TBD:{key}]"

    return re.sub(r"\{([a-zA-Z0-9_]+)\}", rep, text), missing


def build() -> None:
    values = _load_values()
    out_dir = ROOT / "requirements"
    rows = []
    for level, reqs, fname, title in (
        ("Mission", MISSION, "mission_requirements.md", "Mission Requirements"),
        ("System", SYSTEM, "system_requirements.md", "System Requirements"),
    ):
        lines = [f"# TSR-1 {title}", "",
                 "> Generated by `requirements/build_requirements.py` — edit that file, not this one.", "",
                 "Verification: A = analysis, T = test, I = inspection, D = demonstration. "
                 "`[TBD:key]` = value not yet produced by a model.", ""]
        cur_cat = None
        for r in reqs:
            text, missing = _resolve(r["text"], values)
            status = "OPEN (TBD)" if missing else "DERIVED/CLOSED"
            if r["cat"] != cur_cat:
                lines += [f"## {r['cat']}", ""]
                cur_cat = r["cat"]
            lines += [f"### {r['id']}" + (f" (parent {r['parent']})" if r.get("parent") else ""),
                      f"- **Statement:** {text}",
                      f"- **Rationale:** {r['rat']}",
                      f"- **Source:** {r['src']}",
                      f"- **Verification:** {r['ver']}",
                      f"- **Status:** {status}", ""]
            rows.append([r["id"], level, r["cat"], r.get("parent", ""), text, r["rat"], r["src"], r["ver"],
                         status])
        (out_dir / fname).write_text("\n".join(lines))
    with open(out_dir / "requirements_traceability.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["req_id", "level", "category", "parent", "statement", "rationale", "source",
                    "verification", "status", "verified_by_model", "design_freeze_ref"])
        for row in rows:
            w.writerow(row + [_model_ref(row[6]), _freeze_ref(row[0])])
    n_open = sum(1 for r in rows if r[8].startswith("OPEN"))
    print(f"requirements: {len(rows)} total, {n_open} open")


def _model_ref(src: str) -> str:
    m = re.findall(r"DESIGN-DERIVED\(([^)]*)\)", src)
    return "; ".join(m)


FREEZE_MAP = {
    "MOB": "DESIGN_FREEZE_V1 §3 Mobility", "MAN": "DESIGN_FREEZE_V1 §5 Manipulation",
    "SRV": "DESIGN_FREEZE_V1 §6 Service spine", "PWR": "DESIGN_FREEZE_V1 §8 Power",
    "THM": "DESIGN_FREEZE_V1 §9 Thermal", "AUT": "DESIGN_FREEZE_V1 §11 Autonomy",
    "AVI": "DESIGN_FREEZE_V1 §10 Avionics", "COM": "DESIGN_FREEZE_V1 §12 Comms/Nav",
    "NAV": "DESIGN_FREEZE_V1 §12 Comms/Nav", "DST": "DESIGN_FREEZE_V1 §13 Dust",
    "STR": "DESIGN_FREEZE_V1 §14 Structure", "REC": "DESIGN_FREEZE_V1 §7 Recovery",
    "REL": "DESIGN_FREEZE_V1 §16 Reliability", "MNT": "DESIGN_FREEZE_V1 §16 Reliability",
    "INT": "DESIGN_FREEZE_V1 §6 Service spine", "SAF": "DESIGN_FREEZE_V1 §11 Autonomy",
    "SNS": "DESIGN_FREEZE_V1 §10 Avionics",
}


def _freeze_ref(rid: str) -> str:
    if rid.startswith("MR-"):
        return "DESIGN_FREEZE_V1 §1 Summary"
    return FREEZE_MAP.get(rid.split("-")[1], "")


if __name__ == "__main__":
    build()
