# PROJECT_STATE — TODARO CORP. TSR-1

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other organizations are used solely as technical and architectural context.

## Current phase
Phase 1 complete (literature review); Phase 2 (ConOps, requirements, parameter register) next.

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
- None yet.

## Major findings
- L-1: NASA officially lists autonomous inspection/maintenance/repair, health management, logistics
  reliability, standard and dust-tolerant interfaces as surface-system gaps (S001).
- L-2: NASA's 2025 architecture added a robotic logistics "Lunar Utility Rover" that could
  "maintain, repair, and service" — direct overlap with TSR-1 (S004, S005). Must be treated as baseline
  competitor.
- L-5: Power interface must be ISPSIS 120 VDC (S011); exchange <100 m at 120 VDC; grid 3 kVAC + UMIC (S012).
- L-6: Reduced-gravity traction penalty (~-20 % DP, +40 % sinkage) must be applied (S043).
- Delivery bounds: Griffin ~0.63 t, Argonaut 1.5 t, Blue Moon Mk1 3.0 t (S047, S056, S057).

## Rejected approaches
- None yet.

## Unresolved issues
- Network egress policy blocks NTRS/nasa.gov/esa.int full text (HTTP 403); research relies on search
  excerpts. Seed NTRS 20260001878 unresolved; seed 20210022361 resolves to NTRS 20220002618.
- No quantitative regolith anchor data, lunar failure-rate data or lander load factors found.

## Repository health
- No tests yet.

# NEXT ACTION
Phase 2: write `engineering/conops.md`, `engineering/assumptions.md`, `requirements/mission_requirements.md`,
`requirements/system_requirements.md`, `requirements/requirements_traceability.csv`, and the parameter
register infrastructure `src/tsr1/common/params.py` exporting `engineering/parameter_register.csv`.
