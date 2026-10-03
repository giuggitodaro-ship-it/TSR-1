# TSR-1 simulations

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other
> organizations are used solely as technical and architectural context.

All quantitative results in the repository are produced by the scripts in this directory from the models in
`src/tsr1/` and the configuration in `configs/run_config.json`. Every stochastic analysis is seeded, so a rerun
on the same code reproduces the same numbers.

## How to reproduce

```
pip install numpy scipy pandas matplotlib pytest
PYTHONPATH=src pytest -q                                  # calculation tests
PYTHONPATH=src python simulations/build_all.py            # everything: results, figures, documents, paper
PYTHONPATH=src python simulations/build_all.py --quick    # reduced Monte Carlo sizes (smoke test, ≈ 3 min)
PYTHONPATH=src python simulations/run_all.py              # results only (≈ 6 min)
PYTHONPATH=src python simulations/capacity_study.py       # capacity study only (also run by run_all.py)
```

`build_all.py` runs, in order: `run_all.py` → `figures/make_figures.py` → `engineering/build_materials_matrix.py`
→ `engineering/build_specs.py` → `trade_studies/build_trade_docs.py` → `results/build_reports.py` →
`paper/build_bib.py` → `paper/build_paper.py`. Documents are generated from the result files, so they cannot
contradict the models.

## Configuration (`configs/run_config.json`)

| Block | Content |
|---|---|
| `baseline_options` | the frozen TSR-1 configuration (`design.configuration.Options`) |
| `value_model` | reference base size (30 assets), MOD-KA inventory (`"rule"` → `value_model.keepalive_inventory_for_base`, 4 at 30 assets), asset-count sweep (inventory scaled per base), TSR-1 spares mass per year |
| `seeds` | random seeds for the value, recovery and mass Monte Carlo analyses |
| `full` / `quick` | Monte Carlo sample sizes for the full run and the smoke test |
| `cdr` | critical-design-review cases: robot skill factors, shared-host cases, effective speeds |

## Analyses performed by `run_all.py`

| Section | Model(s) | Output |
|---|---|---|
| Baseline configuration | `design.configuration.build` (mass, CoM, power by mode) | `baseline_summary.json`, `engineering/mass_budget.csv`, `engineering/power_budget.csv` |
| Mobility | Wong–Reece/Bekker wheel model, vehicle slope/tow, LRV energy calibration | `mobility.json` |
| Stability | static tip-over/sliding cases C1–C7c, crane capacity curve | `stability.json` |
| Recovery | spade/anchor capacity, recovery scenarios A–D3, envelope probability | `recovery.json`, `recovery_scenarios.csv` |
| Power, energy, thermal | DRM-1..DRM-6 energy, battery, tether, survival, radiator, WEB dissipation | `energy_power_thermal.json` |
| TSR-1 self-reliability | ORU failure/repair Monte Carlo | `tsr_reliability.json` |
| Servicing success | task-step model by interface level L0–L3 | `servicing_success.json` |
| Value model | discrete-event Monte Carlo of a distributed base with/without TSR-1 (common random numbers) | `value_model.json`, `value_mc_base.npz`, `value_asset_sweep.csv` |
| CDR analyses | skill factor, shared host, speed → radius, service kit | `cdr_analyses.json` |
| Capacity study | fault load × 1/2 TSR-1 × 2/4/8 keep-alive modules (CDR-19) | `capacity_study.json/.csv` |
| Trade studies | TS-01..TS-10 incl. TS-07b keep-alive module sizing | `trades.json`, `trade_*.csv` |
| Sensitivity | tornado (slope, mass, DRM energy, recovery), mass Monte Carlo, value correlations | `sensitivity.json` |
| Closure | 44 independent budget-closure checks (directive §44) | `closure.json` |
| Requirements | design values → requirement text and traceability | `design_values.json`, `requirements/` |
| Parameter register | every registered parameter with provenance and range | `engineering/parameter_register.csv` |

`results/pre_cdr/` holds the snapshot taken before the critical design review; `results/build_reports.py` uses
it to document what the review changed.

## Common random numbers

Every value-model sub-study (asset sweep, level mixes, keep-alive inventory and options, crew presence, two rovers,
CDR cases) reuses the reference seed, so replicate k draws the same epistemic scenario everywhere and rows of
different tables are paired. With and without TSR-1 are also simulated on the same asset fault histories. The
standard error of a mean ΔA is ≈ 0.3 pp (400 replicates) to ≈ 0.4 pp (200 replicates).

## Value-model metrics

* **ΔA** — change in 10-year mean infrastructure availability (performance-weighted uptime).
* **Preventable losses** (`plost`) — assets lost from serviceable faults (thermal death, abandonment, failed
  repair). Losses from non-serviceable ("catastrophic") faults are reported separately: their number grows with
  operating exposure, so a base that TSR-1 keeps running longer has more of them (CDR-19).
* **Earth mass** — replacement assets plus ORU spares; also reported **per available asset-year**.
* **Keep-alive demand / denied / hold time** — inputs to the inventory rule `value_model.keepalive_inventory`.

## Run log

`results/run_log.txt` records the timestamp, run mode, number of registered parameters and closure-check
outcome of the last run.
