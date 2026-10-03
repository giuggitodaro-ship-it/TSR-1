# TSR-1 Concept of Operations (ConOps)

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other
> organizations are used solely as technical and architectural context.

Status: written as the Phase-2 baseline before modelling; the five values originally left as TBD-1..TBD-5 have since
been resolved by the models in `src/tsr1/` (resolutions shown inline, frozen values in `DESIGN_FREEZE_V1.md`).

---

## 1. Purpose

TSR-1 is a mobile robotic system whose purpose is **infrastructure availability**: to keep distributed
lunar surface assets operating, to prevent recoverable faults from becoming asset losses, and to reduce
crew EVA and Earth-supplied replacement logistics. It is **not** a crew transport, not an exploration
rover and not a bulk-cargo hauler (the latter is the role of the NASA-defined Lunar Utility Rover class,
S005; overlap is analysed in TS-07 and CDR-01).

## 2. Stakeholders

| ID | Stakeholder | Primary interest | Interaction with TSR-1 |
|---|---|---|---|
| SH-1 | Infrastructure owners (agency Moon Base programme, international partners, commercial power/comm service providers) | asset availability, asset life, cost | task requests; interface data; ORU spares |
| SH-2 | Surface crew | fewer/shorter EVAs, safety | task delegation; safety keep-out; occasional crew-assisted repair of TSR-1 |
| SH-3 | Mission operations (Earth MOC + local base operations) | supervisable, predictable robot | task-level commanding; approvals; telemetry |
| SH-4 | Science users | instrument uptime; contamination control | inspection/servicing of science packages; dust-plume limits |
| SH-5 | Other robotic assets (LTV uncrewed mode, utility rovers, CADRE-class, drones) | interoperability, rescue | recovery client; cooperative tasks; TSR-to-TSR servicing |
| SH-6 | Launch/lander provider | accommodation | mass, envelope, loads, deployment |
| SH-7 | Todaro Corp. (study owner) | defensible design | — |

## 3. Operational environment

- **Location:** lunar south-polar region, Moon Base site on/near the Shackleton–de Gerlache
  connecting-ridge complex (S007, S030). Sunlit ridgelines (92–96 % illumination at the best sites,
  longest darkness 3–5 days, S030), adjacent permanently shadowed regions (< 40 K, S032), DTE
  availability ≈ 51 % (S073). Full environment model: `src/tsr1/environment/lunar.py`.
- **Epoch:** operations ~2036–2041, i.e., Moon Base Phase 3 with Phase-2 infrastructure in place
  (S054): ridge solar arrays (> 10 kW class), storage, grid segments (3 kVAC + UMIC-type converters,
  S012), communications towers (~10 km radius each), RTG-class powered PSR stations, landers, LTVs,
  the pressurized rover, drones, science packages, and early habitat elements.

## 4. Target asset classes

| Class | Examples | Typical mass | Mobile? | Expected compatibility level |
|---|---|---|---|---|
| AC-1 Small robotic rover | VIPER-, FLIP-, CADRE-class | 20–500 kg | yes | L0–L1 (legacy), L2 (new) |
| AC-2 Utility / crew rover (uncrewed mode) | LTV (CLV-1, Pegasus) | ≈ 1–2 t (ASSUMPTION A-12) | yes | L1–L2 |
| AC-3 Communication node | surface comm tower, relay mast | 100–500 kg | no | L2–L3 |
| AC-4 Power generation | ridge solar array, VSAT-type mast | 200–1500 kg | no | L2–L3 |
| AC-5 Power storage / distribution | battery node, grid converter, cable junction | 50–500 kg | no | L2–L3 |
| AC-6 Science station | seismic/heat-flow/PSR instrument package (incl. RTG-class) | 10–200 kg | no | L0–L2 |
| AC-7 Lander (spent / stationary) | CLPS, Argonaut, Mk1 | 0.5–5 t (dry) | no | L0–L1 |
| AC-8 Habitat external equipment | radiators, external ORUs, umbilicals | ORU 5–150 kg | no | L2–L3 |
| AC-9 ISRU / construction equipment | excavator, regolith processor | 0.2–2 t | some | L1–L2 |

## 5. Servicing compatibility levels (directive §7)

| Level | Definition | TSR-1 capability |
|---|---|---|
| **L0** Non-service-ready | no robotic fixtures, no external ports, unknown fasteners | inspect (visual, macro, thermal IR, LiDAR mapping); dust remediation of exposed surfaces; push/tow/winch **only via structurally suitable members** identified by inspection |
| **L1** Accessible | external diagnostic/test port and/or power port, identifiable lift/tow points | L0 + external diagnostics, limited power connection (ISPSIS 120 VDC via adapter), basic intervention (reset, connector reseat) |
| **L2** Robotic-service-ready | ORUs with robot-compatible handles and captive standard fasteners, robot-mateable connectors, fiducials | L1 + ORU replacement, connector manipulation, modular component exchange |
| **L3** Fully interoperable | standard docking/grapple fixtures, standardized data (LunaNet/DTN service interface), ISPSIS power port, (optionally) standard fluid couplings | L2 + autonomous docking, full robotic servicing, standardized health data download |

Servicing success probability per level is modelled in `src/tsr1/reliability/servicing.py` from a
task-step decomposition (results in paper §21).

## 6. Mission scenarios (design reference missions, DRM)

| DRM | Scenario | Trigger | Flow (nominal) | Principal design drivers |
|---|---|---|---|---|
| DRM-1 | Routine inspection patrol | schedule | traverse → stand-off imaging, thermal IR, LiDAR → macro inspection of flagged items → report | sensors, autonomy, range |
| DRM-2 | Electrical failure (Level 2/3 asset) | asset fault telemetry or loss of signal | traverse → inspect → connect emergency power (ISPSIS) → diagnose bus → identify failed ORU → replace ORU → functional test → disconnect | dexterous arm, tools, ORU carriage, 120 VDC transfer, autonomy |
| DRM-3 | Dust contamination | power/thermal degradation trend | traverse → inspect array/radiator → remediate (brush/EDS-wand/gas-free contact cleaning) → verify recovery | cleaning tools, reach, contamination control |
| DRM-4 | Immobilized rover | client distress / loss of mobility | traverse → stand-off assessment → keep-alive power → repair attempt **or** recovery (winch/tow) → return to service zone | recovery system, stability, anchors, power |
| DRM-5 | Communication asset failure | loss of link | traverse → temporary power → replace modular electronics ORU → link test | ORU handling at height (mast), dexterity |
| DRM-6 | Heavy ORU / infrastructure repositioning | planned | lift/transport ORU or reposition light element | heavy lifting, stability |
| DRM-7 | TSR-1 self-rescue and TSR-to-TSR service | own fault | degraded-mode drive (wheel lockout), self-winch, peer servicing | redundancy, self-serviceability |
| DRM-8 | Survival / hibernation | darkness, comm loss, fault | park at charging node or sunlit site → minimum-power mode → resume | power, thermal |

Quantified timelines, energies and risks for DRM-2 to DRM-5 are produced by
`src/tsr1/budgets/scenarios.py` (paper §23).

## 7. Operations concept

### 7.1 Command hierarchy
1. **Task request** (owner or operations) → task enters TSR-1 mission planner queue with priority.
2. **Task plan** generated onboard/at base (verified skill sequence) → **human approval at task level**
   (not joystick) by Earth MOC or local base operator.
3. **Execution** autonomous, with deterministic safety supervisor; **hold points** before irreversible
   steps (power connection, fastener release on load-bearing items, winch tensioning above threshold).
4. **Contingency:** loss of comm → continue to next hold point, then safe-hold (DRM-8 rules).

### 7.2 Communications assumptions
- Local surface network (comm towers, ≈ 10 km cells, S054) available within the base area; mesh
  fallback between TSR-1, assets and towers.
- Relay services (LunaNet/LCRNS, Moonlight; S017, S018) for Earth link; DTE ≈ 51 % availability (S073).
- **Design case (TBD-1/2 resolved, MR-08, A-19):** Earth-link outages up to 72 h and local-network outages up to 24 h.
  Autonomy continues to the next hold point and then safe-holds, so an outage costs time, not safety; the base
  network + relay + mesh architecture gives ≈ 0.98 link availability (TS-08), against ≈ 0.51 for direct-to-Earth
  alone. Delay
  tolerant (DTN, CCSDS bundle protocol, L020) store-and-forward for all non-real-time data.

### 7.3 Crew availability assumptions
- Crew present for part of each year only (ASSUMPTION A-07: 0–2 surface missions/yr, ≤ 30 days each,
  baseline 1 per year in the 2036–2041 epoch). TSR-1 must be fully useful when no crew are present.

### 7.4 Service area and response
- Base service radius **R_s = 10 km** (TBD-3 resolved: comm-tower cell size, S054; closed by battery sizing with a 50 h
  reserve, CDR-06). Excursions beyond 10 km (TBD-4 resolved) are limited by the effective-speed rule of CDR-13 (e.g.
  ≈ 6 km at 0.7 km/h, ≈ 22 km at 2.5 km/h) and by the 34 km single-charge range.
- Response time **≤ 10 h** from task approval to arrival at the service edge (TBD-5 resolved, MR-15): 10 km at the
  effective 1.26 km/h plus 2 h preparation, far inside the 24–120 h survival time of an unpowered asset.

### 7.5 Servicing frequency assumptions
- Serviceable fault rate per asset is unknown (literature gap L-3); modelled as exponential with MTBF
  1–10 years (ASSUMPTION A-08) and type mix A-09. Annual task demand for N assets is an *output*.

## 8. Operational phases and modes

| Phase | Description |
|---|---|
| Delivery | stowed on lander; launch/landing loads; survival heater power from lander |
| Deployment & commissioning | egress via lander ramp/offloader; checkout; calibration of arms and sensors |
| Routine operations | patrols, scheduled maintenance, on-call response |
| Servicing sortie | DRM-2 … DRM-6 |
| Survival | darkness/comm-loss hibernation (DRM-8) |
| Degraded operations | after TSR-1 failures (FMEA degraded modes) |
| End of life | park at designated site as spares source; passivation |

Operating modes used in the power budget: M1 dormant/standby, M2 communications standby, M3 driving,
M4 inspection, M5 manipulation, M6 heavy manipulation, M7 recovery/winch, M8 emergency power delivery,
M9 charging, M10 thermal survival, M11 fault/safe mode.

## 9. Constraints accepted at ConOps level

- No crew transport; no pressurized volume.
- Must coexist with crew: speed and force limits in crew proximity (safety requirements SR-SAF-x).
- No proprietary-only interfaces (ISPSIS, LunaNet, ISO 9409-1/IERIIS-derived; S011, S013, S017).
- Delivery on one commercial lander of the 1.5–3.0 t payload class (S047, S056).
