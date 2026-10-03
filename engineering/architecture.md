# TSR-1 System Architecture

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other
> organizations are used solely as technical and architectural context.

Numerical values for the frozen configuration are in `DESIGN_FREEZE_V1.md` (generated from the models);
this document explains the architecture and the logic connecting its elements. Figures: `figures/fig01`–`fig09`.

## 1. Architectural logic

The study's models drove the architecture in a specific order:

1. **Traction, not suspension, limits slopes.** Lunar soil shear strength and compaction resistance both scale with
   wheel load, so the climbable slope is a soil property (≈ 20° nominal, ≈ 15° conservative) almost independent of
   suspension type (TS-01). This made the lightest architecture that still supports self-repair and stabilisation the
   rational choice: a **six-wheel rocker-bogie with body lowering**.
2. **The vehicle is light compared with the forces servicing and recovery need.** At 1.62 m/s², a ~1.25 t rover weighs
   only ≈ 2 kN. A 150 kg serial arm would need ≈ 1.5 kN·m shoulder actuators (TS-03), and a useful winch pull exceeds
   the vehicle's weight (TS-04). Hence: **lifting by crane in tension/compression**, **dexterity by light 20 kg arms**,
   and **ground reaction by spades and anchors** rather than vehicle weight.
3. **Value comes from preventing losses, which needs power.** The value model shows the largest benefit is keeping
   unpowered assets alive (thermal death within 24–120 h) and repairing them later. This made the
   **ISPSIS 120 VDC power-transfer module** and deployable **keep-alive modules** core, not optional, functions.
4. **Interoperability is decisive.** Robotic ORU success falls from ≈ 0.96 (L3) to ≈ 0 (L0); TSR-1 adopts open
   standards and carries adapters (interfaces.md), and the project's main recommendation targets asset standards.

## 2. Physical architecture

```
                     ┌──────────── sensor mast (NavCam stereo, thermal IR, LEDs, relay antenna) ───────────┐
   front ▲           │                                                                                      │
         │   dex arm L ◄─┐   tool rack   ┌─ crane boom (2.6 m, 150 kg, 360° slew) ─┐   radiator (zenith, EDS) │
         │   dex arm R ◄─┤   service spine (6 slots, 150 kg)   PV panels (vertical, both sides)            │
         │               └──────────── chassis torque box (Al honeycomb) = deck + WEB ──────────────────────┘
         │                    WEB: battery · PCDU (120 VDC) · PTM (3 kW isolated) · HPSC + 2× safety RT · radios
         │   6 × Ø0.9 m Ti wheels on rocker-bogie (body lowering 0.45 → 0.10 m, differential lock)
   rear  ▼   winch (4 kN, fairlead 0.25 m) · 2 rear spades · 2 helical anchors (+2 in MOD-REC) · LiDAR rear
```

## 3. Functional architecture

| Function | Elements | Key interfaces |
|---|---|---|
| F1 Traverse & localise | wheels/drives/steering, rocker-bogie, NavCam/HazCam/LiDAR, IMU/star tracker, autonomy | base map, LunaNet PNT |
| F2 Inspect & diagnose | mast cameras, thermal IR, macro camera, LiDAR, electrical probe, contact vibration | asset data port (EI-04) |
| F3 Emergency power & charging | PTM, tether, dust-tolerant connector, MOD-KA | ISPSIS 120 VDC (EI-01) |
| F4 Service ORUs | two dex arms, crane, tools, spine | robotic interfaces (EI-03) |
| F5 Clean | brush and EDS wand tools | asset surfaces |
| F6 Recover / reposition | winch, line, spades, anchors, hitch tools, crane lift, scoop | tow points (EI-06) |
| F7 Self-maintain / peer service | ORU design, grapple fixtures, fiducials, body lowering | II-03/II-04/II-07 |
| F8 Survive | battery, PV, MLI/LHP/radiator, heaters, safe modes | — |
| F9 Communicate & be supervised | surface radio, relay radio, mesh, DTN, hold points | EI-07 |

## 4. Avionics and autonomy architecture

Two physically separate computing domains (SR-AVI-01, SR-AUT-01):

* **Autonomy domain** (HPSC-class): mission planner → task planner → verified skill sequencer → motion planner;
  hosts ML components (terrain classification, anomaly ranking, pose estimation, diagnosis ranking, plan
  proposal) in an advisory role.
* **Safety/real-time domain** (dual-lane rad-hard computers): servo loops, force/impedance control, winch tension
  loop, and independent guards (force/torque, speed near crew, tip factor from measured CoP, winch tension, power-port
  interlocks, keep-out zones, watchdog → safe hold). It accepts only commands that pass its checks; it can execute
  pre-verified skills and minimal navigation alone (degraded mode DM-7).

Time synchronisation: chip-scale atomic clock disciplined by LunaNet time. Health monitoring: every ORU reports
temperature, current and fault flags; trending feeds the mission planner (preventive maintenance requests).

## 5. Communications concept

Three independent paths (base surface network, LunaNet S-band relay, UHF peer mesh), DTN for all non-real-time
data, autonomy that proceeds to the next hold point during outages (MR-08). A deployable repeater module extends
links into shadowed craters.

## 6. Variants identified by the critical design review

* **TSR-1 dedicated carrier** (this baseline) — justified where no utility-rover host can guarantee response within
  the asset survival time.
* **TSR-1 service-and-recovery kit** — the same arms, crane, tools, spine, PTM and recovery hardware packaged for
  a NASA-class Lunar Utility Rover or an uncrewed LTV host (CDR-01). Mass and value comparison:
  `results/FEASIBILITY_VERDICT.md`.
