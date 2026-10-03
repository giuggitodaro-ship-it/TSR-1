# TSR-1 Interface Definition (preliminary)

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other
> organizations are used solely as technical and architectural context.

Principle (MR-12): TSR-1 adopts existing/open interface standards and carries **adapters** rather than
defining a proprietary ecosystem. Where no standard exists (lunar surface robotic servicing), TSR-1
defines a minimal *recommended* interface and treats compatibility level (L0–L3, ConOps §5) as an
explicit variable in the value model.

## 1. External interfaces

| ID | Interface | Counterpart | Standard / basis | TSR-1 provision | Key parameters |
|---|---|---|---|---|---|
| EI-01 | Power exchange port | grid charging nodes, serviced assets, peer TSR | ISPSIS Rev A 120 VDC (S011); exchange < 100 m (S012) | PTM (isolated, bidirectional) + 25 m tether + dust-tolerant connector head on dexterous arm | 120 VDC; 3 kW continuous each direction; 4.5 kW for 60 s; single-point ground at TSR battery return; insulation monitor; pre-charge/inrush limiting; contact-resistance check before energising |
| EI-02 | Grid connection (indirect) | lunar grid 3 kVAC | NASA GRC grid + UMIC (S012) | none on TSR-1: the node's UMIC-type converter provides 120 VDC | TSR-1 never connects to the AC grid directly |
| EI-03 | Robotic mechanical interface (asset side) | L2/L3 ORUs, panels | IERIIS classes, ISO 9409-1 (S013); NASA/SP-20260001900 practices (S002) | tool changer with ISO 9409-1 bolt pattern; adapters: OTCM-type grapple/socket, androgynous (HOTDOCK-class, S048), payload-deck (FLEX-class, S037) | recommended ORU: robot handle + captive fastener(s) ≤ 50 N·m, guide pins with ≥ 5 mm capture, fiducial marker, blind-mate connector |
| EI-04 | Data interface (asset health) | L3 assets | LunaNet/CCSDS + DTN (S017, L020); recommended local wired port | electrical diagnostic unit + umbilical through connector head; wireless via surface network | DTN bundles; health-telemetry dump; command authority only via asset owner's keys |
| EI-05 | Diagnostic probing | L1+ assets | none (TSR-1 recommendation) | electrical probe tool | voltage/current/insulation-resistance measurement; ≤ 150 V |
| EI-06 | Tow / recovery points | rovers, LTVs, landers | none (TSR-1 recommendation: tow eye rated ≥ 4 kN with marked load path) | shackle/hitch tool, slings, 4 kN winch, 50 m line | line pull ≤ 4 kN (load-limited); for L0 assets: attach only to members identified as load paths by inspection |
| EI-07 | Communications | base surface network, relay, peer mesh, Earth | LunaNet LNIS v4 (S017); CCSDS Proximity-1, DTN (L020) | 3 independent radios | relay S-band ~0.4 Mbit/s @10 000 km; surface network multi-Mbit/s within cells |
| EI-08 | PNT | LunaNet augmented navigation, local beacons | LANS/Moonlight (S017, S018) | sun sensor/star tracker, IMU, VO, LiDAR map matching | base-frame localisation ≤ 1 m |
| EI-09 | Lander accommodation | Argonaut-/Mk1-class cargo lander | lander user guides (S075, values not retrieved) | 4 launch locks under chassis box; deploy via ramp/offloader | stowed 3.6 × 2.4 × 1.2 m (mast folded); delivered 1.19 t incl. 5 % accommodation; f₁ ≥ 35 Hz on locks |
| EI-10 | Crew interface | surface crew | NASA-STD-3001 maintainability practice (S049) | EVA handles, manual brake/spade/latch releases, status lights | speed ≤ 0.2 m/s and EE force ≤ 50 N within 10 m of crew |
| EI-11 | Keep-alive module (MOD-KA, KA-C) | disabled assets | EI-01 | ≈ 73 kg double-slot module with its own 120 VDC connector on 10 m cable, 4 kWh usable battery, two back-to-back fold-out vertical PV panels 1.5 m² each (TS-07b) | sustains ≈ 230 W average at a 0.75-illuminated site; ≈ 38 h darkness bridging at 100 W; P(sustains a sampled asset) ≈ 0.77 (CDR-20; spec sheet in subsystem_specs/service_spine.md) |

## 2. Internal interfaces

| ID | Interface | Between | Definition |
|---|---|---|---|
| II-01 | Service-spine slot | spine ↔ modules/ORUs | androgynous latch on ISO 9409-1-derived pattern; 120 VDC ≤ 1 kW per slot; 100 Mbit/s Ethernet (TSN); 1-wire ID; passive thermal pad; ≤ 40 kg and ≤ 0.45 × 0.45 m footprint × 0.6 m height per occupied slot (2 × 3 slot grid, CDR-21); double-slot modules (MOD-KA) ≤ 80 kg over two adjacent latches |
| II-02 | Arm tool changer | dex arm ↔ tools | ISO 9409-1 pattern + power/data pass-through (28 V/120 V tools); tool ID; change time ≤ 5 min |
| II-03 | Arm base | arm ↔ deck | ORU interface: 4 captive bolts, blind-mate connector, grapple handle — arm replaceable by the other arm (with crane assist) or by a peer TSR |
| II-04 | Wheel drive unit | drive ORU ↔ bogie | 4 captive fasteners on a hub flange, blind-mate connector; unload the wheel by body lowering (M2 suspension) |
| II-05 | WEB equipment | electronics ↔ WEB baseplate | conduction-cooled to heat-pipe baseplate; Al 6061 3 mm enclosures |
| II-06 | Battery module | 4 modules ↔ PCDU/PTM | module-level fusing, contactors, BMS bus |
| II-07 | Peer servicing | TSR ↔ TSR | 2 grapple fixtures on chassis, fiducials on every ORU, service data port (EI-04 class) |

## 3. Interface-control gaps (open items)

1. No surface standard for robotic ORU handles/fasteners: TSR-1 recommendation EI-03 must be negotiated
   with asset owners; until then success probabilities for L0/L1 dominate value (paper §21).
2. ISPSIS power-quality limits (ripple, transients) and connector definition for *surface* exchange were
   not available in full text; PTM design assumes ISPSIS 120 VDC quality rules apply at the port.
3. Tow-point standard (EI-06) does not exist; recovery of L0 vehicles depends on improvised attachment
   (p ≈ 0.80, servicing.py `attach_tow_point`).
