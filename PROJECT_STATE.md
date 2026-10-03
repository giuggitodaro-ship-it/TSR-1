# PROJECT_STATE — TODARO CORP. TSR-1

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other organizations are used solely as technical and architectural context.

## Current phase
**Phase 7 complete — final deliverables produced and internally consistent.** The project has passed all quality
gates of directive §51 and produced all final deliverables of §52 (checklists below). Branch:
`claude/happy-feynman-043306`. Study baseline date: 2026-10-03.

## Completed work (by phase)
| Phase | Content | Key outputs |
|---|---|---|
| 0 | repository skeleton, state file | `README.md`, `PROJECT_STATE.md`, `.gitignore` |
| 1 | literature review (search excerpts; agency servers blocked) | `research/` (97 sources with access labels, search log, review, programme context) |
| 2 | need, ConOps, assumptions, requirements generator, parameter register, environment model | `engineering/conops.md`, `engineering/assumptions.md` (A-01..A-35), `requirements/` (48 requirements, 0 open) |
| 3 | physics models with tests | `src/tsr1/` (terramechanics, vehicle, stability, arm, crane, recovery, power, thermal, structure, design layout, configuration, budgets, reliability, value model) |
| 4 | ten formal trade studies | `trade_studies/*.md` (generated), `src/tsr1/trades/` |
| 5 | budgets, closure, specs, FMEA, interfaces, materials, TRL | `engineering/*`, `engineering/subsystem_specs/` (29 sheets + tool table), `research/technology_readiness.md` |
| 6 | figures, adversarial review, design freeze, verdict | `figures/` (fig01–fig22), `CRITICAL_DESIGN_REVIEW.md` (CDR-01..CDR-21), `DESIGN_FREEZE_V1.md`, `results/*.md` |
| 7 | capacity study, keep-alive module redesign, deck layout, paper, final consistency gate | `simulations/capacity_study.py`, `src/tsr1/design/layout.py`, `paper/paper.md`, `paper/references.bib`, `CHANGELOG.md`, `simulations/README.md`, `simulations/build_all.py` |

## Files created (generated files are rebuilt by `simulations/build_all.py`)
- Generators: `simulations/run_all.py`, `simulations/capacity_study.py`, `simulations/build_all.py`,
  `figures/make_figures.py`, `engineering/build_specs.py`, `engineering/build_materials_matrix.py`,
  `trade_studies/build_trade_docs.py`, `results/build_reports.py`, `requirements/build_requirements.py`,
  `paper/build_bib.py`, `paper/build_paper.py`.
- Generated: `simulations/results/*`, `engineering/{parameter_register,mass_budget,power_budget,materials_matrix}.csv`,
  `engineering/subsystem_specs/*.md`, `requirements/*`, `trade_studies/*.md`, `DESIGN_FREEZE_V1.md`,
  `CRITICAL_DESIGN_REVIEW.md`, `results/*.md`, `figures/*.png`, `paper/figures/*.png`, `paper/paper.md`,
  `paper/references.bib`.
- Hand-written: `README.md`, `PROJECT_STATE.md`, `CHANGELOG.md`, `research/*`, `engineering/{conops,architecture,
  assumptions,fmea,interfaces}.md`, `docs/*`, `simulations/README.md`, `simulations/configs/run_config.json`.

## Simulations completed (full run, seeds in `simulations/configs/run_config.json`)
Mobility (Wong–Reece/Bekker, LRV calibration), stability (C1–C7c), recovery (scenarios A–D3, envelope
probability over 400 sampled cases), power/energy/thermal (11 modes, 6 DRMs), TSR-1 self-reliability, servicing
success by level, value-model Monte Carlo (400 replicates at 30 assets; asset sweep 3–60 with per-base keep-alive
inventory; level mixes; crew presence; keep-alive inventory; two TSR-1), CDR analyses (robot skill, shared host,
speed → radius, service kit), capacity study (5 fault loads × 1/2 rovers × 2/4/8 keep-alive modules), keep-alive
module option × inventory trade, tornado sensitivities (slope, mass, DRM-2 energy, recovery), mass Monte Carlo,
46 closure checks (**46/46 pass**).

## Major findings (final values; source files in `simulations/results/`)
- Frozen design: delivered **1207 kg** (operational 1250 kg; P(≤ 1.5 t) 0.99); six-wheel rocker-bogie with body
  lowering; Ø0.90 × 0.40 m Ti wheels; two 7-DOF dexterous arms (20 kg) + 150 kg cable-stayed crane; 15 kWh usable
  EOL battery; 3 kW ISPSIS 120 VDC power-transfer module; 4 kN winch + 2 spades + 2 helical anchors; 6-slot spine.
- Gradeability 20.7° nominal / 15.6° conservative / 10.3° weak soil (17.4° / 13.4° with one / two drives failed);
  slope is soil-limited, so suspension choice is driven by servicing, not gradeability.
- Heavy service arm rejected (158 kg vs 45 kg for arm + crane); towing rejected for slopes: P(recoverable) 0.27
  direct tow vs **0.92** anchored winch (0.84 in half-strength soil). Anchors are TRL 3.
- Value at 30 assets, 10 yr: availability 0.685 → 0.763 (ΔA P10/P50/P90 1.8/7.0/14.5 pp); preventable losses
  21.7 → 8.9; Earth mass 13.0 → 9.5 t (70 → 46 kg per available asset-year); EVA 786 → 697 crew-h (modest);
  logistics break-even ≈ 12 assets (TSR-1 life-cycle mass 1647 kg incl. 4 MOD-KA).
- Standardisation decides value: ΔA 2.9 pp (legacy L0-heavy) vs 13.3 pp (standardised L2/L3).
- Keep-alive power is the core function; keep-alive modules buy losses and mass, not availability. MOD-KA resized to
  KA-C (4 kWh, 2 × 1.5 m² PV, 72.6 kg, P(sustain) 0.76); inventory by Little's-law rule (4 at 30 assets, 6 at 60).
- One TSR-1 does not saturate on driving/servicing time even at 60 faults/yr; a second unit halves response time but
  barely reduces losses. A host-mounted service kit (≈ 352 kg) is preferable where a utility-rover host can respond
  within asset survival time (CDR-01).
- Verdict: **FEASIBLE WITH IDENTIFIED TECHNOLOGY DEVELOPMENT — conditionally justified**
  (`results/FEASIBILITY_VERDICT.md`). Integrated TRL 4.

## Rejected approaches (kept on record in `CRITICAL_DESIGN_REVIEW.md`)
Asymmetric heavy arm; towing as primary slope recovery; 0.60 m winch fairlead; 0.4 m spades; outriggers; active/4-wheel
suspensions; fluid-servicing module; RPS baseline; Earth joystick teleoperation; second TSR-1 for capacity; 23 kg /
2 kWh keep-alive module; total losses as value metric; 6-slot spine in a 1.6 × 0.5 m strip over the radiator.

## Corrections made in the final phase (see `CHANGELOG.md`)
- CDR-19: value-model exposure artefact (preventable losses, mass per asset-year) and failed-attempt handling.
- CDR-20: MOD-KA placeholder physically inconsistent → KA-C, double-slot, success probability in the value model.
- CDR-21: deck layout did not fit → `design/layout.py`; MOB-1 failed after the forward CoM shift (7.37 kPa) and was
  fixed by moving the WEB 0.5 m aft; closure GEOM-4/5/7/8 now geometric.
- Sensitivity artefacts fixed: DRM-2 tornado now rebuilds the configuration (drive efficiency was frozen at build
  time); Wong–Reece c₁/c₂ read at call time (were import-time constants).
- Stale hand-typed numbers in figures/specs replaced by values read from results (battery 14 → 15 kWh in fig01/fig11,
  survival power, spine saving, recovery fractions, degraded-mode slopes).

## Unresolved issues (all recorded; none blocks completion)
- Evidence access: NTRS/nasa.gov/esa.int full texts blocked (HTTP 403); sources are excerpt-based (`docs/limitations.md`).
- Open questions OQ-01..OQ-15 (`results/open_questions.md`), technology gaps TG-01..TG-09 (`docs/technology_gaps.md`).
- No lunar data for asset fault rates, regolith anchor capacity, parked-asset survival power or lander loads.

## Quality gates (directive §51) — all met
| Gate | Evidence |
|---|---|
| requirements exist | `requirements/` (48, 0 open) |
| source register exists | `research/source_register.csv` (97) |
| major parameters traceable | `engineering/parameter_register.csv` (190 parameters with provenance and range) |
| trade studies complete | `trade_studies/` TS-01..TS-10 + TS-07b |
| mass / power budgets close | closure MASS-1..5, POWER-1..3 |
| mobility, recovery, stability, reliability/value models run | `simulations/results/*.json` |
| uncertainty analysis exists | `sensitivity.json`, value Monte Carlo, mass Monte Carlo |
| critical design review complete | `CRITICAL_DESIGN_REVIEW.md` CDR-01..CDR-21 |
| contradictions resolved | documents generated from one result set; hand-written docs synchronised (this phase) |
| major code tests pass | `PYTHONPATH=src pytest -q` → 41 passed |

## Final deliverables (directive §52)
1 `README.md` · 2 `PROJECT_STATE.md` · 3 `DESIGN_FREEZE_V1.md` · 4 `results/FINAL_SPECIFICATIONS.md` ·
5 `results/EXECUTIVE_SUMMARY.md` · 6 `results/FEASIBILITY_VERDICT.md` · 7 `CRITICAL_DESIGN_REVIEW.md` ·
8 `engineering/subsystem_specs/` · 9 `engineering/materials_matrix.csv` · 10 `engineering/mass_budget.csv` ·
11 `engineering/power_budget.csv` + DRM energies in `simulations/results/energy_power_thermal.json` ·
12 `requirements/requirements_traceability.csv` · 13 `engineering/fmea.md` · 14 `trade_studies/` ·
15 `src/tsr1/`, `simulations/` · 16 `tests/` · 17 `simulations/results/` · 18 `figures/`, `paper/figures/` ·
19 `research/source_register.csv` · 20 `paper/paper.md` + `paper/references.bib` · 21 `docs/development_roadmap.md` ·
22 `docs/VISUAL_RENDER_SPEC.md` · 23 `results/open_questions.md`.

## Repository health
- `PYTHONPATH=src pytest -q` → **41 passed**.
- `PYTHONPATH=src python simulations/build_all.py` → full rebuild ≈ 10 min; last run: 46/46 closure checks pass,
  48 requirements / 0 open, 190 parameters, paper 29 sections / 63 cited sources.

# NEXT ACTION
The project is complete. A future session should only act on new input. If asked to change an assumption or the
design: edit the model or `simulations/configs/run_config.json`, run `PYTHONPATH=src pytest -q` and
`PYTHONPATH=src python simulations/build_all.py`, re-read the regenerated `CRITICAL_DESIGN_REVIEW.md`,
`results/FEASIBILITY_VERDICT.md` and `paper/paper.md` for changed conclusions, synchronise the hand-written
documents listed under "Files created", update `CHANGELOG.md` and this file, then commit and push to
`claude/happy-feynman-043306`. If network access to NTRS/nasa.gov/esa.int becomes available, re-verify the
EXCERPT and LITERATURE-RECALL sources in `research/source_register.csv` first (OQ-12).
