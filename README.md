# TODARO CORP. — TSR-1
## Lunar Autonomous Service & Recovery Rover — Preliminary Systems Engineering Study

> **Disclaimer.** TSR-1 is an independent conceptual engineering study by Todaro Corp. References to
> NASA, ESA and other organizations are used solely as technical and architectural context. This is not
> a NASA, ESA, JAXA, CSA or commercial-partner project and implies no endorsement or partnership.

**Status:** complete — design freeze V1, critical design review (CDR-01..CDR-21), feasibility verdict and the full
paper are generated from the models. Current state and continuation instructions: `PROJECT_STATE.md`.

### Research question
Can a dedicated autonomous lunar servicing and recovery rover materially increase the availability and
operational lifetime of distributed lunar surface infrastructure while reducing crew EVA requirements,
asset loss, downtime and Earth-supplied maintenance logistics, within physically and technologically
plausible mass, power, thermal and mobility constraints?

### Answer in one paragraph
**Feasible with identified technology development, and conditionally justified.** A ≈ 1.2 t (delivered) six-wheel
rocker-bogie rover with two light dexterous arms, a 150 kg cable-stayed crane, a 3 kW 120 VDC power-transfer module,
deployable keep-alive modules and an anchored 4 kN winch closes in mass, power, energy, thermal, mobility, recovery,
manipulation, geometry and mission time. Its value comes mainly from keeping unpowered assets alive and depends on
base size (logistics break-even at roughly a dozen serviceable assets) and, above all, on assets carrying
robot-serviceable interfaces. Two original hypotheses failed (heavy service arm; towing as the primary recovery
method), and the review found a host-mounted service kit preferable wherever a utility-rover host can respond in time.
Details: `results/EXECUTIVE_SUMMARY.md`, `results/FEASIBILITY_VERDICT.md`, `paper/paper.md`.

### Where to start reading
| Document | What it is |
|---|---|
| `results/EXECUTIVE_SUMMARY.md` | what TSR-1 is and why it exists (one page) |
| `paper/paper.md` | full scientific/engineering paper (29 sections, figures in `paper/figures/`, bibliography `paper/references.bib`) |
| `DESIGN_FREEZE_V1.md` | frozen configuration; every number points to its derivation |
| `CRITICAL_DESIGN_REVIEW.md` | adversarial review, objections CDR-01..CDR-21, failed ideas |
| `results/FEASIBILITY_VERDICT.md` | verdict and the conditions under which TSR-1 is justified |
| `results/FINAL_SPECIFICATIONS.md` | requirement compliance, component list, closure verification |
| `results/open_questions.md` | unresolved problems OQ-01..OQ-15 |
| `docs/limitations.md` | what the study cannot claim and why |

### Repository layout
| Path | Content |
|---|---|
| `research/` | literature review, source register (97 sources with access labels), search log, programme context, TRL assessment |
| `requirements/` | mission & system requirements (generated from model outputs), traceability matrix |
| `engineering/` | ConOps, architecture, assumptions register, parameter register, mass/power budgets, materials matrix, interfaces, FMEA, component specification sheets |
| `trade_studies/` | ten formal trade studies (generated from results) |
| `src/tsr1/` | Python engineering models (importable package `tsr1`) |
| `tests/` | automated tests of the calculations (`pytest`) |
| `simulations/` | run configuration, master runner, capacity study, results (`simulations/README.md`) |
| `figures/` | programmatically generated figures fig01–fig22 |
| `paper/` | paper generator, paper, bibliography generator, bibliography, figures |
| `docs/` | limitations, technology gaps, development roadmap, visual render specification |
| `results/` | executive summary, final specifications, feasibility verdict, open questions (generated) |

The source package lives in `src/tsr1/` (a standard "src layout") rather than directly in `src/` so the models are
importable and testable as one package.

### Reproducing everything
```
pip install numpy scipy pandas matplotlib pytest
PYTHONPATH=src pytest -q                                  # calculation tests
PYTHONPATH=src python simulations/build_all.py            # results → figures → specs → trades → reports → paper (≈ 10 min)
PYTHONPATH=src python simulations/build_all.py --quick    # reduced Monte Carlo sizes (smoke test)
```
All stochastic analyses are seeded (`simulations/configs/run_config.json`); a rerun reproduces the same numbers.
Documents marked "generated" are overwritten by the build — edit their generators, not the files.

### Evidence-access note
The study environment's network policy blocked full-text access to NASA NTRS, nasa.gov and esa.int. Sources were read
through search-engine excerpts attributed to the primary documents; every source carries an access label in
`research/source_register.csv`, and the consequences are discussed in `docs/limitations.md`.
