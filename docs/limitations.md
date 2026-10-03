# TSR-1 Study Limitations

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other
> organizations are used solely as technical and architectural context.

## 1. Evidence access
- The study environment's network policy blocked full-text access to NASA NTRS, nasa.gov, esa.int and most
  journals (HTTP 403, 2026-10-03). All agency sources were read through **search-engine excerpts** attributed to the
  primary documents. Verification labels per source: `research/source_register.csv`.
- Seed document NTRS 20260001878 could not be resolved; seed NTRS 20210022361 resolves (by title) to NTRS 20220002618.
- Full texts of NASA/SP-20260001900 (robotic interface best practices) and the LTV System Requirements Document were not
  read; their numerical interface rules are not used.
- Several handbook values (factors of safety, material properties, MGA percentages other than harness, Bekker
  depth-table values below 30 cm, MLI emittance, solar cell efficiency) are **literature-recall** values: they are
  standard published values but were not re-verified against the full text in this session.

## 2. Model limitations
| Model | Main limitation | Consequence |
|---|---|---|
| Terramechanics (Wong–Reece/Bekker) | rigid wheel, quasi-static, first-order grousers, no bulldozing; soil parameters uncertain | slope claims carry ±(4–10)° uncertainty (tornado); calibrated only on one datum (LRV energy) |
| Vehicle | static load distribution, no dynamics, no steering/side-slope traction | turning and cross-slope performance not quantified |
| Stability | static only; no dynamic tip-over from impacts or load swing | crane load swing in 1/6 g not analysed |
| Manipulators | planar worst case; MER for actuator mass (torque density 15–40 N·m/kg) | arm masses ±40 % |
| Crane | statics + buckling; no dynamics | swing control unproven |
| Recovery | Rankine/breakout soil mechanics without lunar validation; embedded-wheel extraction bounded by two very different models | recovery envelope contingent on TG-03 |
| Thermal | lumped two-node; no transient orbit-of-sun analysis, no shadowing geometry | radiator sizing ±30 % |
| Structure | equivalent-box beam, no FEM; launch loads assumed | primary-structure mass ±30 % |
| Power | mode-average loads; no transient/inrush/power-quality analysis | PCDU/PTM sizing first-order |
| Value model | assumed fault rates (no lunar data), assumed task-step success probabilities, simplified crew and logistics processes, no patrol/pre-detection benefit, no cost model | results are comparative, not predictive; conclusions rely on robust trends (sign, scale dependence, standardisation dependence), not on absolute values |
| Reliability | exponential failures, independent units, calendar rates (ESTIMATE) | P(capable) optimistic if common-cause dust failures dominate |

## 3. Scope exclusions
- No cost estimate (no defensible cost data for lunar surface robotics were retrieved); mass is used as the logistics
  proxy.
- No detailed software architecture, cybersecurity or command-authority design for third-party assets.
- No lander-specific accommodation design.
- No crew-interaction human-factors analysis beyond speed/force limits.

## 4. What would change the conclusions
- A demonstrated lunar regolith anchor capacity well below the model (TG-03) would remove most slope-recovery capability.
- Assets designed without robotic servicing interfaces would reduce TSR-1 to an inspection/emergency-power/recovery
  role (ΔA ≈ 2 pp for a legacy base).
- A utility-rover host with guaranteed response availability would make the dedicated carrier unnecessary (CDR-01).
- Asset fault rates much lower than MTBF ≈ 10 yr would remove the value case at any base size.
