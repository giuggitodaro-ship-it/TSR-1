"""Generate component specification sheets (directive §43) into engineering/subsystem_specs/.

Mass, power, peak power, TRL basis and calculated values are pulled from the baseline configuration
(`design.configuration.build`) and simulation results, so the sheets cannot drift from the budgets.
Qualitative fields are curated below. Run after simulations/run_all.py:

    PYTHONPATH=src python engineering/build_specs.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tsr1.design.configuration import MODES, Options, build  # noqa: E402
from tsr1.common.params import REGISTRY as R  # noqa: E402
import tsr1.reliability.value_model  # noqa: E402,F401  (registers MOD-KA and value parameters)

RES = ROOT / "simulations" / "results"
OUT = ROOT / "engineering" / "subsystem_specs"


def J(n):
    return json.loads((RES / n).read_text())


_PENV = J("recovery.json")["p_env"]
_MOBJ = J("mobility.json")["slopes_deg"]
_B, _EN, _TR = J("baseline_summary.json"), J("energy_power_thermal.json"), J("trades.json")
_MOB = {x["candidate"][:2]: x for x in _TR["mobility"]}
_ACT = [_MOB[k]["delivered_mass_kg"] - _MOB["M2"]["delivered_mass_kg"] for k in ("M3", "M4")]
_MAN = {a["architecture"][:2]: a for a in _TR["manipulators"]}
_WEIGHT = _B["vehicle"]["mass"] * 1.62

# key: (subsystem file, [config component names or prefixes], curated fields)
SPECS = {}


def spec(file, comps, **kw):
    SPECS[kw["COMPONENT"]] = (file, comps, kw)


# ------------------------------------------------------------------------------------------- mobility
spec("mobility", ["wheel_"], COMPONENT="Wheel (×6)", FUNCTION="Support vehicle load, generate traction, roll over regolith and rocks",
     TECH="Rigid wheel, Ø0.90 m × 0.40 m, 18 Ti grousers h = 20 mm, internal flexure spokes",
     MAT="Ti-6Al-4V rim (1.2 mm skin) and spokes; plasma-nitrided grouser tips",
     WHY_T="Contact pressure 6.6 kPa ≤ 7 kPa rule (S023) with DP/W(40 %) ≥ 0.36 at lowest wheel mass in the TS-02 sweep; rigid-wheel terramechanics applies (model confidence)",
     WHY_M="Toughness and fatigue strength at 40–390 K, abrasion resistance after nitriding; Al rims suffered rock damage on MSL",
     ALT="Ø0.8 × 0.35 m (pressure 7.1 kPa at final mass), LRV wire mesh, NiTi spring tyre, Al 7075 rigid wheel",
     REJ="smaller wheel violated 7 kPa at final mass; mesh/NiTi: dust ingress, unproven 10-yr fatigue, low model confidence (NiTi kept as upgrade); Al: damage history",
     DIM="Ø0.90 m, width 0.40 m, grouser height 0.020 m", TEMP="−230 °C to +120 °C (non-operating extremes); no limit for operation",
     LOADS="static wheel load ≈ 330 N (lunar); design 3 g lunar dynamic + launch 6 g/3 g on locks",
     RAD="none (metallic)", DUST="no enclosed volume; grousers shed regolith; fender + skirt limit ejecta",
     LIFE="10 yr / ≥ 1500 km traverse (no flight data at this distance)", RED=f"6 wheels; mobility with 5/6 driven ({_MOBJ['one_wheel_out']:.1f}°) or 4/6 driven ({_MOBJ['two_wheels_out']:.1f}°)",
     FAIL="rim crack (fatigue), grouser wear, spoke buckling on rock impact", MAINT="wheel+drive ORU at hub flange (II-04); body lowering unloads wheel",
     TRL="6 (rigid lunar/Mars wheels flown; this size/material in lunar dust not qualified)", HER="VIPER, Yutu, Pragyan, MSL/M2020 rigid wheels",
     ASM="A-03 soil; wheel_rim_t ESTIMATE", UNC="rim thickness for 10-yr fatigue (±50 %); grouser effectiveness (first-order model)")
spec("mobility", ["drive_actuator_"], COMPONENT="Wheel drive actuator (×6)", FUNCTION="Drive wheel; hold vehicle with power-off brake",
     TECH="Frameless BLDC motor + strain-wave gear (~100:1) + power-off brake + absolute encoder, in-hub",
     MAT="Ti-6Al-4V housing; 15-5PH/maraging flexspline, 440C circular spline; hybrid Si3N4 bearings; MoS2 + Braycote 601EF",
     WHY_T="LRV used 80:1 harmonic drive per wheel (S027); compact, backlash-free, high ratio",
     WHY_M="Ti housing CTE close to steel gear/bearing set (preload stability); dry + PFPE lubrication for cold start",
     ALT="planetary gearbox; direct-drive torque motor; hydraulic", REJ="planetary: backlash/mass; direct drive: mass ×3 for the torque; hydraulics: vacuum/cold incompatibility",
     DIM="≈ Ø0.22 × 0.18 m", TEMP="operate −55 °C to +70 °C (warm start from −120 °C via winding self-heating)",
     LOADS="rated torque = soil-limited max (20° climb, heaviest wheel, i = 0.6) × 1.25", RAD="encoder/driver electronics in WEB; motor passive",
     DUST="labyrinth + PTFE bellows at output; no exposed dynamic elastomers", LIFE="10 yr, > 2×10^7 output revolutions at derated torque",
     RED="6 units; free-wheel clutch on brake failure", FAIL="gear wear, brake stuck, encoder fault (F-01)", MAINT="ORU with wheel at hub",
     TRL="5", HER="LRV traction drives, MSL/M2020 wheel actuators", ASM="act_torque_density 25 N·m/kg (ESTIMATE)", UNC="torque density 15–40 N·m/kg → ±40 % mass")
spec("mobility", ["steer_actuator_"], COMPONENT="Steering actuator (×6)", FUNCTION="Steer each wheel ±90° (crab, point turn, Ackermann)",
     TECH="BLDC + strain-wave gear + brake; spring-centring to 0°", MAT="Ti-6Al-4V/Al housing, steel gears, MoS2",
     WHY_T="all-wheel explicit steering avoids skid-steer scrubbing torque in loose regolith", WHY_M="as drive actuator",
     ALT="skid steering; 4-wheel steering only", REJ="skid steering: high scrub energy and dust generation; 4-wheel: larger turning radius on a 3.6 m vehicle",
     DIM="≈ Ø0.14 × 0.14 m", TEMP="as drive actuator", LOADS="scrub torque μN·√(l²+b²)/3 × 1.5 × MF 2", RAD="as drive", DUST="as drive",
     LIFE="10 yr", RED="5 of 6 sufficient; skid fallback", FAIL="stuck at angle (F-02)", MAINT="ORU at bogie", TRL="5", HER="MSL/M2020 steering actuators",
     ASM="scrub-torque model ESTIMATE", UNC="steering torque in compacted ruts ±100 %")
spec("mobility", ["suspension_rocker_bogie", "differential_lock", "body_lowering_actuator_"], COMPONENT="Rocker-bogie suspension with body lowering and differential lock",
     FUNCTION="Equalise wheel loads on rough terrain; lower chassis onto belly skid; lock body attitude for manipulation",
     TECH="Passive 6-wheel rocker-bogie (differential bar), two lead-screw actuators at rocker pivots lowering the body 0.35 m, differential brake",
     MAT="Al 7075-T7351 links, Ti-6Al-4V pivots, BMG lead-screw nuts",
     WHY_T=f"TS-01: slope capability within {_MOB['M3']['max_slope_nom_deg'] - _MOB['M2']['max_slope_nom_deg']:.1f}° of active designs (traction-limited, {_MOB['M2']['max_slope_nom_deg']:.1f}°) at {min(_ACT):.0f}–{max(_ACT):.0f} kg less delivered mass; lowering enables wheel-drive ORU swap and lower CoM",
     WHY_M="stiff, light, machinable Al links; Ti pivots for bearing CTE compatibility",
     ALT="passive rocker-bogie; fully active 6-leg; 4-wheel active", REJ="passive: no wheel unloading for self-repair; active: +80–100 kg, +3–6 actuators, no slope gain",
     DIM="wheelbase 2.6 m, track 2.0 m, clearance 0.45 m (0.10 m lowered)", TEMP="structure: any; actuators as drive actuator",
     LOADS="half vehicle weight per lowering actuator × 1.5 dynamic × MF 2", RAD="n/a", DUST="sealed pivots; actuators booted",
     LIFE="10 yr", RED="lowering actuator fails safe at drive height", FAIL="pivot seizure (F-03), lowering actuator stuck (F-04)", MAINT="links not ORUs; actuators ORU",
     TRL="6 (rocker-bogie TRL 9 on Mars; lowering feature TRL 5)", HER="MER, MSL, M2020", ASM="suspension 4.5 % of operational mass (ESTIMATE)", UNC="link mass ±30 %")
spec("dust", ["fender_"], COMPONENT="Fenders with skirts (×6)", FUNCTION="Contain wheel ejecta (rooster tail) away from radiator, optics and mechanisms",
     TECH="CFRP fender with replaceable PTFE-coated glass-fabric skirt", MAT="CFRP, PTFE-coated glass fabric",
     WHY_T="Apollo 16/17 fender loss caused dust deposition and LRV battery overheating (S022)", WHY_M="light, stiff, low thermal mass; skirt sacrificial",
     ALT="no fenders; EDS-only protection", REJ="ejecta flux onto radiators/optics would dominate dust deposition (A-30)",
     DIM="arc over upper 120° of wheel, 0.45 m wide", TEMP="−230/+120 °C", LOADS="aerodynamic none; rock strikes", RAD="n/a", DUST="primary dust control element",
     LIFE="10 yr (skirts 2–3 yr)", RED="—", FAIL="detachment (Apollo lesson)", MAINT="skirt replaceable by arm", TRL="7", HER="Apollo LRV fenders",
     ASM="A-30", UNC="ejecta trajectories in lunar vacuum at 0.5 m/s")
# ------------------------------------------------------------------------------------------- structure
spec("structure", ["chassis_torque_box", "secondary_structure", "belly_skid_plate"], COMPONENT="Chassis torque box, secondary structure and belly skid",
     FUNCTION="Primary load path for launch, mobility, manipulation and recovery loads; houses the WEB; deck for equipment",
     TECH="Closed honeycomb-sandwich box 2.6 × 1.5 × 0.45 m with machined Ti hard points; cleated belly skid",
     MAT="Al 7075-T7351 faces 0.5 mm (each) on Al 5056 core 25 mm; Ti-6Al-4V fittings; Al skid with Ti cleats",
     WHY_T="Box section gives high bending/torsional stiffness at minimum gauge (f₁ ≥ 35 Hz on 4 launch locks)",
     WHY_M="TS-10: minimum-gauge driven; Al avoids CFRP thermal-cycling microcracking for −15 kg penalty, spreads WEB heat",
     ALT="Al tube space-frame (LRV-like), CFRP sandwich, Ti panels", REJ="space-frame needs separate WEB enclosure; CFRP marginal mass gain; Ti +21 kg",
     DIM="2.6 × 1.5 × 0.45 m box; deck 3.9 m²", TEMP="−150 to +110 °C structure (WEB interior −20/+40 °C)",
     LOADS="launch 6 g axial + 3 g lateral (A-05); hard points: winch 4 kN × 1.4, crane/arm reactions, anchor straps", RAD="n/a; 0.5 mm faces + WEB walls add shielding",
     DUST="closed box; deck components shed dust", LIFE="10 yr; ~3650 thermal cycles", RED="none (accepted SPF, F-26)",
     FAIL="insert pull-out, face/core disbond, fitting crack", MAINT="not replaceable; inspect via cameras", TRL="7", HER="spacecraft honeycomb buses; MSL WEB",
     ASM="A-05, A-22, f1_req (A-05b)", UNC="launch loads (no lander data: S075); thermal-cycling life of bonded joints")
spec("structure", ["sensor_mast"], COMPONENT="Sensor mast", FUNCTION="Elevate NavCams, IR imager, LEDs, relay antenna to 2.2 m",
     TECH="Single deployable CFRP tube with Ti hinge; pan-tilt head", MAT="CFRP, Ti-6Al-4V", WHY_T="height increases hazard look-ahead and illumination geometry in long shadows",
     WHY_M="low CTE for pointing stability", ALT="body-mounted cameras only; telescoping mast", REJ="low viewpoint loses 10 cm @ 15 m detection; telescoping = dust-sensitive sliding seals",
     DIM="1.2 m tube Ø60 mm; head at 2.15–2.2 m", TEMP="as structure", LOADS="launch latched; deploy once", RAD="n/a", DUST="hinge sealed",
     LIFE="10 yr", RED="arm cameras fallback", FAIL="deploy failure (F-27)", MAINT="mast head ORU", TRL="6", HER="VIPER, MSL masts", ASM="—", UNC="—")
# ------------------------------------------------------------------------------------------- manipulation
spec("manipulation", ["dexterous_arm", "dexterous_arm_2"], COMPONENT="Dexterous service arm (×2, identical)",
     FUNCTION="ORU ≤ 20 kg swaps, connector/fastener work, probing, cleaning, tow rigging, anchor installation, guiding crane loads; bimanual tasks",
     TECH="7-DOF serial arm (3 pitch joints + 4 roll/yaw), 1.6 m reach, wrist 6-axis F/T sensor, tool changer, macro camera",
     MAT="Ti-6Al-4V link tubes and joint housings; strain-wave gears; BMG gears in wrist joints; MoS2",
     WHY_T=f"TS-03: two identical dexterous arms + crane give {_MAN['A7']['weighted_coverage']:.2f} weighted task coverage at {_MAN['A7']['mass_kg']:.0f} kg vs {_MAN['A3']['mass_kg']:.0f} kg for heavy+dex; second arm removes the arm SPF (λ {R.v('lambda_dexterous_arm'):.2f}/yr)",
     WHY_M="arm mass actuator-dominated; Ti tougher for contact work and avoids bonded CFRP joints over 40–390 K",
     ALT="one general 100 kg arm; heavy+dexterous asymmetric pair; single dex arm + crane", REJ="general arm 102 kg with 0.83 coverage; asymmetric pair +113 kg for +4 % coverage; single arm leaves SPF",
     DIM="links 0.75/0.70/0.15 m; shoulder Ø≈0.12 m", TEMP="operate −55/+70 °C (BMG wrist to −173 °C, S040)", LOADS="20 kg rated payload at full reach (lunar g), tip deflection ≤ 3 mm; ≤ 150 N contact force",
     RAD="joint electronics in WEB except encoders (rad-tolerant)", DUST="joint bellows boots + labyrinths; EDS on camera window",
     LIFE="10 yr; λ 0.08/yr per arm (ESTIMATE)", RED="two arms", FAIL="joint/brake/encoder failure (F-05)", MAINT="arm-level ORU at base (II-03); joint ORUs",
     TRL="5 (space arms TRL 9 in µg/Mars; lunar dust + cold joints TRL 4–5)", HER="M2020 arm, Dextre, xLink, COLDArm",
     ASM="motorisation factor 2 (L024), torque density 25 N·m/kg", UNC="actuator mass ±40 %; contact-task success rates (servicing.py)")
spec("manipulation", ["crane_boom"], COMPONENT="Crane boom (cable-stayed luffing, slewing)", FUNCTION="Lift/place ORUs and modules ≤ 150 kg, support damaged equipment, lift target vehicle corners, route lines",
     TECH="2.6 m CFRP boom + A-frame, luff and hoist winches, 360° slew turntable; cooperative placement with dex arm",
     MAT="CFRP tubes, Ti end fittings, Vectran lines", WHY_T=f"TS-03/M-4: {_B['crane']['mass']:.0f} kg CBE vs ≈ {_MAN['A3']['mass_kg'] - _MAN['A2']['mass_kg'] / 2:.0f} kg for an equivalent heavy serial arm (LSMS principle S015)",
     WHY_M="buckling-driven member → specific stiffness; low CTE", ALT="heavy 6-DOF arm; no heavy lift", REJ="mass; coverage loss of T02/T03/T10/T11",
     DIM="boom 2.6 m Ø≥50 mm; reach 2.56 m at 10° luff", TEMP="as actuators", LOADS="150 kg hook (243 N) + boom; side load 10 %; luff tension ≈ 0.8 kN",
     RAD="n/a", DUST="sheave guards; line wiper", LIFE="10 yr", RED="none (DM-4)", FAIL="F-06", MAINT="winch/slew ORUs; spare line in MOD-REC", TRL="4",
     HER="LSMS ground prototypes", ASM="—", UNC="load swing control in lunar g (pendulum period ~5 s at 1 m)")
spec("manipulation", ["ft_sensor_and_tool_changer"], COMPONENT="End effector: F/T sensor + tool changer + gripper interface",
     FUNCTION="6-axis force/torque sensing for compliant contact; automatic tool exchange with power/data pass-through",
     TECH="strain-gauge F/T sensor (±500 N/±50 N·m), ISO 9409-1 tool changer with 120/28 V and data pins", MAT="Ti-6Al-4V, PEEK, Au contacts",
     WHY_T="contact tasks need local force loops (latency, TS-09)", WHY_M="stiffness, CTE match", ALT="joint-torque sensing only", REJ="insufficient resolution for connector mating",
     DIM="Ø0.10 × 0.12 m", TEMP="−40/+60 °C (heated)", LOADS="tool reaction ≤ 50 N·m (fastener torque reacted through tool clamp)", RAD="rad-tolerant ADC in arm electronics",
     DUST="covered interface face when no tool", LIFE="> 5000 tool changes", RED="per arm", FAIL="pin contamination", MAINT="part of arm ORU", TRL="5", HER="ISS OTCM, RRM tools",
     ASM="—", UNC="—")
# ------------------------------------------------------------------------------------------- service spine & modules
spec("service_spine", ["service_spine"], COMPONENT="Modular service spine", FUNCTION="Carry, power and exchange ORUs, spares and service modules; standard interface shared with assets and host vehicles",
     TECH="Rail with 6 androgynous latch slots (HOTDOCK-class), 120 VDC/1 kW and Ethernet per slot", MAT="Al 7075 rail, Ti latches",
     WHY_T=f"TS-07: −{_TR['service_modules']['mass_saving_per_sortie_kg']:.0f} kg average carried mass per sortie vs integrated; deployable modules (MOD-KA) inherently modular; portability to other hosts (CDR-01)",
     WHY_M="light rail; Ti latches for wear", ALT="integrated fixed mounts", REJ="carries all kits always; no reuse on other vehicles",
     DIM="2 × 3 grid of 0.45 m slots, 0.90 × 1.35 m on the mid-deck (design.layout, CDR-21); ≤ 40 kg and ≤ 0.45 × 0.45 × 0.6 m (high) per occupied slot (double-slot modules such as MOD-KA ≤ 80 kg over two adjacent latches); total ≤ 150 kg", TEMP="−150/+110 °C (modules self-heated)",
     LOADS="150 kg × launch 6 g (modules launch-locked separately)", RAD="n/a", DUST="latch covers", LIFE="10 yr, 2000 latch cycles",
     RED="6 slots", FAIL="latch jam (F-23)", MAINT="latches ORU", TRL="5", HER="HOTDOCK (S048), FLEX payload interfaces (S037)", ASM="—", UNC="—")
# ------------------------------------------------------------------------------------------- recovery
spec("recovery", ["recovery_winch", "recovery_line"], COMPONENT="Recovery winch and line", FUNCTION="Pull immobilised vehicles/elements while TSR-1 is anchored",
     TECH="4 kN electric winch, drum Ø0.12 m, level-wind, load cell, auto tension limiting; 50 m Vectran line; low fairlead (0.25 m)",
     MAT="Ti drum, steel gear, Vectran with aramid/PTFE jacket", WHY_T=f"TS-05: anchored winching raises recoverable fraction from {_PENV['R0 direct towing (drive)']['mid']:.2f} (direct tow) to {_PENV['R4 winch + 2 spades + 2 helical anchors']['mid']:.2f}",
     WHY_M="line mass 0.03 kg/m vs 0.15 kg/m steel rope; low creep", ALT="direct towing only; steel rope", REJ=f"traction-limited ({next(t for t in J('mobility.json')['tow_capacity'] if t['slope_deg'] == 15)['nominal_N']:.0f} N drawbar pull on 15°); 5× line mass",
     DIM="≈ 0.45 × 0.3 × 0.3 m", TEMP="operate −55/+70 °C", LOADS="4 kN line pull × FoS 1.4 at hard point; snap-back keep-out",
     RAD="n/a", DUST="fairlead wiper; drum cover", LIFE="10 yr; 500 pulls", RED="none (DM-5)", FAIL="F-07, F-08", MAINT="ORU; spare line in MOD-REC",
     TRL="5 (terrestrial winches TRL 9; lunar vacuum/dust TRL 4–5)", HER="terrestrial recovery vehicles", ASM="winch_eff 0.65", UNC="line abrasion life on regolith")
spec("recovery", ["spade_", "helical_anchor_", "tow_hardpoints_front_rear"], COMPONENT="Ground-reaction system: rear spades, helical anchors, hard points",
     FUNCTION="Resist line pull and overturning moment during winching",
     TECH="2 rear spades 0.6 × 0.3 m (pressed by body lowering, self-embedding under pull); 2 Ø0.15 m helical anchors at 0.6 m depth installed by dex arm; front hold-down straps",
     MAT="Ti-6Al-4V with TiN edges", WHY_T=f"M-5: 4 kN pull is {4000 / _WEIGHT:.1f}× TSR lunar weight ({_WEIGHT:.0f} N); spades+anchors give the restraint and tipping factor ≥ 1.5 (stability case C7a/b)",
     WHY_M="strength/mass, non-magnetic", ALT="outriggers; braked wheels only; 4 anchors", REJ="outriggers do not resist sliding; braked wheels ≈1.6 kN only; 4 anchors +0.02 p_env",
     DIM="spade plate 0.6 × 0.3 × 0.006 m; anchor shaft 0.7 m Ø25 mm", TEMP="any", LOADS="spade 1.3 kN each (P50 soil); anchor 0.92 kN axial; install torque 28 N·m",
     RAD="n/a", DUST="n/a (ground-engaging)", LIFE="10 yr; anchors reusable", RED="spare anchors in MOD-REC", FAIL="F-09, F-10", MAINT="spades ORU",
     TRL="3–4 (no lunar regolith anchor data: literature gap)", HER="terrestrial helical anchors (Hoyt & Clemence L026), recovery-vehicle spades",
     ASM="A-26, helix_Nq, spade_shape_factor ESTIMATES", UNC="capacity ±50 % (weak soil p_env 0.83); refusal on clasts")
# ------------------------------------------------------------------------------------------- power
spec("power", ["battery_pack"], COMPONENT="Battery", FUNCTION="Energy storage for sorties, emergency power and survival",
     TECH="Li-ion 18650 PPR pack, 4 modules, 28s strings (≈101 V nominal), BMS with module isolation", MAT="NCA/NMC cells, Al 6061 interstitial heat sinks, mica sleeves",
     WHY_T=f"TS-06: DRM-2 at 10 km ({_EN['drms'][1]['energy_kwh']:.1f} kWh) + 50 h reserve ({_EN['reserve_kwh']:.1f} kWh) needs {_EN['drms'][1]['energy_kwh'] + _EN['reserve_kwh']:.1f} kWh usable EOL (CDR-06)", WHY_M="passive propagation resistance (S070)",
     ALT="RFC; RPS (MMRTG); larger PV", REJ="RFC TRL 4 and hazards; RPS availability/approval; PV insufficient alone in shadow",
     DIM="≈ 0.8 × 0.5 × 0.18 m in WEB", TEMP="charge 0/+30 °C, discharge −20/+40 °C (S071)", LOADS="launch 6 g/3 g; mounted to WEB baseplate",
     RAD="cells insensitive at ~0.1 krad; BMS rad-tolerant", DUST="inside WEB", LIFE="10 yr, 20 % fade at EOL (A-16)", RED="4 modules (3/4 usable)",
     FAIL="cell thermal runaway (F-11)", MAINT="module ORU through WEB service door", TRL="6", HER="NASA PPR 18650 batteries; VIPER/rovers Li-ion",
     ASM="A-15 160 Wh/kg, A-16", UNC="specific energy 130–200 Wh/kg → ±20 % mass")
spec("power", ["pcdu_bus_regulator"], COMPONENT="PCDU / 120 VDC bus regulator", FUNCTION="Regulate 120 VDC primary bus (ISPSIS), derive 28 VDC, protect loads (SSPCs)",
     TECH="3-phase interleaved bidirectional buck-boost (4 kW), SiC switches; isolated 28 V converters", MAT="Al housing, SiC",
     WHY_T="bus regulation independent of battery state of charge keeps ISPSIS power quality", WHY_M="thermal conduction", ALT="unregulated battery bus", REJ="102–139 V swing violates ISPSIS 120 V interoperability intent",
     DIM="≈ 0.35 × 0.25 × 0.12 m", TEMP="−20/+50 °C (WEB)", LOADS="launch", RAD="SEE-hardened SiC gate drivers, SEL protection", DUST="inside WEB", LIFE="10 yr",
     RED="2-of-3 phases", FAIL="F-12", MAINT="ORU", TRL="5", HER="ISS 120 VDC systems; ISPSIS", ASM="conv_eff 0.95, 300 W/kg", UNC="converter specific power 150–500 W/kg")
spec("power", ["power_transfer_module", "power_tether_and_reel", "dust_tolerant_connector_head"], COMPONENT="Power-transfer module, tether and connector (emergency power / charging)",
     FUNCTION="Bidirectional isolated 120 VDC power exchange with grid nodes, assets and peers",
     TECH="Isolated bidirectional DC-DC (3 kW, 4.5 kW/60 s) directly on battery string; 25 m tether 2 × 6.9 mm² Cu; dust-tolerant connector with clamshell cover, carried by dex arm",
     MAT="Al housing, SiC, planar transformer; Cu/PTFE/aramid tether; Ti/PEEK/Au connector", WHY_T="ISPSIS 120 VDC exchange < 100 m (S011, S012); single stage keeps WEB heat 350 W at 3 kW (THERMAL-1)",
     WHY_M="as per materials matrix", ALT="proprietary voltage; inductive (wireless) coupling; no PTM", REJ="interoperability; inductive TRL 4 and alignment; no emergency power",
     DIM="PTM ≈ 0.3 × 0.25 × 0.12 m; reel Ø0.35 m", TEMP="PTM in WEB; tether −150/+100 °C flexible", LOADS="tether pull ≤ 200 N",
     RAD="SEE-protected", DUST="DTC with self-closing cover; pre-mate brush", LIFE="10 yr; > 500 mate cycles (S042 class)", RED="MOD-KA independent connector",
     FAIL="F-13, F-14", MAINT="PTM ORU; connector head on arm tool changer", TRL="4 (DTC TRL 4–6; PTM 5)", HER="ISS power interfaces, Honeybee DTC",
     ASM="p_keepalive 300 W", UNC="ISPSIS surface power-quality limits not retrieved")
spec("power", ["solar_arrays_vertical", "solar_array_regulator"], COMPONENT="Vertical solar arrays and MPPT", FUNCTION="Contingency charging and indefinite survival in sunlight",
     TECH="two fixed vertical side panels 0.75 m² each, triple-junction cells; MPPT 600 W", MAT="IMM/TJ GaAs on CFRP", WHY_T=f"sun ≤ 1.54° elevation at the pole → vertical panels; ≈ {_EN['solar_avg_W']:.0f} W average > {_EN['survival_power_W']:.0f} W survival (ENERGY-3)",
     WHY_M="heritage cells", ALT="no PV; deployable tracking mast (MOD-SOL)", REJ="stranded TSR would die in 7.7 days; mast only for no-grid scenario",
     DIM="2 × (1.5 × 0.5 m)", TEMP="−150/+110 °C", LOADS="launch", RAD="cell degradation small", DUST="vertical orientation low deposition; brushable", LIFE="10 yr (EOL factor 0.85)",
     RED="two panels", FAIL="string open", MAINT="panel ORU", TRL="7", HER="spacecraft arrays, VIPER side arrays", ASM="sortie_sunlit_frac 0.5", UNC="shadowing by own mast/crane")
# ------------------------------------------------------------------------------------------- thermal
spec("thermal", ["mli_blankets", "radiator_panel_eds", "loop_heat_pipe_switch", "heaters_thermostats"], COMPONENT="Thermal control system",
     FUNCTION="Hold WEB/battery in limits; reject peak dissipation; survive darkness and PSR excursions",
     TECH="MLI-insulated WEB (2.86 m²) inside chassis; zenith radiator with OSR + EDS film coupled by LHP with thermal switch; redundant heaters",
     MAT="Kapton/Mylar/Beta MLI; Al 6063 heat-pipe panel, Ag-FEP/OSR, ITO EDS film; SS/Al LHP (ammonia)",
     WHY_T=f"variable conductance needed: 380 W hot case vs ≈ {_EN['thermal']['leak_cold_w']:.0f} W leak in PSR cold case", WHY_M="materials matrix",
     ALT="louvers; phase-change storage; RHUs", REJ="louvers dust-sensitive; PCM mass for multi-hour peaks (WEB capacity suffices, THERMAL-1b); RHUs need Pu-238",
     DIM="radiator ≈ 1.6 m²", TEMP="WEB −20/+40 °C", LOADS="launch", RAD="FEP minor darkening", DUST="EDS restores α (S019); zenith orientation; fenders",
     LIFE="10 yr", RED="dual heater circuits, two heat-pipe paths", FAIL="F-21, F-22", MAINT="heater controllers ORU", TRL="5 (EDS 6 after lunar demo)",
     HER="MSL/M2020 WEB + LHPs; Blue Ghost EDS", ASM="ε* 0.03, G_leak 0.25 W/K", UNC="dust-degraded α factor 1.4–2.6 (S062)")
# ------------------------------------------------------------------------------------------- avionics
spec("avionics", ["autonomy_computer_hpsc"], COMPONENT="Autonomy computer", FUNCTION="Mission/task planning, perception, motion planning, ML inference (advisory)",
     TECH="HPSC-class rad-hard RISC-V multicore SoC + FPGA co-processor, 64 GB EDAC memory", MAT="Al chassis",
     WHY_T="perception/planning load beyond RAD750/GR740 class; HPSC ~100× (S039)", WHY_M="conduction cooling", ALT="COTS GPU (Snapdragon-class)", REJ="SEL/SEFI risk over 10 yr without shielding/upsets management",
     DIM="≈ 0.25 × 0.2 × 0.1 m", TEMP="−20/+50 °C", LOADS="launch", RAD="100 krad TID part vs 10 krad design (RDM 10); SEL immune", DUST="in WEB",
     LIFE="10 yr", RED="functions degrade to safety lanes (DM-7)", FAIL="F-15", MAINT="ORU", TRL="6 (qualification completing 2026)", HER="HPSC program", ASM="A-18", UNC="availability/cost")
spec("avionics", ["safety_rt_computer_A", "safety_rt_computer_B"], COMPONENT="Safety / real-time computers (dual lane)",
     FUNCTION="Deterministic control loops (1 kHz), safety guards (force, speed, tip factor, tension, keep-out), FDIR, safe hold",
     TECH="dual rad-hard processors (LEON4/RISC-V class) + FPGA, cross-strapped, independent power", MAT="Al chassis",
     WHY_T="separation of safety-critical determinism from AI/autonomy (directive §20)", WHY_M="—", ALT="single computer", REJ="no fault tolerance; no independence from ML",
     DIM="2 × 0.2 × 0.15 × 0.08 m", TEMP="−30/+60 °C", LOADS="launch", RAD="TMR FPGA, EDAC, watchdog", DUST="in WEB", LIFE="10 yr", RED="dual lane",
     FAIL="F-16", MAINT="ORU", TRL="7", HER="GR740/RTG4-class flight computers", ASM="—", UNC="—")
spec("avionics", ["motor_control_units", "mass_memory_and_timing"], COMPONENT="Motor control units, mass memory and timing",
     FUNCTION="Drive 28 actuators; store data for DTN; time synchronisation", TECH="distributed MCUs in WEB (SiC drivers), 1 TB rad-tolerant flash, chip-scale atomic clock + LunaNet time",
     MAT="Al", WHY_T="actuator count; DTN store-and-forward", WHY_M="—", ALT="joint-local electronics", REJ="cold/radiation exposure of electronics in joints",
     DIM="—", TEMP="−20/+50 °C", LOADS="launch", RAD="rad-tolerant", DUST="in WEB", LIFE="10 yr", RED="spare channels", FAIL="driver failure → joint loss",
     MAINT="ORU", TRL="6", HER="MSL motor control assemblies", ASM="0.4 kg per actuator channel (ESTIMATE)", UNC="harness length to joints")
# ------------------------------------------------------------------------------------------- sensors
spec("sensors", ["navcam_stereo_pair", "mast_pan_tilt", "led_illuminators", "hazcams_x6"], COMPONENT="Navigation & hazard camera suite with illumination",
     FUNCTION="Terrain perception in long shadows, visual odometry, stand-off inspection", TECH="mast stereo pair 70° FOV on pan-tilt (400°/75°), 6 HazCams, blue LED headlights",
     MAT="Ti housings, sapphire windows with EDS film", WHY_T="VIPER heritage: 10 cm rock at 15 m (S064) sets v_nom 0.5 m/s", WHY_M="window abrasion/EDS",
     ALT="LiDAR only", REJ="no texture/colour for inspection; LiDAR window dust", DIM="—", TEMP="−40/+60 °C heated", LOADS="launch", RAD="CMOS SEE tolerant", DUST="EDS windows, covers",
     LIFE="10 yr", RED="pairs + HazCams + arm macro camera", FAIL="F-17", MAINT="camera head ORU", TRL="7", HER="VIPER, MSL", ASM="—", UNC="performance at grazing sun")
spec("sensors", ["lidar_front", "lidar_rear"], COMPONENT="LiDAR (front, rear)", FUNCTION="3-D mapping for hazard detection, docking pose, inspection metrology",
     TECH="SPAD flash/scanning LiDAR, 50 m range, 0.1° resolution", MAT="Al/Ti housing, EDS window", WHY_T="illumination-independent ranging in PSRs and shadows",
     WHY_M="—", ALT="stereo only", REJ="fails in PSR darkness without lighting", DIM="≈ 0.15 m cube", TEMP="−30/+50 °C heated", LOADS="launch", RAD="tolerant", DUST="EDS window",
     LIFE="10 yr", RED="two units", FAIL="F-18", MAINT="ORU", TRL="5", HER="Jena-Optronik/Fraunhofer SPAD LiDAR developments", ASM="mass/power ESTIMATE", UNC="±50 %")
spec("sensors", ["thermal_ir_imager", "macro_inspection_camera", "contact_vibration_sensors", "electrical_diagnostic_unit"], COMPONENT="Inspection & diagnostic sensors",
     FUNCTION="Thermal anomaly detection, macro imaging of connectors/cracks, contact vibration of mechanisms, electrical diagnosis",
     TECH="uncooled microbolometer (NETD ≤ 50 mK), macro camera with ring light on arm, contact accelerometers on tool, V/I/insulation measurement",
     MAT="—", WHY_T="no acoustics in vacuum → contact vibration only (directive §14); IR detects dust/thermal faults (S062)", WHY_M="—",
     ALT="airborne microphones", REJ="no sound propagation in vacuum", DIM="—", TEMP="−30/+50 °C", LOADS="—", RAD="tolerant", DUST="covers", LIFE="10 yr",
     RED="arm-mounted duplicates", FAIL="—", MAINT="ORU", TRL="6", HER="planetary instruments", ASM="—", UNC="—")
spec("sensors", ["imu_ln200s", "sun_sensor_star_tracker"], COMPONENT="Inertial and celestial navigation sensors", FUNCTION="Attitude, heading, dead reckoning",
     TECH="LN-200S-class FOG IMU; sun sensor + star tracker", MAT="—", WHY_T="Mars rover heritage (S065)", WHY_M="—", ALT="MEMS IMU", REJ="drift for long traverses",
     DIM="—", TEMP="−20/+50 °C", LOADS="—", RAD="space-qualified", DUST="star tracker baffle cover", LIFE="10 yr", RED="VO fallback", FAIL="F-19", MAINT="ORU", TRL="9",
     HER="Spirit, Opportunity, Curiosity, Perseverance", ASM="—", UNC="—")
# ------------------------------------------------------------------------------------------- comms
spec("communications", ["surface_network_radio", "lunanet_relay_transceiver", "relay_antenna_gimballed", "mesh_uhf_radio"], COMPONENT="Communication system",
     FUNCTION="Base surface network, LunaNet relay, peer mesh; DTN store-and-forward", TECH="LTE-class surface radio; S-band relay transceiver 5 W RF + 10 dBi gimballed antenna; UHF mesh",
     MAT="—", WHY_T="TS-08: availability 0.98 with surface + relay vs 0.51 DTE only (S073)", WHY_M="—", ALT="DTE only; relay only", REJ="availability",
     DIM="—", TEMP="−20/+50 °C", LOADS="—", RAD="tolerant", DUST="antenna radome", LIFE="10 yr", RED="three links", FAIL="F-20", MAINT="ORU", TRL="6",
     HER="Nokia LSCS (S068), CADRE mesh (S069), LunaNet (S017)", ASM="relay range 10 000 km, G/T 0 dB/K", UNC="relay constellation geometry not retrieved")
# ------------------------------------------------------------------------------------------- dust self-protection
spec("dust", ["optics_eds_and_covers", "joint_boots_seals"], COMPONENT="Dust self-protection (EDS on optics, joint boots/seals)",
     FUNCTION="Keep optical windows clear; exclude regolith from mechanisms", TECH="EDS transparent electrodes on windows (1–4 kV, 10–500 Hz), labyrinth + PTFE bellows on all external joints",
     MAT="ITO/PI films, PTFE-coated fabric, Ti", WHY_T="EDS lunar demo 2025 (S019), 3.3 mWh/m²/cycle (S063); Apollo seal/clogging lessons (S022)",
     WHY_M="no elastomers below Tg", ALT="covers only; wipers", REJ="wipers abrade optics; covers alone insufficient during operation",
     DIM="—", TEMP="—", LOADS="—", RAD="—", DUST="primary function", LIFE="10 yr", RED="covers as backup", FAIL="F-25", MAINT="boots ORU", TRL="6 (EDS) / 5 (boots in lunar dust)",
     HER="Blue Ghost EDS, MSL boots", ASM="—", UNC="long-term EDS efficiency on rover optics")
spec("harness", ["harness"], COMPONENT="Harness", FUNCTION="Power and data distribution", TECH="PTFE/polyimide-insulated Cu, shielded twisted pairs, Ethernet",
     MAT="Cu, PTFE, polyimide", WHY_T="—", WHY_M="cold flexibility", ALT="—", REJ="—", DIM="—", TEMP="−150/+110 °C", LOADS="flex cycles at joints", RAD="negligible dose",
     DUST="routed inside booted joints", LIFE="10 yr", RED="dual power feeds to critical loads", FAIL="chafing at joints", MAINT="joint harness segments part of ORUs",
     TRL="8", HER="all rovers", ASM="6 % of other CBE + 60 % MGA", UNC="harness is the largest MGA item")
# tools sheet handled as a table below

TOOL_TABLE = [
    ("tool_parallel_gripper", "Grasp handles, cables, small ORUs ≤ 20 kg", "Ti body, PEEK/Vespel fingers", "ISO 9409-1 tool changer", "≤ 150 N grip; −55/+70 °C", "generic handles, cables", "tool rack holster"),
    ("tool_socket_driver", "Drive captive fasteners ≤ 50 N·m, torque-reacted through clamp", "Ti body, DLC tool-steel sockets", "tool changer", "≤ 50 N·m, ±5 % torque", "captive bolts (OTCM-type)", "rack"),
    ("tool_electrical_probe", "Measure V, I, insulation resistance at test points", "PEEK/Ti, Au probes", "tool changer + data", "≤ 150 V", "L1+ test ports", "rack"),
    ("tool_connector_mate", "Mate/demate circular and blind-mate connectors", "Ti/PEEK", "tool changer", "≤ 150 N axial", "MIL-38999-class, DTC", "rack"),
    ("tool_dust_brush", "Mechanical removal of regolith from arrays/radiators/optics", "Ti frame, PTFE-coated aramid bristles", "tool changer", "contact pressure ≤ 1 kPa to protect coatings", "all surfaces", "rack"),
    ("tool_eds_wand", "Electrodynamic dust removal from sensitive surfaces (non-contact)", "CFRP frame, ITO/PI electrode film, HV supply", "tool changer + 28 V", "1–4 kV, 10–500 Hz", "arrays, optics, radiators", "rack"),
    ("tool_anchor_driver", "Install/remove helical anchors", "Ti body, steel bit", "tool changer + 120 V", "≤ 60 N·m, ≤ 200 N crowd", "TSR anchors", "rack"),
    ("tool_oru_adapter_otcm", "Grapple OTCM-type ORU interfaces", "Ti-6Al-4V", "tool changer", "≤ 20 kg (arm) / ≤ 150 kg with crane", "ISS-heritage ORUs", "rack"),
    ("tool_oru_adapter_androgynous", "Couple HOTDOCK-class androgynous interfaces", "Ti-6Al-4V/Al 7075", "tool changer + power/data", "as above", "HOTDOCK-class ORUs/modules", "rack"),
    ("tool_lifting_fixture_slings", "Rig loads for crane", "Vectran slings, Ti hooks", "crane hook", "≤ 150 kg", "any lift point", "MOD-REC"),
    ("tool_recovery_shackle_hitch", "Attach line to tow points", "Ti-6Al-4V", "manipulated by arm", "≤ 4 kN", "tow eyes, structural members", "MOD-REC"),
    ("tool_regolith_scoop", "Excavate ramps in front of embedded wheels; pre-dig anchor holes", "Ti-6Al-4V blade, PTFE-coated", "tool changer", "≤ 100 N digging force", "regolith", "rack"),
]


def comp_values(cfg, comps):
    sel = [c for c in cfg.comps if any(c.name == n or (n.endswith("_") and c.name.startswith(n)) for n in comps)]
    cbe = sum(c.cbe for c in sel)
    pred = sum(c.predicted for c in sel)
    pw = {m: sum(c.power.get(m, 0.0) for c in sel) for m in MODES}
    peak = sum(c.peak for c in sel)
    basis = sorted({c.basis for c in sel})
    trl = min([c.trl for c in sel if c.trl] or [0])
    return len(sel), cbe, pred, pw, peak, basis


def main():
    cfgfile = json.loads((ROOT / "simulations" / "configs" / "run_config.json").read_text())
    o = cfgfile["baseline_options"]
    o["dex_links"] = tuple(o["dex_links"])
    cfg = build(Options(**o))
    OUT.mkdir(parents=True, exist_ok=True)
    files = {}
    for name, (f, comps, k) in SPECS.items():
        n, cbe, pred, pw, peak, basis = comp_values(cfg, comps)
        ops = ", ".join(f"{m.split('_', 1)[1]} {v:.0f} W" for m, v in pw.items() if v > 0.05) or "none (passive)"
        txt = f"""### {name}
```
COMPONENT:            {name}
SUBSYSTEM:            {f}
FUNCTION:             {k['FUNCTION']}

SELECTED TECHNOLOGY:  {k['TECH']}
SELECTED MATERIAL(S): {k['MAT']}

WHY THIS TECHNOLOGY:  {k['WHY_T']}
WHY THIS MATERIAL:    {k['WHY_M']}

ALTERNATIVES CONSIDERED: {k['ALT']}
WHY REJECTED:         {k['REJ']}

DIMENSIONS:           {k['DIM']}
MASS:                 CBE {cbe:.1f} kg; predicted {pred:.1f} kg incl. MGA ({n} configuration item(s); engineering/mass_budget.csv)
OPERATING POWER:      {ops}
PEAK POWER:           {peak:.0f} W (sum of item peaks)

OPERATING TEMPERATURE: {k['TEMP']}
MECHANICAL LOADS:     {k['LOADS']}
RADIATION CONSIDERATIONS: {k['RAD']}
DUST CONSIDERATIONS:  {k['DUST']}

EXPECTED LIFE:        {k['LIFE']}
REDUNDANCY:           {k['RED']}
FAILURE MODES:        {k['FAIL']}
MAINTENANCE METHOD:   {k['MAINT']}

TRL:                  {k['TRL']}
HERITAGE:             {k['HER']}

SOURCE DATA:          see research/source_register.csv (IDs cited above)
CALCULATED VALUES:    {'; '.join(basis)}
ASSUMPTIONS:          {k['ASM']}
UNCERTAINTIES:        {k['UNC']}
```
"""
        files.setdefault(f, []).append(txt)
    # MOD-KA keep-alive module (base inventory item, not part of the TSR-1 mass budget) — values from TS-07b
    val = J("value_model.json")
    ka = val["keepalive_trade"]["selected_row"]
    files.setdefault("service_spine", []).append(f"""### MOD-KA keep-alive power module (base inventory ×{val['base_scenario']['keepalive_modules']})
```
COMPONENT:            MOD-KA keep-alive power module ({val['keepalive_trade']['selected']})
SUBSYSTEM:            service_spine (deployable module; base inventory, not in the TSR-1 mass budget)
FUNCTION:             Left connected to a disabled asset whose repair failed, supplying survival power until a spare is
                      fitted (robotically after the Earth spare arrives, or by crew for L0/L1 assets)

SELECTED TECHNOLOGY:  Li-ion PPR battery {ka['usable_kwh']:.0f} kWh usable at EOL (28s strings, 120 V ISPSIS output), two
                      back-to-back fold-out vertical PV panels {ka['face_m2']:.1f} m² each, MPPT + isolated output stage,
                      ISPSIS-compatible connector on 10 m cable, double-slot spine latch, crane lift point, fiducials
SELECTED MATERIAL(S): Al 7075 frame, CFRP panel substrates, MLI on battery enclosure, Ti latch/hinge fittings

WHY THIS TECHNOLOGY:  TS-07b: highest net Earth-mass benefit per handled module; KA-D (+50 % battery) gains less than the
                      Monte Carlo scatter at +27 kg per module and only one fits the spine
WHY THIS MATERIAL:    same family as TSR-1 structure and arrays (shared qualification)

ALTERNATIVES CONSIDERED: KA-A 0.75 m²/2 kWh, KA-B 1.0 m²/3 kWh, KA-D 1.5 m²/6 kWh; TSR-1 staying at the asset
WHY REJECTED:         KA-A/KA-B sustain too few assets (P = 0.40/0.57); staying ties up the only servicing vehicle

DIMENSIONS:           stowed 0.9 × 0.45 × 0.45 m (two slots); deployed panel height ≈ 1.6 m
MASS:                 CBE {ka['mass_cbe_kg']:.1f} kg; predicted {ka['mass_kg']:.1f} kg incl. 20 % MGA (battery {ka['battery_kg']:.1f} kg, PV {ka['pv_kg']:.1f} kg)
OPERATING POWER:      output to asset = asset survival power (A-33, 40–250 W); self-consumption {R.v('ka_self_w'):.0f} W
PEAK POWER:           {ka['p_sunlit_w']:.0f} W PV output with the lit face normal to the Sun

PERFORMANCE:          sustained {ka['p_sustained_nominal_w']:.0f} W at a 0.75-illuminated site; {ka['bridge_nominal_h']:.0f} h darkness bridging at
                      100 W; P(sustains a sampled asset) = {ka['p_sustain']:.2f} (asset power ×1.5: {ka['p_sustain_low']:.2f}; ×0.67: {ka['p_sustain_high']:.2f})
OPERATING TEMPERATURE: battery 0–40 °C (self-heated under MLI); panels −180/+120 °C
MECHANICAL LOADS:     launch 6 g on locks; crane lift 1.5 × weight
RADIATION CONSIDERATIONS: rad-tolerant MPPT/BMS electronics (TID ≥ 20 krad)
DUST CONSIDERATIONS:  vertical panels (low deposition); connector with self-closing cover; brushed at each TSR-1 visit

EXPECTED LIFE:        10 yr; ≥ 20 deployments
REDUNDANCY:           inventory of {val['base_scenario']['keepalive_modules']} (rule value_model.keepalive_inventory, CDR-19)
FAILURE MODES:        battery cell string failure (graceful), panel hinge jam, connector contamination
MAINTENANCE METHOD:   recovered by TSR-1 when the asset is repaired; battery/electronics swappable at the base depot

TRL:                  5 (space Li-ion, PV and MPPT TRL 9; robot-deployed lunar surface power module not flown)
HERITAGE:             small-lander power systems; ISPSIS interface concept (S011)

SOURCE DATA:          S011, S030, A-15, A-16
CALCULATED VALUES:    trades.other_trades.keepalive_module_sizing; value_model.json keepalive_trade
ASSUMPTIONS:          A-33 asset survival power, A-34 site illumination, A-35 dark period, pv_areal_density (ESTIMATE)
UNCERTAINTIES:        asset survival power (no data), dark-period statistics at actual asset sites
```
""")
    # tools table into tools file
    tool_lines = ["| Tool | Function | Material | Mass CBE [kg] | Power peak [W] | Attachment | Operating limits | Compatibility | Storage |",
                  "|---|---|---|---|---|---|---|---|---|"]
    for t in TOOL_TABLE:
        c = next(cc for cc in cfg.comps if cc.name == t[0])
        tool_lines.append(f"| {t[0].replace('tool_', '')} | {t[1]} | {t[2]} | {c.cbe:.1f} | {c.peak:.0f} | {t[3]} | {t[4]} | {t[5]} | {t[6]} |")
    files.setdefault("tools", []).insert(0, "\n".join(tool_lines) + "\n\nTool selection rule (directive §13): every tool maps to "
                                         "at least one DRM step (budgets/scenarios.py) or recovery scenario (C-dig → scoop). Rejected: cutting tools "
                                         "(no DRM need; debris/hazard), fluid-servicing tools (no fluid-serviceable asset identified, TS-07).\n")
    for f, parts in files.items():
        (OUT / f"{f}.md").write_text(f"# Component specifications — {f}\n\n> TSR-1 is an independent conceptual engineering study by "
                                     "Todaro Corp. References to NASA, ESA and other organizations are used solely as technical and "
                                     "architectural context.\n\nGenerated by `engineering/build_specs.py` from the baseline configuration.\n\n"
                                     + "\n".join(parts))
    print(len(SPECS) + 1, "spec sheets (incl. MOD-KA) in", len(files), "files")


if __name__ == "__main__":
    main()
