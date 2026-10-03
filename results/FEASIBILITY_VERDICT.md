# TSR-1 FEASIBILITY VERDICT

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other organizations are used solely as technical and architectural context.

## Verdict: FEASIBLE WITH IDENTIFIED TECHNOLOGY DEVELOPMENT — conditionally justified

**Engineering feasibility.** A ≈ 1.2 t rover performing inspection, ISPSIS-compatible emergency power, robotic ORU servicing, dust remediation and anchored-winch recovery closes in mass, power, energy, thermal, mobility, recovery, manipulation, geometry and mission time (44/44 independent closure checks pass) using technology that exists today at TRL 5–7 for most elements, **but** depends on four immature items: ground-reaction anchors (TRL 3), cold/dust-tolerant long-life actuators (TRL 4), verified supervised servicing autonomy (TRL 4) and robot-mateable dust-tolerant kW connectors (TRL 4–5). None requires new physics; each has a defined test path (`docs/development_roadmap.md`).

**Why not 'feasible with current/near-term technology':** the integrated system is TRL 4 and its recovery and long-life claims rest on TRL 3–4 elements with no lunar test data.

**Why not 'partially feasible':** the full functional scope survives in mass and power; what failed were specific means (heavy arm → crane; towing → anchored winch), not functions.

**Why not 'not currently justified':** at ≳ 10 serviceable assets the model shows a positive logistics balance and an availability gain whose P10 is positive from about 20 assets (ΔA P10 1.2 pp at 20, 1.5 pp at 30).

## Conditions under which TSR-1 is justified

| Condition | Evidence | If not met |
|---|---|---|
| Base has ≳ 10 serviceable assets (break-even ≈ 9) | net Earth-mass benefit -0.84 t (3 assets), 0.15 t (10), 1.68 t (30) | **not justified**: a 3-asset outpost should rely on crew + Earth spares |
| Most assets are L2/L3 robot-serviceable | ΔA 2.4 pp (legacy) vs 13.4 pp (standardised) | TSR-1 degenerates to inspection + emergency power + recovery |
| Assets have non-negligible fault rates (MTBF ≲ 10 yr) | corr(MTBF, ΔA) ≈ -0.45 | value scales down with fault rate |
| Crew presence is intermittent | ΔA 12.5 pp with no crew vs 5.7 pp with 2 missions/yr | value falls as crew presence rises |
| Anchors validated (TG-03) | p_env 0.92 with anchors vs 0.51 braked wheels only | slope recovery largely lost |
| A dedicated carrier only if no host can respond within asset survival time | kit ≈ 352 kg vs dedicated 1207 kg; assets lost 20.7 (dedicated) vs 24.1 (shared host busy 60 %) | choose the kit variant on a utility-rover host |

## Answer to the research question

For a 30-asset south-polar base over 10 years, one TSR-1 raises mean infrastructure availability from 0.68 to 0.76 (ΔA P10/P50/P90 = 2.2/6.7/14.4 pp), reduces assets lost from 31 to 22 and Earth-supplied replacement mass from 12.7 t to 9.4 t. **Crew EVA is reduced only modestly** (736 → 654 crew-h): TSR-1 saves assets that then still need crew for repairs it cannot perform on non-standard interfaces. The answer is therefore **yes, materially, for asset availability, asset loss and logistics mass, at bases of roughly ten or more serviceable assets — and only weakly for EVA reduction**, with the value dominated by emergency power/keep-alive and by asset interface standardisation rather than by manipulation sophistication.
