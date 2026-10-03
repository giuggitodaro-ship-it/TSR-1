# TSR-1 Preliminary FMEA, Single-Point-Failure Analysis and Degraded Modes

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other
> organizations are used solely as technical and architectural context.

Scope: functional/hardware FMEA at ORU level (directive §24). Failure rates are the ESTIMATE values in
`src/tsr1/reliability/tsr_reliability.py` (`lambda_*` in the parameter register); no lunar field data
exist (literature gap L-3). Quantitative roll-up: `simulations/results/tsr_reliability.json`.

**Severity classes**: **1** loss of TSR-1 or hazard to crew/critical asset · **2** loss of a primary
function (mobility, servicing, recovery, emergency power, communication) · **3** degraded function with
work-around · **4** negligible. **R** suffix = redundancy or work-around exists (e.g. 2R).
**Likelihood** (10-yr, per unit, without repair): A > 50 %, B 20–50 %, C 5–20 %, D 1–5 %, E < 1 %.

## 1. FMEA table

| ID | Item | Failure mode | Cause | Local effect | System effect | Detection | Sev | Lik. | Mitigation / design provision | Degraded mode |
|---|---|---|---|---|---|---|---|---|---|---|
| F-01 | Wheel drive actuator (×6) | seizure / motor open | dust ingress past seals, lubricant starvation in cold, winding open | wheel cannot be driven; brake may lock | mobility reduced | current/encoder mismatch, slip estimate | 2R | B (λ 0.03/yr → 26 %/10 yr per unit) | labyrinth + PTFE bellows, BMG/MoS2 dry lubrication, warm start; clutch/free-wheel release of failed brake; ORU-replaceable at wheel hub | 5 of 6 driven: 17.4° slope; 4 of 6: 13.4° (mobility.json) |
| F-02 | Steering actuator (×6) | stuck at angle | as F-01 | wheel scrubs | turning degraded | steer encoder | 3R | C | spring-centring to 0° on power loss; remaining 5 steer; skid-steer fallback | crab/skid steering |
| F-03 | Rocker / bogie pivot | bearing seizure | dust, cold welding | loss of articulation | rough-terrain performance degraded | joint angle telemetry | 3 | D | sealed hybrid bearings, dry film | operate on ≤ 10° smooth terrain |
| F-04 | Body-lowering actuator (×2) | stuck | as F-01 | cannot lower/raise | loss of skid stabilisation; wheel-drive ORU swap harder | encoder | 3 | D | mechanical stop in raised position (fail-to-drive-height) | spades/anchors still available |
| F-05 | Dexterous arm (×2) | joint failure (any of 7) | gear wear, encoder, brake fault | arm loses a DOF or locks | bimanual tasks lost; single-arm servicing continues | joint telemetry, F/T anomaly | 2R | A (λ 0.08/yr → 55 %/10 yr per arm) | two identical arms (TS-03); joint ORU / arm-level ORU at base interface; second arm can assist replacement | single-arm + crane + fixtures (coverage 0.94, TS-03) |
| F-06 | Crane (hoist/luff/slew) | winch or slew drive failure; line damage | dust in sheaves, line abrasion | heavy lift unavailable | ORU > 20 kg handling lost | tension/encoder | 2 | C | line inspection by cameras; spare line on spine; brake fail-safe holds load | dex arm ≤ 20 kg ORUs only |
| F-07 | Winch | drum/brake/level-wind failure | dust, overload | recovery by winch lost | recovery limited to direct tow (p_env 0.27) | load cell, encoder | 2 | C | load limiting at 4 kN; spool guard; ORU-replaceable | direct towing on flat |
| F-08 | Recovery line | abrasion/cut, snap-back | rock edge, overload | line parts | target not recovered; snap-back hazard | tension drop | 2 | C | FoS 5; jacket; tension ramp; keep-out zone in safety layer | spare line (MOD-REC) |
| F-09 | Spade deploy actuator (×2) | stuck deployed/stowed | dust | restraint reduced | lower winch limit (2.6 → ~1.9 kN) | position switch | 3R | D | manual stow via arm; mechanical release pin | anchors only |
| F-10 | Helical anchor | pull-out / refusal on rock | weak soil, clast | restraint lost/not installed | winching aborted at hold point | tension vs displacement, driver torque | 3 | C (case-dependent) | proof-load before use (hold point); relocate; 4 anchors in MOD-REC | reduced envelope (weak soil p_env 0.83) |
| F-11 | Battery module (×4) | cell short / thermal runaway / capacity loss | manufacturing defect, cold charging | module isolated | energy −25 % per module | cell voltage/temperature, BMS | 1→2R | D | PPR design (S070), module-level fusing/isolation, charge only 0–30 °C (S071) | 3/4 modules: range ~−25 %, survival ~138 h |
| F-12 | PCDU converter (3 phases) | converter fail open/short | SEE, overstress | bus capacity reduced | power-limited operations | bus telemetry | 2R | D | 3 interleaved phases (2-of-3 for full load), SSPC isolation | ≤ 2.7 kW bus |
| F-13 | Power-transfer module | failure / isolation fault | SEE, port fault | no charging/emergency power | cannot charge from grid; emergency power lost | insulation monitor | 2 | C | charge fallback via PV (≈166 W); PTM ORU; port interlocks | PV-only charging; no emergency power |
| F-14 | Power tether / connector | contact contamination, cable damage | dust, abrasion, mis-mate | high resistance / no mate | no power transfer | contact resistance check before energising | 2 | C | DTC with self-closing cover (S042); pre-mate brush; spare connector head | keep-alive via MOD-KA (own connector) |
| F-15 | Autonomy computer (HPSC) | hard failure / SEFI | radiation, thermal | high-level autonomy lost | servicing by approved skill scripts only; navigation slow | heartbeat to safety computer | 2 | C | safety computers run minimal navigation and pre-verified skills; ORU-replaceable | teleop-assisted "point-and-go" via MOC; reduced productivity |
| F-16 | Safety/RT computer (×2) | failure | SEE, part failure | one lane lost | none (dual) | cross-check | 1R→2R | D | dual lanes, independent power; second failure → safe hold | single lane, no manipulation near crew |
| F-17 | NavCam / HazCam / IR camera | failure, window obscuration | dust, radiation | perception reduced | slower driving; inspection degraded | image quality metrics | 3R | C | EDS on windows, covers, redundant pairs, arm-mounted macro camera as backup | LiDAR + remaining cameras |
| F-18 | LiDAR (×2) | failure, window dust | as F-17 | 3-D mapping reduced | hazard detection relies on stereo | return statistics | 3R | C | two units (front/rear); stereo fallback | stereo-only, lower speed |
| F-19 | IMU / star tracker | failure | part failure | attitude estimate degraded | navigation degraded | consistency checks | 3R | D | visual odometry + sun sensor + wheel odometry | VO-based navigation |
| F-20 | Comm links (3) | failure / outage | radio failure, terrain shadow, relay outage | link lost | autonomy continues to next hold point (MR-08) | link status | 2R | C (per radio) | three independent paths + DTN; MOD-RPT repeater for PSRs | any one link sufficient |
| F-21 | Loop heat pipe / radiator | blockage, dust coverage | dust, deprime | heat rejection reduced | power-limited operations | WEB temperatures | 2 | D | EDS film; zenith orientation; second heat-pipe path; operational throttling | low-power modes, stop charging at 3 kW |
| F-22 | Survival heaters / thermostats | heater open / stuck on | element failure | cold or energy drain | battery out of limits | PRT readings | 2R | D | redundant heater circuits, dual thermostats with SW override | survive with remaining circuit |
| F-23 | Service-spine latch | jam / fails to release | dust, misalignment | module stuck/unsecured | module unavailable / loose | latch sensors | 3 | D | manual override by arm tool; dust covers | slot disabled |
| F-24 | Software (autonomy) | wrong plan / misclassification | ML error, unmodelled situation | unsafe or wasteful action proposed | potentially damaging contact | deterministic guards, hold points | 1→3 | C | ML advisory only; force/torque/tip-factor guards; approvals at irreversible steps (SR-AUT-02) | safe hold, request human review |
| F-25 | Dust contamination (general) | coating of optics, radiators, mechanisms, connectors | own wheel ejecta, operations near other vehicles | degradation across subsystems | gradual performance loss | trending | 2 | A (certain to occur) | fenders + skirts, EDS, labyrinth seals, covers, cleaning tools usable on itself by peer/arm | scheduled self-cleaning |
| F-26 | Chassis / primary structure | crack | fatigue from thermal cycling, overload | — | loss of vehicle | inspection imagery | 1 | E | FoS 1.25/1.4, fracture control, CTE-compliant joints, load limiting | none (accepted SPF) |
| F-27 | Mast deploy hinge | fails to deploy / stuck | cold, dust | NavCams low | navigation severely degraded | hinge sensor | 2 | E | redundant actuation path, deploy once in daylight at commissioning | arm-mounted cameras |

## 2. Single-point failures (SPF)

| SPF | Effect | Justification for acceptance / mitigation |
|---|---|---|
| Primary structure (F-26) | loss of vehicle | conventional practice: structural SPFs accepted under factor-of-safety and fracture-control discipline |
| Mast hinge (F-27) | navigation degraded, not lost | one-time deployment; arm cameras provide fallback |
| Power-transfer module (F-13) | loss of emergency power and grid charging | PV charging keeps TSR-1 alive; PTM is an ORU (peer/crew swap). A second PTM (+12 kg) was **not** adopted: value model shows TSR outage ≤ 2 % of time at λ = 0.04/yr; revisit in CDR if PTM λ proves higher |
| Crane (F-06) | heavy-ORU handling lost | ≈ 7 % of weighted task content (T02, T03, T10, T11, TS-03); ORU-replaceable |
| Winch (F-07) | recovery capability reduced | direct towing remains for flat-ground cases |
| Thermal loop (F-21) | power-limited operation | low λ; throttling keeps WEB in limits |

No single failure other than primary structure causes loss of mobility on ≤ 17° terrain or loss of the
ability to communicate and safe the vehicle (SR-REL-01).

## 3. Fault trees (qualitative, top events)

**TE-1 Loss of mobility** = (≥ 3 of 6 wheel drives failed) OR (both body-lowering actuators jammed
low) OR (primary structure failure) OR (loss of both safety computers) OR (battery < 2 of 4 modules)
OR (PCDU < 2 of 3 phases). With ORU repair at 30 days and p_spare 0.85, P(TE-1 at 10 yr) ≈ 1 % (Monte
Carlo, `tsr_reliability.json`, `crew_repair.p_capable_10yr` = 0.99 includes all LOST conditions).

**TE-2 Loss of servicing capability** = (both dexterous arms failed) OR (autonomy computer AND both
safety lanes failed) OR TE-1. Single-arm loss is a degraded state, not TE-2.

## 4. Degraded-mode catalogue

| Mode | Trigger | Capability retained | Operational rule |
|---|---|---|---|
| DM-1 five-wheel drive | one drive failed | 17.4° slopes, full servicing | avoid > 15° routes, schedule ORU swap |
| DM-2 four-wheel drive | two drives failed | 13.4° slopes | routes ≤ 10°, peer recovery on standby |
| DM-3 single arm | one dex arm failed | ~94 % weighted task coverage with crane + fixtures | no bimanual tasks without fixture |
| DM-4 no crane | crane failed | ORUs ≤ 20 kg | heavy ORUs deferred |
| DM-5 no winch | winch failed | direct towing only | recovery only on flat, p_env ≈ 0.27 |
| DM-6 no PTM | PTM failed | PV charging only (~166 W) | no emergency power; dispatch MOD-KA by peer |
| DM-7 minimal autonomy | HPSC failed | safety-lane navigation, pre-verified skills | slower, more approvals |
| DM-8 comm-degraded | 2 of 3 links lost | autonomy to next hold point; DTN | defer irreversible steps |
| DM-9 survival | battery low / darkness / fault | survival 184 h full battery; indefinite in sunlight | park sunlit, request recovery |
