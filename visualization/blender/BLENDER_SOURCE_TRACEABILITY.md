# TSR-1 source traceability

This map names logical collections/object families; procedural per-instance suffixes are allowed. Every major visible component must retain a source path in object metadata or build configuration. Inferred detail belongs in `BLENDER_CONFLICT_LOG.md`; a source citation supports the existence and specified dimensions, not an undocumented exact shape.

| Blender collection / object family | Engineering source | Authority / scope |
|---|---|---|
| TSR1_ROOT / configuration root | DESIGN_FREEZE_V1.md §§1–2; simulations/configs/run_config.json | Frozen dedicated TSR-1; metric global frame |
| STRUCTURE / chassis_torque_box | DESIGN_FREEZE_V1.md §14; structure.md | 2.6×1.5×.45 torque box |
| STRUCTURE / secondary_structure, mounts | structure.md; materials_matrix.csv | Bracket details inferred |
| STRUCTURE / hardpoints, tow lugs, grapple fixtures | DESIGN_FREEZE §7/14; interfaces.md EI-06, II-07 | Front/rear load paths, two peer grapple fixtures |
| STRUCTURE / belly_skid, cleats | structure.md; mobility.md | Al skid, Ti cleats, lowering contact function |
| STRUCTURE / launch_locks | interfaces.md EI-09; VISUAL_RENDER_SPEC §6 | Four chassis locks, arm/boom stow locks; exact geometry inferred |
| MOBILITY / wheels_FL,ML,RL,FR,MR,RR | DESIGN_FREEZE §3; run_config; mobility.md | Six Ti rigid wheels, .90×.40,18 grousers each |
| MOBILITY / wheel_hubs, drives | mobility.md; interfaces.md II-04 | .22×.18 actuator housings, ORU flange |
| MOBILITY / steering_assemblies | mobility.md | Six .14×.14 housings; origin at steer axis |
| MOBILITY / rocker_L/R, bogie_L/R | DESIGN_FREEZE §3; mobility.md; VISUAL_RENDER_SPEC §3 | Rocker-bogie topology; exact pivots inferred |
| MOBILITY / differential, differential_lock | mobility.md | Transverse equalizer/lock |
| MOBILITY / body_lowering_L/R | DESIGN_FREEZE §3; mobility.md | Two lead-screw actuators, .35 stroke |
| DUST_MITIGATION / fender_1..6, skirts | dust.md; materials_matrix.csv; visual spec §3 | Six upper-third shells and fabric skirts |
| DUST_MITIGATION / boots, labyrinths, EDS covers | DESIGN_FREEZE §13; dust.md | Joint and optical protection |
| DEX_ARM_L, DEX_ARM_R / shoulder, links, seven joint pivots | DESIGN_FREEZE §5/14; run_config dex_links/material; manipulation.md; layout.py | Identical 7DOF Ti arms, .75/.70/.15 links; front-corner bases |
| DEX_ARM_* / wrist FT, tool_changer, macro_camera | manipulation.md; sensors.md; interfaces.md II-02 | .10×.12 interface envelope, optical aperture |
| CRANE / turntable, slew, boom_pivot | layout.py; manipulation.md | Front-center base at X1.075 Y0, Z1.05 boom datum |
| CRANE / boom, A_frame, luff_line, hoist_line, hook | DESIGN_FREEZE §5; manipulation.md; manipulation/crane.py | 2.60 boom, .9 A-frame operational rise; inferred stow fold in log |
| SERVICE_SPINE / rails, six slot latches/connectors | DESIGN_FREEZE §6; layout.py; service_spine.md; interfaces II-01 | 2×3 .45 grid; X.90×Y1.35 |
| SERVICE_SPINE / MOD_KA enclosure, folded_PV, latches, lift eye | service_spine.md; DESIGN_FREEZE §6; interfaces EI-11 | KA-C .90×.45×.45 double slot,72.6kg; segmented folding inferred |
| SERVICE_SPINE / ORU_cradles, MOD_REC | DESIGN_FREEZE §6; VISUAL_RENDER_SPEC §4; tools.md | Low empty cradles/recovery tray keep specified boom corridor clear |
| RECOVERY / winch, drum, levelwind, cover | DESIGN_FREEZE §7; recovery.md | 4kN/50m, drumØ.12, envelope .45×.30×.30 |
| RECOVERY / low_fairlead, Vectran_line | DESIGN_FREEZE §7; recovery.md; stability/envelope.py | .25 ground height in lowered working recovery; pose distinction in log |
| RECOVERY / spade_L/R, hinges | recovery.md; VISUAL_RENDER_SPEC §5 | .60×.30×.006 each, rear deployed/stowed poses |
| RECOVERY / anchor_1/2, clips, hold_down_straps | recovery.md; VISUAL_RENDER_SPEC §§5–6 | .70×Ø.025 shaft,Ø.15 helix; carried right, installed front |
| SENSOR_MAST / base, hinge, tube, pan_tilt | layout.py; structure.md; VISUAL_RENDER_SPEC §4 | Ø.06×1.20, head2.20 raised; rearward fold angle inferred |
| SENSOR_MAST / stereo_pair, IR, LEDs, relay_panel | sensors.md; communications.md; VISUAL_RENDER_SPEC §4 | .25 baseline, real optical windows, small relay antenna |
| SENSORS / HazCam_1..6, LiDAR_front/rear | sensors.md; DESIGN_FREEZE §10 | Six hazard cameras, two .15 cubes; placements inferred to expose FOV |
| SENSORS / sun_sensor, star_tracker | sensors.md; interfaces EI-08 | External apertures/baffle supported; exact placement inferred |
| POWER / PV_left/right | DESIGN_FREEZE §8; run_config solar_area; power.md | Two fixed vertical1.50×.50 side panels |
| POWER / tether_reel, front_guide, connector_head | power.md; interfaces EI-01; VISUAL_RENDER_SPEC §4 | ReelØ.35,25m tether,frontY+.55 guide |
| POWER / battery, PCDU, PTM hidden packaging | power.md; configuration.py | Internal volumes, not exterior embellishment |
| THERMAL / radiator, OSR_tiles, EDS_film | layout.py; thermal.md; materials_matrix.csv | Exact1.6429435507420518m² full-width rear allocation |
| THERMAL / WEB, MLI | configuration.py web_*; thermal.md; CDR-21 | Hidden WEB X−1..0; no invented radiator service hatches |
| TOOL_RACK / front_face_holsters, ten rigid tools | layout.py tool_rack; tools.md | X1.30–1.38,Y±.55; tools individually labeled |
| TOOL_RACK or MOD_REC / slings, shackle | tools.md storage column | Rigging stored MOD-REC, not arbitrary cargo |
| BRANDING / TODARO_CORP, TSR1, fiducials | VISUAL_RENDER_SPEC §8; interfaces II-07 | No agency ownership marks |
| TRAVERSE,SERVICING,RECOVERY,EMERGENCY_POWER,LANDER_STOW poses | User master directive §38; VISUAL_RENDER_SPEC §6; ConOps | Poses demonstrate functions; no claim of solved motion planning |
| Ground / neutral stage / lunar lighting | User directive §§43–45; VISUAL_RENDER_SPEC §7 | Presentation environment excluded from rover measured bounds |

Read-source coverage: PROJECT_STATE first; full freeze/run config/layout/visual spec; all subsystem sheets (structure, mobility, manipulation, recovery, service_spine, power, thermal, sensors, dust, tools, avionics, communications, harness); materials matrix; interfaces; final specifications; architecture; ConOps; CDR; supporting configuration/crane/layout code, parameter register, mass budget and baseline result. Supporting trade outcomes are cross-checked through freeze and CDR; no rejected historical figure is geometry authority. No engineering generator was run and no frozen document changed.
