# Changelog

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other
> organizations are used solely as technical and architectural context.

Study baseline date: 2026-10-03. Entries list what changed in the engineering content and why; the git history
holds the file-level detail.

## v1.0 — design freeze, capacity study, paper

### Added
- Capacity study (`simulations/capacity_study.py`, CDR-19): fault load × number of TSR-1 units × keep-alive
  inventory, with fault-exposure-normalised metrics (preventable losses, Earth mass per available asset-year).
- Keep-alive module sizing and option × inventory trade (TS-07b, CDR-20); MOD-KA specification sheet.
- Keep-alive inventory rule `value_model.keepalive_inventory` (Little's law + Poisson 95th percentile).
- Assumptions A-31 (task-step success), A-32 (stowed envelope), A-33..A-35 (parked-asset survival power, site
  illumination, dark period). A-31 and A-32 were already used in the code but missing from the register.
- Figure fig22 (capacity study); fig18 split into four single-measure panels.
- `simulations/build_all.py` (one-command rebuild), `simulations/README.md`, `paper/build_bib.py`,
  `paper/build_paper.py`, `paper/paper.md`, `paper/references.bib`.
- Tests for the inventory rule, MOD-KA sizing and value-model loss accounting.

### Changed
- MOD-KA keep-alive module: 2 kWh / 0.75 m² / 23 kg placeholder → KA-C 4 kWh / 2 × 1.5 m² / ≈ 73 kg double-slot
  module. The placeholder was physically inconsistent (2 kWh usable needs ≈ 20 kg of cells) and sustained only
  ≈ 40 % of plausible assets.
- MOD-KA base inventory 2 → 4 at the 30-asset reference base, scaled with the inventory rule.
- Deck layout (CDR-21): one definition (`src/tsr1/design/layout.py`) now drives component positions, crane base,
  closure checks and fig03. Radiator full width at the rear; spine as a 2 × 3 grid of 0.45 m slots mid-deck (the
  pre-review 1.6 × 0.5 m spine could not hold six 0.45 m slots and overlapped the radiator); crane turntable, mast
  and arm bases in the front strip; tools on the chassis front face; arms stow upright (stowed height 1.75 m);
  WEB moved 0.5 m aft under the radiator after the forward shift pushed MOB-1 to 7.37 kPa (failed).
- Closure: GEOM-4 uses the computed stowed height; GEOM-5 checks containment and non-overlap instead of area;
  new GEOM-7 (radiator capacity with boom shading) and GEOM-8 (crane reach to every slot).
- Spine interface II-01: ≤ 40 kg per occupied slot; double-slot modules ≤ 80 kg.
- Value model: a failed TSR-1 recovery or repair no longer means immediate loss when crew could still act within
  the survival or abandonment time (the no-TSR baseline already allowed this); keep-alive success now depends on
  the module's probability of sustaining the asset (`ka_sustain_p`, calculated from TS-07b).
- TSR-1 life-cycle mass uses the computed MOD-KA mass.
- All value-model sub-studies share the reference seed (common random numbers across studies); before, different
  seeds drew different epistemic samples (e.g. mean asset MTBF 3.5 vs 4.0 yr) and shifted absolute ΔA by ≈ 1 pp
  between tables.
- Sensitivity: the DRM-2 energy tornado rebuilds the configuration (drive efficiency had been frozen at build time
  and showed zero swing); Wong–Reece c₁/c₂ are read at call time (they were import-time constants and showed zero
  swing on gradeability).
- Figures: footer placed below all artists; stale hand-typed values removed (fig01 battery, fig11 usable-energy
  line was drawn for 14 kWh); overlapping titles, legends and labels fixed in fig02/03/05/09/12/13/14/15/16/18/19/22.
- Reports quote preventable losses and mass per available asset-year next to total losses and total mass.

## v0.6 — critical design review (commit 012cdd6)
- CDR-01..CDR-18. Design changes: battery 14 → 15 kWh usable at end of life (closure ENERGY-1 failed after the
  survival-heater correction); slope requirement split into nominal 20° / conservative 15°; service radius tied to
  demonstrated effective speed; host-agnostic service-and-recovery kit variant.
- Rejected: asymmetric heavy arm (replaced by crane boom), towing as primary slope recovery (replaced by anchored
  winch), high fairlead, deep spades, outriggers, fluid-servicing module, RPS baseline, joystick teleoperation.

## v0.5 — trade studies, budgets, value model (commit 012cdd6)
- TS-01..TS-10; mass/power/energy/thermal budgets; 44 closure checks; discrete-event value model; component
  specifications; FMEA; interfaces; materials matrix; TRL register; figures fig01–fig21.

## v0.3 — engineering models (commit a602ef3)
- Terramechanics, vehicle, stability, arm/crane, recovery, power, thermal, structure models with tests.

## v0.2 — need, ConOps, requirements (commit 62b19a5)
- ConOps, assumptions A-01..A-30, requirements generator, parameter register, environment model.

## v0.1 — literature review (commits 4a5bd0e, 6237e94)
- Repository skeleton, source register (97 sources with access labels), literature review, programme context.
