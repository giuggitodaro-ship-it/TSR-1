# PROJECT_STATE — TODARO CORP. TSR-1

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other organizations are used solely as technical and architectural context.

## Current phase
Phase 3 (numerical models) — core models implemented and tested; trade-study drivers, run_all and figures next.

## Completed work
- Phase 0: repository structure, README, PROJECT_STATE.
- Phase 1: literature review via search excerpts (~88 queries). 97 sources registered
  (`research/source_register.csv`), raw evidence in `research/search_log.md`, synthesis in
  `research/literature_review.md`, programme context in `research/nasa_esa_context.md`.

## Files created
- `.gitignore`, `PROJECT_STATE.md`, `README.md`
- `research/search_log.md`, `research/source_register.csv`, `research/literature_review.md`,
  `research/nasa_esa_context.md`

## Simulations completed
- Exploratory runs only (terramechanics, vehicle, arm/crane, recovery, power, thermal, chassis, value MC,
  TSR self-reliability, DRM energy, stability cases). Canonical runs to be produced by
  `simulations/run_all.py` (not yet written).

## Major findings
- L-1: NASA officially lists autonomous inspection/maintenance/repair, health management, logistics
  reliability, standard and dust-tolerant interfaces as surface-system gaps (S001).
- L-2: NASA's 2025 architecture added a robotic logistics "Lunar Utility Rover" that could
  "maintain, repair, and service" — direct overlap with TSR-1 (S004, S005). Must be treated as baseline
  competitor.
- L-5: Power interface must be ISPSIS 120 VDC (S011); exchange <100 m at 120 VDC; grid 3 kVAC + UMIC (S012).
- L-6: Reduced-gravity traction penalty (~-20 % DP, +40 % sinkage) must be applied (S043).
- Delivery bounds: Griffin ~0.63 t, Argonaut 1.5 t, Blue Moon Mk1 3.0 t (S047, S056, S057).
- M-1 (models): Wong-Reece model with Lunar Sourcebook soil over-predicts LRV energy; k_cal = 0.62.
- M-2: slope capability is traction-limited (~19 deg nominal / ~14 deg conservative for a 1.1-1.4 t 6-wheeler,
  40 % slip); friction angle is the dominant sensitivity.
- M-3: direct towing up 15 deg is ~infeasible (<= 0.2 kN); anchored winching (braked wheels + 2 spades + 2
  helical anchors) gives ~5-6 kN restraint -> ~20x recoverable mass on slopes.
- M-4: heavy serial arm (150 kg @ 2.3 m) ~133 kg vs cable-stayed crane ~20 kg -> dex arm + crane favoured.
- M-5: winch pull 4 kN = 2.3x TSR lunar weight; fairlead 0.60 m pitches the vehicle over (TF 0.98);
  fairlead 0.25 m + front hold-down anchors required.
- M-6: robotic ORU success L0 ~0, L1 ~0.12, L2 ~0.78, L3 ~0.96 (task-step model, assumptions).
- M-7: keep-alive power modules materially reduce asset losses in the value model.
- M-8: DRM-2 at 10 km needs ~9.7 kWh + 3.8 kWh reserve -> battery >= 14 kWh usable EOL.

## Rejected approaches
- None yet.

## Unresolved issues
- Network egress policy blocks NTRS/nasa.gov/esa.int full text (HTTP 403); research relies on search
  excerpts. Seed NTRS 20260001878 unresolved; seed 20210022361 resolves to NTRS 20220002618.
- No quantitative regolith anchor data, lunar failure-rate data or lander load factors found.

## Repository health
- `PYTHONPATH=src pytest -q` → 36 passed (tests/test_terramechanics.py, test_stability_manipulation.py,
  test_recovery_power_thermal.py, test_system_models.py).

# NEXT ACTION
Write `src/tsr1/trades/` drivers for the 10 trade studies (mobility, wheel, manipulator, stabilization,
recovery, energy, service module, comms, autonomy, structural materials) using `design.configuration.build`
and the physics models; then `simulations/run_all.py` (writes `simulations/results/*.json|csv`,
`simulations/results/design_values.json`, exports parameter register, regenerates requirements) and
figures. Then write trade_studies/*.md from the results.
