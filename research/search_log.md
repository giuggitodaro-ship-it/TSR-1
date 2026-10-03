# Research search log (traceability record)

**Purpose.** Records every literature query made during the TSR-1 study, the source(s) located, and the
excerpt-level facts extracted. This is the raw evidence trail behind `source_register.csv`.

**Access limitation (important).** During this study session the container's network egress policy
blocked direct retrieval from `ntrs.nasa.gov`, `www.nasa.gov`, `www.esa.int`, `arxiv.org`,
`en.wikipedia.org`, `lsic.jhuapl.edu`, `standards.nasa.gov`, `ecss.nl` and other hosts (HTTP 403 at the
egress proxy, logged 2026-10-03). Only a search-engine interface was available. Therefore:

- Facts below are taken from **search-engine excerpts of the named primary document**, not from a
  full-text read, unless stated otherwise. Verification level is recorded per source in
  `source_register.csv` (`verification` column):
  - `EXCERPT` — fact quoted/paraphrased in search excerpt attributed to the primary document URL.
  - `SECONDARY` — fact reported by a secondary outlet (news, trade press) about a primary event.
  - `LITERATURE-RECALL` — well-established handbook/literature value used by the engineering team
    from prior knowledge of the published work; exact page/table must be re-checked against full text
    before any use beyond this conceptual study. These are flagged in the parameter register.
- No number has been invented. Where no source exists, values are labelled ENGINEERING ASSUMPTION.

---

## Q01–Q03 Seed documents
- **S001** Surface Systems Capability Gaps for Enabling NASA's Sustainable Lunar Operations. IEEE Aerospace
  Conf. 2022 (IEEE Xplore 9843600); NTRS 20220002618. *The directive gives NTRS 20210022361; the search
  engine resolves the same title to NTRS 20220002618 — likely the same work (abstract vs. final record).
  Discrepancy recorded, not resolved.* Excerpt: TX-13 (Ground, Test and Surface Systems) gaps.
  Architecture gaps: standardized architectures and interfaces; multi-element SE&I; design for
  supportability. Technology gaps (uncrewed surface operations focus): autonomous cryogenic servicing;
  **health determination and fault management; automated/autonomous planning and scheduling;
  automated/autonomous inspection, maintenance and repair; logistics management and reliability**;
  launch/landing site preparation; commodity management; **advanced umbilicals and dust tolerant
  interfaces**. Rationale text: infusing automation/autonomy early reduces "reliance on humans to
  perform tasks" and accommodates ground communication delays.
- **S002** Lambert, R.D., Visinsky, M.L., Jerome, T.J., Amick, R.Z., Dunkelberger, N.B., Wright, M.D.
  *Robotic Interface Best Practices and Lessons Learned for Surface Operations*, NASA/SP-20260001900,
  NASA JSC, 4 Mar 2026 (NTRS 20260001900). Excerpt: guidance for designing interfaces between robotic
  systems, crew operations and cargo/payloads on lunar/Martian surface; draws on terrestrial and LEO
  robotic experience; aims at interoperable robotic systems "compatible with the widest range of
  potential robots". **Full text not retrieved — specific numeric interface rules could not be
  extracted.**
- **S003** NTRS 20260001878 (lunar dust management and equipment longevity) — **not resolvable by search**
  in this session. Related dust documents located instead: S020 (NASA Lunar Dust Mitigation Roadmap,
  Fall 2024, NTRS 20240013978), S021 (Lunar Dust Considerations for Vertical Solar Arrays, NASA
  TM-20240003496 — dust infiltration limits mechanism range, increases torque, reduces lifetime),
  S022 (Gaier 2005, The Effects of Lunar Dust on EVA Systems During the Apollo Missions,
  NASA/TM-2005-213610, NTRS 20050160460).

## Q04–Q10 Current NASA programme context (2025–2026)
- **S004** NASA, *2025 Moon to Mars Architecture update* (Dec 2025,
  nasa.gov/wp-content/uploads/2025/12/2025-architecture-update-for-publication.pdf). Excerpt: in 2025
  NASA added two new elements: **a robotic mobility system to move logistics around the lunar surface**
  and a nuclear fission power system providing external power augmentation.
- **S005** NASA, *Lunar Logistics, Mobility, and Cargo* white paper, Feb 2025 Architecture Workshops.
  Excerpt: LTV and Pressurized Rover are "primarily for crew transportation, with limited cargo mobility
  functions"; CLPS provides only small-scale mobility; cargo must move from point of delivery to point
  of use; a **Lunar Utility Rover** would reposition 100s of kg (limited) and 1000s of kg (moderate)
  cargo in the south-pole region and "could support continuous presence ... with capabilities to
  **maintain, repair, and service** other exploration systems".
- **S006** NASA "Ignition" event / Moon Base plan, 24 Mar 2026 (Spaceflight Now 25 Mar 2026; CNN
  24 Mar 2026; ABC). Secondary: ~US$20 billion over 7 years; Moon Base near lunar south pole with
  habitats, pressurized rovers, nuclear and solar power; Gateway "paused" and components repurposed;
  three phases: Phase 1 (to ~2028) high landing cadence, rovers, instruments, tech payloads; Phase 2
  (2029–early 2030s) permanent infrastructure incl. **power grid** and fission reactor; Phase 3 (2030s)
  extended crew stays. Moon Base Program consolidates non-Artemis lunar programmes (NASA "Moon Base –
  About" page, nasa.gov/reference/moonbase-about/).
- **S007** NASA news release, *NASA Provides Update on Moon Base Rovers, Landers, Missions*, 26 May 2026.
  Excerpt: LTV Phase 1 task orders to **Astrolab (US$219 M, CLV-1)** and **Lunar Outpost (US$220 M,
  Pegasus)**, firm-fixed-price, delivery by 2028 via CLPS (Blue Origin delivery reported); Pegasus
  capable of manual, autonomous or tele-operated control; Moon Base I (Blue Origin Mk1, Shackleton
  connecting ridge, NET autumn 2026); Moon Base II (Astrobotic Griffin, >500 kg cargo incl. Astrolab
  FLIP rover); Moon Base III (IM Nova-C, Lunar Vertex); MoonFall drones (Firefly/JPL, NET 2028).
- **S008** NextSTEP-3 Appendix B: Moon Base Demonstrations (solicitation 80MSFC26R0003). Excerpt:
  TRL ≥ 6 system-level integration and lunar demonstrations; first directed topic: **surface power**.
- **S009** Fission Surface Power RFI/AFPP 2025 (Military & Aerospace Electronics; Aerospace America).
  Secondary: ≥ **100 kWe**, < 15 t, closed Brayton cycle, launch readiness Q1 FY2030; Dec 2025
  executive order: initial elements of lunar surface base by 2030; NASA–DOE "Lunar Reactor-1".
- **S010** NASA *2026 Civil Space Shortfalls* (released 12 Jan 2026) and *FY26 Civil Space Shortfall
  Prioritization* (May 2026). Secondary/excerpt: #1 integrated shortfall Thermal-1618 "survive and
  operate through the lunar night"; #2 high-power energy generation on Moon/Mars; #3 high-performance
  spaceflight computing; highly ranked: autonomous robotics, in-space maintenance and repair, dust-
  driven wear, cold-tolerant mobility, charge dissipation, PMAD.

## Q11–Q16 Power and robotic interface standards
- **S011** *International Space Power System Interoperability Standards (ISPSIS)*, Rev A, 27 Jul 2022
  (internationaldeepspacestandards.com). Excerpt: defines bus voltages, power quality and single-point
  grounding for **120 VDC and 28 VDC** systems for interoperability between orbital habitats, vehicles,
  ascent/descent vehicles and **surface systems**; "120 VDC is the Interoperability Power Standard for
  vehicle-to-vehicle and element-to-element interfaces".
- **S012** Csank, J. et al., NASA GRC, *Electric Power on the Moon / Lunar Surface Power* presentations
  (NTRS 20250000763, 20240013588, 20240008802 IAC-2024). Excerpt: "Power exchange must occur at
  **120 VDC and a distance less than 100 m (limitation of 120 VDC)**"; trade identified **3 kV AC** as
  ideal transmission voltage for an Artemis-scale grid; **Universal Modular Interface Converter (UMIC)**:
  bidirectional, 120 VDC bus ↔ medium/high-voltage 3-phase AC grid, boost/buck 100–1500 VDC, demo
  scale up to 2 kW over up to 2 km; grid transmission up to 10 km in early Artemis; demand 100s kW.
- **S013** *International External Robotic Interface Interoperability Standards (IERIIS)*, baseline
  Mar 2019 (internationaldeepspacestandards.com). Excerpt: common generic mounting interfaces for all
  external robotic interface classes; interchangeability consistent with **ISO 9409-1**; Large
  Fixture Interfaces for handling vehicles/modules/large payloads or as robotic bases.
- **S014** International Docking System Standard surface variant (IDSS-S) under consideration at JSC
  (NTRS 20220011643 IDSS IDD Rev F context; NASA "surface mating" page). Excerpt: TRL 9 estimated 2031
  for surface standard docking (pressurized) — relevant only as a precedent for surface standards.
- **S015** NASA LaRC *Lunar Surface Manipulation System (LSMS)* (technology.nasa.gov LAR-TOPS-73).
  Excerpt: crane/manipulator hybrid for lander offloading, transport, installation and "service and
  replacement during component life"; device mass ≈ **3 % of heaviest tip payload** (1.8 % at
  mid-span) for advanced-structure variant; tension/compression truss with spreaders.
- **S016** GITAI datasheets (gitai.tech). Inchworm robot: 2 m, 50 kg, 7 DOF, 2 grapple end-effectors,
  **5.0 kg payload** (as listed). GITAI Lunar Rover R1: 1.6×1.4×1.9 m, **220 kg**, wheels 0.40×0.15 m,
  two arms. JAXA contract (Mar 2025) for arm on pressurized rover concept.

## Q17–Q20 Communications and navigation
- **S017** NASA *LunaNet Interoperability Specification (LNIS) v4*, effective 14 Dec 2022; NASA *Lunar
  Relay Services Requirements Document (SRD)* (Aug 2025); LCRNS project (lcrd.gsfc.nasa.gov). Excerpt:
  LNIS is the agreed set of standards/protocols making NASA LCRNS, ESA and JAXA services function as one
  network; LCRNS commercial service (Near Space Network) once validated.
- **S018** ESA *Moonlight* programme press release (Oct 2024). Excerpt: 5 satellites (4 navigation, 1
  communications), south-pole coverage priority; Lunar Pathfinder (SSTL) relay operations from 2026;
  initial services end-2028, full operation 2030.

## Q21 Dust shield flight demonstration
- **S019** NASA, *NASA's Dust Shield Successfully Repels Lunar Regolith on Moon* (2025) — EDS on Firefly
  Blue Ghost Mission 1 (mission ended 16 Mar 2025): first lunar demonstration; regolith removed from
  glass and thermal-radiator samples. Earlier ISS (MISSE) testing reported >99 % removal in vacuum
  (excerpt, AIAA 2025-99748 review). **No quantitative lunar removal efficiency or power figure
  retrieved.**

## Q22–Q32 Lunar environment, terramechanics, heritage mobility
- **S023** Carrier, W.D. III, Olhoeft, G.R., Mendell, W. (1991) *Physical Properties of the Lunar Surface*,
  ch. 9 in Heiken, Vaniman & French (eds.) *Lunar Sourcebook*, CUP/LPI. Excerpts: **Table 9.14
  recommended trafficability parameters: c = 0.017 N/cm² (170 Pa), φ = 35°, K = 1.78 cm, n = 1,
  k_c = 0.14 N/cm² (1.4 kN/m²), k_φ = 0.82 N/cm³ (820 kN/m³)** (also reported as 830 kN/m³ in some
  secondary tabulations); recommended in-situ properties by depth: **0–15 cm ρ = 1.50 g/cm³,
  c = 0.52 kPa, φ = 42°; 0–30 cm ρ = 1.58 g/cm³, c = 0.90 kPa, φ = 46°**; design rule from Apollo/
  Lunokhod experience: "almost any vehicle with round wheels will perform satisfactorily ... provided
  the **ground contact pressure is no greater than about 7–10 kPa**".
- **S024** Carrier, W.D. III, *Lunar Soil Simulation and Trafficability Parameters* (LPI web document;
  Lunar Geotechnical Institute). Same Table 9.14 set; definitions of K, n, k_c, k_φ.
- **S025** Connolly, J. & Carrier, W.D., *An Engineering Guide to Lunar Geotechnical Properties*, IEEE
  Aerospace Conf. 2023 (NTRS 20220014634). Excerpt: summary of particle size, shape, bulk density, shear
  strength, cohesion, bearing strength and depth dependence.
- **S026** Colwell, J.E. et al. (2007) *Lunar surface: dust dynamics and regolith mechanics*, Rev.
  Geophys. 45, RG2006 — reproduces the Lunar Sourcebook depth table (excerpt).
- **S027** NASA NSSDC *The Apollo Lunar Roving Vehicle* page + secondary compilations. LRV: empty mass
  **210 kg**, payload **490 kg**; slopes **25°** climb/descend; obstacles 30 cm; wheels **81.8 cm
  diameter × 23 cm wide**, woven piano-wire mesh; each wheel DC series motor **0.25 hp (≈186 W)**,
  10 000 rpm, **80:1 harmonic drive**; two **36 V** Ag-Zn batteries, 121 A·h (stated capacity);
  frame 2219 aluminium tubing welded assemblies.
- **S028** Costes, N.C. et al. (1972) *Mobility Performance of the Lunar Roving Vehicle: Terrestrial
  Studies – Apollo 15 Results*, NASA TR R-401 (existence/scope confirmed; numerical content not
  retrieved). **S029** Asnani, V., Delap, D., Creager, C. (2009) *The Development of Wheels for the
  Lunar Roving Vehicle*, NASA/TM (NTRS 20100000019) — existence confirmed.
- **S030** Gläser, P. et al. (2014) *Illumination conditions at the lunar south pole using high
  resolution Digital Terrain Models from LOLA*, Icarus 243, 78–90, doi:10.1016/j.icarus.2014.08.013.
  Excerpt: best Connecting-Ridge locations sunlit **92.27 % of time at 2 m** and **95.65 % at 10 m**
  above ground (19-yr simulation); **longest continuous darkness typically 3–5 days**. **S031**
  Mazarico, E. et al. (2011) *Illumination conditions of the lunar polar regions using LOLA
  topography*, Icarus 211, 1066–1081 (240 m DTM; long-period simulation) — existence confirmed.
- **S032** Paige, D.A. et al. (2010) *Diviner Lunar Radiometer observations of cold traps in the Moon's
  south polar region*, Science 330, 479–482. Excerpt: PSR daytime brightness temperatures below
  ~35–40 K in places; LCROSS impact site subsurface ≈ 38 K. Secondary (LPI south-pole page): sunlit
  elevated rims often > 223 K, peaks up to ~300 K. NASA 2026 shortfall text: "−245 °C during lunar
  night" (≈ 28 K) used as cold bound.
- **S033** Zhang, S. et al. (2020) *First measurements of the radiation dose on the lunar surface*,
  Science Advances 6, eaaz1334. Excerpt: Chang'e-4 LND, absorbed dose rate in silicon **13.2 ± 1 µGy/h**,
  neutral-particle dose rate 3.1 ± 0.5 µGy/h, dose equivalent 1369 µSv/day (solar minimum, GCR).
- **S034** NASA Artemis III landing-region analyses (LPSC 2024 abstract 1695; Acta Astronautica 2024
  multi-criteria paper; NASA region announcement Oct 2024). Excerpt: HLS landing slope threshold
  **≤ 8°** (goal ≤ 5°); slope maps from 20 m/px LDEM; 13 regions (2022) narrowed to 9 (Oct 2024).
- **S035** VIPER (NASA ARC; mission overview NTRS 20205000864; Moog avionics selection). Excerpt/
  secondary: ≈ **430 kg**, 4 wheels **0.5 m** diameter, designed for **15°** slopes with ease and
  **25–30°** if needed; peak power ≈ 450 W; survive up to **50 h darkness** on full charge; project
  terminated Jul 2024, revived; Blue Origin selected 19 Sep 2025 for 2027 delivery.
- **S036** LTV System Requirements (as summarized from NASA LTVS RFP/SRD, 2023; NASA news release
  "NASA Pursues Lunar Terrain Vehicle Services"): 10-yr crewed/uncrewed operations; survive lunar night
  (≈ 50 K) and extended shadow; up to **2 h in PSRs**; ≥ **800 kg** payload over **20 km** per charge;
  remote traverse **6 km (threshold)/8 km (goal) per 24 h**; available ≥ 8 h per Earth day.
  *SECONDARY verification — SRD not read in full.* Secondary (2026): each LTV ~800 mi/yr, ~12 mi/day per
  charge, ≥ 1765 lb payload. Pegasus (Lunar Outpost): operational up to 1 year, manual/autonomous/
  teleoperated, > 9 mph. Eagle: survives to −173 °C ambient (company claim).
- **S037** Astrolab FLEX (company page): **1600 kg** payload, > 3 m³; robotic docking to payloads at
  three interfaces (two top, one below), "intermodal" lander↔rover payload interface.

## Q33–Q40 Hardware heritage
- **S038** Space Li-ion cells/packs (EaglePicher, Saft datasheets via satnow/satsearch): Saft VES16
  4.5 A·h, 16 Wh, 155 g (**≈103 Wh/kg cell**); EaglePicher SLC-16050 **121 Wh/kg**, SLC-21060
  **132 Wh/kg**, LP-33165 (lunar) **109 Wh/kg**; EaglePicher COTS-18650 satellite batteries **75–100
  Wh/kg pack level**.
- **S039** Microchip PIC64-HPSC (NASA HPSC). Excerpt: ~100× (reported up to ~500×) performance of
  current rad-hard processors; rad-hard variant **100 krad(Si) TID, SEL 78 MeV·cm²/mg**; rad-tolerant
  50 krad, 42 MeV; HPSC requirement 200 krad; as of Mar 2026 still completing qualification testing.
- **S040** NASA JPL COLDArm / BMG gears (NASA Spinoff; JPL PIA24567). Excerpt: bulk-metallic-glass gear
  motors operated at **≈ −173 °C without heaters**, no wet lubricant; integrated into COLDArm joints 2022.
- **S041** Braycote 601EF (Castrol; MSL usage): rated **−80 °C to 204 °C**; MSL robotic-arm actuators
  minimum operating AFT **−55 °C** requiring warm-up heaters (excerpt).
- **S042** Dust-tolerant connectors: Honeybee Robotics DTC (LSIC Surface Power, 26 Jun 2024) — **> 500
  mate/demate cycles in vacuum with regolith simulant without degradation**; NASA SBIR to Yank
  Technologies (2025) for dust-tolerant (wireless/inductive) kW-class power links; KSC dust-tolerant
  connector patent US 8,011,941.
- **S043** Reduced-gravity traction: Kobayashi, T. et al. (2010) *Mobility performance of a rigid wheel
  in low gravity environments*, J. Terramechanics 47, 261–274; Wong, J.Y. (2012) *Predicting the
  performances of rigid rover wheels on extraterrestrial surfaces based on test results obtained on
  earth*, J. Terramechanics 49, 49–61. Excerpt: lunar-g parabolic tests show **≈ 20 % lower drawbar
  pull and up to 40 % higher sinkage** than 1-g tests at equal wheel load; Wong hypothesizes a
  gravity-proportional pressure-sinkage coefficient.
- **S044** Reduced-gravity grouser test (CMU/GRC, IEEE Aero 2012, Moreland et al. / "Soil behavior of
  wheels with grousers"): **DP/W = 0.11 ± 0.02 at 20 % slip in lunar gravity on GRC-1**
  (23 cm rigid grousered wheel).
- **S045** JPL Axel/DuAxel tethered extreme-terrain rover (JPL Robotics). Tether provides mechanical
  support on steep slopes; DuAxel acts as anchor; "Dynamic Anchoring in Soft Regolith: Testing and
  Prediction", ASCE J. Aerosp. Eng. (anchor geometries with sufficient holding force for legged
  rovers) — **no quantitative anchor holding force retrieved**.
- **S046** MER Spirit embedding at "Troy" (2009, permanent) after right-front wheel failure (2006);
  Opportunity "Purgatory" dune extraction (2005) took > 5 weeks of planning/testing.

## Q41–Q60 Programme scale, logistics, standards, reliability
- **S047** ESA Argonaut / European Large Logistics Lander (ESA multimedia Nov 2025, Jul 2026 PATP
  signature). Excerpt: up to **1.5 t** cargo to lunar surface per lander; first mission **2030**;
  Ariane 6; ~250 m landing accuracy; up to 5 years surface life (reported); Thales Alenia Space prime.
- **S048** HOTDOCK standard robotic interface (Space Applications Services product sheet; IAC-2020
  paper 60218). Excerpt: androgynous, 90° symmetric; mechanical, power, data and (optional fluidic)
  thermal coupling; mating cone up to 130°; spring-loaded pogo-pin central connection plate; selected
  as standard interface in EU H2020 space-robotics projects. **No load/mass numbers retrieved.**
- **S049** ISS maintenance experience (NASA, *On-Orbit Maintenance Operations Strategy for the ISS*,
  NTRS 20100042525, and NASA-STD-3001 technical brief OCHMO-TB-036 "Design for Maintainability").
  Excerpt: first five years of ISS: > **4000 h** crew maintenance; **421 h EVA maintenance, 777 h
  EVR (robotics), 2536 h IVA**; ≈ 1.9 h per workday; exceeded design estimates; ISS manages > 6000
  ORU types.
- **S050** *Assessment of Crew Time for Maintenance and Repair Activities for Lunar Surface Missions*,
  IEEE Aerospace Conf. (NTRS 20210026843). Excerpt: expected corrective-maintenance crew time
  **> 24 h per (Surface Habitat) mission**; methodology from ISS empirical data.
- **S051** *Uncrewed Lunar Surface Operations and Support Activities* (NTRS 20220013667). Excerpt:
  balance of crewed/uncrewed operations maximizes crew exploration time; example robotic surface
  actions: lifting/handling, servicing, powering, traversing, inspecting, cleaning, maintaining,
  safing; objectives include **increasing availability of surface infrastructure** and reducing O&M
  cost.
- **S052** ANSI/AIAA S-120A-2015 *Mass Properties Control for Space Systems*. Method confirmed: MGA by
  hardware category × design maturity, depleting through milestones; excerpt of Table 1 gives wire
  harness MGA **60 → 30 → 25 → 10 %** across maturity classes. Other category values not retrieved.
  NASA/SAWE mass-growth history study (NTRS 20205003211) exists.
- **S053** NASA-STD-5001B w/Change 3 (2022-10-24) *Structural Design and Test Factors of Safety for
  Spaceflight Hardware*; ECSS-E-ST-32-10C *Structural factors of safety*. Existence confirmed; numerical
  factors used in this study are **LITERATURE-RECALL** (metallic yield 1.25 / ultimate 1.4 with test
  verification) and must be confirmed against the standard text.
- **S054** NASA *Moon Base Phases* page / Astronomy.com (2026). Secondary: Phase 1 (to 2028/29):
  ~21 landings across 25 missions; **Phase 2 (2029–2032): demonstration solar arrays > 10 kW with
  storage on ridgelines; small RTGs (few hundred W) for PSR assets; communications towers each
  ≈ 10 km radius; JAXA pressurized rover; 27 launches/24 landings ≈ 60 000 kg delivered**; Phase 3
  (2032+): permanent habitats, large nuclear. NASA *Moon Base Systems* and *Lunar Surface Technology*
  pages (nasa.gov) describe power, comms, mobility, habitat element families.
- **S055** LTV Phase-1 award details (NASA 26 May 2026; NASASpaceflight; Register): > 14.5 km/h,
  > 200 km lifetime traverse for initial units; Blue Origin task order US$188 M (+US$280.4 M option)
  to deliver LTVs on Blue Moon Mk1. Astrolab CLV-1 derived from FLEX; uncrewed cargo-hauler mode.
- **S056** Blue Origin Blue Moon Mk1: up to **3.0 t** payload to lunar surface (reported).
  **S057** Astrobotic Griffin: **625–650 kg** payload (reported); Astrolab FLIP ≈ 500 kg mass, 30 kg
  payload.
- **S058** JAXA/Toyota Lunar Cruiser pressurized rover: ≈ 6 × 5.2 × 3 m, ≈ 10 t loaded, fuel cells;
  GITAI robotic arm with grapple end-effector tool exchange for vehicle inspection/maintenance;
  JAXA provides PR in Moon Base Phase 2.
- **S059** NASA LSII strategy (NTRS 20240008865): thrust areas — sustainable power, dust mitigation,
  ISRU, excavation/construction/outfitting, extreme access/environments; LSIC key capability areas
  include logistics, robotics and autonomy.

## Q61–Q88 Thermal, dust, sensors, comms, power storage, standards
- **S060** Apollo LRV energy use (Apollo Lunar Surface Journal, Apollo 17 close-out; NSSDC). Excerpt:
  Apollo 17 drove **36.0 km using 57.2 A·h** (rover) of 242 A·h available → **1.58 A·h/km**;
  Apollo 15 **1.67 A·h/km**; Apollo 16 ≈ 2× (unexplained malfunction). At 36 V nominal this is
  **≈ 57–60 Wh/km** for a loaded LRV (≈ 700 kg class: 210 kg + crew + payload).
- **S061** *Micrometeoroid Impact Rate Analysis for an Artemis-Era Lunar Base* (arXiv:2511.04740, 2025),
  using NASA MEM 3. Excerpt: ISS-sized base (100 × 100 × 10 m) receives **≈ 15 000 impacts/yr at the
  south pole** (≈ 23 000 at sub-Earth maximum) for 10⁻⁶–10 g; Whipple-penetrating threshold 0.07 g;
  ~1 penetrating strike per 42 yr at the pole for that base.
- **S062** Gaier, J.R. et al., dusted thermal control surfaces (NTRS 20110013486 and TFAWS 2024 paper
  PT-4). Excerpt: **sub-monolayer** dust significantly degrades AZ-93 and Ag/FEP; emissivity −16 %
  (AZ-93) / +11 % (Ag-FEP); solar absorptance modification factor **1.4–2.6 at 25 % coverage**, up to
  ~5 for 140–840 µg/cm².
- **S063** EDS technical papers (NASA KSC, Calle et al.; NTRS 20120003264, 20200000920). Excerpt:
  ≈ **3.3 mWh/m² per daily cleaning cycle**; voltages 0.8–10 kV, 10–500 Hz tested; ~4 kV p-p at
  500 Hz for fine adhesive dust; later coatings at half voltage, 90 % thinner.
- **S064** VIPER Visible Imaging System (NASA). Excerpt: 8 cameras — NavCam stereo pair on gimballed mast
  (pan 400°, tilt 75°, **70° FOV**), AftCam stereo pair, 4 HazCams; **detect 10 cm rocks at 15 m**;
  blue LED headlights; hazard lights.
- **S065** Northrop Grumman LN-200S IMU datasheet: **0.75 kg, 12 W**, FOG + MEMS accelerometers;
  heritage Spirit, Opportunity, Curiosity, Perseverance.
- **S066** Perseverance arm (JPL press kit): **≈ 2 m (7 ft)** long, turret **45 kg**; Motiv xLink
  (company): 7-axis, **50 kg payload** (environment unspecified), Mars 2020 heritage.
- **S067** Dextre/SPDM (CSA): ≈ **1662 kg**, two 7-joint arms, OTCM end-effectors (jaws, retractable
  socket drive, camera, lights, power/data/video umbilical) for ORU change-out.
- **S068** Nokia Lunar Surface Communication System (Nokia/IM, Jan 2025): first 4G/LTE network on IM-2
  Athena lander with device modules in IM Micro-Nova hopper and Lunar Outpost MAPP rover.
  (IM-2 landed tipped over in Mar 2025; full network demonstration outcome not retrieved.)
- **S069** NASA CADRE (JPL): three small autonomous rovers, mesh radios, lander base station, one lunar
  day, IM-3 (Reiner Gamma, 2026).
- **S070** NASA JSC 18650 Li-ion PPR batteries (NTRS 20170001655, 20190014045, 20180004170). Excerpt:
  Orion-type partially conductive design **150–160 Wh/kg**, thermally isolated designs **160–170
  Wh/kg** pack level; goal > 160 Wh/kg, 200 Wh/L; passive propagation resistance (Al interstitial
  heat sinks, 0.5 mm spacing, mica sleeves, individually fused cells).
- **S071** JPL Li-ion for Mars landers/rovers (SAE 1999-01-1390; MER). Excerpt: MER battery charge
  **0–25 °C**, discharge **> −20 °C**; 16 A·h at RT, 10 A·h at −20 °C.
- **S072** NASA NPR 7123.1 Appendix E TRL definitions (via NASA/NAP reproductions). TRL 6 definition
  confirmed (high-fidelity prototype in relevant environment).
- **S073** JPL IPN Progress Report 42-176 (lunar south pole communications). Excerpt: proposed south-
  pole sites have **≈ 51 % average DTE availability**; relay coverage needed for the remainder.
- **S074** Gaier, J.R. (2005) NASA/TM-2005-213610 (= S022). Excerpt: nine dust-effect categories
  (vision obscuration, false instrument readings, dust coating/contamination, loss of traction,
  clogging of mechanisms, abrasion, thermal control problems, seal failures, inhalation/irritation);
  LRV fender-extension loss on Apollo 16/17 → "rooster tail" dust, **LRV batteries exceeded
  thermal limits** owing to dust on radiators; simple measures ineffective against clogging,
  abrasion, heat-rejection loss.
- **S075** OrbitBeyond, Firefly, Astrobotic, New Glenn payload user guides (existence; define
  quasi-static, sine, random and acoustic environments). **No numerical load factors retrieved** —
  TSR-1 launch loads are therefore an explicit ENGINEERING ASSUMPTION with sensitivity cases.
