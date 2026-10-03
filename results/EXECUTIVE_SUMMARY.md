# TODARO CORP. TSR-1 — Executive Summary

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other organizations are used solely as technical and architectural context.

**What it is.** TSR-1 is a concept for an autonomous lunar service-and-recovery rover whose job is to keep distributed south-polar infrastructure (power, communication, science and robotic assets) working: inspect it, restore power to disabled assets, replace robot-serviceable modules, clean dust, and recover immobilised vehicles — without crew EVA.

**What the study found it must be.** A 1207 kg (delivered) six-wheel rocker-bogie rover with body lowering; two identical 20 kg-class dexterous arms plus a 150 kg cable-stayed crane (a heavy arm was rejected: ~110 kg heavier); a 3 kW ISPSIS-compatible 120 VDC power-transfer module with a 25 m tether and deployable keep-alive modules; a 4 kN anchored winch with rear spades and helical anchors (towing was rejected on slopes: < 0.2 kN available on 15°); a 15 kWh battery plus vertical solar panels; supervised autonomy behind a deterministic safety layer.

**Performance.** 21° slopes (nominal soil; 16° conservative), 10 km service radius, 183 h darkness survival (indefinite in sunlight), recovery of 92 % of sampled immobilisation cases, ORU swaps up to 150 kg.

**Value.** At 30 assets over 10 years: availability 0.68 → 0.76, assets lost 31 → 22, Earth replacement mass 12.7 → 9.4 t; logistics break-even at ≈ 9 assets. EVA savings are modest. Value depends overwhelmingly on assets having standard robotic interfaces.

**Verdict.** Feasible with identified technology development (anchors, cold/dust-tolerant actuators, servicing autonomy, dust-tolerant power connectors), and justified only for bases of roughly ten or more serviceable, standardised assets. The review found a dedicated vehicle would be idle > 95 % of the time; the recommended path is a host-agnostic service-and-recovery kit, with the dedicated TSR-1 carrier used where no utility-rover host can respond in time.
