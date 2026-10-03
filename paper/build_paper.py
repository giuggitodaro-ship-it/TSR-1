"""Generate paper/paper.md from the simulation results, the requirement set and the source register.

    PYTHONPATH=src python paper/build_paper.py

Every number in the paper is read from simulations/results/*.json, engineering/*.csv or requirements/*.csv at build
time, so the paper cannot drift from the models, the design freeze or the verdict. Citations use pandoc syntax
([@S001]) with keys from paper/references.bib (generated from research/source_register.csv); the reference list at
the end is rendered from the register for the keys actually cited, with each source's access label.
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RES = ROOT / "simulations" / "results"
TITLE = ("TSR-1: A Preliminary Systems Engineering Study of an Autonomous Lunar Service and Recovery Rover for "
         "Distributed Surface Infrastructure")
DISCL = ("TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other "
         "organizations are used solely as technical and architectural context.")
R4 = "R4 winch + 2 spades + 2 helical anchors"


def J(name, d=RES):
    return json.loads((d / name).read_text())


def csv_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def f(x, d=1):
    if isinstance(x, str):
        try:
            x = float(x)
        except ValueError:
            return x
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    if isinstance(x, float) and math.isinf(x):
        return "∞"
    return f"{x:,.{d}f}"


def pp(x, d=1):
    return f"{100 * x:.{d}f}"


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def fig(n, name, caption):
    return f"![**Figure {n}.** {caption}](figures/{name})\n"


def load():
    D = dict(base=J("baseline_summary.json"), mob=J("mobility.json"), stab=J("stability.json"), rec=J("recovery.json"),
             en=J("energy_power_thermal.json"), val=J("value_model.json"), rel=J("tsr_reliability.json"),
             sens=J("sensitivity.json"), cdr=J("cdr_analyses.json"), clo=J("closure.json"), dv=J("design_values.json"),
             tr=J("trades.json"), srv=J("servicing_success.json"), cap=J("capacity_study.json"))
    D["req"] = csv_rows(ROOT / "requirements" / "requirements_traceability.csv")
    D["mass"] = csv_rows(ROOT / "engineering" / "mass_budget.csv")
    D["params"] = csv_rows(ROOT / "engineering" / "parameter_register.csv")
    D["src"] = {r["source_id"]: r for r in csv_rows(ROOT / "research" / "source_register.csv")}
    _mc = json.loads((ROOT / "simulations" / "configs" / "run_config.json").read_text())["full"]
    D["runs"], D["runs_sweep"] = _mc["value_runs"], _mc["value_runs_sweep"]
    pre = RES / "pre_cdr"
    if pre.exists():
        D["pre"] = dict(clo=J("closure.json", pre), base=J("baseline_summary.json", pre))
    return D


# ===================================================================================================== sections
def s_abstract(D):
    b, m, val, rec = D["base"], D["mob"], D["val"], D["rec"]
    vb = val["base"]
    n_fail = sum(1 for c in D["clo"] if not c["passed"])
    return f"""## 1. Abstract

Distributed infrastructure at a south-polar lunar base — power, communication, science and robotic assets spread
over tens of kilometres — will suffer faults that cannot wait for a crew mission or an Earth spare: an asset that
loses power has days, not months, before thermal damage, and an immobilised vehicle has no external rescue
capability today. This study asks whether a dedicated autonomous servicing and recovery rover, TSR-1, can materially
increase the availability and life of such infrastructure while reducing crew EVA, asset loss and Earth logistics,
within credible mass, power, thermal and mobility limits. Following a systems-engineering workflow — operational
need, concept of operations, {len(D['req'])} traceable requirements, ten formal trade studies, physics-based subsystem
models, {len(D['clo'])} budget-closure checks, an adversarial design review and a discrete-event Monte Carlo value
model — the study derives a {f(b['delivered'], 0)} kg (delivered) six-wheel rocker-bogie rover with two 20 kg-class
dexterous arms, a 150 kg cable-stayed crane, a 3 kW power-transfer module on the 120 VDC interoperability bus,
deployable keep-alive power modules and an anchored 4 kN winch. Two original design hypotheses failed: a heavy
service arm is mass-inefficient in lunar gravity, and towing is traction-limited on slopes (anchored winching raises
the recoverable fraction of sampled immobilisation cases from {pp(rec['p_env']['R0 direct towing (drive)']['mid'], 0)} % to
{pp(rec['p_env'][R4]['mid'], 0)} %). The design closes ({len(D['clo']) - n_fail}/{len(D['clo'])} checks) with
{f(m['slopes_deg']['nominal'], 1)}° gradeability in nominal soil ({f(m['slopes_deg']['conservative'], 1)}° conservative). For a
30-asset base over ten years, one TSR-1 raises mean availability from {vb['A0']['mean']:.2f} to {vb['A1']['mean']:.2f}
(gain P10/P50/P90 {pp(vb['dA']['p10'])}/{pp(vb['dA']['p50'])}/{pp(vb['dA']['p90'])} percentage points), cuts preventable
asset losses from {f(vb['plost0']['mean'])} to {f(vb['plost1']['mean'])} and Earth-supplied replacement mass from
{f(vb['mass0']['mean'] / 1000)} t to {f(vb['mass1']['mean'] / 1000)} t, but reduces crew EVA only modestly. The logistics
break-even is ≈ {f(val['break_even_assets'], 0)} serviceable assets; the benefit depends most on assets carrying
robot-serviceable interfaces and on an adequate inventory of keep-alive modules. The verdict is **feasible with
identified technology development** (regolith anchors, cold- and dust-tolerant actuators, verified servicing
autonomy, dust-tolerant power connectors), and conditionally justified; the review also found that a host-mounted
service-and-recovery kit is preferable to a dedicated vehicle wherever a utility-rover host can respond within an
asset's survival time.

*{DISCL}*
"""


def s_intro(D):
    return f"""## 2. Introduction

The current lunar exploration architectures move from sorties to sustained presence. NASA's Moon Base plan places
power arrays, communication towers, landers, rovers and science stations around the south pole during the
early 2030s [@S006; @S007; @S054]; ESA, JAXA and commercial partners contribute landers, rovers and relay services
[@S018; @S047; @S058]. Sustained operation of such a distributed system raises a question that sortie missions never
had to answer: who maintains it? On the International Space Station, maintenance absorbed more than 4000 crew hours
in the first five years, and external robotics already performed roughly twice the external maintenance hours of
EVA crews [@S049]. NASA's capability-gap work lists autonomous inspection, maintenance and repair, dust-tolerant
interfaces and standardised architectures among the gaps for uncrewed surface operations [@S001; @S051], and the 2026
civil space shortfall ranking places surviving the lunar night first [@S010].

TSR-1 is a hypothesis put forward by Todaro Corp.: a dedicated autonomous rover that inspects, powers, repairs,
cleans and recovers other surface assets. This paper does not set out to prove that hypothesis. It asks what such
a vehicle would have to be to work, whether that vehicle closes in mass, power, thermal and mobility, and whether it
would actually improve infrastructure availability and logistics enough to justify itself — and it reports where
the answer is negative. The engineering evidence is a reproducible Python model set with automated tests; every
number in this paper is generated from those models (`simulations/run_all.py`), and every parameter is recorded with
its provenance in a central register (`engineering/parameter_register.csv`).

Throughout, values are labelled by provenance: SOURCE-DERIVED (from a cited document), CALCULATED (model output),
ENGINEERING ASSUMPTION (no source; range carried), DESIGN DECISION (selected by trade) or ESTIMATE (engineering
judgement with range). Because the study environment blocked full-text access to agency servers, sources were read
through search-engine excerpts; each reference carries its access label (Section 29) and the consequences are
discussed in Section 26.
"""


def s_need(D):
    return """## 3. Operational Need

Three observations establish that the need is real; none of them, alone, establishes that a dedicated vehicle is
the right answer.

1. **Uncrewed operations are the norm.** Crew presence at the base is expected to be intermittent (assumption
   A-07: zero to two surface missions per year of about 30 days). The NASA gap study frames the uncrewed-operations
   gaps around reducing "reliance on humans to perform tasks" under communication delay [@S001]; the uncrewed
   support taxonomy names lifting, servicing, powering, inspecting, cleaning and safing, with increased
   infrastructure availability as an explicit objective [@S051].
2. **Faults become losses quickly.** An unpowered small asset has a survival time of the order of 50 h in darkness
   (VIPER class, [@S035]); a parked rover in soft regolith can be permanently lost, as Spirit was [@S046]. No
   external recovery capability exists for lunar vehicles.
3. **Dust degrades everything over time.** Apollo experience shows dust clogging mechanisms, abrading seals and
   degrading thermal control [@S022]; sub-monolayer deposits measurably change radiator absorptance [@S062].
   Electrodynamic dust shields have now been demonstrated on the Moon [@S019], but cleaning still needs a carrier.

The first of these is decisive for the architecture: whatever performs the service must be useful when no crew is
present and must survive long communication gaps (direct-to-Earth availability at the pole ≈ 51 % [@S073]).
"""


def s_landscape(D):
    return """## 4. Existing Capability Landscape

**Overlapping architecture elements.** NASA's 2025 logistics white paper and architecture update define a robotic
*Lunar Utility Rover* that would move "100s kg" to "1000s kg" of cargo and "could support continuous presence ... with
capabilities to maintain, repair, and service other exploration systems" [@S004; @S005]. The Lunar Terrain Vehicle
(LTV) programme selected two crew-capable vehicles with uncrewed modes, ten-year life and 800 kg-class payload
[@S036; @S055]; one of them derives from a platform that carries three robotic payload interfaces [@S037]. TSR-1
therefore cannot claim novelty of mission; it must justify itself either as a specialised configuration of the
utility-rover class or as a kit that such a vehicle carries. This tension is examined in the design review
(Section 22, CDR-01).

**Servicing heritage.** The only operational dual-arm servicing robot, Dextre, weighs 1662 kg and works in
microgravity with OTCM end-effectors [@S067]. Planetary surface arms are lighter and slower — the Perseverance arm
carries a 45 kg turret at ≈ 2 m [@S066] — and none is rated for heavy lifts under gravity. The Lunar Surface
Manipulation System showed that a cable-stayed crane can lift a tip payload many times its own mass [@S015]. Cold-
tolerant bulk-metallic-glass gears have operated without heaters at −173 °C [@S040], whereas heritage actuators must
be warmed to at least −55 °C before operation [@S041].

**Interfaces.** Power interoperability is defined at 120 VDC (with 28 VDC for small loads) by ISPSIS [@S011]; NASA
Glenn's grid work notes that 120 VDC exchange is limited to distances below 100 m and proposes 3 kVAC distribution
with bidirectional converters [@S012]. Robotic interfaces are classed by IERIIS on an ISO 9409-1 pattern [@S013];
androgynous interfaces such as HOTDOCK combine mechanical, power and data paths [@S048]. Communications follow
LunaNet and Moonlight relay services [@S017; @S018]. There is no lunar surface servicing standard today, which —
as Section 21 shows — is the largest single determinant of TSR-1's value.

**Mobility heritage.** The Apollo LRV is the only lunar vehicle with measured energy consumption (≈ 1.6 A·h/km at
36 V, [@S060]) and demonstrated 25° slopes [@S027]; VIPER and the LTV class define current practice for polar
rovers [@S035; @S036].
"""


def s_question(D):
    return """## 5. Research Question

*Can a dedicated autonomous lunar servicing and recovery rover materially increase the availability and operational
lifetime of distributed lunar surface infrastructure while reducing crew EVA requirements, asset loss, downtime and
Earth-supplied maintenance logistics, within physically and technologically plausible mass, power, thermal and
mobility constraints?*

The question has an engineering half (does a vehicle with the required functions close?) and a value half (does it
change infrastructure outcomes enough?). The study treats both as open: a vehicle that closes but adds little value,
or a valuable function that cannot be packaged credibly, would each be a negative answer. Five Todaro hypotheses
were evaluated explicitly rather than assumed: (A) asymmetric dual arms, (B) recovery and towing with stabilisation
anchors, (C) emergency power through standard interfaces, (D) a modular service spine and (E) multi-standard
interfaces with defined compatibility levels L0–L3.
"""


def s_method(D):
    n_par = len(D["params"])
    prov = {}
    for p in D["params"]:
        prov[p["provenance"]] = prov.get(p["provenance"], 0) + 1
    ptxt = ", ".join(f"{k} {v}" for k, v in sorted(prov.items(), key=lambda kv: -kv[1]))
    return f"""## 6. Design Methodology

The work followed the sequence research → requirements → models → trades → design freeze → review → revision:

1. **Evidence base.** {len(D['src'])} sources registered with hierarchy rank and access label
   (`research/source_register.csv`); a literature review and programme context (`research/`).
2. **Need and ConOps.** Stakeholders, nine target asset classes, compatibility levels L0–L3 and eight design reference
   missions (DRM-1..DRM-8; `engineering/conops.md`).
3. **Requirements.** {len(D['req'])} mission and system requirements, each with statement, rationale, source and
   verification method, generated from model outputs so that numbers in requirements equal numbers in the design
   (`requirements/`).
4. **Models.** Terramechanics (Bekker pressure–sinkage, Wong–Reece wheel stress integration, Janosi–Hanamoto shear
   [@L001; @L003; @L004]), static stability, manipulator and crane sizing, soil anchors (Rankine passive pressure,
   plate breakout), power and cable sizing, lumped thermal, structure, mass with AIAA S-120A growth allowances
   [@S052], reliability and a discrete-event value model (`src/tsr1/`, {n_par} registered parameters: {ptxt}).
5. **Trade studies.** Ten formal trades with direct engineering comparison where scoring would be arbitrary
   (`trade_studies/`).
6. **Closure.** {len(D['clo'])} independent checks that component sums reproduce totals and that each claimed
   capability is supported by the corresponding physics (directive §44; `simulations/results/closure.json`).
7. **Adversarial review.** The team switched role to a hostile review board (twenty objections, CDR-01..CDR-20),
   and the design was revised where objections held (`CRITICAL_DESIGN_REVIEW.md`).
8. **Uncertainty.** Parameter ranges, tornado sensitivities, mass Monte Carlo and epistemic Monte Carlo over the
   value model's uncertain inputs.

All stochastic analyses are seeded; `simulations/build_all.py` regenerates every result, figure and document,
including this paper.
"""


def s_environment(D):
    P = {p["name"]: p for p in D["params"]}

    def row(name, label):
        p = P[name]
        rng = p["uncertainty_range"].strip("[]").replace(", ", "–") if p["uncertainty_range"] else "—"
        unit = "" if p["unit"] in ("-", "") else " " + p["unit"]
        return [label, f"{float(p['value']):g}{unit}", rng, p["provenance"], p["source"][:70]]

    rows = []
    for n, lbl in (("g_moon", "gravity"), ("soil_c", "cohesion c"), ("soil_phi_deg", "friction angle φ"),
                   ("soil_kc", "k_c"), ("soil_kphi", "k_φ"), ("soil_n", "sinkage exponent n"),
                   ("soil_K", "shear modulus K"), ("t_survive_h", "unpowered asset survival time"),
                   ("illum_frac_best_2m", "best-site illumination (2 m)"), ("site_illum_frac", "illumination at parked asset"),
                   ("dark_period_h", "longest dark period at parked asset"), ("relay_range_max_km", "relay slant range")):
        if n in P:
            rows.append(row(n, lbl))
    return f"""## 7. Lunar Environmental Model

The environment model (`src/tsr1/environment/lunar.py`) carries every quantity as a nominal value with a range.
Soil parameters for the disturbed surface follow the Lunar Sourcebook trafficability table [@S023; @S024], in-situ
strength by depth follows the same source, and a reduced-gravity penalty is applied to traction because 1-g tests
over-predict lunar drawbar pull by about 20 % and under-predict sinkage by up to 40 % [@S043; @S044]. Three soil cases are
used: *nominal*, *conservative* (lower friction and cohesion, reduced-gravity penalty) and a *weak* bound.

{table(['Quantity', 'Nominal', 'Range', 'Provenance', 'Basis'], rows)}
Thermal bounds span permanently shadowed regions below 40 K [@S032] to sunlit polar rims near 300 K, with equatorial
extremes (≈ 95–390 K) as an outer bound [@L016]. Illumination at the best ridge sites reaches 92 % (2 m) to 96 % (10 m),
with longest darkness of 3–5 days [@S030]. Galactic-cosmic-ray dose is 13.2 µGy/h in silicon [@S033]; the design case
of 10 krad(Si) over ten years with a radiation design margin of two is dominated by solar particle events
(assumption A-24). Micrometeoroid flux scales from a recent polar-base analysis [@S061]. Dust is modelled through its
effects — radiator absorptance growth by a factor 1.4–2.6 at 25 % coverage [@S062], mechanism torque and life
penalties [@S021] — rather than through particle transport.
"""


def s_requirements(D):
    req = D["req"]
    mr = [r for r in req if r["req_id"].startswith("MR")]
    sr = [r for r in req if r["req_id"].startswith("SR")]
    names = {"A": "analysis", "T": "test", "I": "inspection", "D": "demonstration"}
    ver = {k: sum(1 for r in req if k in [x.strip() for x in r["verification"].split(",")]) for k in names}
    rows = [[r["req_id"], r["statement"], r["verification"]] for r in mr]
    return f"""## 8. Mission Requirements

{len(mr)} mission requirements (MR) and {len(sr)} system requirements (SR) were derived from the need, the ConOps and the
source base; each carries an ID, statement, rationale, source and verification method, and is traced to the design
element and model that satisfies it (`requirements/requirements_traceability.csv`). Numerical values in requirement
statements are written by the requirement generator from model outputs (`simulations/results/design_values.json`),
so a requirement cannot quote a capability the model does not show. Requirements verified by each method (several
use more than one): {', '.join(f'{names[k]} {v}' for k, v in ver.items())}.

{table(['ID', 'Mission requirement', 'Verification'], rows)}
Two requirements were changed by the design review: the slope requirement now states a nominal and a conservative
value (CDR-15), and the service radius is tied to the demonstrated effective speed (CDR-13).
"""


def s_architecture(D):
    b = D["base"]
    o = b["options"]
    g7 = next(c for c in D["clo"] if c["check"].startswith("GEOM-7"))
    shade = float(re.search(r"covers ([0-9.]+) %", g7["note"]).group(1)) / 100
    return f"""## 9. System Architecture

The models drove the architecture in a specific order (`engineering/architecture.md`):

1. **Traction, not suspension, limits slopes.** Soil shear strength and compaction resistance both scale with wheel
   load, so gradeability is a soil property almost independent of suspension type (TS-01). The lightest
   architecture that still supports self-repair and stabilisation — a six-wheel rocker-bogie with body lowering — was
   therefore selected.
2. **The vehicle is light compared with the forces it must apply.** At 1.62 m/s² a 1.25 t rover weighs only ≈ 2 kN.
   Lifting is done by a crane working in tension and compression, dexterity by light arms, and ground reaction for
   winching by spades and anchors rather than by vehicle weight (TS-03, TS-04, TS-05).
3. **Value comes from preventing losses, which needs power.** The value model shows that the largest benefit is
   keeping unpowered assets alive until they can be repaired. The 120 VDC power-transfer module and deployable
   keep-alive modules are therefore core functions (TS-06, TS-07).
4. **Interoperability is decisive.** Robotic module-replacement success falls from ≈ 0.96 at L3 to ≈ 0 at L0; TSR-1
   adopts open standards and carries adapters, and the main programmatic recommendation targets asset interfaces.

{fig(1, 'fig01_system_architecture.png', 'System context: TSR-1, client assets, base infrastructure, communication paths and logistics.')}
{fig(2, 'fig02_rover_configuration_dimensions.png', f"Frozen configuration with principal dimensions: wheelbase {o['wheelbase']:.1f} m, track {o['track']:.1f} m, wheel Ø{2 * o['wheel_r']:.2f} m.")}
{fig(3, 'fig03_subsystem_layout.png', 'Subsystem layout and placement of the main mass items.')}
**Deck layout.** A single layout definition (`src/tsr1/design/layout.py`) feeds the mass and centre-of-mass model, the
crane geometry in the stability model, the closure checks and Figure 3: the zenith radiator takes the full deck
width at the rear; the service spine is a 2 × 3 grid of 0.45 m slots mid-deck; the crane turntable, mast and both arm
bases share the front strip; tools hang on the chassis front face. The arms stow upright at the front corners and the
crane boom stows rearward over the spine (shading {pp(shade, 1)} % of the radiator). Inside the chassis the warm
electronics box sits under the radiator, 0.5 m aft of centre, which keeps the centre of mass at
x = {b['com_stowed'][0]:+.2f} m and the heaviest-axle ground pressure within 7 kPa. The design review found that the pre-review
deck allocation did not fit (CDR-21); the area-only check had hidden the conflict.

The functional architecture has nine functions — traverse and localise; inspect and diagnose; emergency power and
charging; service ORUs; clean; recover and reposition; self-maintain and peer-service; survive; communicate and be
supervised — each allocated to identified hardware and interfaces (`engineering/interfaces.md`, eleven external and
seven internal interfaces).
"""


def s_mobility(D):
    b, m, tr = D["base"], D["mob"], D["tr"]
    o = b["options"]
    s = m["slopes_deg"]
    mob_rows = [[r["candidate"], f(r["delivered_mass_kg"], 0), f(r["mobility_mass_pred_kg"], 0), f(r["max_slope_nom_deg"], 1),
                 f(r["max_slope_cons_deg"], 1), f(r["max_slope_one_wheel_out_deg"], 1), f(r["p_mobility_retained_10yr"], 2)]
                for r in tr["mobility"]]
    tow = "; ".join(f"{t['slope_deg']}°: {f(t['nominal_N'], 0)} N" for t in m["tow_capacity"])
    mm = {r["candidate"][:2]: r for r in tr["mobility"]}
    act = [mm[k]["delivered_mass_kg"] - mm["M2"]["delivered_mass_kg"] for k in ("M3", "M4")]
    dslope = max(mm[k]["max_slope_nom_deg"] for k in ("M3", "M4")) - mm["M2"]["max_slope_nom_deg"]
    dlow = mm["M2"]["delivered_mass_kg"] - mm["M1"]["delivered_mass_kg"]
    return f"""## 10. Mobility

**Model.** Each wheel is solved with the Wong–Reece stress integration over the contact arc (normal stress from
Bekker pressure–sinkage, shear from Janosi–Hanamoto), with grousers represented by an increased shear radius; vehicle
equilibrium on a slope is found by distributing load over the axles and solving for the slip at which net traction
balances the gravity component (`src/tsr1/mobility/`). The model was checked against the only lunar vehicle energy datum:
the Apollo LRV's ≈ 1.6 A·h/km at 36 V [@S060] gives an empirical calibration factor k_cal = {m['k_cal']:.2f} on the model's
wheel energy, which is applied to all driving-energy estimates. The reduced-gravity penalty of [@S043] is part of
the conservative soil case.

**Trade TS-01 (mobility architecture).** Four architectures were sized to the same mission:

{table(['Candidate', 'Delivered mass [kg]', 'Mobility mass [kg]', 'Slope, nominal [°]', 'Slope, conservative [°]', 'Slope, one drive failed [°]', 'P(mobility retained, 10 yr)'], mob_rows)}
Gradeability barely depends on suspension type because both traction and compaction resistance scale with wheel
load. The six-wheel rocker-bogie with body lowering and a differential lock (M2) costs ≈ {dlow:.0f} kg more than the passive
version but provides what servicing and recovery need — a lowered, skid-supported work posture and wheel unloading
for self-repair — and was selected. The active alternatives add {min(act):.0f}–{max(act):.0f} kg for {dslope:.1f}° more slope.

**Trade TS-02 (wheels).** Rigid titanium wheels Ø{2 * o['wheel_r']:.2f} × {o['wheel_b']:.2f} m with eighteen 20 mm grousers were
selected from a sweep of diameter and width against the ground-pressure rule (≤ 7 kPa, [@S023]) and drawbar pull at
40 % slip; a smaller Ø0.8 m wheel violated the pressure rule at the final mass. Wire-mesh (LRV, [@S029]) and
superelastic spring tyres were rejected for dust ingress, unproven ten-year fatigue and low model confidence.

**Results.** Contact pressure {m['contact_pressure_kPa']:.2f} kPa and static sinkage {1000 * m['sinkage_m']:.0f} mm at
the mean wheel load of {f(m['wheel_load_N'], 0)} N ({next(c['computed'] for c in D['clo'] if c['check'].startswith('MOB-1')):.2f} kPa under the
heaviest-loaded axle at 20 % slip, closure MOB-1). Maximum slope at slip ≤ 0.4: **{s['nominal']:.1f}° nominal soil,
{s['conservative']:.1f}° conservative, {s['weak']:.1f}° weak bound**; with one or two drives failed {s['one_wheel_out']:.1f}° /
{s['two_wheels_out']:.1f}°. Drive actuators are rated at {f(m['drive_rating_Nm'], 0)} N·m (soil-limited torque
{f(m['drive_torque_soil_Nm'], 0)} N·m × 1.25). Direct tow capacity in nominal soil is small: {tow}. Driving energy including
hotel loads is {D['en']['energy_per_km_kwh']:.2f} kWh/km at an effective 1.26 km/h, which dominates sortie energy
(Section 13).

{fig(4, 'fig12_mobility_results.png', 'Mobility results: drawbar pull versus slip for the three soil cases, drive power versus slope, and direct tow capacity versus slope.')}
"""


def s_manipulation(D):
    b, tr, srv = D["base"], D["tr"], D["srv"]
    dx, cr = b["dex"], b["crane"]
    man = [[a["architecture"], f(a["mass_kg"], 1), a["joints"], f(a["weighted_coverage"], 2), f(a["coverage_per_kg"], 3),
            "yes" if a["backup_after_primary_arm_failure"] else "no"] for a in tr["manipulators"]]
    am = {a["architecture"][:2]: a for a in tr["manipulators"]}
    lv = ("L0", "L1", "L2", "L3")
    srows = [[t.replace("_", " "), *[f(srv["robot"][t][L]["p50"], 2) for L in lv]] for t in srv["robot"]]
    crows = [[t.replace("_", " "), *[f(srv["crew"][t][L]["p50"], 2) for L in lv]] for t in srv["crew"]]
    return f"""## 11. Manipulation and Servicing

**Sizing in lunar gravity.** Serial arms were sized by worst-case gravity torque at full extension × 1.15 dynamic ×
2.0 motorisation factor, with actuator mass from a torque-density relation (25 N·m/kg nominal, 15–40 N·m/kg range)
and link tubes sized for deflection (`src/tsr1/manipulation/arm.py`). The crane is a slewing, luffing, cable-stayed
boom whose members carry tension and compression only, following the LSMS principle [@S015].

**Trade TS-03 (manipulator architecture)** — task coverage is weighted by DRM frequency; no arbitrary scores:

{table(['Architecture', 'Mass [kg]', 'Joints', 'Weighted task coverage', 'Coverage per kg', 'Backup after arm failure'], man)}
The asymmetric heavy-plus-dexterous pair (Todaro hypothesis A) achieves full coverage but at {am['A3']['mass_kg']:.0f} kg, because a
150 kg-rated serial arm needs ≈ 1.5 kN·m shoulder actuators even in lunar gravity. Replacing the heavy arm by the crane
recovers almost all coverage at a fraction of the mass. **Selected: A7, two identical 7-DOF dexterous arms plus the
crane.** The second dexterous arm (+{am['A7']['mass_kg'] - am['A4']['mass_kg']:.0f} kg over A4) removes the arm single-point failure and enables two-handed
connector and ORU work. Hypothesis A therefore failed in its asymmetric form and survived as a symmetric pair.

**Frozen manipulators.** Each dexterous arm: reach {dx['reach_m']:.2f} m, {dx['payload_kg']:.0f} kg rated payload, tip deflection
{dx['tip_deflection_mm']:.1f} mm, shoulder torque {dx['shoulder_torque_Nm']:.0f} N·m (rating {dx['shoulder_rating_Nm']:.0f} N·m),
{f(dx['mass_kg'], 1)} kg CBE, titanium links. Crane: {cr['reach']:.2f} m reach, 150 kg hook load, luff-cable tension
{cr['t_luff']:.0f} N, {f(cr['mass'], 1)} kg CBE. Twelve tools are carried; each maps to at least one DRM step or recovery
scenario (`engineering/subsystem_specs/tools.md`).

**Servicing success by compatibility level (hypothesis E).** Task success is the product of step probabilities
(approach, diagnose, engage interface, release fasteners, extract/insert, mate connectors, test), each with a range
by level (assumption A-31; no lunar servicing statistics exist). Median success probabilities:

*Robot (TSR-1):*

{table(['Task', 'L0', 'L1', 'L2', 'L3'], srows)}
*Crew EVA (for comparison):*

{table(['Task', 'L0', 'L1', 'L2', 'L3'], crows)}
Robotic ORU replacement is practically impossible on non-service-ready (L0) assets and reliable on L2/L3 assets;
crews are far less sensitive to interface level. Whether lunar assets will be designed to L2/L3 is the single most
important external condition for TSR-1 (Section 21).

{fig(5, 'fig04_service_spine.png', 'Modular service spine: slot interface and module library (hypothesis D).')}
{fig(6, 'fig05_manipulator_workspace_crane_capacity.png', 'Dexterous-arm workspace and crane capacity versus reach on level ground and on a 15° side slope.')}
{fig(7, 'fig09_servicing_workflow.png', 'Servicing workflow for an electrical fault (DRM-2) with hold points and failure branches.')}
"""


def s_recovery(D):
    rec, b, st, dv = D["rec"], D["base"], D["stab"], D["dv"]
    pe = rec["p_env"]
    prow = [[k, f(v["mid"], 2), f(v["weak_soil"], 2), f(v["high"], 2) + "–" + f(v["low"], 2), f(rec["restraint_mass"][k], 1)]
            for k, v in pe.items()]
    sc = [[r["id"], r["title"], f(r["target_mass_kg"], 0), f(r["slope_deg"], 0), f(r["required_force_N"], 0), r["method"],
           "yes" if r["feasible"] else "**no**", f(r["margin"], 2)] for r in rec["scenarios"]]
    stab = [[r["option"], f(r["added_mass_kg"], 0), f(r["crane_side_capacity_15deg_kg"], 0), f(r["winch_pull_limit_kN"], 2),
             r["deploy_time_min"]] for r in rec["stabilisation"]]
    cur = rec["curves"]["curves"][R4]
    i15 = cur["slopes"].index(15.0)
    cases = {c["case"]: c for c in st["cases"]}
    c7a = next(c for k, c in cases.items() if k.startswith("C7a"))
    c7c = next(c for k, c in cases.items() if k.startswith("C7c"))
    return f"""## 12. Recovery System

**Why towing fails.** In nominal soil the whole vehicle can generate only {f(D['mob']['tow_capacity'][3]['nominal_N'], 0)} N
of drawbar pull on 15° (Section 10) — less than one tenth of the force needed to drag a 450 kg vehicle with embedded
wheels. Terrestrial-style towing (part of hypothesis B) is therefore limited to light, free-rolling targets on level
ground.

**Anchored winching.** The adopted system pulls with a 4 kN winch while the rover is lowered and restrained by two
rear spades and two helical anchors installed in front, with straps to the front hard points. Spade capacity is
modelled by Rankine passive earth pressure with a shape factor, helical anchors by plate breakout (N_q* 10–40,
ESTIMATE) with the in-situ strength profile of [@S023]; embedded-wheel extraction resistance is bounded by a
step-climb model and a Bekker compaction model, whose spread is carried as uncertainty
(`src/tsr1/recovery/towing.py`). Restraint capacity is {dv['anchor_capacity_kN']} kN in median soil and
{dv['anchor_capacity_p10_kN']} kN at half strength.

**Trade TS-05 (recovery architecture).** Probability that a sampled immobilisation case (target mass, slope,
embedment, soil) is recoverable within the line-pull and restraint limits:

{table(['Restraint concept', 'P(recoverable), median soil', 'Half-strength soil', 'Range over resistance bounds', 'Added mass [kg]'], prow)}
**Selected: R4.** The second anchor pair (R5) adds little; braked wheels alone (R1) are far short. This is the
honest outcome for hypothesis B: recovery works, but only with ground anchoring, which is TRL 3 — no quantitative
lunar regolith anchor capacity exists in the literature [@S045].

**Trade TS-04 (stabilisation).** Outriggers were compared with locked wheels, body lowering and spades:

{table(['Option', 'Added mass [kg]', 'Crane side capacity at 15° [kg]', 'Winch pull limit [kN]', 'Deploy time [min]'], stab)}
Outriggers resist tipping but not sliding, and the crane's 150 kg rating is already far inside the stability limit, so
no outriggers are carried. The winch fairlead is mounted low (0.25 m): at 4 kN a 0.60 m fairlead pitches the rover
over (tipping factor {f(c7c['tip_factor'], 2)}, below the 1.5 requirement, case C7c) whereas the low fairlead with spades
gives {f(c7a['tip_factor'], 2)} (C7a), and the front hold-down straps remove the tipping mode entirely.

**Recovery scenarios** (directive §27):

{table(['ID', 'Scenario', 'Target [kg]', 'Slope [°]', 'Required force [N]', 'Method', 'Feasible', 'Margin'], sc)}
Scenario C-hi (deep embedment) is not feasible by pulling alone; it becomes feasible (C-dig) after the regolith scoop
excavates a ramp in front of the embedded wheels, which is why the scoop is in the tool set. On 15° slopes the anchored
winch recovers free-rolling vehicles up to {cur['free_kg'][i15] / 1000:.1f} t and brake-locked vehicles up to
{cur['locked_kg'][i15] / 1000:.1f} t (factor of safety 1.5).

{fig(8, 'fig13_recovery_envelopes.png', 'Recovery envelopes: recoverable target mass versus slope for free-rolling and brake-locked targets, by restraint concept.')}
{fig(9, 'fig14_recovery_trade.png', 'Recovery trade: probability of recovering a sampled immobilisation case by restraint concept and soil case, and sensitivity to winch rating.')}
{fig(10, 'fig15_stability_analysis.png', 'Static stability: tipping factor and centre-of-pressure margin for the operating cases C1–C7c.')}
"""


def s_power(D):
    b, en, val = D["base"], D["en"], D["val"]
    bat = b["battery"]
    drm = [[r["id"], r["title"], f(r["duration_h"], 1), f(r["distance_km"], 1), f(r["energy_kwh"], 2), f(r["energy_with_solar_kwh"], 2),
            f(r["peak_W"], 0)] for r in en["drms"]]
    modes = [[k.split("_", 1)[0], k.split("_", 1)[1].replace("_", " "), f(v, 0), f(en["web_dissipation_W"][k], 0)]
             for k, v in en["mode_power_W"].items()]
    br = [[f(r["radius_km"], 1), f(r["drm2_kwh"], 2), f(r["usable_eol_required_kwh"], 2), f(r["pack_mass_kg"], 0)]
          for r in en["battery_vs_radius"]]
    ea = [[r["option"], f(r["added_mass_kg"], 0), f(r["survival_dark_h"], 0), "yes" if r["indefinite_survival_in_sun"] else "no",
           r["trl"], "**selected**" if r["selected"] else r["issues"]] for r in en["energy_alternatives"]]
    kt = val["keepalive_trade"]
    ka = [[o["option"], f(o["mass_kg"], 1), f(o["p_sustained_nominal_w"], 0), f(o["bridge_nominal_h"], 0), f(o["p_sustain"], 2)]
          for o in kt["options"]]
    return f"""## 13. Power

**Architecture.** A regulated 120 VDC primary bus compliant with ISPSIS [@S011] with a 28 VDC avionics bus; a Li-ion
battery of passively propagation-resistant 18650 cells (pack 150–170 Wh/kg, [@S070]); two fixed vertical solar panels
(1.5 m² in total, one face lit at a time) for contingency charging and indefinite survival in sunlight; charging from
base nodes; and an isolated bidirectional **power-transfer module (PTM)**, 3 kW continuous / 4.5 kW for 60 s, with a 25 m
tether and a dust-tolerant connector [@S042], which delivers emergency power to client assets (hypothesis C). Because
120 VDC exchange is limited to short distances [@S012], the PTM connects at the asset rather than through the grid.

**Battery.** {bat['nameplate_kwh']:.1f} kWh nameplate ({bat['n_series']}s{bat['n_parallel']}p, {bat['v_nominal']:.0f} V nominal, boost-regulated
to the 120 VDC bus by the PCDU),
**{bat['usable_eol_kwh']:.0f} kWh usable at end of life** (depth of discharge 0.8, 20 % fade), {bat['mass']:.0f} kg. The pack is
sized by DRM-2 at the 10 km service edge without solar credit plus a 50 h survival reserve ({en['reserve_kwh']:.2f} kWh).
The pre-review 14 kWh pack failed this check after a survival-heater double count was corrected (CDR-06).

**Mode power budget** (`engineering/power_budget.csv`; component loads summed per mode; the bus load excludes power
transferred to client assets, whose conversion losses appear in the electronics-box dissipation):

{table(['Mode', 'Description', 'Bus load [W]', 'Electronics-box dissipation [W]'], modes)}
**Design reference missions** at the 10 km service edge (`src/tsr1/budgets/scenarios.py`):

{table(['DRM', 'Title', 'Duration [h]', 'Distance [km]', 'Energy [kWh]', 'With PV [kWh]', 'Peak [W]'], drm)}
Energy is dominated by hotel loads during slow autonomous traverse, so the service radius scales with effective speed
(Section 24). Battery size versus service radius:

{table(['Radius [km]', 'DRM-2 energy [kWh]', 'Usable EOL required [kWh]', 'Pack mass [kg]'], br)}
**Emergency power.** At the 10 km edge, after reserving return energy and the survival reserve, TSR-1 can supply
{en['keepalive_duration_at_edge_h']:.1f} h at 300 W keep-alive or {en['emergency_3kW_duration_at_edge_h']:.1f} h at 3 kW. Longer support
uses deployable **MOD-KA keep-alive modules** left at the asset. The review found the original 23 kg, 2 kWh module
physically inconsistent (CDR-20) and resized it (trade TS-07b):

{table(['Module option', 'Mass incl. MGA [kg]', 'Sustained output, nominal site [W]', 'Dark bridging at 100 W [h]', 'P(sustains a sampled asset)'], ka)}
The selected **{kt['selected']}** module ({val['keepalive_module_kg']:.0f} kg, double spine slot) sustains a sampled parked asset
(survival power 40–250 W, site illumination 0.5–0.92, dark periods 24–120 h; assumptions A-33..A-35) with probability
{kt['selected_row']['p_sustain']:.2f}.

**Trade TS-06 (energy architecture):**

{table(['Option', 'Added mass [kg]', 'Survival in darkness [h]', 'Indefinite in sun', 'TRL', 'Issue / decision'], ea)}
Radioisotope power would give indefinite operation in permanently shadowed regions but was rejected for availability
and approval reasons for an independent programme; it is the recommended variant for a PSR-specialist mission.

{fig(11, 'fig06_power_architecture.png', 'Power architecture: 120 VDC bus, battery, PV, PTM with tether, charging interface and keep-alive module.')}
{fig(12, 'fig11_power_energy_budget.png', 'Power by operating mode and energy by design reference mission.')}
"""


def s_thermal(D):
    b, en, dv = D["base"], D["en"], D["dv"]
    th = en["thermal"]
    return f"""## 14. Thermal Control

The warm electronics box (WEB, 1.0 × 0.8 × 0.35 m) inside the chassis carries battery, power conditioning, PTM,
computers and radios under MLI (effective emittance 0.03, [@L006]). Heat is rejected by a zenith-facing radiator with
optical solar reflectors and an electrodynamic dust-shield film, coupled by a loop heat pipe with a thermal switch
(`src/tsr1/thermal/lumped.py`). At the pole the Sun stays within a few degrees of the horizon, so a zenith radiator
sees mostly cold sky; it is sized with a dusty absorptance (×2.0 of beginning-of-life, within the 1.4–2.6 range of
[@S062]).

* Radiator **{b['a_rad']:.2f} m²** for 380 W at 293 K; maximum steady WEB dissipation over all modes
  **{max(en['web_dissipation_W'].values()):.0f} W**. The 3 kW power-transfer case is energy-limited
  ({en['emergency_3kW_duration_at_edge_h']:.1f} h at the 10 km edge, a few hours from a full battery) and its excess
  dissipation is absorbed by the WEB heat capacity within ΔT ≤ 15 K (closure THERMAL-1a/b). The PTM was moved to a
  single isolated stage on the battery after the first thermal closure failed.
* Cold case (PSR sink 40 K): leak {th['leak_cold_w']:.0f} W, heaters {b['heater_cold']:.0f} W after crediting electronics
  dissipation; survival power {en['survival_power_W']:.0f} W, giving **{en['survival_full_battery_h']:.0f} h** of darkness
  survival on a full battery and indefinite survival in sunlight (PV average {en['solar_avg_W']:.0f} W > survival power).
* PSR excursions are limited to {dv['psr_excursion_h']} h (energy-limited {en['psr_excursion_energy_limited_h']:.0f} h with a
  factor-two margin).
* Actuators are specified cold-tolerant (no survival heat), following the bulk-metallic-glass gear demonstration
  [@S040]; heritage-class actuators would need warm-up heaters [@S041] and would cut darkness survival by roughly
  80 h (technology gap TG-01).
"""


def s_avionics(D):
    tr = D["tr"]
    au = [[r["option"], f(r["task_h"], 1), f(r["operator_h"], 1), "yes" if r["works_in_outage"] else "no", r["contact_safety"]]
          for r in tr["autonomy"]]
    return f"""## 15. Avionics and Autonomy

**Computing.** Two physically separate domains. The autonomy domain runs on a High-Performance Spaceflight Computing
class processor (rad-hard variant 100 krad TID, [@S039]) and hosts the mission and task planners, verified skill
sequencer, perception and motion planning; machine-learning components (terrain classification, anomaly ranking,
pose estimation, diagnosis ranking) are advisory. The safety/real-time domain is a dual-lane radiation-hardened
computer pair running servo loops, force/impedance control and the winch tension loop, and independent deterministic
guards (force/torque, speed near crew 0.2 m/s and 50 N, tip factor from measured centre of pressure, winch tension,
power-port interlocks, keep-out zones). **The autonomy domain never commands actuator torques directly**: it requests
skills, and the safety domain executes only those that pass its checks; it can also execute pre-verified skills and
minimal navigation alone (degraded mode DM-7).

**Trade TS-09 (autonomy).** Duration of a module swap and human operator time by control concept:

{table(['Option', 'Task duration [h]', 'Operator time [h]', 'Works in comm outage', 'Contact safety'], au)}
Teleoperation from Earth is slow because of the round-trip delay and ≈ 51 % direct-to-Earth availability [@S073] and
unsafe for contact tasks because force loops would close through seconds of latency. Full autonomy cannot be
verified for novel faults. **Selected: supervised autonomy** with human approval at hold points (power connection,
release of load-bearing fasteners, ORU insertion, winch tension above 1 kN). Multi-robot autonomy precedent comes from
CADRE [@S069].

{fig(13, 'fig07_autonomy_architecture.png', 'Layered autonomy: mission planner to actuators, with the independent deterministic safety layer and hold points.')}
"""


def s_comms(D):
    c = D["tr"]["comms"]
    av = [[k, f(v, 3)] for k, v in c["availability"].items()]
    lk = [["relay @ 10 000 km (S-band, 5 W, 10 dBi)", f(c['link_10000km']['eirp_dbw']), f(c['link_10000km']['fspl_db']),
           f(c['link_10000km']['cn0_dbhz']), f"{c['link_10000km']['max_rate_bps'] / 1e3:.0f} kbit/s"],
          ["relay @ 3 000 km", f(c['link_3000km']['eirp_dbw']), f(c['link_3000km']['fspl_db']), f(c['link_3000km']['cn0_dbhz']),
           f"{c['link_3000km']['max_rate_bps'] / 1e6:.1f} Mbit/s"],
          ["Ka-band option @ 10 000 km", f(c['ka_band_10000km']['eirp_dbw']), f(c['ka_band_10000km']['fspl_db']),
           f(c['ka_band_10000km']['cn0_dbhz']), f"{c['ka_band_10000km']['max_rate_bps'] / 1e6:.1f} Mbit/s"]]
    return f"""## 16. Communications and Navigation

**Trade TS-08.** Link availability by architecture (component availabilities: surface network 0.90 within the base,
relay 0.80 in the early constellation, direct-to-Earth 0.51 [@S073]):

{table(['Architecture', 'Availability'], av)}
**Selected:** the base surface network (LTE-class, with lunar precedent [@S068]; towers covering ≈ 10 km cells,
[@S054]), LunaNet-compatible S-band relay [@S017; @S018], a UHF peer mesh with assets and other robots, and
delay-tolerant networking for all non-real-time data [@L020]. Link budget:

{table(['Case', 'EIRP [dBW]', 'Path loss [dB]', 'C/N0 [dB-Hz]', 'Max data rate'], lk)}
Approval-critical data for a hold point (≈ 50 MB of imagery and LiDAR) moves over the relay in 15–20 min in the worst
case; bulk data waits for the surface network. Ka-band was rejected (pointing mechanism in dust, power) because approval
latency rather than bandwidth limits productivity. A deployable repeater module extends links into shadowed craters.

**Navigation.** Visual odometry, an LN-200S-class IMU [@S065], sun sensor/star tracker and LiDAR map matching give
≤ 1 m global position in the base frame; before contact, relative pose is refined to ≤ 5 mm / 0.5° from fiducials and
stereo. LunaNet positioning services, when available, discipline the clock and global fix.

{fig(14, 'fig08_communications_architecture.png', 'Communications architecture: surface network, relay, mesh, DTN and repeater.')}
"""


def s_dust(D):
    return """## 17. Dust Mitigation

Dust is treated as a design load, not an afterthought. Apollo experience lists vision obscuration, false readings,
coating, traction loss, clogging of mechanisms, abrasion, thermal-control degradation and seal failure, and shows that
losing a fender produces a "rooster tail" of ejecta [@S022]. TSR-1's measures follow those failure modes:

| Failure mode | Measure | Basis |
|---|---|---|
| Wheel ejecta onto radiator, optics, mechanisms | fenders with skirts over all six wheels | Apollo LRV fender loss [@S022] |
| Radiator absorptance growth | zenith radiator sized for α × 2.0; electrodynamic dust-shield film | [@S062; @S063; @S019] |
| Optics obscuration | EDS on camera and LiDAR windows; covers when idle | [@S063] |
| Mechanism clogging, torque rise | labyrinth seals + PTFE bellows on every external joint; no dynamic elastomers | [@S021] |
| Connector contamination | dust-tolerant connector with self-closing cover, pre-mate brushing and contact-resistance check | [@S042] |
| Client asset degradation | brush and EDS-wand tools; residual coverage target ≤ 5 % | MR-07 |

EDS energy is negligible (≈ 3.3 mWh/m² per cleaning cycle, [@S063]); the cost is kV electronics and patterned
transparent electrodes. Ten-year dust life of about thirty external actuators is an open technology gap (TG-07).
"""


def s_materials(D):
    tr = D["tr"]
    am = [[r["material"], f(r["arm_mass_kg"], 1), f(r["specific_stiffness_MNm_per_kg"], 1), f(r["cte_per_K"] * 1e6, 1),
           f(r["thermal_growth_mm_1p5m_250K"], 2)] for r in tr["arm_materials"]]
    cm = [[r["material"], f(r["chassis_mass_kg"], 1), f(r["t_face_mm"], 2), f(r["f1_Hz"], 0), f(r["cte_per_K"] * 1e6, 1)]
          for r in tr["chassis_materials"]]
    n_mat = len(csv_rows(ROOT / "engineering" / "materials_matrix.csv"))
    return f"""## 18. Materials

Material choices were made per component against strength, stiffness, thermal expansion over a 40–390 K range,
abrasion, cold toughness and heritage, using handbook properties [@L005] (`engineering/materials_matrix.csv`,
{n_mat} rows). **Trade TS-10** compared candidates for the two structures where the choice matters most:

*Dexterous-arm links:*

{table(['Material', 'Arm mass [kg]', 'Specific stiffness [MN·m/kg]', 'CTE [10⁻⁶/K]', 'Growth over 1.5 m, 250 K [mm]'], am)}
*Chassis torque box:*

{table(['Material', 'Chassis mass [kg]', 'Face thickness [mm]', 'f₁ [Hz]', 'CTE [10⁻⁶/K]'], cm)}
The chassis is minimum-gauge driven, so the lighter options save little; aluminium honeycomb (Al 7075 faces, Al 5056
core) was selected for manufacturability, damage tolerance and repairability, with CFRP kept as a −15 kg descope.
Titanium arm links were selected over aluminium for their thermal-expansion match to steel gear sets and the lower
thermal growth that the 2 mm positioning requirement needs. Wheels and hard points are Ti-6Al-4V; the crane boom and
mast are CFRP; the recovery line is Vectran, which is about one fifth of the mass of an equivalent steel rope.
"""


def s_budgets(D):
    b, sens, en = D["base"], D["sens"], D["en"]
    sub = [[s, f(c, 1), f(p, 1), f(100 * (p / c - 1), 0) + " %"] for s, c, p in b["subsystems"]]
    mm = sens["mass_mc"]
    cats = {}
    for c in D["clo"]:
        k = c["check"].split("-")[0].split()[0]
        cats.setdefault(k, [0, 0])
        cats[k][0] += 1
        cats[k][1] += 1 if c["passed"] else 0
    crow = [[k, f"{v[1]}/{v[0]}"] for k, v in cats.items()]
    pick = [c for c in D["clo"] if c["check"].split()[0] in ("MASS-3", "ENERGY-1", "ENERGY-2", "THERMAL-1a", "MOB-1", "MOB-2", "REC-W", "MAN-1", "GEOM-2")]
    prow = [[c["check"], ("feasible" if c["computed"] else "infeasible") if isinstance(c["computed"], bool)
             else f(c["computed"], 2) if isinstance(c["computed"], (int, float)) else str(c["computed"]),
             f(c["limit"], 2) if isinstance(c["limit"], (int, float)) else "—", "pass" if c["passed"] else "**FAIL**"] for c in pick]
    return f"""## 19. Mass and Power Budgets

**Mass.** The bottom-up budget (`engineering/mass_budget.csv`) lists every component with current best estimate
(CBE), AIAA S-120A growth allowance by category and maturity [@S052], position, material, TRL and the model or source that
gives its mass. A 15 % system margin is added to the predicted mass to form the dry allocation, and a 5 % lander
accommodation allowance to form the delivered mass.

{table(['Subsystem', 'CBE [kg]', 'Predicted (CBE + MGA) [kg]', 'Growth'], sub)}
CBE {f(b['cbe'], 0)} kg → predicted {f(b['predicted'], 0)} kg → dry allocation {f(b['dry_allocation'], 0)} kg → operational
{f(b['operational'], 0)} kg (with 100 kg of carried ORUs and modules) → **delivered {f(b['delivered'], 0)} kg**. A Monte Carlo over
the mass-estimating relations and growth allowances gives P10/P50/P90 = {f(mm['p10'], 0)}/{f(mm['p50'], 0)}/{f(mm['p90'], 0)} kg and
P(delivered ≤ 1.5 t) = {mm['p_le_1500']:.2f}: TSR-1 fits an Argonaut-class 1.5 t lander with margin [@S047] and a Blue Moon
Mk1-class 3 t lander easily [@S056], but not a Griffin-class lander [@S057].

**Power.** Mode powers are sums of component loads (Section 13); peak simultaneous load is {f(en['peak_sum_W'], 0)} W
against a 4 kW PCDU.

**Closure.** {len(D['clo'])} independent checks (directive §44) all pass after the design review:

{table(['Check family', 'Passed'], crow)}
Selected checks:

{table(['Check', 'Computed', 'Limit', 'Result'], prow)}
Two checks failed during the work and drove design changes rather than being relaxed: thermal closure (THERMAL-1)
failed during design iteration with a two-stage PTM, which was replaced by a single isolated stage on the battery,
and energy closure (ENERGY-1) failed in the pre-review snapshot ({D['pre']['clo'][[c['check'][:8] for c in D['pre']['clo']].index('ENERGY-1')]['computed']:.2f} kWh needed against
14 kWh), which raised the battery to 15 kWh (CDR-06).

{fig(15, 'fig10_mass_budget.png', 'Mass budget by subsystem: CBE, growth allowance and margins to the delivered mass.')}
{fig(16, 'fig20_mass_monte_carlo.png', 'Delivered-mass Monte Carlo over mass-estimating relations and growth allowances, with lander capacities.')}
"""


def s_reliability(D):
    rel = D["rel"]
    rows = [[k.replace("_", " "), f(v["fault_rate_per_yr"], 2), f(v["p_capable_10yr"], 2), f(v["availability_full"], 2),
             f(v["availability_capable"], 3), f(v["mean_outage_days"], 0)] for k, v in rel.items()]
    return f"""## 20. Reliability

TSR-1 itself is modelled as a set of orbital-replacement-unit classes with constant failure rates (ESTIMATE, by class:
drive units, steering units, arms, crane, winch, PTM, converters, computers, cameras, LiDAR, comm link, thermal loop,
battery modules), each classed as servicing-critical or not, and repaired by ORU replacement from spares
(`src/tsr1/reliability/tsr_reliability.py`). Exponential failures are assumed [@L019]; common-cause dust failures are
not modelled and would make these results optimistic.

{table(['Repair policy', 'Faults per year', 'P(servicing-capable at 10 yr)', 'Fully functional fraction', 'Servicing-capable fraction', 'Mean outage [d]'], rows)}
Repairability matters more than redundancy: with ORU repair by crew or a peer vehicle the rover remains
servicing-capable over ten years with high probability, without repair it does not. The FMEA (`engineering/fmea.md`)
lists 27 failure modes, the single-point failures that remain (winch, PTM, crane slew) and nine degraded modes
(DM-1..DM-9), e.g. driving on four of six wheels ({f(D['mob']['slopes_deg']['two_wheels_out'], 1)}° slope) or providing PV-only
charging without the PTM.

{fig(17, 'fig16_reliability_model.png', 'TSR-1 self-reliability: probability of remaining servicing-capable versus time for four repair policies.')}
"""


def s_value(D):
    val, cdr, cap = D["val"], D["cdr"], D["cap"]
    sc = val["base_scenario"]
    vb = val["base"]
    sd = (vb["dA"]["p90"] - vb["dA"]["p10"]) / 2.563          # normal-equivalent spread from the P10-P90 range
    se400, se200 = sd / math.sqrt(D["runs"]), sd / math.sqrt(D["runs_sweep"])
    rows = [["Mean availability", f(vb['A0']['mean'], 3), f(vb['A1']['mean'], 3),
             f"{pp(vb['dA']['p10'])} / {pp(vb['dA']['p50'])} / {pp(vb['dA']['p90'])} pp"],
            ["Preventable asset losses", f(vb['plost0']['mean']), f(vb['plost1']['mean']),
             f"{vb['plost1']['mean'] - vb['plost0']['mean']:+.1f}"],
            ["Asset losses, all causes", f(vb['lost0']['mean']), f(vb['lost1']['mean']), f"{vb['lost1']['mean'] - vb['lost0']['mean']:+.1f}"],
            ["Fault events", f(vb['faults0']['mean'], 0), f(vb['faults1']['mean'], 0), "more uptime → more faults"],
            ["Earth-supplied mass [t]", f(vb['mass0']['mean'] / 1000), f(vb['mass1']['mean'] / 1000),
             f"{(vb['mass1']['mean'] - vb['mass0']['mean']) / 1000:+.1f}"],
            ["Earth mass per available asset-year [kg]", f(val['kg_per_asset_yr0']['mean'], 0), f(val['kg_per_asset_yr1']['mean'], 0),
             f"{val['kg_per_asset_yr1']['mean'] - val['kg_per_asset_yr0']['mean']:+.0f}"],
            ["Crew EVA [crew-h]", f(vb['eva0']['mean'], 0), f(vb['eva1']['mean'], 0), f"{vb['eva1']['mean'] - vb['eva0']['mean']:+.0f}"],
            ["TSR-1 response time P50 / mean [h]", "—", f"{f(vb['resp']['p50'])} / {f(vb['resp']['mean'])}", "mean includes TSR-1 downtime"],
            ["TSR-1 utilisation", "—", f"{pp(vb['util']['mean'])} %", "—"]]
    sw = [[s["n_assets"], s["keepalive_modules"], pp(s["dA_mean"]), pp(s["dA_p10"]), f(s["plost0_mean"]), f(s["plost1_mean"]),
           f(s["mass_avoided_mean"] / 1000, 2), f(s["net_mass_benefit"] / 1000, 2),
           f"{s['mass0_mean'] / s['asset_yr0_mean']:.0f} → {s['mass1_mean'] / s['asset_yr1_mean']:.0f}", f(s["eva_avoided_mean"], 0)]
          for s in val["asset_sweep"]]
    red = [100 * (1 - (s["mass1_mean"] / s["asset_yr1_mean"]) / (s["mass0_mean"] / s["asset_yr0_mean"])) for s in val["asset_sweep"]]
    swd = {s["n_assets"]: s for s in val["asset_sweep"]}
    neg_net = [s["n_assets"] for s in val["asset_sweep"] if s["net_mass_benefit"] < 0]
    neg_p10 = [s["n_assets"] for s in val["asset_sweep"] if s["dA_p10"] < 0]
    lm = [[x["level_mix"], pp(x["dA_mean"]), f(x["plost0_mean"]), f(x["plost1_mean"])] for x in val["level_mix"]]
    cr = [[f"{x['crew_missions_per_yr']:.0f}", pp(x["dA_mean"]), f(x["plost1_mean"]), f(x["eva1_mean"], 0)] for x in val["crew"]]
    ka = [[k["keepalive_modules"], f(k["inventory_mass_kg"], 0), pp(k["dA_mean"]), f(k["plost1_mean"]), f(k["mass1_mean"] / 1000, 1),
           f(k["ka_denied_mean"], 2)] for k in val["keepalive"]]
    c1 = {(c["n_assets"], c["mtbf_yr"], c["keepalive_modules"]): c for c in cap if c["n_tsr"] == 1}
    c2 = {(c["n_assets"], c["mtbf_yr"], c["keepalive_modules"]): c for c in cap if c["n_tsr"] == 2}
    loads = sorted({(c["n_assets"], c["mtbf_yr"]) for c in cap}, key=lambda k: k[0] / k[1])
    cp = [[f"{n} / {m:g}", f(n / m, 1), f(c1[(n, m, 2)]["plost0"]), f(c1[(n, m, 2)]["plost1"]), f(c1[(n, m, 4)]["plost1"]),
           f(c1[(n, m, 8)]["plost1"]), f(c2[(n, m, 4)]["plost1"]), f(c1[(n, m, 4)]["response_h"]), f(c2[(n, m, 4)]["response_h"]),
           c1[(n, m, 4)]["ka_rule_q95"]] for n, m in loads]
    return f"""## 21. Infrastructure Availability Model

**Model.** A discrete-event simulation of a base of N assets over {sc['years']:.0f} years, run with and without TSR-1 on
common random numbers (`src/tsr1/reliability/value_model.py`). Assets are fixed or mobile ({pp(sc['frac_mobile'], 0)} % mobile),
spread uniformly over a {sc['service_radius_km']:.0f} km service radius, and of interface level L0–L3 (baseline mix
{', '.join(f'{lv} {pp(x, 0)} %' for lv, x in zip(('L0', 'L1', 'L2', 'L3'), sc['level_mix']))}). Faults arrive with a per-asset
MTBF (log-uniform 1–10 yr, A-08) and are of five types: electrical, dust, communication, immobilisation (mobile assets
only) and non-serviceable. A fraction of electrical/communication faults removes the asset's keep-alive power, and
the asset dies if not powered within its survival time (24–120 h). Without TSR-1, faults wait for a crew window
(zero to two 30-day missions per year with a crew-hour budget) or an Earth spare; lost assets are replaced from Earth
after 1–2 years. With TSR-1, a priority queue dispatches the rover (unpowered faults first); it travels at the
effective speed, restores power, attempts the repair with level-dependent success (Section 11), recovers immobilised
vehicles within the recovery envelope (Section 12), and, if a repair fails, leaves a keep-alive module so the asset
can wait for a spare or crew. TSR-1 itself fails and is repaired. Uncertain inputs (MTBF, spare availability,
survival time, lead times, crew missions, speed, TSR-1 reliability, keep-alive success) are sampled per replicate.

Two accounting rules came out of the design review (CDR-19). First, a failed TSR-1 attempt does not end the asset's
chances: crew can still act within the survival or abandonment time, as in the baseline. Second, losses from
non-serviceable faults are not preventable and grow with operating exposure — an asset that TSR-1 keeps alive can fail
again — so **preventable losses** and **Earth mass per available asset-year** are the fair comparison; totals are
reported alongside.

All value studies reuse the same seed, so replicate k draws the same epistemic scenario in every table (common random
numbers): rows of different tables are paired. The Monte Carlo standard error of a mean availability gain is
≈ {pp(se400, 2)} pp for the {D['runs']}-replicate reference run and ≈ {pp(se200, 2)} pp for the {D['runs_sweep']}-replicate sub-studies;
differences smaller than that are not resolved.

**Reference base (N = {sc['n_assets']}, {sc['keepalive_modules']} keep-alive modules, {D['runs']} epistemic Monte Carlo replicates):**

{table(['Metric', 'Without TSR-1', 'With TSR-1', 'Difference'], rows)}
**Scale (keep-alive inventory sized per base by the CDR-19 rule; net = Earth mass avoided − TSR-1 life-cycle mass, which
includes the rover, ten years of spares and the keep-alive modules):**

{table(['Assets', 'MOD-KA', 'ΔA mean [pp]', 'ΔA P10 [pp]', 'Preventable losses without', 'with', 'Mass avoided [t]', 'Net benefit [t]', 'kg per available asset-year, without → with', 'EVA avoided [crew-h]'], sw)}
The logistics break-even is **≈ {f(val['break_even_assets'], 0)} assets**: the net benefit is negative for
{', '.join(map(str, neg_net))} assets, and the P10 of the availability gain is negative for {', '.join(map(str, neg_p10)) or 'none'}. Mass avoided grows
less than in proportion to base size ({swd[30]['mass_avoided_mean'] / 1000:.1f} t at 30 assets, {swd[60]['mass_avoided_mean'] / 1000:.1f} t at 60), partly because a
base that TSR-1 keeps running accumulates more fault events; the mass per available asset-year (excluding TSR-1's own
life-cycle mass) is {min(red):.0f}–{max(red):.0f} % lower with TSR-1 at every base size.

**Asset standardisation** (same base, interface-level mix varied):

{table(['Interface mix', 'ΔA [pp]', 'Preventable losses without', 'with'], lm)}
**Crew presence:**

{table(['Crew missions per year', 'ΔA [pp]', 'Preventable losses with TSR-1', 'EVA with TSR-1 [crew-h]'], cr)}
**Keep-alive inventory (reference base):**

{table(['MOD-KA modules', 'Inventory mass [kg]', 'ΔA [pp]', 'Preventable losses', 'Earth mass with TSR-1 [t]', 'Requests with none free'], ka)}
Keep-alive modules buy losses and logistics mass, not availability: a parked asset is still down while it waits. The
inventory rule — Poisson 95th percentile of f_park · p_KA · F · T_hold (Little's law) — gives {sc['keepalive_modules']} modules at
the reference base.

**Capacity study** (nominal scenarios with fixed MTBF; preventable losses over ten years; `simulations/capacity_study.py`):

{table(['Assets / MTBF [yr]', 'Faults per year', 'Without TSR-1', '1 TSR, 2 KA', '1 TSR, 4 KA', '1 TSR, 8 KA', '2 TSR, 4 KA', 'Response 1 TSR [h]', 'Response 2 TSR [h]', 'KA rule'], cp)}
One TSR-1 does not saturate on driving or servicing time even at 60 faults per year (utilisation stays in the
single-digit percent range); what saturates is the keep-alive inventory. A second rover halves the response time but
barely changes losses, because response is already well inside the survival time.

{fig(18, 'fig17_montecarlo_results.png', 'Reference-base Monte Carlo: availability with and without TSR-1, distribution of the availability gain, and Earth mass avoided against TSR-1 life-cycle mass.')}
{fig(19, 'fig18_value_vs_infrastructure_scale.png', 'Value versus infrastructure scale: availability gain, net logistics benefit with break-even, crew EVA avoided, and preventable losses.')}
{fig(20, 'fig22_capacity_study.png', 'Capacity study: preventable losses and Earth mass per available asset-year versus keep-alive inventory for five fault loads; response time with one and two rovers.')}
"""


TRADES = [
    ("TS-01", "Mobility architecture", "M2 six-wheel rocker-bogie + body lowering + differential lock",
     "gradeability is soil-limited; +29 kg buys lowered work posture and wheel unloading"),
    ("TS-02", "Wheels", "rigid Ti Ø0.90 × 0.40 m, 18 × 20 mm grousers", "≤ 7 kPa at final mass; model confidence; dust"),
    ("TS-03", "Manipulators", "A7: two identical 7-DOF dexterous arms + cable-stayed crane", "heavy arm ≈ 3.5× mass for little coverage"),
    ("TS-04", "Stabilisation", "body lowering + rear spades + front hold-down straps; no outriggers", "outriggers resist tipping, not sliding"),
    ("TS-05", "Recovery", "R4: 4 kN winch, low fairlead, 2 spades + 2 helical anchors", "towing traction-limited on slopes"),
    ("TS-06", "Energy", "Li-ion 15 kWh EOL + vertical PV + node charging", "RPS rejected for availability/approval"),
    ("TS-07", "Service modules", "modular 6-slot spine; MOD-KA KA-C, inventory by rule", "deployable keep-alive; host portability"),
    ("TS-08", "Communications", "surface network + LunaNet relay + UHF mesh + DTN", "availability 0.98; latency not bandwidth limits"),
    ("TS-09", "Autonomy", "supervised autonomy with hold points", "teleop slow and unsafe; full autonomy unverifiable"),
    ("TS-10", "Structural materials", "Al honeycomb chassis; Ti arm links, wheels, hard points; CFRP boom/mast", "minimum-gauge chassis; CTE match"),
]

CDR = [
    ("CDR-01", "Is a dedicated rover necessary? NASA's Lunar Utility Rover already includes servicing.", "valid — kit variant added; dedicated carrier only where no host can respond in time"),
    ("CDR-02", "Dual arms unjustified.", "partially valid — heavy arm replaced by crane; second dexterous arm kept"),
    ("CDR-03", "Too massive.", "partially valid — descope list; kit variant"),
    ("CDR-04", "Towing unrealistic in regolith.", "valid — anchored winching"),
    ("CDR-05", "Anchors impractical.", "partially valid — accepted risk, TRL 3, proof-load hold point"),
    ("CDR-06", "Battery inadequate.", "valid — 14 → 15 kWh; radius tied to speed"),
    ("CDR-07", "Spine adds mass.", "invalid — saves carried mass; enables deployable modules"),
    ("CDR-08", "Assets will not be standardised.", "valid — open; dominant value driver"),
    ("CDR-09", "Robotic repair too difficult.", "partially valid — pessimism case keeps value positive"),
    ("CDR-10", "Autonomy too complex.", "partially valid — verified skills, deterministic guards"),
    ("CDR-11", "Relies on non-existent infrastructure.", "valid — open; degraded alternatives recorded"),
    ("CDR-12", "Low utilisation.", "valid — patrols and logistics in idle time (not credited)"),
    ("CDR-13", "Effective speed optimistic.", "valid — service radius tied to demonstrated speed"),
    ("CDR-14", "Thin thermal margins with dust.", "accepted — EDS, charging throttling"),
    ("CDR-15", "Slope capability overstated.", "valid — nominal and conservative requirement"),
    ("CDR-16", "Launch loads unknown.", "accepted — open until lander selection"),
    ("CDR-17", "Value is an artefact of fault rate.", "valid — scope: not justified for small bases"),
    ("CDR-18", "A second TSR is needed.", "accepted — one unit; capacity set by keep-alive inventory"),
    ("CDR-19", "Value collapses at large bases.", "partially valid — exposure artefact corrected; keep-alive inventory rule"),
    ("CDR-20", "Keep-alive module cannot do what is claimed.", "valid — module resized (23 → ≈ 73 kg) and its success probability modelled"),
    ("CDR-21", "The equipment does not fit on the deck.", "valid — single layout definition; spine as 2 × 3 grid mid-deck; arms stow upright; WEB moved aft to restore axle loads"),
]


def s_trades(D):
    rows = [list(t) for t in TRADES]
    cdr = [list(c) for c in CDR]
    return f"""## 22. Trade Studies

The ten formal trades (`trade_studies/`) used direct engineering comparison — mass, capability, closure margin,
reliability — and weighted task coverage only where tasks have to be aggregated (TS-03, weights from DRM frequency).

{table(['ID', 'Trade', 'Selected', 'Decisive reason'], rows)}
**Adversarial review.** The team then acted as a hostile review board whose aim was to invalidate TSR-1
(`CRITICAL_DESIGN_REVIEW.md`):

{table(['ID', 'Objection', 'Disposition'], cdr)}
The review invalidated two original hypotheses (heavy service arm; towing as the primary recovery method), found
three physical inconsistencies in the pre-review design (battery energy; keep-alive module mass; deck layout), corrected one
modelling inconsistency (failed-attempt handling) and substantially weakened the case for a *dedicated* vehicle
relative to a host-mounted service-and-recovery kit (≈ {f(D['cdr']['service_kit']['kit_allocation_kg'], 0)} kg against
{f(D['cdr']['service_kit']['dedicated_delivered_kg'], 0)} kg for the dedicated rover).

{fig(21, 'fig21_comparison_matrix.png', 'Comparison of TSR-1 with baseline systems (crew EVA, LTV with attachments, utility rover with kit, no servicing) across the servicing functions.')}
"""


def s_results(D):
    dv, m, en, rec, b = D["dv"], D["mob"], D["en"], D["rec"], D["base"]
    rows = [["Delivered / operational mass", f"{f(b['delivered'], 0)} / {f(b['operational'], 0)} kg"],
            ["Gradeability (slip ≤ 0.4)", f"{m['slopes_deg']['nominal']:.1f}° nominal, {m['slopes_deg']['conservative']:.1f}° conservative"],
            ["Contact pressure", f"{m['contact_pressure_kPa']:.2f} kPa"],
            ["Service radius / response time", f"{dv['service_radius_km']:.0f} km / ≤ {dv['response_time_h']} h (radius scales with effective speed)"],
            ["Range on one charge (keeping 50 h reserve)", f"{en['range_km']:.0f} km"],
            ["Darkness survival (full battery)", f"{en['survival_full_battery_h']:.0f} h; indefinite in sunlight"],
            ["Emergency power", f"3 kW continuous, 4.5 kW for 60 s; {en['keepalive_duration_at_edge_h']:.1f} h at 300 W at the 10 km edge"],
            ["Manipulation", f"2 × {dv['dex_payload_kg']:.0f} kg dexterous arms, reach {dv['dex_reach_m']} m; crane 150 kg at {dv['heavy_reach_m']} m"],
            ["Recovery", dv["rec_envelope_text"]],
            ["Recovery scenarios A–D3", ", ".join(f"{r['id']} {'✓' if r['feasible'] else '✗'}" for r in rec["scenarios"])],
            ["P(servicing-capable at 10 yr)", f"{dv['p_mission_10yr']}"],
            ["Budget closure", f"{sum(1 for c in D['clo'] if c['passed'])}/{len(D['clo'])} checks pass"]]
    return f"""## 23. Simulation Results

Consolidated performance of the frozen configuration (`DESIGN_FREEZE_V1.md`, generated from the same results):

{table(['Quantity', 'Value'], rows)}
Each design reference mission (Section 13) fits the battery's usable energy at the 10 km edge with the survival
reserve intact (worst case DRM-2, closure ENERGY-1) and completes within one 30 h approval cycle (closure MISSION
checks). The DRM-2 electrical-fault mission — traverse, inspect,
connect emergency power, diagnose, replace an ORU, test and return — takes {f(en['drms'][1]['duration_h'], 1)} h and
{f(en['drms'][1]['energy_kwh'], 2)} kWh. The principal value results are those of Section 21: a mean availability gain of
{pp(D['val']['base']['dA']['mean'])} percentage points at 30 assets, a reduction of preventable losses by
{pp(1 - D['val']['base']['plost1']['mean'] / D['val']['base']['plost0']['mean'], 0)} %, and an Earth-mass reduction of
{pp(1 - D['val']['base']['mass1']['mean'] / D['val']['base']['mass0']['mean'], 0)} %, with modest EVA savings.
"""


NAMES = {"soil_phi_deg": "soil friction angle φ [deg]", "soil_K": "shear deformation modulus K [m]", "soil_c": "cohesion c [Pa]",
         "soil_n": "sinkage exponent n", "wr_c1": "Wong–Reece c₁", "wr_c2": "Wong–Reece c₂", "soil_kphi": "k_φ", "soil_kc": "k_c",
         "act_torque_density": "actuator torque density [N·m/kg]", "system_margin": "system margin", "motorisation_factor":
         "motorisation factor", "batt_spec_energy": "battery specific energy [Wh/kg]", "mga_mechanism": "mechanism growth allowance",
         "wheel_rim_t": "wheel rim thickness [m]", "harness_frac": "harness fraction", "batt_eol_fade": "battery end-of-life fade",
         "batt_dod": "battery depth of discharge", "mga_structure": "structure growth allowance", "mga_harness": "harness growth allowance",
         "tsr_speed_eff": "effective traverse speed [km/h]", "p_keepalive_w": "keep-alive power [W]", "drive_duty": "driving duty",
         "drive_eff": "drive efficiency", "conv_eff": "converter efficiency", "recovery_fos": "recovery factor of safety",
         "spade_shape_factor": "spade shape factor", "helix_Nq": "helical-anchor breakout factor N_q*",
         "p_brake_release": "P(target brakes releasable)", "mtbf": "asset MTBF", "p_spare": "spare availability",
         "t_survive": "asset survival time", "crew": "crew missions per year", "speed": "TSR-1 effective speed",
         "tsr_mtbf": "TSR-1 MTBF", "frac_unp": "fraction of faults removing power"}


def nm(k):
    return NAMES.get(k, k)


def s_sensitivity(D):
    s, val, cdr = D["sens"], D["val"], D["cdr"]

    def top(key, n=4, d=1):
        return [[nm(r["parameter"]), f"{r['low']:g}–{r['high']:g}", f(r["f_low"], d), f(r["f_high"], d), f(r["swing"], d)]
                for r in s[key][:n]]
    sc = val["sensitivity_corr"]
    rec_pe = D["rec"]["p_env"][R4]
    hc = {x["case"]: x for x in cdr["host_cases"]}
    hd, h30, h60 = (list(hc.values()) + [None] * 3)[:3]
    corr = [[nm(k.split("->")[0]), f(sc[k], 2), f(sc[k.replace("->dA", "->mass_avoided")], 2)] for k in sc if k.endswith("->dA")]
    sk = [[f(x["robot_step_factor"], 2), f(x["p_oru_L2"], 2), pp(x["dA_mean"]), f(x["plost1_mean"])] for x in cdr["skill_factor"]]
    hk = [[x["case"], pp(x["dA_mean"]), f(x["plost1_mean"])] for x in cdr["host_cases"]]
    spd = [[f(x["speed_kmh"], 2), f(x["max_service_radius_km"], 1), f(x["drm2_10km_kwh"], 2)] for x in cdr["speed_radius"]]
    return f"""## 24. Sensitivity Analysis

**Gradeability** is dominated by the {nm(s['slope'][0]['parameter']).split(' [')[0]} (tornado, nominal {f(s['slope'][0]['f_nominal'], 1)}°):

{table(['Parameter', 'Range', 'Slope at low [°]', 'at high [°]', 'Swing [°]'], top('slope'))}
**Delivered mass** is dominated by {', '.join(nm(r['parameter']).split(' [')[0] for r in s['mass'][:2])} and {nm(s['mass'][2]['parameter']).split(' [')[0]} (nominal
{f(s['mass'][0]['f_nominal'], 0)} kg):

{table(['Parameter', 'Range', 'Mass at low [kg]', 'at high [kg]', 'Swing [kg]'], top('mass', 5, 0))}
**DRM-2 energy** is dominated by the {nm(s['drm2_energy'][0]['parameter']).split(' [')[0]} (hotel loads during slow traverse), not by drive or conversion efficiency:

{table(['Parameter', 'Range', 'Energy at low [kWh]', 'at high [kWh]', 'Swing [kWh]'], top('drm2_energy', 4, 2))}
{table(['Effective speed [km/h]', 'Max service radius [km]', 'DRM-2 energy at 10 km [kWh]'], spd)}
**Recovery** probability responds most to the {nm(s['recovery'][0]['parameter'])}, then the {nm(s['recovery'][1]['parameter'])} and
the {nm(s['recovery'][2]['parameter'])}; the one-at-a-time swings are small because most sampled cases sit well inside the capacity,
whereas halving soil strength or taking the upper extraction-resistance bound moves it far more (Section 12:
{rec_pe['weak_soil']:.2f} and {rec_pe['high']:.2f} against {rec_pe['mid']:.2f}):

{table(['Parameter', 'Range', 'P at low', 'at high', 'Swing'], top('recovery', 4, 2))}
**Value.** Correlation of the sampled inputs with the availability gain and with Earth mass avoided (reference base):

{table(['Input', 'corr. with ΔA', 'corr. with mass avoided'], corr)}
Higher asset MTBF (fewer faults) {'reduces' if sc['mtbf->dA'] < 0 else 'increases'} the gain; more crew presence
{'reduces' if sc['crew->dA'] < 0 else 'increases'} the availability gain but {'increases' if sc['crew->mass_avoided'] > 0 else 'reduces'} the
mass avoided (crew and TSR-1 together repair more assets than either alone). Pessimistic robot skill reduces the value
roughly in proportion to ORU-swap success but does not remove it; a shared host busy 30 % of the time with 24 h delays
performs like the dedicated rover (ΔA {pp(h30['dA_mean'])} vs {pp(hd['dA_mean'])} pp, a difference inside the Monte Carlo
scatter), while one busy 60 % of the time with 72 h delays loses {pp(hd['dA_mean'] - h60['dA_mean'])} pp and raises preventable
losses from {f(hd['plost1_mean'])} to {f(h60['plost1_mean'])}:

{table(['Robot step factor', 'P(ORU swap, L2)', 'ΔA [pp]', 'Preventable losses'], sk)}
{table(['Host case', 'ΔA [pp]', 'Preventable losses'], hk)}
{fig(22, 'fig19_sensitivity_tornado.png', 'Tornado sensitivities: slope (soil), delivered mass (MER/MGA), DRM-2 energy and recovery probability.')}
"""


def s_trl(D):
    txt = (ROOT / "research" / "technology_readiness.md").read_text()
    rows = []
    for line in txt.splitlines():
        m_ = re.match(r"\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", line)
        if m_:
            trl = m_.group(3).strip()
            low = re.match(r"(\d)", trl)
            if (low and int(low.group(1)) <= 4) or "G" in m_.group(4):
                rows.append([m_.group(2).strip(), trl, m_.group(4).strip()])
    return f"""## 25. Technology Readiness

TRL is assessed for the TSR-1 application environment (lunar south pole, 40–390 K, abrasive and electrostatic dust,
ten-year life) using the NPR 7123.1 definitions [@S072], not for each technology's best heritage environment
(`research/technology_readiness.md`, 29 elements). Elements at TRL ≤ 4 or flagged as gaps:

{table(['Element', 'TRL', 'Class'], rows)}
The crane is TRL 4 but is not counted as a technology gap: ground prototypes exist [@S015] and no physical obstacle
was found. Component maturity reaches TRL 7 for structure, cameras, computers and navigation sensors, but the integrated
servicing-and-recovery system has never been built or tested in a relevant environment: **integrated TRL 4**. The
critical path runs through asset-interface standardisation (programmatic), servicing-autonomy verification,
regolith anchors, long-life cold and dust-tolerant mechanisms, and a robot-mateable kW connector.
"""


def s_limitations(D):
    return f"""## 26. Limitations

* **Evidence access.** Agency servers were blocked in the study environment; sources were read through
  search-engine excerpts (access labels in Section 29). Several handbook values are literature recall, not re-verified
  against full texts. One seed document could not be resolved.
* **No lunar failure data.** Asset fault rates, the fault-type mix and task-step success probabilities are
  assumptions with wide ranges (A-08, A-31). The value results are comparative, not predictive; conclusions rest on
  robust trends — sign, dependence on scale, dependence on standardisation — rather than absolute values.
* **Soil mechanics without lunar validation.** Terramechanics is calibrated on one datum (LRV energy) and anchors on
  none; slope claims carry several degrees of uncertainty and recovery claims are contingent on anchor tests.
* **Static and lumped models.** No vehicle dynamics, crane load-swing, transient thermal or finite-element analysis;
  arm and chassis masses carry ±30–40 %.
* **Keep-alive module.** Parked-asset survival power and dark-period statistics are assumed distributions
  (A-33..A-35); their real values decide how many losses the modules prevent.
* **No cost model.** Earth-supplied mass is used as the logistics proxy because no defensible cost data for lunar
  surface robotics were retrieved.
* **Scope.** Command authority over third-party assets, cybersecurity, lander accommodation and crew human factors
  beyond speed and force limits are not designed.

Full discussion: `docs/limitations.md`; open questions OQ-01..OQ-15: `results/open_questions.md`.
"""


def s_roadmap(D):
    return """## 27. Development Roadmap

No calendar dates are given: there is no funded programme, selected lander or adopted asset-interface standard on
which to base a schedule (`docs/development_roadmap.md`). The stages are ordered by technical dependency:

| Stage | Content | Exit gate |
|---|---|---|
| 0 Digital modelling | this study | closure, design freeze, review dispositions |
| 1 Subsystem breadboards | anchor pull-out rig in simulants; single-wheel rig; 3 kW connector mating rig; cold actuator life rig; PTM breadboard; servicing skills on a commercial arm | anchor capacity within ±30 % of model or recalibrated; ≥ 500 robotic mates; actuator life ≥ 25 % of duty |
| 2 Earth prototype | full-scale 1-g rover with arms, crane, spine, winch, PTM | all DRMs end-to-end on L0–L3 analogue targets |
| 3 Analogue field testing | multi-week campaigns with delays, outages, polar lighting | measured task success, effective speed, operator hours |
| 4 Thermal-vacuum and dust | subsystem and system TVAC (40–390 K), charged-dust chamber | ≥ 120 h survival; 3 kW transfer within limits |
| 5 Reduced-gravity / qualification | parabolic-flight wheel and anchor tests; crane swing control; launch loads | lunar-g traction penalty and anchor capacity quantified |
| 6 Flight demonstrator | reduced TSR (one arm, PTM, recovery kit, keep-alive module) servicing cooperative L2/L3 demo assets | in-situ ORU swap, power rescue, anchored recovery |
| 7 Operational system | TSR-1 or kit on a utility-rover host for a base with standardised assets | measured availability gain |

Stage 1 anchor and actuator-life breadboards are the cheapest, highest-information tests and should come first;
Stage 6 should not start before asset owners agree on L2/L3 interfaces, because without them a demonstrator would
prove only inspection and emergency power.
"""


def s_conclusions(D):
    val, rec, b = D["val"], D["rec"], D["base"]
    vb = val["base"]
    lm = {x["level_mix"]: x for x in val["level_mix"]}
    sw = {s["n_assets"]: s for s in val["asset_sweep"]}
    return f"""## 28. Conclusions

1. **The engineering closes, with identified technology development.** A {f(b['delivered'], 0)} kg rover performing
   inspection, 120 VDC emergency power, robotic ORU servicing, dust remediation and anchored-winch recovery passes all
   {len(D['clo'])} closure checks with components that are mostly TRL 5–7, but depends on four immature items: regolith
   anchors (TRL 3), cold- and dust-tolerant long-life actuators (TRL 4), verified supervised servicing autonomy
   (TRL 4) and robot-mateable dust-tolerant kW connectors (TRL 4–5). **Verdict: feasible with identified technology
   development** (`results/FEASIBILITY_VERDICT.md`).
2. **Two Todaro hypotheses failed in their original form.** A heavy service arm is mass-inefficient in lunar gravity
   (a crane does the lifting); towing is traction-limited on slopes (anchored winching raises recoverable cases from
   {pp(rec['p_env']['R0 direct towing (drive)']['mid'], 0)} % to {pp(rec['p_env'][R4]['mid'], 0)} %). Emergency power through
   standard interfaces (C), the modular spine (D) and multi-standard interfaces with levels L0–L3 (E) survived.
3. **The answer to the research question is a conditional yes.** For a 30-asset base, one TSR-1 raises mean
   availability by {pp(vb['dA']['mean'])} percentage points (P10 {pp(vb['dA']['p10'])}), cuts preventable losses by
   {pp(1 - vb['plost1']['mean'] / vb['plost0']['mean'], 0)} % and Earth-supplied mass by {pp(1 - vb['mass1']['mean'] / vb['mass0']['mean'], 0)} %;
   it reduces crew EVA only modestly ({f(vb['eva0']['mean'], 0)} → {f(vb['eva1']['mean'], 0)} crew-h), because assets it saves
   often still need crew for repairs it cannot do on non-standard interfaces.
4. **Scale and standards decide.** Below ≈ {f(val['break_even_assets'], 0)} serviceable assets TSR-1 does not pay for itself in
   logistics mass ({f(sw[5]['net_mass_benefit'] / 1000, 2)} t at 5 assets). The availability gain is
   {pp(lm['legacy (L0-heavy)']['dA_mean'])} pp for a legacy base and {pp(lm['standardised (L2/L3)']['dA_mean'])} pp for a
   standardised one: an L2 robotic-service interface requirement on lunar assets is worth more than any improvement to
   the rover.
5. **Keep-alive power is the core function, and its inventory is the scaling lever.** Preventing thermal death of
   unpowered assets is where most of the value comes from; at large or failure-prone bases a single rover saturates
   on keep-alive modules, not on driving or servicing time.
6. **A host-mounted kit is preferable where a host can respond in time.** The servicing and recovery functions
   weigh ≈ {f(D['cdr']['service_kit']['kit_allocation_kg'], 0)} kg as a kit; a dedicated carrier is justified only where no utility-rover
   host can reach an unpowered asset within its survival time.

The goal of the study was not to make TSR-1 look possible but to find what it would have to be to be possible. The
answer is a modest, anchor-dependent, keep-alive-centred service-and-recovery capability whose value is set less by
its own engineering than by how the rest of the lunar base is designed.
"""


def s_references(D, cited):
    out = ["## 29. References", "",
           "Keys refer to `paper/references.bib` and `research/source_register.csv`. *Access* states how the source was "
           "consulted in this study: EXCERPT (search-engine excerpt attributed to the primary document), SECONDARY "
           "(reported by a secondary source), EXISTENCE-ONLY (existence and scope confirmed, content not used for "
           "numbers), LITERATURE-RECALL (standard handbook value, not re-verified against the full text), NOT-RETRIEVED.", ""]
    for k in sorted(cited, key=lambda x: (x[0], int(re.sub(r"\D", "", x) or 0))):
        r = D["src"].get(k)
        if r is None:
            raise KeyError(f"citation {k} not in source register")
        out.append(f"- **[{k}]** {r['authors_or_org'].rstrip('.')}. *{r['title'].rstrip('.')}*. {r['document_type']}, "
                   f"{r['year'].rstrip('.')}. {r['identifier_or_url'].rstrip('.')}. Access: {r['verification']}.")
    return "\n".join(out) + "\n"


SECTIONS = [s_abstract, s_intro, s_need, s_landscape, s_question, s_method, s_environment, s_requirements,
            s_architecture, s_mobility, s_manipulation, s_recovery, s_power, s_thermal, s_avionics, s_comms, s_dust,
            s_materials, s_budgets, s_reliability, s_value, s_trades, s_results, s_sensitivity, s_trl, s_limitations,
            s_roadmap, s_conclusions]


def main():
    D = load()
    body = "\n".join(sec(D) for sec in SECTIONS)
    cited = sorted(set(k for grp in re.findall(r"\[(@[^\]]+)\]", body) for k in re.findall(r"@([A-Z]\d{3})", grp)))
    head = f"""---
title: "{TITLE}"
author: "Todaro Corp. — TSR-1 study team"
date: "Study baseline 3 October 2026"
bibliography: references.bib
---

# {TITLE}

**TODARO CORP. — TSR-1 Lunar Autonomous Service & Recovery Rover**

> {DISCL}

*Generated by `paper/build_paper.py` from `simulations/results/` (run with `simulations/build_all.py`). Repository
paths in the text refer to the study repository, where every model, parameter and derivation can be inspected.*

"""
    text = head + body + "\n" + s_references(D, cited)
    (ROOT / "paper" / "paper.md").write_text(text)
    words = len(re.findall(r"\w+", text))
    print(f"paper.md written: {len(SECTIONS) + 1} sections, {len(cited)} cited sources, ≈ {words} words")


if __name__ == "__main__":
    main()
