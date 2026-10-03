# TODARO CORP. TSR-1 — DESIGN FREEZE V1

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other organizations are used solely as technical and architectural context.

Frozen preliminary configuration after trade studies (`trade_studies/`) and the critical design review (`CRITICAL_DESIGN_REVIEW.md`). Every value cites its derivation: model function, result file, source ID (`research/source_register.csv`) or assumption ID (`engineering/assumptions.md`). Regenerate with `simulations/run_all.py` then `results/build_reports.py`.

**Budget closure:** 46/46 independent closure checks pass (`simulations/results/closure.json`).

## §1 Summary

| Item | Frozen value | Derivation |
|---|---|---|
| Role | autonomous lunar service & recovery rover for distributed infrastructure (not crew transport) | ConOps |
| Operating site / epoch | lunar south pole (Shackleton–de Gerlache ridge complex), ~2036–2041 | A-01, A-02 |
| Delivered mass (charged to lander) | 1,207 kg | design.configuration.build; mass_budget.csv |
| Dry mass allocation (CBE + MGA + 15 % margin) | 1,150 kg | AIAA S-120A method (S052), A-23 |
| Operational mass (incl. 100 kg carried ORUs/modules) | 1,250 kg | mass_budget.csv |
| Payload / spares capacity | 150 kg in 6 spine slots | TS-07 |
| Compatible landers | Argonaut-class (1.5 t) with margin; Blue Moon Mk1-class (3.0 t) | S047, S056; closure MASS-3/4 |
| Design life | 10 years | MR-09 (S036 precedent) |
| Integrated-system TRL | 4 | research/technology_readiness.md |

## §2 Dimensions and mass properties

| Item | Value | Derivation |
|---|---|---|
| Overall length × width (deployed) | 3.60 × 2.40 m | wheelbase + wheel Ø + fenders; track + wheel width |
| Deck height / mast height | 0.90 m / 2.20 m | chassis 0.45 m on 0.45 m clearance |
| Ground clearance | 0.45 m (0.10 m lowered) | TS-01 |
| Wheelbase / track | 2.60 m / 2.00 m | TS-01/02 packaging, GEOM-6 |
| Stowed envelope (mast folded, arms in upright stow) | 3.60 × 2.40 × 1.75 m | closure GEOM-2..4 vs A-32 envelope 4.0 × 2.6 × 2.0 m |
| Deck layout | rear: zenith radiator, full width; middle: service spine 2 × 3 slots; front: crane turntable, mast, arm bases; tools on the chassis front face | design.layout; closure GEOM-5/7/8; fig03 (CDR-21) |
| Centre of mass (stowed, loaded) | x +0.03 m, y +0.01 m, z 0.76 m | Config.com() |
| Static tip-over angles | 59° longitudinal / 52° lateral | stability.envelope.static_tip_angles |
| Mass CBE / predicted | 812 kg / 1,000 kg | mass_budget.csv |
| Mass P50 / P90 (MER + MGA Monte Carlo) | 1,246 / 1,374 kg; P(≤ 1.5 t) = 0.99 | budgets.sensitivity.mass_monte_carlo |

Subsystem predicted masses (CBE + MGA): avionics 30.6 kg; communications 8.4 kg; dust 17.1 kg; harness 73.6 kg; manipulation 92.3 kg; mobility 261.1 kg; power 219.2 kg; recovery 62.6 kg; sensors 21.6 kg; service_spine 17.5 kg; stabilisation 11.3 kg; structure 116.6 kg; thermal 25.8 kg; tools 41.9 kg.

## §3 Mobility

| Item | Value | Derivation |
|---|---|---|
| Architecture | 6-wheel rocker-bogie, body lowering (2 lead-screw actuators), differential lock, all-wheel steering | TS-01 |
| Wheels | 6 × rigid Ti-6Al-4V, Ø0.90 × 0.40 m, 18 grousers × 20 mm | TS-02 |
| Ground pressure / sinkage | 6.64 kPa / 18 mm at 337 N per wheel | terramechanics.solve; S023 limit 7 kPa |
| Max slope (i ≤ 0.4) | 20.7° nominal soil; 15.6° conservative; 10.3° weak bound | vehicle.max_slope; soils S023/S043 |
| Max slope with 1 / 2 drives failed | 17.4° / 13.4° | vehicle.max_slope(failed_wheels) |
| Slope claim (requirement SR-MOB-02) | 20° nominal / 15° conservative; hold 25° | design_values.json |
| Step obstacle / ditch | 0.45 m / 0.4 m (0.5 D conservative rocker-bogie rule) | obstacle_ratio_rb (ESTIMATE) |
| Speed | 0.5 m/s nominal, 1.0 m/s max; effective 1.26 km/h with 70 % motion duty | v_drive_nom, drive_duty, tsr_speed_eff |
| Drive actuator rating | 210 N·m per wheel (soil-limited 168 N·m × 1.25) | configuration._drive_rating |
| Steering torque | 49 N·m per wheel (× MF 2 rating) | configuration (scrub model) |
| Energy per km (traverse incl. hotel loads) | 0.32 kWh/km at 1.26 km/h | budgets.scenarios; LRV k_cal 0.62 |
| Range on one charge (keeping 50 h reserve) | 34 km | run_all energy analysis |
| Direct tow capacity | 0° 766 N; 5° 586 N; 10° 402 N; 15° 215 N; 20° 26 N | vehicle.max_tow_force (nominal soil) |

## §4 Stability

| Case | Tipping factor | CoP margin [m] | Sliding OK |
|---|---|---|---|
| C1 stowed, level | ∞ | 0.99 | yes |
| C1 stowed, 20° longitudinal | ∞ | 0.99 | yes |
| C1 stowed, 20° lateral | 45.38 | 0.74 | yes |
| C1 stowed, 25° longitudinal | 33.51 | 0.97 | yes |
| C1 stowed, 25° lateral | 27.66 | 0.66 | yes |
| C2 crane side lift 150 kg @ 2.56 m, level | 4.93 | 0.68 | yes |
| C2 crane side lift 150 kg @ 2.56 m, 10° lateral, load downhill | 3.94 | 0.56 | yes |
| C3 crane front lift 150 kg | 4.06 | 0.84 | yes |
| C4 dexterous arm extended (front-right) with rated payload | 63.10 | 0.97 | yes |
| C5 both extended same side (worst) | 4.62 | 0.67 | yes |
| C6 towing 200 N on 10° slope | ∞ | 0.99 | yes |
| C7a winch 4.0 kN, fairlead 0.25 m, spades only | 3.00 | 0.99 | yes |
| C7b winch 4.0 kN + spades + 2 front hold-down anchors (80 % preload) | ∞ | 0.99 | yes |
| C7c winch 4.0 kN, fairlead 0.60 m, spades only (rejected) | 1.25 | 0.29 | yes |

Requirement: tipping factor ≥ 1.5 for planned operations (tip_factor_req, TS-04). C7c (0.60 m fairlead) is the rejected design shown for comparison.

## §5 Manipulation

| Item | Value | Derivation |
|---|---|---|
| Architecture | 2 identical 7-DOF dexterous arms + cable-stayed luffing crane boom (heavy arm rejected) | TS-03 |
| Dexterous arm | reach 1.60 m, rated 20 kg (lunar g), tip deflection 1.9 mm, 27.0 kg CBE each | manipulation.arm.size_arm (Ti links) |
| Shoulder torque / rating | 98 / 197 N·m (MF 2) | size_arm |
| Arm move power | 20 W per arm at 5°/s | size_arm |
| Positioning | ≤ 2 mm with visual servoing; 6-axis F/T; tool change ≤ 5 min | SR-MAN-01/03 (DESIGN) |
| Crane | boom 2.6 m (reach 2.56 m), hook load 150 kg, luff tension 751 N, 19.9 kg CBE | manipulation.crane.size_crane |
| Crane stability limit at max reach, 15° side slope | 368 kg (TF 1.5) ≫ 150 kg rating | envelope.crane_capacity_curve |
| Max ORU | 150 kg (crane + arm cooperative); ≤ 20 kg single arm | MR-04 |

## §6 Service spine, tools and interfaces

| Item | Value | Derivation |
|---|---|---|
| Service spine | 6 androgynous slots in a 2 × 3 grid of 0.45 m (0.90 × 1.35 m on the mid-deck), ≤ 40 kg per occupied slot (double-slot modules ≤ 80 kg), ≤ 150 kg total, 120 VDC ≤ 1 kW + Ethernet per slot | TS-07; interfaces II-01; design.layout |
| Service modules | MOD-KA keep-alive (KA-C 1.5 m² / 4 kWh, 73 kg, double slot; ×4 in base inventory, ≤ 2 carried), MOD-ORU cradles, MOD-REC recovery kit, MOD-RPT repeater; MOD-SOL optional; no fluid module | TS-07, TS-07b, CDR-19/20 |
| Keep-alive inventory rule | n_KA = Poisson 95th percentile of f_park · p_KA · F · T_hold (fault rate F; f_park ≈ 0.14; T_hold ≈ 1–2 yr) | value_model.keepalive_inventory; capacity_study.json |
| Tools (12) | gripper, socket driver (≤ 50 N·m), electrical probe, connector tool, dust brush, EDS wand, anchor driver, OTCM adapter, androgynous adapter, slings, shackle/hitch, regolith scoop | engineering/subsystem_specs/tools.md |
| Interfaces | ISPSIS 120 VDC power port; ISO 9409-1/IERIIS tool interface + adapters; LunaNet/DTN data | engineering/interfaces.md |

## §7 Recovery

| Item | Value | Derivation |
|---|---|---|
| Winch | 4 kN line pull, 50 m Vectran line, 0.05 m/s, 308 W, fairlead 0.25 m | recovery.towing.size_winch; fairlead_height |
| Ground reaction | 2 rear spades 0.6 × 0.3 m + 2 helical anchors Ø0.15 m @ 0.6 m (924 N each) + 2 spare in MOD-REC; restraint 5.9 kN (P50 soil), 3.9 kN (half strength) | recovery.towing |
| Recovery envelope (15°, FoS 1.5) | free-rolling ≤ 4.8 t; brakes locked ≤ 2.3 t | trades.recovery_trades.recovery_curves |
| P(sampled immobilisation case recoverable) | 0.92 (range 0.77–0.96 over resistance bounds; 0.84 in half-strength soil) | envelope_probability |
| Scenario outcomes | A: OK (margin 8.81); B: OK (margin 10.78); B2: OK (margin 5.12); C: OK (margin 1.07); C-hi: NOT feasible (margin 0.52); C-dig: OK (margin 4.58); D: OK (margin 1.55); D2: OK (margin 4.08); D3: OK (margin 3.32) | recovery.scenarios |

## §8 Power

| Item | Value | Derivation |
|---|---|---|
| Battery | Li-ion PPR, 23.6 kWh nameplate (28s67p, 1876 cells, 101 V nom.), 15 kWh usable at EOL, 148 kg | power.electrical.size_battery; A-15/16 |
| Bus | regulated 120 VDC (ISPSIS) primary, 28 VDC avionics; PCDU 4 kW, 3 interleaved phases | S011; TS-06 |
| Power-transfer module | isolated bidirectional, single stage on battery, 3 kW continuous / 4.5 kW 60 s; 25 m tether 2 × 6.9 mm² Cu | S012; power.electrical.size_cable |
| Emergency power at 10 km edge | 10.6 h at 300 W keep-alive or 1.4 h at 3 kW; MOD-KA for longer | run_all energy analysis |
| Solar | 1.5 m² fixed vertical PV, 166 W average in sunlight | budgets.scenarios.solar_avg_w |
| Survival power / full-battery survival | 82 W / 183 h darkness; indefinite in sunlight | thermal + power closure |
| Mode powers [W] | dormant 60, comm_standby 75, driving 471, inspection 242, manipulation 391, heavy_manip 301, recovery_winch 365, emergency_power 110, charging 74, survival 82, safe 136 | power_budget.csv |

## §9 Thermal

| Item | Value | Derivation |
|---|---|---|
| Concept | MLI-insulated WEB (1.0 × 0.8 × 0.35 m) in chassis; zenith radiator with OSR + EDS film; LHP with thermal switch | thermal.lumped |
| Radiator | 1.64 m² for 380 W at 293 K with dusty α (×2.0) and 12° solar incidence | radiator_area |
| Cold-case leak / heater | 82 W leak (PSR sink 40 K) / 63 W heaters | cold_leak |
| Max WEB dissipation | 350 W steady (≤ 380 W); 3 kW transfer transient within ΔT ≤ 15 K | closure THERMAL-1a/b |
| PSR excursion | ≤ 8 h (energy-limited 19 h, × 0.5 margin, cap 8 h) | run_all |
| Actuator thermal policy | cold-tolerant actuators (no survival heat); warm-start heaters only for heavy-duty drives | TG-01 |

## §10 Avionics and sensors

| Item | Value | Derivation |
|---|---|---|
| Autonomy computer | HPSC-class rad-hard (100 krad TID part, SEL-immune), 45 W active | S039; A-18, A-24 |
| Safety/RT computers | 2 independent rad-hard lanes, 10 W each, deterministic guards | SR-AVI-01 |
| Sensors | mast NavCam stereo (70° FOV) + pan-tilt + LEDs; 6 HazCams; front/rear LiDAR; thermal IR; arm macro camera; 2 wrist F/T; LN-200S IMU; sun sensor/star tracker; electrical diagnostic unit; contact vibration sensors; no acoustic sensors | SR-SNS-01; S064, S065 |
| Radiation design | TID 10 krad(Si)/10 yr (GCR alone ≈ 0.12 krad), RDM 2 → parts ≥ 20 krad; SEE mitigation | S033; A-24 |

## §11 Autonomy and safety

Layered: mission planner → task planner → verified skills → motion planning → real-time control → actuators; independent deterministic safety layer; ML advisory only; human approval at hold points (power connection, load-path fastener release, ORU insertion, winch > 1 kN). Crew-proximity limits 0.2 m/s and 50 N (SR-SAF-01). Comm-outage behaviour: continue to next hold point, then safe hold (MR-08). Details: `trade_studies/autonomy.md`.

## §12 Communications and navigation

Surface network radio (LTE-class), LunaNet S-band relay (5 W, 10 dBi; ≈ 407 kbit/s at 10 000 km), UHF peer mesh, DTN; availability ≈ 0.98. Navigation: visual odometry + IMU + star tracker + LiDAR map matching; base-frame ≤ 1 m; relative pose before contact ≤ 5 mm / 0.5°.

## §13 Dust mitigation

Self-protection: fenders + skirts (Apollo lesson S022), zenith radiator with EDS film, EDS on camera/LiDAR windows, labyrinth + PTFE bellows on all external joints (no dynamic elastomers), dust-tolerant connector with self-closing cover, latch covers. External cleaning: brush and EDS wand tools; target residual coverage ≤ 5 % (MR-07).

## §14 Structure and materials

Closed Al 7075-T7351/Al 5056 honeycomb torque box 2.6 × 1.5 × 0.45 m (equivalent wall 1.0 mm, f₁ = 41 Hz on launch locks, minimum-gauge driven), Ti-6Al-4V hard points; Ti-6Al-4V wheels and arm links; CFRP crane boom and mast; Vectran recovery line. Launch loads 6 g axial + 3 g lateral (A-05), FoS 1.25/1.4 (A-22). Full matrix: `engineering/materials_matrix.csv`.

## §15 Mission performance (design-reference missions at the 10 km service edge)

| DRM | Title | Duration [h] | Distance [km] | Energy [kWh] (no PV) | Energy with PV [kWh] | Peak [W] |
|---|---|---|---|---|---|---|
| DRM-1 | Routine inspection patrol | 20.4 | 20.0 | 7.42 | 5.73 | 402 |
| DRM-2 | Electrical failure: emergency power + ORU replacement | 22.9 | 20.0 | 10.05 | 8.15 | 707 |
| DRM-3 | Dust contamination of solar array / radiator | 11.9 | 10.0 | 4.61 | 3.62 | 402 |
| DRM-4 | Immobilized rover recovery (450 kg, 10° slope) | 20.3 | 16.2 | 7.89 | 6.21 | 602 |
| DRM-5 | Communication node electronics replacement | 19.9 | 20.0 | 8.11 | 6.46 | 512 |
| DRM-6 | Heavy ORU exchange (100 kg battery module of a power node) | 9.1 | 6.0 | 3.23 | 2.48 | 402 |

Battery usable at EOL 15 kWh; reserve retained 4.09 kWh (50 h survival).

## §16 Reliability and lifetime

Expected repairable faults 1.26 per year; P(servicing-capable at 10 yr) = 0.99 with 30-day ORU repair (peer: 0.99; no repair: 0.59); fully functional 41 % of the time. FMEA and degraded modes: `engineering/fmea.md`.

## §17 System-level value (30 assets, 10 years, epistemic Monte Carlo)

| Metric | Without TSR-1 (mean) | With TSR-1 (mean) | Difference P10 / P50 / P90 |
|---|---|---|---|
| Infrastructure availability | 0.685 | 0.763 | 1.8 / 7.0 / 14.5 pp |
| Preventable asset losses (excl. non-serviceable faults) | 21.7 | 8.9 | — |
| Assets lost, all causes | 31.6 | 21.3 | — |
| Fault events (grow with uptime) | 65 | 81 | — |
| Earth-supplied mass [t] | 13.0 | 9.5 | — |
| Earth mass per available asset-year [kg] | 70 | 46 | — |
| Crew EVA [crew-h] | 786 | 697 | — |
| Mean response time [h] | — | 26.8 | — |
| TSR-1 utilisation | — | 1.5 % | — |

Logistics break-even (Earth mass avoided = TSR-1 life-cycle mass 1.65 t incl. 4 MOD-KA): ≈ 12 serviceable assets. Losses from non-serviceable faults are not preventable and grow with operating exposure (a kept-alive asset can fail again), so preventable losses and mass per available asset-year are the fair comparison (CDR-19).

## §18 Changes from the pre-CDR configuration

| Item | Pre-CDR | Frozen | Reason |
|---|---|---|---|
| Battery usable EOL | 14 kWh | 15 kWh | CDR-06: ENERGY-1 failed after survival-heater correction |
| Delivered mass | 1192 kg | 1207 kg | battery change |
| Slope requirement | nominal soil only | 20° nominal / 15° conservative | CDR-15 |
| MOD-KA keep-alive module | 2 kWh, 0.75 m² PV, 23 kg (placeholder) | KA-C 1.5 m² / 4 kWh, 73 kg, double slot | CDR-20: placeholder physically inconsistent; sustains only ≈ 40 % of assets |
| MOD-KA inventory | 2 | 4 (scaling rule) | CDR-19: capacity study |
| Value-model loss accounting | failed TSR-1 attempt = immediate loss | crew may still attempt within survival/abandonment time | CDR-19 (consistency with the no-TSR baseline) |
