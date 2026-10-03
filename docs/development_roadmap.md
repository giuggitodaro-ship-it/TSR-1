# TSR-1 Development Roadmap

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other
> organizations are used solely as technical and architectural context.

No calendar dates are given: there is no funded programme, no selected lander and no adopted asset
interface standard on which to base a schedule. Stages are ordered by technical dependency; each has
explicit entry/exit criteria tied to the technology gaps (TG-xx, `docs/technology_gaps.md`) and TRL
targets (`research/technology_readiness.md`). Durations are not estimated because no comparable
programme data were retrieved in this study.

| Stage | Content | Entry criteria | Exit criteria (gates) | Gaps addressed |
|---|---|---|---|---|
| **0 Digital modelling** (this study) | parametric models, trades, budgets, value model | — | closure checks pass; design freeze V1; CDR objections dispositioned | — |
| **1 Subsystem breadboards** | (a) anchor/spade pull-out rig in simulants (JSC-1A/LHS-1 class) at several densities; (b) single-wheel terramechanics rig incl. grouser variants; (c) dust-tolerant 3 kW connector mating rig; (d) BMG/dry-lube actuator life rig in vacuum + simulant; (e) PTM breadboard to ISPSIS rules; (f) skill-library prototypes on a commercial arm | Stage 0 | anchor capacity within ±30 % of model or model recalibrated (TG-03); actuator life ≥ 25 % of 10-yr duty without failure (TG-01); connector ≥ 500 robotic mates at rated current (TG-02); DP/W vs slip validated (TG-06) | TG-01/02/03/06 |
| **2 Earth prototype** | 1-g full-scale engineering rover (mass-scaled or g-compensated arm loads), two dex arms + crane, spine, winch/anchors, PTM | Stage 1 gates | all DRMs executed end-to-end on analogue targets built to L0–L3 interface definitions; closure re-run with measured masses (MGA reduced) | TG-04/05 |
| **3 Integrated analogue field testing** | multi-week campaigns on lunar-analogue terrain with comm delays/outages, long-shadow lighting, multiple simulated assets | Stage 2 | measured task success by level vs servicing.py; measured effective speed vs 1.26 km/h assumption; operator hours per task | TG-04/05/08 |
| **4 Thermal-vacuum and dust testing** | subsystem and system TVAC (40–390 K), dust chamber with charged simulant, EDS performance, radiator degradation | Stage 2 (subsystems), Stage 3 (system) | survival ≥ 120 h demonstrated; WEB within limits at 3 kW transfer; mechanism torque growth within margin | TG-01/07 |
| **5 Reduced-gravity / mechanism qualification** | parabolic-flight wheel and anchor tests; crane load-swing control; launch-load qualification once a lander is selected | Stages 1–4 | lunar-g traction penalty quantified; anchors validated in reduced g; qualification to lander environments | TG-03/06 |
| **6 Flight demonstrator** | reduced TSR (one dex arm, PTM, recovery kit, keep-alive module) delivered to a Moon Base site; services cooperative L2/L3 demo assets | Stage 5 + asset owner agreement on interfaces | in-situ ORU swap, power rescue, anchored winch recovery of a demo vehicle; dust/thermal life telemetry | all |
| **7 Operational system** | full TSR-1 (or service-kit variant on a utility-rover host, CDR-01) supporting a base above the logistics break-even (≈ a dozen serviceable assets, paper §21) | Stage 6 + standardised assets in the base | availability gain measured against the value model | — |

**Dependency logic.** Stage 6 must not proceed before the asset-interface question (TG-05) has an agreed answer:
without L2/L3 assets the demonstrator would only prove inspection and emergency power. The anchor and actuator-life
breadboards (Stage 1) are the cheapest, highest-information tests and should come first.
