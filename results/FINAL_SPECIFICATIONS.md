# TSR-1 FINAL SPECIFICATIONS

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other organizations are used solely as technical and architectural context.

Complete technical specification of the frozen configuration. System-level values: `DESIGN_FREEZE_V1.md` (same generator, same data). Component specification sheets: `engineering/subsystem_specs/`. Requirements with model-derived values: `requirements/`.

## 1. Requirement compliance

| Req | Statement | Verification | Status |
|---|---|---|---|
| MR-01 | TSR-1 shall increase the time-averaged availability of serviceable surface assets in its service area relative to an otherwise identical base without TSR-1, by at least 2.2 percentage points for the reference base of 30 assets. | A | DERIVED/CLOSED |
| MR-02 | TSR-1 shall perform all nominal inspection, servicing, emergency-power and recovery functions without crew EVA support. | D | DERIVED/CLOSED |
| MR-03 | TSR-1 shall inspect assets of classes AC-1 to AC-9 at compatibility levels L0–L3 using visible, thermal-infrared and 3-D imaging, and report anomalies with location and severity. | D | DERIVED/CLOSED |
| MR-04 | TSR-1 shall remove and replace robot-compatible ORUs of mass up to 150 kg on L2 and L3 assets. | T | DERIVED/CLOSED |
| MR-05 | TSR-1 shall deliver temporary electrical power to a disabled asset through an ISPSIS 120 VDC compatible interface at up to 3 kW continuous for at least 10 h at keep-alive load (300 W). | T | DERIVED/CLOSED |
| MR-06 | TSR-1 shall recover or reposition immobilized vehicles within the envelope: free-rolling vehicles up to 4.8 t and brake-locked vehicles up to 2.3 t on slopes ≤ 15° (anchored winch, FoS 1.5); 450 kg-class rovers with wheels embedded ≤ 0.15 m after ramp excavation; direct towing of free-rolling vehicles ≤ 1.5 t on level ground; P(sampled immobilisation case recoverable) = 0.92. | A,T | DERIVED/CLOSED |
| MR-07 | TSR-1 shall remove regolith dust from asset solar-array, radiator and optical surfaces such that the residual area coverage is ≤ 5 %. | T | DERIVED/CLOSED |
| MR-08 | TSR-1 shall execute service tasks under task-level human supervision only (no continuous teleoperation) and shall safely continue to the next hold point or abort predefined tasks during Earth-link outages up to 72 h and local-network outages up to 24 h. | D | DERIVED/CLOSED |
| MR-09 | TSR-1 shall have an operational design life of 10 years on the lunar surface. | A | DERIVED/CLOSED |
| MR-10 | TSR-1 shall operate in the south-polar environment (sunlit ridges, shadowed terrain) including PSR excursions of up to 8 h, and shall survive 120 h without external power or sunlight. | A,T | DERIVED/CLOSED |
| MR-11 | TSR-1 shall be deliverable as a single payload on a commercial lander with ≤ 3.0 t surface payload capacity (threshold) and ≤ 1.5 t (goal), including accommodation hardware. | A,I | DERIVED/CLOSED |
| MR-12 | TSR-1 shall use open interface standards: ISPSIS for power, LunaNet/CCSDS for communications and PNT, and ISO 9409-1/IERIIS-derived mechanical tool interfaces with adapters; it shall not require proprietary-only interfaces on serviced assets. | I | DERIVED/CLOSED |
| MR-13 | TSR-1's life-limited and failure-prone items shall be replaceable at ORU level by another TSR-class vehicle or by crew without special tools. | D | DERIVED/CLOSED |
| MR-14 | TSR-1 shall not create a catastrophic hazard to crew or to other assets; all motion shall be bounded by a deterministic safety layer independent of high-level autonomy. | A,T | DERIVED/CLOSED |
| MR-15 | TSR-1 shall serve assets within a service radius of 10 km of its home charging node and reach any such asset within 10 h of task approval. | A,D | DERIVED/CLOSED |
| SR-MOB-01 | Mean static ground contact pressure shall not exceed 7 kPa at maximum operational mass on level ground (computed: 6.64 kPa). | A,T | DERIVED/CLOSED |
| SR-MOB-02 | TSR-1 shall climb and descend 20° slopes under nominal soil and 15° under conservative (lunar-gravity-penalised) soil at maximum operational mass with wheel slip ≤ 40 %, and shall hold position (brakes) on 25°. | A,T | DERIVED/CLOSED |
| SR-MOB-03 | TSR-1 shall negotiate step obstacles of 0.45 m and ditches of 0.4 m width. | T | DERIVED/CLOSED |
| SR-MOB-04 | Autonomous average traverse speed shall be ≥ 0.35 m/s on ≤ 10° terrain; maximum speed 1 m/s. | T | DERIVED/CLOSED |
| SR-MOB-05 | Range on one charge shall be ≥ 34 km on nominal terrain at maximum operational mass while retaining the survival energy reserve. | A,T | DERIVED/CLOSED |
| SR-MOB-06 | Loss of any single wheel drive shall not prevent mobility on slopes ≤ 17°. | A,T | DERIVED/CLOSED |
| SR-MAN-01 | The dexterous arm shall handle 20 kg at 1.6 m reach in lunar gravity with end-effector positioning accuracy ≤ 2 mm (visual-servo closed loop) and 6-axis force/torque sensing. | T | DERIVED/CLOSED |
| SR-MAN-02 | The heavy-handling system shall lift and place 150 kg at 2.56 m horizontal reach in lunar gravity within the stability envelope. | T | DERIVED/CLOSED |
| SR-MAN-03 | Tools shall be exchanged autonomously via a tool changer; tool change time ≤ 5 min. | D | DERIVED/CLOSED |
| SR-SRV-01 | The service spine shall carry ≥ 150 kg of ORUs, tools and modules in ≥ 6 standard slots. | I,T | DERIVED/CLOSED |
| SR-SRV-02 | The fastener tool shall deliver up to 50 N·m with reaction taken through the arm/fixture and torque measurement accuracy ±5 %. | T | DERIVED/CLOSED |
| SR-PWR-01 | The primary power bus shall be 120 VDC with power quality and grounding compatible with ISPSIS; 28 VDC secondary bus for avionics. | I,T | DERIVED/CLOSED |
| SR-PWR-02 | A bidirectional, galvanically isolated power-transfer port shall accept ≥ 3 kW for charging and deliver ≥ 3 kW continuous / 4.5 kW peak (60 s) at 120 VDC through a tether ≤ 25 m. | T | DERIVED/CLOSED |
| SR-PWR-03 | Battery usable energy shall be ≥ 15 kWh at end of life, sufficient for the design-reference sortie plus 120 h survival reserve. | A,T | DERIVED/CLOSED |
| SR-THM-01 | Battery temperature shall be held within 0 to +30 °C while charging and −20 to +40 °C while discharging. | A,T | DERIVED/CLOSED |
| SR-THM-02 | The thermal system shall reject 350 W peak internal dissipation in the hot case and limit survival heater demand to ≤ 82 W in the cold case. | A,T | DERIVED/CLOSED |
| SR-AUT-01 | Autonomy shall be layered (mission planner → task planner → verified skills → motion planning → real-time control); no learned or generative component shall command actuator torques or currents directly. | I,A | DERIVED/CLOSED |
| SR-AUT-02 | Every irreversible step (power connection, release of load-bearing fasteners, winch tension above 1 kN, cutting) shall be preceded by a hold point requiring human approval or a pre-authorised rule. | D | DERIVED/CLOSED |
| SR-AVI-01 | Avionics shall separate a high-performance autonomy computer from a dual-redundant deterministic safety/real-time computer; parts shall tolerate ≥ 20 krad(Si) TID and be SEL-immune or protected. | A,T | DERIVED/CLOSED |
| SR-COM-01 | TSR-1 shall communicate via (a) the base surface network, (b) a LunaNet-compliant relay link and (c) a peer mesh link, using DTN store-and-forward for non-real-time data. | T | DERIVED/CLOSED |
| SR-NAV-01 | TSR-1 shall localise to ≤ 1 m in the base frame and determine relative pose to a servicing interface to ≤ 5 mm / 0.5° before contact. | T | DERIVED/CLOSED |
| SR-DST-01 | All external mechanisms shall use labyrinth + seal protection; optics and radiators shall have dust removal (EDS) or covers; wheels shall have fenders limiting ejecta onto the vehicle; connectors shall have self-closing dust covers. | I,T | DERIVED/CLOSED |
| SR-STR-01 | Primary structure shall withstand launch/landing quasi-static loads of 6 g axial + 3 g lateral with factors of safety 1.25 (yield) and 1.4 (ultimate). | A,T | DERIVED/CLOSED |
| SR-STR-02 | Recovery hard points and the winch load path shall withstand 4 kN line pull at any angle within the recovery cone with FoS 1.4 (ultimate). | A,T | DERIVED/CLOSED |
| SR-REC-01 | The winch shall provide 4 kN line pull, 50 m usable line, with continuous tension measurement and automatic limiting. | T | DERIVED/CLOSED |
| SR-REC-02 | The ground-reaction system shall resist ≥ 5.9 kN horizontal load (P50 soil) and ≥ 3.9 kN (P10 soil). | A,T | DERIVED/CLOSED |
| SR-REL-01 | No single failure other than primary-structure failure shall cause loss of mobility on terrain ≤ 17°, or loss of the ability to communicate and safe the vehicle. | A | DERIVED/CLOSED |
| SR-REL-02 | Probability that TSR-1 retains at least degraded-mode servicing capability after 10 years shall be ≥ 0.99 (with peer/crew ORU replacement). | A | DERIVED/CLOSED |
| SR-MNT-01 | Wheel drive units, battery modules, avionics modules, cameras, tools, power electronics and arms (at the arm base) shall be ORUs with grapple handles, captive fasteners and blind-mate connectors. | I,D | DERIVED/CLOSED |
| SR-MNT-02 | TSR-1 shall carry ≥ 2 grapple fixtures, fiducial markers on each ORU and a service port for peer diagnostics. | I | DERIVED/CLOSED |
| SR-INT-01 | The arm tool interface shall follow an ISO 9409-1 bolt pattern and carry adapters for OTCM-type grapple/socket interfaces, HOTDOCK-type androgynous interfaces and payload-deck-type interfaces. | I,T | DERIVED/CLOSED |
| SR-SAF-01 | Within 10 m of crew, vehicle speed shall be limited to 0.2 m/s and manipulator end-effector force to 50 N by the deterministic safety layer. | T | DERIVED/CLOSED |
| SR-SNS-01 | The sensor suite shall comprise at minimum: mast stereo navigation cameras with illumination, hazard cameras, LiDAR, macro inspection camera, thermal-IR imager, wrist F/T sensors, IMU, wheel and joint encoders, and electrical diagnostic instrumentation; no airborne acoustic sensors. | I | DERIVED/CLOSED |

## 2. Component list (mass budget)

| Component | Subsystem | CBE [kg] | Predicted [kg] | Material | TRL |
|---|---|---|---|---|---|
| wheel_1 | mobility | 10.392 | 12.99 | Ti-6Al-4V | 5 |
| drive_actuator_1 | mobility | 8.985 | 11.232 | Ti housing, BLDC, strain-wave gear, BMG/MoS2 | 5 |
| wheel_2 | mobility | 10.392 | 12.99 | Ti-6Al-4V | 5 |
| drive_actuator_2 | mobility | 8.985 | 11.232 | Ti housing, BLDC, strain-wave gear, BMG/MoS2 | 5 |
| wheel_3 | mobility | 10.392 | 12.99 | Ti-6Al-4V | 5 |
| drive_actuator_3 | mobility | 8.985 | 11.232 | Ti housing, BLDC, strain-wave gear, BMG/MoS2 | 5 |
| wheel_4 | mobility | 10.392 | 12.99 | Ti-6Al-4V | 5 |
| drive_actuator_4 | mobility | 8.985 | 11.232 | Ti housing, BLDC, strain-wave gear, BMG/MoS2 | 5 |
| wheel_5 | mobility | 10.392 | 12.99 | Ti-6Al-4V | 5 |
| drive_actuator_5 | mobility | 8.985 | 11.232 | Ti housing, BLDC, strain-wave gear, BMG/MoS2 | 5 |
| wheel_6 | mobility | 10.392 | 12.99 | Ti-6Al-4V | 5 |
| drive_actuator_6 | mobility | 8.985 | 11.232 | Ti housing, BLDC, strain-wave gear, BMG/MoS2 | 5 |
| steer_actuator_1 | mobility | 4.246 | 5.307 | Ti/Al housing | 5 |
| steer_actuator_2 | mobility | 4.246 | 5.307 | Ti/Al housing | 5 |
| steer_actuator_3 | mobility | 4.246 | 5.307 | Ti/Al housing | 5 |
| steer_actuator_4 | mobility | 4.246 | 5.307 | Ti/Al housing | 5 |
| steer_actuator_5 | mobility | 4.246 | 5.307 | Ti/Al housing | 5 |
| steer_actuator_6 | mobility | 4.246 | 5.307 | Ti/Al housing | 5 |
| suspension_rocker_bogie | mobility | 61.043 | 73.252 | Al 7075-T7351 tubes, Ti-6Al-4V pivots | 6 |
| differential_lock | mobility | 2.5 | 3.125 | steel/Ti | 5 |
| body_lowering_actuator_L | mobility | 3.025 | 3.781 | Ti ball-screw, BMG nut | 4 |
| body_lowering_actuator_R | mobility | 3.025 | 3.781 | Ti ball-screw, BMG nut | 4 |
| belly_skid_plate | stabilisation | 9.442 | 11.33 | Al 7075-T7351 + Ti cleats | 6 |
| fender_1 | dust | 1.38 | 1.656 | CFRP + PTFE-coated fabric | 7 |
| fender_2 | dust | 1.38 | 1.656 | CFRP + PTFE-coated fabric | 7 |
| fender_3 | dust | 1.38 | 1.656 | CFRP + PTFE-coated fabric | 7 |
| fender_4 | dust | 1.38 | 1.656 | CFRP + PTFE-coated fabric | 7 |
| fender_5 | dust | 1.38 | 1.656 | CFRP + PTFE-coated fabric | 7 |
| fender_6 | dust | 1.38 | 1.656 | CFRP + PTFE-coated fabric | 7 |
| chassis_torque_box | structure | 72.965 | 87.558 | Al 7075-T7351 faces / Al 5056 honeycomb; Ti-6Al-4V hard points | 7 |
| secondary_structure | structure | 18.241 | 21.89 | Al 6061/7075 | 7 |
| sensor_mast | structure | 6.0 | 7.2 | CFRP tube, Ti hinge | 6 |
| dexterous_arm | manipulation | 26.973 | 33.716 | CFRP links, Ti-6Al-4V joints, strain-wave gears, BMG/MoS2 | 5 |
| dexterous_arm_2 | manipulation | 26.973 | 33.716 | CFRP links, Ti-6Al-4V joints, strain-wave gears, BMG/MoS2 | 5 |
| crane_boom | manipulation | 19.903 | 24.879 | CFRP links, Ti-6Al-4V joints, strain-wave gears, BMG/MoS2 | 4 |
| ft_sensor_and_tool_changer | manipulation | 0.0 | 0.0 | Ti-6Al-4V | 6 |
| tool_parallel_gripper | tools | 2.0 | 2.5 | Ti/PEEK fingers, Vespel pads | 6 |
| tool_socket_driver | tools | 2.5 | 3.125 | Ti body, tool-steel socket set | 6 |
| tool_electrical_probe | tools | 1.5 | 1.875 | PEEK/Ti, Au-plated probes | 5 |
| tool_connector_mate | tools | 2.0 | 2.5 | Ti/PEEK | 5 |
| tool_dust_brush | tools | 1.5 | 1.875 | Ti frame, PTFE-coated aramid bristles | 5 |
| tool_eds_wand | tools | 2.5 | 3.125 | CFRP frame, ITO/PI electrode film, HV supply | 4 |
| tool_anchor_driver | tools | 4.0 | 5.0 | Ti body, steel bit | 4 |
| tool_oru_adapter_otcm | tools | 3.0 | 3.75 | Ti-6Al-4V | 5 |
| tool_oru_adapter_androgynous | tools | 2.5 | 3.125 | Ti-6Al-4V/Al 7075 | 5 |
| tool_lifting_fixture_slings | tools | 2.0 | 2.5 | Vectran slings, Ti hooks | 6 |
| tool_recovery_shackle_hitch | tools | 2.0 | 2.5 | Ti-6Al-4V | 6 |
| tool_regolith_scoop | tools | 2.0 | 2.5 | Ti-6Al-4V blade, PTFE-coated | 6 |
| tool_rack_holsters | tools | 6.0 | 7.5 | Al 7075, Ti latches | 6 |
| service_spine | service_spine | 14.6 | 17.52 | Al 7075, Ti latches | 5 |
| recovery_winch | recovery | 24.2 | 30.25 | Ti drum, steel gear, BMG level-wind | 5 |
| recovery_line | recovery | 1.5 | 1.8 | Vectran with PTFE/aramid jacket | 6 |
| spade_1 | recovery | 8.784 | 10.98 | Ti-6Al-4V | 4 |
| spade_2 | recovery | 8.784 | 10.98 | Ti-6Al-4V | 4 |
| helical_anchor_1 | recovery | 2.0 | 2.5 | Ti-6Al-4V | 4 |
| helical_anchor_2 | recovery | 2.0 | 2.5 | Ti-6Al-4V | 4 |
| tow_hardpoints_front_rear | recovery | 3.0 | 3.6 | Ti-6Al-4V | 7 |
| battery_pack | power | 147.735 | 162.508 | Li-ion 18650 PPR pack (Al interstitials, mica) | 6 |
| pcdu_bus_regulator | power | 16.333 | 20.417 | Al housing, SiC FETs | 5 |
| power_transfer_module | power | 12.0 | 15.0 | Al housing, SiC, planar transformer | 4 |
| power_tether_and_reel | power | 8.954 | 11.192 | Cu/PTFE/aramid jacket; Al reel | 5 |
| dust_tolerant_connector_head | power | 2.5 | 3.125 | Ti shell, Au contacts, PEEK | 4 |
| solar_arrays_vertical | power | 4.2 | 5.04 | IMM/triple-junction GaAs on CFRP | 7 |
| solar_array_regulator | power | 1.5 | 1.875 | Al | 6 |
| autonomy_computer_hpsc | avionics | 6.0 | 7.5 | Al chassis | 6 |
| safety_rt_computer_A | avionics | 3.0 | 3.75 | Al chassis | 7 |
| safety_rt_computer_B | avionics | 3.0 | 3.75 | Al chassis | 7 |
| motor_control_units | avionics | 11.2 | 14.0 | Al chassis | 5 |
| mass_memory_and_timing | avionics | 1.3 | 1.625 | Al chassis | 7 |
| navcam_stereo_pair | sensors | 0.8 | 1.0 |  | 6 |
| mast_pan_tilt | sensors | 5.0 | 6.25 |  | 6 |
| led_illuminators | sensors | 1.0 | 1.25 |  | 7 |
| hazcams_x6 | sensors | 1.5 | 1.875 |  | 7 |
| lidar_front | sensors | 2.5 | 3.125 |  | 5 |
| lidar_rear | sensors | 2.5 | 3.125 |  | 5 |
| thermal_ir_imager | sensors | 0.6 | 0.75 |  | 6 |
| macro_inspection_camera | sensors | 0.4 | 0.5 |  | 6 |
| imu_ln200s | sensors | 0.75 | 0.938 |  | 9 |
| sun_sensor_star_tracker | sensors | 0.5 | 0.625 |  | 8 |
| electrical_diagnostic_unit | sensors | 1.5 | 1.875 |  | 5 |
| contact_vibration_sensors | sensors | 0.2 | 0.25 |  | 6 |
| surface_network_radio | communications | 1.5 | 1.875 |  | 6 |
| lunanet_relay_transceiver | communications | 2.5 | 3.125 |  | 6 |
| relay_antenna_gimballed | communications | 2.2 | 2.75 |  | 6 |
| mesh_uhf_radio | communications | 0.5 | 0.625 |  | 7 |
| mli_blankets | thermal | 2.288 | 2.86 | Kapton/Mylar/Dacron netting, Beta-cloth outer | 8 |
| radiator_panel_eds | thermal | 9.858 | 12.322 | Al 6063 heat-pipe panel, OSR/AgFEP, ITO EDS film | 5 |
| loop_heat_pipe_switch | thermal | 3.5 | 4.375 | SS/Al, ammonia | 6 |
| heaters_thermostats | thermal | 5.0 | 6.25 | Kapton/Inconel | 8 |
| optics_eds_and_covers | dust | 1.2 | 1.5 | ITO/PI, Ti covers | 5 |
| joint_boots_seals | dust | 4.5 | 5.625 | PTFE-coated fabric, Ti | 5 |
| harness | harness | 45.99 | 73.584 | Cu/PTFE, connectors | 7 |
| TOTAL predicted (CBE + MGA) |  | 812.49 | 999.58 | None | None |
| system margin (15%) |  |  | 149.94 | None | None |
| DRY MASS ALLOCATION |  |  | 1149.52 | None | None |
| carried payload (ORUs/modules, nominal) |  |  | 100.0 | None | None |
| OPERATIONAL MASS |  |  | 1249.52 | None | None |
| lander accommodation (5% of dry allocation) |  |  | 57.48 | None | None |
| DELIVERED MASS (charged to lander) |  |  | 1207.0 | None | None |

## 3. Closure verification

| Check | Computed | Limit | Result |
|---|---|---|---|
| MASS-1 component CBE sum reproduces total | 812.490 | — | PASS |
| MASS-2 MGA roll-up reproduces predicted mass | 999.585 | — | PASS |
| MASS-3 delivered mass ≤ 1.5 t (goal, Argonaut-class) | 1,206.999 | 1,500.000 | PASS |
| MASS-4 delivered mass ≤ 3.0 t (threshold, Mk1-class) | 1,206.999 | 3,000.000 | PASS |
| MASS-5 sizing mass = operational mass (iteration converged) | 1,249.523 | — | PASS |
| POWER-1 subsystem loads reproduce all mode totals | True | — | PASS |
| POWER-2 worst mode + full PTM delivery ≤ PCDU rating | 3,471.307 | 4,000.000 | PASS |
| POWER-3 simultaneous-peak discharge C-rate ≤ 1C | 0.144 | 1.000 | PASS |
| ENERGY-1 worst DRM (DRM-2) + 50 h reserve ≤ usable EOL (no solar) | 14.142 | 15.000 | PASS |
| ENERGY-2 full-battery survival ≥ 120 h (longest darkness at best sites, S030) | 183.299 | 120.000 | PASS |
| ENERGY-3 solar average ≥ survival power (indefinite survival in sunlight) | 165.707 | 81.833 | PASS |
| THERMAL-1a max steady WEB dissipation (M9_charging) ≤ radiator design load | 319.920 | 380.000 | PASS |
| THERMAL-1b 3 kW delivery transient (3.3 h, energy-limited): WEB ΔT ≤ 15 K | 0.000 | 15.000 | PASS |
| THERMAL-2 survival heater + electronics ≤ survival-mode power used for energy closure | 81.833 | 81.833 | PASS |
| MOB-1 ground pressure ≤ 7 kPa | 6.706 | 7.000 | PASS |
| MOB-2 traction supports claimed 20° climb at ≤ 40 % slip | True | — | PASS |
| MOB-3 drive actuator rating ≥ wheel torque at claimed slope | 102.106 | 209.636 | PASS |
| REC-A claimed scenario feasible with FoS (margin) | 8.812 | 1.000 | PASS |
| REC-B claimed scenario feasible with FoS (margin) | 10.782 | 1.000 | PASS |
| REC-B2 claimed scenario feasible with FoS (margin) | 5.122 | 1.000 | PASS |
| REC-C-dig claimed scenario feasible with FoS (margin) | 4.577 | 1.000 | PASS |
| REC-D claimed scenario feasible with FoS (margin) | 1.551 | 1.000 | PASS |
| REC-D2 claimed scenario feasible with FoS (margin) | 4.081 | 1.000 | PASS |
| REC-D3 claimed scenario feasible with FoS (margin) | 3.325 | 1.000 | PASS |
| REC-W winch rating ≥ max claimed line tension | 1,186.687 | 4,000.000 | PASS |
| MAN-1 dexterous shoulder rating ≥ payload moment × MF | 150.336 | 196.500 | PASS |
| STAB C2 crane side lift 150 kg @ 2.56 m, level | 4.982 | 1.500 | PASS |
| STAB C2 crane side lift 150 kg @ 2.56 m, 10° lateral, load downhi | 3.978 | 1.500 | PASS |
| STAB C3 crane front lift 150 kg | 6.456 | 1.500 | PASS |
| STAB C4 dexterous arm extended (front-right) with rated payload | 104.936 | 1.500 | PASS |
| STAB C5 both extended same side (worst) | 4.697 | 1.500 | PASS |
| STAB C7b winch 4.0 kN + spades + 2 front hold-down anchors (80 %  | inf | 1.500 | PASS |
| GEOM-1 WEB volume ≥ packaged equipment volume | 0.161 | 0.280 | PASS |
| GEOM-2 stowed length ≤ envelope | 3.600 | 4.000 | PASS |
| GEOM-3 stowed width ≤ envelope | 2.400 | 2.600 | PASS |
| GEOM-4 stowed height (mast folded) ≤ envelope | 1.200 | 2.000 | PASS |
| GEOM-5 deck area ≥ allocations (radiator, spine, crane, arms, mast, tool rack) | 3.643 | 3.900 | PASS |
| GEOM-6 adjacent wheel clearance ≥ 0.15 m | 0.400 | 0.150 | PASS |
| MISSION DRM-1 duration ≤ 30 h (fits one comm/approval shift cycle + margin) | 20.373 | 30.000 | PASS |
| MISSION DRM-2 duration ≤ 30 h (fits one comm/approval shift cycle + margin) | 22.873 | 30.000 | PASS |
| MISSION DRM-3 duration ≤ 30 h (fits one comm/approval shift cycle + margin) | 11.937 | 30.000 | PASS |
| MISSION DRM-4 duration ≤ 30 h (fits one comm/approval shift cycle + margin) | 20.298 | 30.000 | PASS |
| MISSION DRM-5 duration ≤ 30 h (fits one comm/approval shift cycle + margin) | 19.873 | 30.000 | PASS |
| MISSION DRM-6 duration ≤ 30 h (fits one comm/approval shift cycle + margin) | 9.062 | 30.000 | PASS |
