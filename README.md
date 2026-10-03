# TODARO CORP. — TSR-1
## Lunar Autonomous Service & Recovery Rover — Preliminary Systems Engineering Study

> **Disclaimer.** TSR-1 is an independent conceptual engineering study by Todaro Corp. References to
> NASA, ESA and other organizations are used solely as technical and architectural context. This is not
> a NASA, ESA, JAXA, CSA or commercial-partner project and implies no endorsement or partnership.

**Status:** in progress — see `PROJECT_STATE.md`.

### Research question
Can a dedicated autonomous lunar servicing and recovery rover materially increase the availability and
operational lifetime of distributed lunar surface infrastructure while reducing crew EVA requirements,
asset loss, downtime and Earth-supplied maintenance logistics, within physically and technologically
plausible mass, power, thermal and mobility constraints?

### Repository layout
| Path | Content |
|---|---|
| `research/` | literature review, source register, search log, NASA/ESA context, TRL assessment |
| `requirements/` | mission & system requirements, traceability matrix |
| `engineering/` | ConOps, architecture, assumptions, parameter register, budgets, materials, interfaces, FMEA, subsystem specs |
| `trade_studies/` | formal trade studies |
| `src/tsr1/` | Python engineering models (importable package `tsr1`) |
| `tests/` | automated tests of the calculations (`pytest`) |
| `simulations/` | run configurations, scripts and results |
| `figures/` | programmatically generated figures |
| `paper/` | scientific paper and bibliography |
| `docs/` | limitations, technology gaps, roadmap, visual render specification |
| `results/` | executive summary, final specifications, feasibility verdict, open questions |

The source package lives in `src/tsr1/` (a standard "src layout") rather than directly in `src/` so the
models are importable and testable as one package.

### Reproducing the models
```
pip install numpy scipy pandas matplotlib pytest
PYTHONPATH=src pytest -q
PYTHONPATH=src python simulations/run_all.py
```
