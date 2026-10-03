# NASA / ESA / International Context for TSR-1

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other
> organizations are used solely as technical and architectural context. TSR-1 is **not** a NASA, ESA,
> JAXA, CSA or commercial-partner project and has no endorsement from any of them.

Baseline: 3 October 2026. Sources: see `source_register.csv`.

## 1. Programme landscape relevant to a servicing rover

| Programme / element | Owner | Status (Oct 2026) | Relevance to TSR-1 | Source |
|---|---|---|---|---|
| Moon Base Program (Phases 1–3) | NASA | Announced Mar 2026; Phase 1 under way | Defines the infrastructure TSR-1 would serve; Phase 2 (2029–2032) installs power, comm towers, mobility | S006, S054 |
| Lunar Utility Rover (robotic logistics mobility) | NASA (architecture element) | Added in 2025 architecture update; no procurement found | **Direct overlap**: cargo repositioning + maintain/repair/service | S004, S005 |
| Lunar Terrain Vehicle (CLV-1, Pegasus) | NASA / Astrolab, Lunar Outpost | Phase-1 orders May 2026; delivery 2028 | Crew vehicle with uncrewed/autonomous modes; possible host for service kits; potential recovery client | S007, S036, S055 |
| Pressurized Rover (Lunar Cruiser) | JAXA / Toyota | Phase-2 contribution | Large, high-value asset; GITAI arm for self-inspection | S058 |
| VIPER | NASA | Revived; Blue Origin delivery 2027 | Representative small science rover (recovery Scenario A/B client) | S035 |
| CADRE | NASA JPL | IM-3, 2026 | Multi-robot autonomy precedent | S069 |
| MoonFall drones | NASA JPL / Firefly | NET 2028 | Aerial inspection competitor for *imaging-only* tasks | S007 |
| Fission Surface Power / Lunar Reactor-1 | NASA / DOE | Industry call 2025; FY2030 target | Grid anchor; 120 VDC user interface via converters | S009, S012 |
| Lunar grid (3 kVAC + UMIC) | NASA GRC | Technology development | Defines TSR-1 charging/emergency-power interface | S012 |
| ISPSIS 120 VDC | International partners | Rev A 2022 | **Baseline TSR-1 power interface standard** | S011 |
| IERIIS / ISO 9409-1 | International partners | Baseline 2019 | Robotic interface classes | S013 |
| NASA/SP-20260001900 | NASA JSC | Published Mar 2026 | Surface robotic interface best practices | S002 |
| LunaNet / LCRNS | NASA SCaN | LNIS v4; relay services procurement | Comms/PNT interoperability | S017 |
| Moonlight / Lunar Pathfinder | ESA / SSTL | Pathfinder ops 2026; services end-2028 | Relay/PNT | S018 |
| Argonaut (EL3) | ESA / Thales Alenia Space | First mission 2030; 1.5 t cargo | Candidate TSR-1 delivery vehicle | S047 |
| HOTDOCK | Space Applications Services (EU) | Ground demonstrations; H2020 standard | Candidate androgynous service interface | S048 |
| EDS | NASA KSC | Lunar demo 2025 (Blue Ghost M1) | Dust self-protection and external cleaning | S019, S063 |
| LSMS | NASA LaRC | Prototype/ground | Crane-manipulator alternative to a heavy arm | S015 |
| COLDArm / BMG gears | NASA JPL | Ground demo | Heaterless cold actuators | S040 |
| HPSC | NASA / Microchip | Qualification 2026 | Avionics compute baseline | S039 |

## 2. Where TSR-1 overlaps, complements, or duplicates

- **Overlap (high):** NASA Lunar Utility Rover concept (maintain/repair/service + cargo). If NASA
  procures a utility rover with an integrated manipulator, TSR-1's *servicing* role is largely
  duplicated. TSR-1's distinct elements would then be recovery/towing hardware, a
  bidirectional 120 VDC emergency-power module, and a multi-standard servicing tool set — all of
  which could be packaged as **modules for a utility-rover-class chassis** (see TS-07, CDR-01).
- **Overlap (medium):** LTV uncrewed mode (FLEX/CLV-1 explicitly offers robotic cargo-hauler mode and
  robotic payload interfaces). LTV is optimised for crew transport; its availability for servicing is
  limited by crew-mission priority, and it carries no recovery or emergency-power function per the
  public requirement summaries.
- **Complementary:** MoonFall drones (aerial imaging/inspection only, no contact work); CADRE-class
  small rovers (scouting); fixed infrastructure robots (e.g., arms on landers or habitats).
- **Unique to the TSR-1 hypothesis (not found in any surveyed element):** dedicated vehicle-recovery
  capability (winch + ground reaction), bidirectional ISPSIS emergency power with thermal life
  support of disabled assets, and an explicit multi-compatibility-level servicing doctrine.

## 3. Implications adopted by the study

1. Do not design a proprietary interface ecosystem: power = ISPSIS 120 VDC; data = LunaNet/DTN +
   standard surface networks; mechanical = ISO 9409-1/IERIIS-derived with adapters.
2. Treat the Lunar Utility Rover as the **baseline competitor** in the value model and CDR.
3. Size TSR-1 to fit an Argonaut- or Mk1-class lander; reject configurations requiring Starship-class
   delivery unless mass analysis forces it (and then report that as a negative finding).
