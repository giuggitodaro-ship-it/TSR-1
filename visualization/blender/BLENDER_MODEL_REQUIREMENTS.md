# TSR-1 Blender model requirements

Status: repository extraction complete before detailed modeling. Baseline: `claude/happy-feynman-043306`, frozen preliminary study 2026-10-03; PROJECT_STATE reports phase 7 complete. This document authorizes geometric reconstruction, not redesign or manufacturing certification. Units: metres; +X forward, +Y left, +Z up; ground origin below chassis centre. Blender 1 unit = 1 m.

Authority within Tier 1 is explicitly **DESIGN_FREEZE_V1.md > simulations/configs/run_config.json > src/tsr1/design/layout.py**. Tier 2: subsystem specifications, materials matrix, interfaces, final specifications in that order. Tier 3: VISUAL_RENDER_SPEC. Tier 4: figures, trades, architecture, ConOps, CDR, supporting model code/results. Exact calculated values may refine rounded authoritative values where consistent. Unspecified manufacturing geometry is a labeled visualization assumption.

| Parameter | Value | Unit | Source file | Authority tier | Confidence / note |
|---|---|---|---|---|---|
| Dedicated vehicle | Complete TSR-1; not host-mounted kit | — | DESIGN_FREEZE_V1.md §1; CRITICAL_DESIGN_REVIEW.md CDR-01 | 1 | Frozen |
| Overall travel length / width | 3.60 / 2.40 | m | DESIGN_FREEZE_V1.md §2 | 1 | Rounded envelope incl. fenders; do not stretch wheelbase |
| Stowed envelope | 3.60 × 2.40 × 1.75 | m | DESIGN_FREEZE_V1.md §2 | 1 | Mast folded, arms upright; see A-frame conflict |
| Deck top / deployed mast top | 0.90 / 2.20 | m | DESIGN_FREEZE_V1.md §2 | 1 | Raised configuration |
| Body underside raised / lowered | 0.45 / 0.10 | m | DESIGN_FREEZE_V1.md §2 | 1 | 0.35 m body lowering; wheel contacts remain on ground |
| Chassis torque box | 2.60 × 1.50 × 0.45 | m | DESIGN_FREEZE_V1.md §14 | 1 | Bounds X ±1.30, Y ±0.75, raised Z 0.45–0.90 |
| Primary structure | Al 7075 faces / Al 5056 core; Ti hardpoints | — | DESIGN_FREEZE_V1.md §14 | 1 | No CFRP chassis substitution |
| Sandwich detail | 0.5 mm faces each; 25 mm core | mm | engineering/subsystem_specs/structure.md | 2 | Concept model need not resolve skin thickness |
| Belly skid | 1.4 m², 1.5 mm Al with Ti cleats | m²/mm | engineering/subsystem_specs/structure.md | 2 | Exact outline unspecified; preserve underside clearance datum |
| Launch locks | 4 under chassis | count | engineering/interfaces.md EI-09 | 2 | Locations inferred; not vehicle landing legs |
| Wheels | 6 driven, 6 independently steered | count | DESIGN_FREEZE_V1.md §3 | 1 | Passive rocker-bogie with two lowering actuators and differential lock |
| Wheel centre coordinates | X +1.30, 0, −1.30; Y ±1.00 | m | run_config.json; VISUAL_RENDER_SPEC.md §3 | 1/3 | Z 0.45 nominal radius convention |
| Wheelbase / track | 2.60 / 2.00 | m | DESIGN_FREEZE_V1.md §2 | 1 | Measured between axle/hub centres |
| Wheel diameter / axial width | 0.90 / 0.40 | m | DESIGN_FREEZE_V1.md §3; run_config.json | 1 | Rigid titanium; see grouser-diameter ambiguity |
| Grousers | 18 per wheel; straight; 0.020 high | count/m | DESIGN_FREEZE_V1.md §3 | 1 | 108 total; distinguish rim diameter and maximum diameter |
| Rim / spokes | Ti rim 1.2 mm; open sides with flexure spokes | mm | engineering/subsystem_specs/mobility.md | 2 | Spoke count not specified |
| Wheel drive housing | Ø0.22 × 0.18 | m | engineering/subsystem_specs/mobility.md | 2 | Approximate in-hub actuator |
| Steering actuator | Ø0.14 × 0.14; ±90° | m/deg | engineering/subsystem_specs/mobility.md | 2 | Validate swept envelope, not just centreline |
| Suspension | Al 7075 links / Ti pivots; two lead screws | — | engineering/subsystem_specs/mobility.md | 2 | Mechanical topology fixed, exact linkage pivots not defined |
| Rocker visual geometry | Ø≈0.070; body pivot X≈+0.20 | m | VISUAL_RENDER_SPEC.md §3 | 3 | Rocker front wheel to body pivot to rear bogie; bogie middle + rear wheels |
| Fenders | 6 CFRP arcs, upper ≈120°; PTFE-glass skirts | count/deg | engineering/subsystem_specs/dust.md; VISUAL_RENDER_SPEC.md §3 | 2/3 | Articulate with wheel steering; exact radius inferred |
| Radiator | 1.6429435507420518 total plan area | m² | DESIGN_FREEZE_V1.md §9; thermal.md; baseline_summary.json a_rad | 1/2/4 | Refines rounded 1.64; horizontal, unobstructed except stowed boom |
| Radiator bounds | X −1.30 to −0.2047042995; Y ±0.75 | m | src/tsr1/design/layout.py | 1 | Area / full 1.50 m width; top deck +0.02 |
| Service spine bounds | X −0.1747042995 to +0.7252957005; Y ±0.675 | m | src/tsr1/design/layout.py | 1 | Exact computed layout, not rounded visual table |
| Spine grid | 2 X rows × 3 Y columns, pitch 0.45; 0.90 × 1.35 footprint | m | DESIGN_FREEZE_V1.md §6; layout.py | 1 | Six latch/interface positions |
| Spine slot loading | ≤40 per slot; ≤80 double slot; ≤150 total | kg | DESIGN_FREEZE_V1.md §6 | 1 | Illustrated modules must be repository-defined |
| Spine electrical/data | 120 VDC ≤1 kW; Ethernet per slot; thermal pad | — | engineering/interfaces.md II-01 | 2 | Include connector region, latch and covered interfaces |
| Slot height allowance | ≤0.60 above interface | m | engineering/interfaces.md II-01 | 2 | layout z_top 0.45 represents typical stowed load, not universal max |
| Crane turntable bounds | X 0.85–1.30; Y ±0.20 | m | src/tsr1/design/layout.py | 1 | Centre 1.075,0; layout top deck +0.25 |
| Crane pivot datum | X 1.075, Y 0, Z 1.05 | m | src/tsr1/design/layout.py crane_base | 1 | Supporting statics datum; pedestal physical envelope must be reviewed |
| Crane boom | 2.60 long; Ø0.050; CFRP | m | DESIGN_FREEZE_V1.md §5; manipulation.md; baseline_summary.json | 1/2/4 | Ti fittings, Vectran stays; rearward centreline stow |
| Crane rating / reach | 150 / 2.56 at 10° luff | kg/m | DESIGN_FREEZE_V1.md §5 | 1 | 360° slew, cable-luff, no hydraulics |
| A-frame geometry | 0.90 rise above boom pivot; 0.30 aft offset | m | src/tsr1/manipulation/crane.py CraneSpec | 4 | Conflicts with 1.75 stow; inferred folding stow, not altered operational statics |
| Hoist | 4 m modeled design line; hook/block | m | src/tsr1/manipulation/crane.py | 4 | Actual hanging portion pose-dependent |
| Dexterous arms | Two identical 7 DOF, each 20 kg rated | count/kg | DESIGN_FREEZE_V1.md §5 | 1 | 3 pitch +4 roll/yaw; joint origins/parenting required |
| Arm principal links | 0.75 / 0.70 / 0.15; total 1.60 | m | run_config.json dex_links | 1 | Measure joint-centre lengths, not decorative shell bounds |
| Arm materials | Ti-6Al-4V links and housings | — | DESIGN_FREEZE_V1.md §14; run_config.json | 1 | Stale CFRP mass text rejected |
| Arm base bounds | X 1.00–1.30; Y +0.45–+0.75 left / −0.75–−0.45 right | m | src/tsr1/design/layout.py | 1 | Centres 1.15, ±0.60 |
| Arm shoulder / link appearance | Shoulder Ø≈0.12; link Ø≈0.06–0.10 | m | manipulation.md; VISUAL_RENDER_SPEC.md | 2/3 | No industrial heavy arm |
| Arm candle stow top | Deck +0.85 =1.75 raised | m | src/tsr1/design/layout.py | 1 | Upper arm vertical, forearm down beside; accommodate housing radii |
| Wrist F/T + changer | Ø0.10 ×0.12; macro camera | m | engineering/subsystem_specs/manipulation.md | 2 | Preserve total link reach; not 0.12 extra reach automatically |
| Mast base bounds | X .7552957005–.9552957005; Y .22–.42 | m | src/tsr1/design/layout.py | 1 | Centre .8552957005,.32 |
| Mast tube | 1.20 × Ø0.060 | m | engineering/subsystem_specs/structure.md | 2 | CFRP, Ti fold hinge, pan/tilt; head top 2.15–2.20 |
| Stereo cameras | 0.25 baseline; 70° FOV | m/deg | VISUAL_RENDER_SPEC.md; sensors.md | 3/2 | Real optical apertures; thermal IR, two LED lamps, relay antenna |
| Other external sensors | 6 HazCams, front/rear LiDAR, arm macro cameras, sun/star optics | count | engineering/subsystem_specs/sensors.md | 2 | LiDAR ≈0.15 m cube; exact mounting positions inferred for clear FOV |
| Solar arrays | Two fixed vertical opposite-side 1.50 ×0.50 panels | m | power.md; run_config.json solar_area | 2/1 | Total area 1.50 m²; GaAs cells on CFRP; no rooftop array |
| Winch | 4 kN; 50 m line; drum Ø0.12; envelope .45×.30×.30 | kN/m | DESIGN_FREEZE_V1.md §7; recovery.md | 1/2 | Rear internal/covered; show drum/level-wind where appropriate |
| Fairlead height in working recovery pose | 0.25 above ground | m | DESIGN_FREEZE_V1.md §7 | 1 | Must remain low during recovery; configuration interpretation in conflict log |
| Spades | 2 ×(.60×.30×.006) | m | DESIGN_FREEZE_V1.md §7; recovery.md | 1/2 | Rear hinged Ti plates; 0.30 penetration dimension; no outriggers |
| Carried helical anchors | 2; shaft .70×Ø.025; helix Ø.15; installed depth .60 | m | recovery.md | 2 | Right side stow; front hold-down locations in recovery; two additional spare in MOD-REC |
| Tool rack | X 1.30–1.38; Y ±.55, on front face | m | src/tsr1/design/layout.py tool_rack | 1 | Holsters not deck cargo |
| Tools | Gripper, socket, probe, connector, brush, EDS wand, anchor driver, OTCM, androgynous adapter, slings, shackle, scoop | 12 types | DESIGN_FREEZE_V1.md §6; tools.md | 1/2 | tools.md stores slings and shackle in MOD-REC; representative shapes, no invented tools |
| Tether / reel | 25 line; Ø.35 reel; front exit Y+.55 | m | DESIGN_FREEZE_V1.md §8; power.md; VISUAL_RENDER_SPEC.md | 1/2/3 | Orange jacket differentiates power from recovery line |
| MOD-KA | .90×.45×.45 stowed; 72.6 kg; 4 kWh; two slots | m/kg/kWh | service_spine.md | 2 | Al frame, MLI, Ti latches, lift point, fiducials |
| MOD-KA PV | 2 back-to-back 1.5 m² faces; ≈1.2×1.25 each; top≈1.6 | m | service_spine.md; VISUAL_RENDER_SPEC.md | 2/3 | Folded panel segmentation unspecified; label inferred packing |
| MOD-KA cable | 10 | m | service_spine.md; interfaces.md EI-11 | 2 | Do not confuse with rover 25 m tether |
| WEB | 1.00×.80×.35; centre X−.50 | m | configuration.py; CDR-21 | 4 | X −1..0 under radiator; hidden standard exterior |
| Battery | .80×.50×.18; four modules | m | power.md | 2 | Internal envelope approximation; no invented external tank |
| PCDU / PTM | .35×.25×.12 / .30×.25×.12 | m | power.md | 2 | In WEB; optional hidden packaging volumes |
| Arm / wheel / peer interfaces | 4 captive fasteners each base/hub; 2 peer grapple fixtures; fiducials and port | count | interfaces.md II-03/04/07 | 2 | Patterns illustrative, no fabricated certification |
| Branding | TODARO CORP.; TSR-1 | — | VISUAL_RENDER_SPEC.md §8 | 3 | Restrained dark lettering; no agency marks |

Required poses: TRAVERSE (raised, candle arms, mast up, crane rearward, spades/anchors carried); SERVICING (lowered, working arms/tool, crane available); RECOVERY (lowered, spades/anchors/line deployed, fairlead .25); EMERGENCY POWER (tether/connector deployed); LANDER STOW (mast folded, candle arms, boom locked, ≤1.75 m). Preserve modular collections and mechanical pivot hierarchy. Outputs and inspections follow the user's master directive: actual .blend, executed reproducible build, GLB, optional reliable FBX, seven neutral views plus five functional renders, measured validation and collision/access review. Technical dimensions are measured on rover hardware only, excluding lights, floor, text callouts, cameras, deployed remote cables and targets.

Dust-sheet refinement: fender axial width0.45 m (`engineering/subsystem_specs/dust.md`, Tier2). With track2.00 this conflicts with centred overall2.40 width; see C17 for25 mm inboard shell-offset interpretation. Full outer fender dimensions must be measured.
