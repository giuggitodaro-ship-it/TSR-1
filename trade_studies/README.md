# Trade studies — index and method

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other organizations are used solely as technical and architectural context.

| ID | Trade | File | Decision |
|---|---|---|---|
| TS-01 | Mobility architecture | [mobility.md](mobility.md) | 6-wheel rocker-bogie + body lowering + differential lock |
| TS-02 | Wheel architecture/sizing | [mobility.md](mobility.md) | rigid Ti-6Al-4V Ø0.90 × 0.40 m, 20 mm grousers |
| TS-03 | Manipulator architecture | [manipulators.md](manipulators.md) | 2 identical 7-DOF dexterous arms + 150 kg crane boom (heavy arm rejected) |
| TS-04 | Stabilisation | [stabilization.md](stabilization.md) | locked wheels + diff lock (manipulation); spades + helical anchors (winching); no outriggers |
| TS-05 | Recovery | [stabilization.md](stabilization.md) | 4 kN anchored winch, 0.25 m fairlead, 2 spades, 2 (+2) helical anchors |
| TS-06 | Energy | [power.md](power.md) | 14 kWh EOL Li-ion + 1.5 m² vertical PV + ISPSIS grid charging; RPS rejected |
| TS-07 | Service modules | [service_modules.md](service_modules.md) | modular 6-slot spine; 2 keep-alive modules; no fluid module |
| TS-08 | Communications | [communications.md](communications.md) | surface network + LunaNet S-band relay + mesh + DTN |
| TS-09 | Autonomy | [autonomy.md](autonomy.md) | supervised autonomy with deterministic safety layer |
| TS-10 | Structural materials | [materials.md](materials.md) | Al honeycomb chassis, Ti arm links/fittings, CFRP boom/mast |

**Method (no arbitrary scoring).** (1) Screen against hard requirements; (2) compare compliant options on discriminators
computed by the project models; (3) choose minimum delivered mass unless a quantified mission effect (value model,
reliability, closure check) justifies more, stating the justification. Weighted scoring is used only in TS-03, with
weights equal to DRM-derived work-content fractions.
