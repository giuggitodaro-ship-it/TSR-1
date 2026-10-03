# TSR-1 Literature Review

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other
> organizations are used solely as technical and architectural context.

**Baseline date:** 3 October 2026. **Evidence trail:** `research/search_log.md` (raw excerpts) and
`research/source_register.csv` (IDs `S0xx`, `L0xx`).

**Method and limitation.** The study environment's network policy blocked full-text retrieval from
NASA NTRS, nasa.gov, esa.int and most scholarly hosts. All agency documents were therefore consulted
through search-engine excerpts attributed to the primary document. Each source carries a verification
label (`EXCERPT`, `SECONDARY`, `EXISTENCE-ONLY`, `LITERATURE-RECALL`, `NOT-RETRIEVED`). Numbers that
drive the design are marked with their label in `engineering/parameter_register.csv`; numbers from
`LITERATURE-RECALL` sources are standard handbook values that must be re-checked against the full text
before any use beyond this conceptual study. This limitation is repeated in `docs/limitations.md`.

---

## 1. Is the operational need real? (Directive §3–4)

### 1.1 NASA's own gap statements
- The NASA TX-13 capability-gap study (S001) lists, as **technology gaps focused on uncrewed surface
  operations**: health determination and fault management; automated/autonomous planning and
  scheduling; **automated/autonomous inspection, maintenance and repair**; logistics management and
  reliability; and **advanced umbilicals and dust-tolerant interfaces**. Its architecture gaps include
  **standardized architectures and interfaces** and **design for supportability**. The stated rationale
  is reducing "reliance on humans to perform tasks" and accommodating ground communication delay.
- *Uncrewed Lunar Surface Operations and Support Activities* (S051) enumerates robotic support actions —
  lifting/handling, servicing, powering, traversing, inspecting, cleaning, maintaining, safing — and
  names **increasing the availability of surface infrastructure** as an explicit objective.
- The 2026 Civil Space Shortfalls (S010) rank "survive and operate through the lunar night" first,
  high-power generation second and high-performance spaceflight computing third; autonomous robotics
  and in-space maintenance and repair are highly ranked.

**Finding L-1.** The *category* of capability TSR-1 targets is an officially recognised gap. This is
necessary but not sufficient: a recognised gap does not prove that a *dedicated* vehicle is the best
way to close it.

### 1.2 NASA has already defined an overlapping element
- The February 2025 *Lunar Logistics, Mobility, and Cargo* white paper (S005) and the December 2025
  architecture update (S004) add a robotic surface-logistics mobility element — described as a
  **Lunar Utility Rover** — that would reposition "limited (100s kg)" and "moderate (1000s kg)" cargo in
  the south-polar region and "could support continuous presence ... with capabilities to **maintain,
  repair, and service** other exploration systems". The same paper notes that the LTV and Pressurized
  Rover are "primarily for crew transportation with limited cargo mobility functions" and CLPS mobility
  is small-scale.

**Finding L-2 (critical for the study).** TSR-1's mission substantially overlaps a NASA-defined
architecture element. TSR-1 therefore cannot claim novelty of *mission*; it must justify itself either
(a) as a specialised servicing/recovery configuration of a utility-rover class, or (b) as a modular
service kit for such a vehicle. This is carried into the trade studies (TS-07 service-module
architecture) and the critical design review (CDR-01).

### 1.3 Evidence on maintenance demand
- ISS (S049): in its first five years, crews spent > 4000 h on maintenance — **421 h EVA, 777 h
  extravehicular robotics (EVR), 2536 h IVA** — exceeding design estimates. Robotics already performed
  roughly twice the external maintenance hours of EVA crews.
- Lunar Surface Habitat estimates (S050): expected corrective-maintenance crew time **> 24 h per
  mission**, derived from ISS data.
- MER (S046): Spirit was permanently lost after embedding in soft soil following a wheel-motor failure;
  Opportunity required > 5 weeks of planning to extract itself from "Purgatory" dune. No external
  recovery capability existed in either case.

**Finding L-3.** External maintenance demand is empirically significant on ISS, and immobilisation is a
demonstrated asset-loss mode for planetary rovers. Neither datum, by itself, establishes the
*frequency* of serviceable failures on lunar infrastructure — no such dataset exists. Failure rates in
the value model (§21 of the paper) are therefore parametric with wide uncertainty.

---

## 2. Programme context and infrastructure scale (Directive §3, §29, §32)

- **Moon Base programme** (S006, S007, S054): announced 24 March 2026; ~US$20 billion over seven years
  (later reporting ~US$30 billion); south-polar site; three phases. **Phase 1 (to ~2028/29):** ~21
  landings/25 missions, rovers, drones, tech demos. **Phase 2 (2029–2032):** demonstration solar arrays
  > 10 kW with storage on ridgelines, small RTG-class units (few hundred W) for PSR assets,
  communications towers each covering ≈ 10 km radius, JAXA pressurized rover, ≈ 27 launches/24
  landings delivering ≈ 60 t. **Phase 3 (2032+):** permanent habitats, large fission power. Gateway was
  "paused".
- **LTV** (S007, S036, S055): Phase-1 task orders (26 May 2026) to Astrolab (CLV-1, FLEX-derived) and
  Lunar Outpost (Pegasus), delivery 2028 via Blue Origin Mk1. LTV requirements (secondary): 10-year
  life, survive lunar night (≈ 50 K) and extended shadow, ≤ 2 h in PSRs, ≥ 800 kg payload over 20 km per
  charge, remote traverse 6 km (threshold)/8 km (goal) per 24 h. Pegasus: autonomous/teleoperated,
  > 14.5 km/h.
- **Fission Surface Power** (S009): ≥ 100 kWe, < 15 t, closed Brayton, launch readiness FY2030.
- **Delivery capacity** (S047, S056, S057): Astrobotic Griffin 625–650 kg; ESA Argonaut 1.5 t (2030);
  Blue Moon Mk1 3.0 t.

**Finding L-4.** Within the 10–15-year plausibility window (≈ 2036–2041) a south-polar base with tens of
distributed assets spread over ~10–30 km is consistent with announced plans. The value model therefore
spans 3–60 assets. Delivery capacity bounds TSR-1: a rover ≤ ~1.3 t (wet, with accommodation) could ride
an Argonaut-class lander; ≤ ~2.5 t a Mk1-class lander; Griffin-class (~0.6 t) would exclude any
heavy-servicing configuration.

---

## 3. Interface standards (Directive §6C, §6E)

- **Power — ISPSIS Rev A** (S011): defines bus voltages, power quality and single-point grounding for
  **120 VDC** and **28 VDC**; "120 VDC is the Interoperability Power Standard for vehicle-to-vehicle and
  element-to-element interfaces" including surface systems.
- **NASA GRC lunar grid work** (S012): "power exchange must occur at **120 VDC and a distance less than
  100 m** (limitation of 120 VDC)"; an Artemis-scale grid at **3 kVAC**; the bidirectional **Universal
  Modular Interface Converter (UMIC)** couples 120 VDC assets to the grid (100–1500 VDC boost/buck;
  demonstrated scale ~2 kW over ~2 km).
- **Robotics — IERIIS** (S013): generic mounting interfaces by class, aligned to **ISO 9409-1**; large
  fixture interfaces for handling modules/payloads. **NASA/SP-20260001900** (S002) gives best practices
  for robot–crew–cargo interfaces on the surface "compatible with the widest range of potential robots"
  (full text not retrieved). **HOTDOCK** (S048): androgynous mechanical/power/data/(fluid-thermal)
  standard interface used across EU H2020 robotics. ISS heritage: OTCM end-effector with jaws,
  retractable socket drive, camera and power/data umbilical (S067). Astrolab FLEX docks to payloads at
  three robotic interfaces (S037).
- **Comms/nav — LunaNet LNIS v4 / Lunar Relay SRD** (S017), ESA Moonlight (S018; services from end-2028).

**Finding L-5.** TSR-1 must adopt **120 VDC ISPSIS-compatible** power interfaces (not a proprietary
voltage), **LunaNet**-compliant communications and **ISO 9409-1/IERIIS-derived** robotic interfaces with
adapter end-effectors (OTCM-like, HOTDOCK-like, FLEX-like). There is **no single lunar surface servicing
standard today**; this is the largest systemic uncertainty for servicing success (§7 compatibility
levels).

---

## 4. Lunar environment (Directive §9)

| Quantity | Value / range | Source |
|---|---|---|
| Gravity | 1.62 m/s² | L018 |
| Trafficability parameters (disturbed surface) | n = 1, k_c = 1.4 kN/m², k_φ = 820 kN/m³, c = 170 Pa, φ = 35°, K = 1.78 cm | S023 Table 9.14 |
| In-situ 0–15 cm | ρ = 1.50 g/cm³, c = 0.52 kPa, φ = 42° | S023 |
| In-situ 0–30 cm | ρ = 1.58 g/cm³, c = 0.90 kPa, φ = 46° | S023 |
| Satisfactory mobility rule | ground contact pressure ≤ 7–10 kPa | S023 |
| Reduced-g traction penalty | ≈ −20 % DP, up to +40 % sinkage vs 1-g tests | S043 |
| Lunar-g DP/W, small grousered wheel, 20 % slip | 0.11 ± 0.02 (GRC-1) | S044 |
| Best south-pole illumination | 92.27 % (2 m), 95.65 % (10 m); longest dark 3–5 days | S030 |
| DTE availability, south-pole sites | ≈ 51 % average | S073 |
| Landing slope criterion (HLS) | ≤ 8° (goal ≤ 5°) at 20 m baseline | S034 |
| PSR temperatures | < 40 K; cold bound ≈ 28 K (−245 °C) | S032, S010 |
| Sunlit polar rims | often > 223 K, up to ≈ 300 K | S032 (secondary) |
| GCR dose rate (Si) | 13.2 ± 1 µGy/h | S033 |
| Micrometeoroids (pole) | ≈ 15 000 impacts/yr per 100×100×10 m base (10⁻⁶–10 g) | S061 |
| Dust effects | 9 Apollo categories; sub-monolayer degrades radiators; α factor 1.4–2.6 at 25 % coverage | S022, S062 |

**Finding L-6.** The terramechanics parameters carry a known optimism bias when derived from 1-g tests.
TSR-1 mobility sizing applies the reduced-gravity penalty explicitly and treats k_c, k_φ, c, φ as
distributions (sensitivity analysis), not point values.

---

## 5. Mobility heritage (Directive §10)

- **Apollo LRV** (S027, S060): 210 kg empty, 490 kg payload, 25° slopes, 30 cm obstacles, wire-mesh
  wheels 0.818 m × 0.23 m, 4 × 0.25 hp motors with 80:1 harmonic drives, 36 V Ag-Zn batteries; measured
  **1.58–1.67 A·h/km ≈ 57–60 Wh/km** at ≈ 700 kg. This is the only measured lunar vehicle energy
  datum and is used to calibrate the TSR-1 driving-energy model.
- **VIPER** (S035): ≈ 430 kg, four 0.5 m wheels, active suspension, 15° nominal / 25–30° capable,
  survives ≈ 50 h darkness.
- **LTV / FLEX / Pegasus** (S036, S037, S055): 800–1600 kg payload class, 10-yr life, autonomous
  modes; FLEX uses a standardised robotic payload interface.
- **Wheels:** woven-wire LRV wheels; superelastic NiTi spring tyres under NASA GRC development (TRL
  ~4–5, no quantitative load data retrieved); rigid grousered wheels (VIPER/Yutu/Pragyan class).

## 6. Manipulation heritage (Directive §6A, §12)

- **Dextre/SPDM** (S067): two 7-joint arms, 1662 kg, OTCM tool/ORU end-effector — the only operational
  dual-arm servicing robot, but designed for microgravity (no gravity load on joints).
- **Perseverance arm** (S066): ≈ 2 m, 45 kg turret, Mars gravity — the closest planetary-surface
  heavy arm. **Motiv xLink**: 7-axis, 50 kg payload. **GITAI** (S016): 7-DOF inchworm with grapple
  end-effectors on both ends (5 kg payload, 1-g rating). **LSMS** (S015): crane-manipulator hybrid,
  device mass ≈ 3 % of tip payload for advanced structure — a strong alternative to a "heavy arm".
- **Cold actuation** (S040, S041): BMG gears operated at −173 °C without heaters (COLDArm); Braycote
  601EF rated to −80 °C; MSL arm actuators require warm-up above −55 °C.

**Finding L-7.** A gravity-loaded heavy lunar arm has no direct flight heritage; LSMS-type
crane/truss architectures are markedly more mass-efficient for lifting than serial arms. The
dual-arm hypothesis must be evaluated against "dexterous arm + lifting device" and "arm + passive
fixtures" (TS-03).

## 7. Power and energy heritage (Directive §6C, §18)

- Space Li-ion: large prismatic/cylindrical space cells 103–132 Wh/kg (cell); NASA JSC passively
  propagation-resistant 18650 packs **150–170 Wh/kg (pack)** (S038, S070). Charge 0–25 °C, discharge
  > −20 °C typical (S071).
- Infrastructure: ISPSIS 120 VDC, grid 3 kVAC + UMIC (S011, S012); Phase-2 arrays > 10 kW (S054);
  FSP ≥ 100 kWe (S009).
- Dust-tolerant connectors: Honeybee DTC > 500 mate/demate cycles in vacuum with simulant; inductive
  dust-tolerant links (Yank SBIR Phase II) aimed at kW class (S042).

## 8. Dust mitigation (Directive §15)

- Apollo (S022/S074): vision obscuration, false readings, coating, traction loss, **clogging of
  mechanisms, abrasion, thermal-control degradation (LRV batteries overheated), seal failures**.
  Fender loss caused "rooster tails". Simple measures were ineffective against clogging, abrasion and
  heat-rejection loss.
- Radiators: sub-monolayer dust significantly degrades AZ-93 and Ag/FEP (S062).
- EDS: first lunar demonstration on Blue Ghost M1 (2025) (S019); ≈ 3.3 mWh/m² per daily cleaning cycle
  (S063) — negligible energy, but requires kV electronics and patterned transparent electrodes.
- Mechanisms: dust infiltration limits range, raises torque, reduces life (S021).

## 9. Avionics, autonomy, communications (Directive §20–22)

- **HPSC** (S039): ≈ 100× current rad-hard performance, rad-hard variant 100 krad TID; completing
  qualification in 2026 — plausible baseline for the 2030s.
- **CADRE** (S069): multi-robot autonomy with mesh radios (demonstration 2026). **Nokia LSCS** (S068):
  LTE surface network precedent. **Moon Base Phase 2** comm towers ≈ 10 km radius (S054).
- **LunaNet** (S017) and **Moonlight** (S018): relay services from ~2028–2030; DTE availability at the
  pole ≈ 51 % (S073) → store-and-forward/DTN mandatory.

## 10. Recovery / anchoring (Directive §6B, §27)

- No lunar vehicle recovery has ever been attempted. Anchoring research exists for legged/tethered
  rovers (S045) but **no quantitative lunar-regolith anchor holding capacity was retrieved**. Anchor
  capacity in TSR-1 models is therefore derived from first-principles soil mechanics (passive earth
  pressure / plate-anchor breakout theory, L001/S023 parameters) and carried as a low-TRL item with
  wide uncertainty.

## 11. Gaps in the evidence base (feeds `docs/limitations.md`)

1. Full texts of S002 (robotic interface best practices) and the LTV SRD were not read; numeric
   interface rules could not be extracted.
2. Seed NTRS 20260001878 could not be resolved.
3. No lunar infrastructure failure-rate data exist; ISS ORU data were not retrievable in tabular form.
4. No quantitative regolith anchor capacity, lunar winch heritage, or lunar-g towing test data.
5. Launch/landing load factors for candidate landers were not retrieved (assumption + sensitivity).
6. Factors of safety and MGA percentages beyond the harness row are literature-recall values.
