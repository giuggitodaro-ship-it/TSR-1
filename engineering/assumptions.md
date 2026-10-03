# TSR-1 Engineering Assumptions Register

Every assumption is an **ENGINEERING ASSUMPTION** unless a source is cited as its basis. Each lists
where it is used and how its uncertainty is handled (range, sensitivity case or Monte Carlo
distribution). Parameter IDs refer to `engineering/parameter_register.csv` (generated from
`src/tsr1/common/params.py`).

| ID | Assumption | Basis / evidence | Used in | Uncertainty treatment |
|---|---|---|---|---|
| A-01 | Operational epoch 2036–2041 (Moon Base Phase 3, Phase-2 infrastructure installed) | S054 phases; directive 10–15-yr window | ConOps, value model, TRL | n/a (scenario) |
| A-02 | Site: Shackleton–de Gerlache connecting-ridge complex with adjacent PSRs | S007, S030 | environment, thermal, comms | PSR excursion case |
| A-03 | Soil (disturbed surface) nominal = Lunar Sourcebook Table 9.14 | S023 | mobility | c 100–1000 Pa; φ 30–46°; k_c, k_φ ×0.5–×2; n 0.8–1.2; K 1.0–2.5 cm (S023 ranges for c, φ; others A) |
| A-03b | Table 9.14 parameters are back-analysed from lunar in-situ data, so the reduced-gravity penalty (S043) is **not** applied in the nominal case but **is** applied in the conservative case (DP ×0.8, sinkage ×1.4) | S023, S043 | mobility, recovery | two-case |
| A-04 | Service-route slopes: ≤ 10° on most routes, ≤ 20° on designated routes, 15–25° for PSR-rim access | S034 (landing regions ≤ 8° at 20 m baseline); S035 VIPER 15/25° | mobility, stability | slope sweep 0–30° |
| A-05 | Launch/landing quasi-static design loads 6 g axial + 3 g lateral (applied simultaneously) | no lander data retrieved (S075) | structures | 4 g / 8 g / 10 g cases |
| A-06 | ≥ 2 charging nodes per 10 km cell provide ISPSIS 120 VDC at ≥ 3 kW (grid via UMIC-type converter) | S011, S012, S054 (Phase-2 grid) | power, ConOps | "no-grid" case (solar-only charging) |
| A-07 | Crew on surface 1 mission/yr × 30 days (baseline) | S054 (Phase 3 extended stays); no schedule published | value model | 0–2 missions/yr |
| A-08 | Serviceable-fault MTBF per asset log-uniform 1–10 yr (baseline 4 yr) | no lunar data (L-3); ISS maintenance burden S049 | value model | Monte Carlo |
| A-09 | Fault-type mix: electrical/ORU 35 %, dust degradation 20 %, communication electronics 15 %, mobility immobilisation (mobile assets only) 15 %, non-serviceable structural/catastrophic 15 % | engineering judgement informed by S022 dust categories, S046 MER | value model | Dirichlet sampling ±50 % |
| A-10 | ORU spare available at base when needed with probability 0.5–0.9 (baseline 0.75) | — | value model | Monte Carlo |
| A-11 | Earth replacement lead time 1–2 yr (baseline 1.5 yr); landing cadence per S054 | S054 (≈ 24 landings over Phase 2) | value model | Monte Carlo |
| A-12 | LTV-class vehicle mass 1.5 t (range 1.0–2.5 t) — no public value found | S036 (800 kg payload class) | recovery Scenario D | sweep |
| A-13 | ORU masses 2–150 kg; ≥ 90 % of ORUs ≤ 50 kg | ISS practice of ORU packaging (S049); engineering judgement | manipulator sizing | sweep 25–200 kg |
| A-14 | An unpowered asset suffers irreversible thermal damage after 24–120 h (baseline 50 h) in darkness | S035 (VIPER ≈ 50 h darkness on full charge) | value model, emergency power | Monte Carlo |
| A-15 | Battery pack specific energy 160 Wh/kg (PPR Li-ion, 2030s) | S070 (150–170 Wh/kg today) | power, mass | 130–200 Wh/kg |
| A-16 | Usable depth of discharge 80 % nominal, 90 % contingency; cycle life ≥ 3000 cycles at ≤ 60 % average DoD | industry practice (L007) | power | 70–90 % |
| A-17 | Drive-train efficiency (motor × gear × controller) 0.70 nominal; DC-DC converter 0.95 | L007; harmonic drive catalogue practice | mobility, power | 0.55–0.80 |
| A-18 | HPSC-class rad-hard processor qualified and available by 2030 | S039 | avionics | fallback: GR740/RAD5545-class (lower performance) |
| A-19 | Communications outage design cases: Earth link ≤ 72 h; local network ≤ 24 h | S073 (≈ 51 % DTE); relays S017/S018 | autonomy, comms | 14-day no-relay case |
| A-20 | Service radius 10 km nominal, 25 km maximum excursion | S054 comm-tower cell ≈ 10 km | ConOps, energy | 5–30 km |
| A-21 | Crew EVA repair of a remote ORU costs 2 crew × 6 h EVA + 2 × 4 h IVA support = 20 crew-h, plus LTV drive time | S049 (ISS EVA practice; secondary EVA:IVA ratio) | value model | 12–40 crew-h |
| A-22 | Structural factors of safety: metallic yield 1.25, ultimate 1.4 (test-verified); composites ultimate 1.4; mechanisms/joints sized at FoS 2.0 on peak operating load | S053 (LITERATURE-RECALL) | structures, manipulators | "no-test" 1.6/2.0 case |
| A-23 | Mass growth allowance by AIAA S-120A category at conceptual maturity: structure 20 %, mechanisms 25 %, electronics 25 %, harness 60 %, battery cells 10 %, thermal 25 %, heritage/COTS units 10 %; plus 15 % system margin on top of MGA | S052 (method; harness 60 % verified), remainder A | mass budget | ±50 % on MGA |
| A-24 | Radiation design TID 10 krad(Si) behind 3 mm Al over 10 yr incl. SPEs; RDM 2 → parts ≥ 20 krad(Si); SEE mitigation mandatory | S033 (GCR 13.2 µGy/h ≈ 0.12 krad/10 yr), L014 (RDM practice) | avionics | 30 krad case |
| A-25 | Micrometeoroid flux scales from S061 (≈ 1.1 impacts m⁻² yr⁻¹ for 10⁻⁶–10 g at the pole) | S061 | structures, dust/MLI | ±factor 2 |
| A-26 | Anchor soil strength from S023 depth table (0–30 cm c = 0.9 kPa, φ = 46°; 30–60 cm c ≈ 3 kPa, φ ≈ 54°), density 1.58–1.74 g/cm³, with strength factor 0.5–1.5 | S023 | recovery | Monte Carlo |
| A-27 | Recovery scenarios: A 300 kg rover on flat; B 450 kg rover on 15°; C 450 kg rover with 0.15 m wheel sinkage; D 1.5 t LTV-class / infrastructure element | S035, S057, A-12 | recovery | mass/slope sweeps |
| A-28 | Inspection/servicing tasks are supervised at task level by humans with ≥ 1 approval per hold point; no joystick control | directive §22; S001 (comm delay) | autonomy | n/a |
| A-29 | Thermal sink temperature for radiators facing zenith at the pole ≈ 4 K sky + terrain view; effective sink 50–100 K | S032; geometry | thermal | 30–150 K |
| A-30 | Lunar regolith dust settles on upward surfaces primarily through TSR-1's own wheel ejecta and nearby operations (rooster tail, S022) | S022 | dust | — |
| A-31 | Robotic and crew task-step success probabilities by interface level L0–L3 (uniform within the stated bounds per step; robotic dexterity factor 0.9–1.0) | no lunar servicing statistics exist; bounds set from interface-design logic (S002, S013, S067 ISS robotic-interface practice for L2/L3; CDR-09) | servicing, value model | per-step uniform ranges; pessimism case ×0.9 (CDR-09) |
| A-32 | Allowable stowed envelope on the delivery lander 4.0 × 2.6 × 2.0 m | no lander user guide retrieved (S075); Mk1/Argonaut-class deck scale | closure GEOM-2..4 | open until lander selection (CDR-16) |
| A-33 | Survival (heater + minimal avionics) power of a parked client asset 40–250 W, log-uniform, nominal 100 W | no survival-power data retrieved for candidate assets; small-rover / infrastructure-box class | MOD-KA sizing (TS-07b), value model | sampled; sensitivity ×1.5 / ×0.67 (CDR-20) |
| A-34 | Time-averaged illumination at a parked asset 0.5–0.92 (nominal 0.75) | upper bound S030 best ridge site at 2 m (0.92); lower bound for infrastructure off the ridges | MOD-KA sizing | sampled |
| A-35 | Longest continuous dark period at a parked asset 24–120 h (nominal 72 h) | S030 (longest darkness 3–5 days at the best-illuminated sites); no site-specific time series used | MOD-KA sizing | sampled |
