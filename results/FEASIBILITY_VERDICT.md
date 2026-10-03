# TSR-1 FEASIBILITY VERDICT

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other organizations are used solely as technical and architectural context.

## Verdict: FEASIBLE WITH IDENTIFIED TECHNOLOGY DEVELOPMENT — conditionally justified

**Engineering feasibility.** A ≈ 1.2 t rover performing inspection, ISPSIS-compatible emergency power, robotic ORU servicing, dust remediation and anchored-winch recovery closes in mass, power, energy, thermal, mobility, recovery, manipulation, geometry and mission time (46/46 independent closure checks pass) using technology that exists today at TRL 5–7 for most elements, **but** depends on four immature items: ground-reaction anchors (TRL 3), cold/dust-tolerant long-life actuators (TRL 4), verified supervised servicing autonomy (TRL 4) and robot-mateable dust-tolerant kW connectors (TRL 4–5). None requires new physics; each has a defined test path (`docs/development_roadmap.md`).

**Why not 'feasible with current/near-term technology':** the integrated system is TRL 4 and its recovery and long-life claims rest on TRL 3–4 elements with no lunar test data.

**Why not 'partially feasible':** the full functional scope survives in mass and power; what failed were specific means (heavy arm → crane; towing → anchored winch), not functions.

**Why not 'not currently justified':** above ≈ 12 serviceable assets the model shows a positive logistics balance, and the P10 of the availability gain is positive from 10 assets (ΔA P10 0.5 pp at 10, 1.7 pp at 30).

## Conditions under which TSR-1 is justified

| Condition | Evidence | If not met |
|---|---|---|
| Base has more than ≈ 12 serviceable assets (logistics break-even) | net Earth-mass benefit -1.02 t (3 assets), -0.20 t (10), 1.76 t (30) | **not justified**: a 3-asset outpost should rely on crew + Earth spares |
| Most assets are L2/L3 robot-serviceable | ΔA 2.9 pp (legacy) vs 13.3 pp (standardised) | TSR-1 degenerates to inspection + emergency power + recovery |
| Assets have non-negligible fault rates (MTBF ≲ 10 yr) | corr(MTBF, ΔA) ≈ -0.33 | value scales down with fault rate |
| Crew presence is intermittent | ΔA 11.6 pp with no crew vs 5.7 pp with 2 missions/yr | value falls as crew presence rises |
| Anchors validated (TG-03) | p_env 0.92 with anchors vs 0.51 braked wheels only | slope recovery largely lost |
| A dedicated carrier only if no host can respond within asset survival time | kit ≈ 352 kg vs dedicated 1207 kg; preventable losses 8.4 (dedicated) vs 12.6 (shared host busy 60 %) | choose the kit variant on a utility-rover host |
| Keep-alive inventory scaled with fault load (CDR-19) | 60 assets, MTBF 1.5 yr: preventable losses 36.8 / 30.1 / 22.6 with 2 / 4 / 8 modules (without TSR-1 53.5) | one TSR-1 saturates on keep-alive capacity, not on driving or servicing time |
| Parked assets' survival power within MOD-KA output (CDR-20) | P(sustain) 0.76 (0.56 if assets need 50 % more power) | losses rise toward the no-module case; larger MOD-KA or MOD-SOL needed |

## Answer to the research question

For a 30-asset south-polar base over 10 years, one TSR-1 raises mean infrastructure availability from 0.69 to 0.76 (ΔA P10/P50/P90 = 1.8/7.0/14.5 pp), reduces preventable asset losses from 21.7 to 8.9 (all causes 32 → 21) and Earth-supplied replacement mass from 13.0 t to 9.5 t (70 → 46 kg per available asset-year). **Crew EVA is reduced only modestly** (786 → 697 crew-h): TSR-1 saves assets that then still need crew for repairs it cannot perform on non-standard interfaces. The answer is therefore **yes, materially, for asset availability, asset loss and logistics mass, at bases of more than ≈ 12 serviceable assets — and only weakly for EVA reduction**, with the value dominated by emergency power/keep-alive and by asset interface standardisation rather than by manipulation sophistication.
