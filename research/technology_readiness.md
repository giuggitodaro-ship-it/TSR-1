# TSR-1 Technology Readiness Assessment

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other
> organizations are used solely as technical and architectural context.

TRL scale: NASA NPR 7123.1 Appendix E (S072). TRL is assessed for the **TSR-1 application environment**
(lunar south pole, 40–390 K, abrasive/electrostatic dust, 10-year life), not for the technology's best
heritage environment — a Mars-flown mechanism is not TRL 9 for 10 years of lunar polar dust.

Maturity classes (directive §30): **H** existing/high heritage · **A** existing but requiring lunar adaptation ·
**P** prototype/emerging · **I** new integration challenge · **G** technology gap.

| # | Element | TRL (TSR-1 env.) | Class | Heritage / evidence | What must happen before deployment |
|---|---|---|---|---|---|
| 1 | Honeycomb chassis / WEB structure | 7 | H | spacecraft buses, MSL WEB | thermal-cycling qualification of inserts/joints (3650 cycles 40–390 K) |
| 2 | Rocker-bogie suspension | 7 | A | MER, MSL, M2020 (Mars) | lunar-dust pivot seals; cold-start torque |
| 3 | Body-lowering + differential lock | 5 | P | lab mechanisms | breadboard, TVAC + dust life test |
| 4 | Rigid Ti grousered wheels | 6 | A | VIPER/Yutu/Pragyan, MSL | 1500 km fatigue/abrasion test on simulant; rock-impact test |
| 5 | Drive/steer actuators (strain-wave, sealed) | 5 | A | LRV, MSL, M2020 | 10-yr dust-life test (regolith simulant in vacuum, thermal cycling) |
| 6 | Cold-tolerant actuators (BMG gears, dry lube, heaterless) | 4 | P / **G** | COLDArm (S040) | flight demo; torque-density growth to 25 N·m/kg class at 200 N·m; life data |
| 7 | 7-DOF dexterous arm in lunar gravity/dust | 5 | I | M2020 arm, Dextre, xLink | integrated arm TVAC + dust; contact-task reliability statistics |
| 8 | Cable-stayed crane boom (LSMS-type) | 4 | P | LSMS ground prototypes (S015) | engineering model; load-swing control in 1/6 g (pendulum period ~5 s) |
| 9 | Tool changer, F/T sensor, tools | 5 | A | ISS OTCM, RRM | dust-tolerant tool interface faces |
| 10 | Dust-tolerant power connector (3 kW, 120 VDC) | 4–5 | P / **G** | Honeybee DTC > 500 cycles (S042), SBIR inductive links | robotic mating qualification at kW level with lunar simulant; ISPSIS connector definition |
| 11 | Isolated bidirectional PTM 3 kW | 5 | A | terrestrial SiC converters, ISS 120 V heritage | radiation qualification; ISPSIS power-quality compliance test |
| 12 | 120 VDC PCDU (ISPSIS) | 6 | A | ISS 120 VDC | — |
| 13 | Li-ion PPR battery | 6 | A | NASA PPR 18650 packs (S070) | lunar thermal envelope test |
| 14 | Vertical PV + MPPT | 7 | H | spacecraft arrays | dust deposition on vertical panels (expected low) |
| 15 | MLI, LHP, radiator | 6 | A | MSL/M2020 thermal | dust-loaded radiator test |
| 16 | EDS on radiator/optics | 6 | A | Blue Ghost M1 2025 (S019) | long-duration efficiency on mobile platform |
| 17 | HPSC autonomy computer | 6 | A | qualification 2026 (S039) | availability; software ecosystem |
| 18 | Dual safety/RT computers | 7 | H | flight computers | — |
| 19 | Stereo/Haz cameras + LED | 7 | H | VIPER (S064) | — |
| 20 | LiDAR (SPAD) | 5 | P | Jena-Optronik/Fraunhofer development | space qualification; window dust |
| 21 | IMU, star tracker | 9 | H | Mars rovers (S065) | — |
| 22 | Surface LTE-class radio | 6 | A | Nokia LSCS on IM-2 (S068, outcome partial) | base network availability |
| 23 | LunaNet relay radio | 6 | A | LCRNS/Moonlight procurement (S017, S018) | relay service availability (programmatic) |
| 24 | Supervised servicing autonomy (verified skills, hold points) | 4 | I / **G** | ISS robotics ops, CADRE (S069) | skill library V&V; analogue field campaigns; formal guard verification |
| 25 | Winch + 0.25 m fairlead + load limiting | 5 | A | terrestrial recovery winches | vacuum/dust drum and line abrasion life |
| 26 | Regolith spades and helical anchors | 3 | **G** | terrestrial anchors (L026), legged-rover anchors (S045) | capacity tests in lunar simulant at 1-g and reduced-g; installation in dense regolith with clasts |
| 27 | Modular service spine (HOTDOCK-class) | 5 | A | HOTDOCK ground demos (S048) | dust-tolerant latch qualification |
| 28 | Keep-alive module (MOD-KA) | 5 | I | integration of existing parts | integrated test |
| 29 | Asset-side robotic servicing standards (L2/L3) | n/a | **G** (programmatic) | IERIIS (S013), NASA/SP-20260001900 (S002) | adoption by asset owners — **dominant value driver** |

## Critical path

1. **Asset standardisation (row 29)** — the value model shows ΔA ≈ 2 pp for a legacy (L0-heavy) base versus
   ≈ 14 pp for a standardised base (paper §21). No hardware maturation compensates for non-serviceable assets.
2. **Supervised servicing autonomy V&V (row 24)** — determines achievable effective speed and task success.
3. **Ground-reaction anchors (row 26)** — TRL 3; recovery claims for slopes depend on it.
4. **Long-life dust/cold mechanisms (rows 5, 6)** — 10-year life of ≈ 30 external actuators.
5. **Dust-tolerant kW connector (row 10)** — enables emergency power, the main asset-loss mitigation.

The integrated system is assessed at **TRL 4** overall (component maturity up to 7, but the servicing-and-
recovery system has never been integrated or tested in a relevant environment).
