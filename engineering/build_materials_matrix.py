"""Builds engineering/materials_matrix.csv (directive §16).

Property values are typical room-temperature handbook values (MMPDS L005, Gilmore L006, SMAD L007,
Roberts L015 — LITERATURE-RECALL; verify against current editions before detailed design). Mass
comparisons for the chassis, arm links and wheels come from the project models (TS-10, TS-02).
Columns: application, candidate, density [kg/m3], E [GPa], strength [MPa] (yield or allowable),
CTE [ppm/K], k [W/(m K)], cryogenic, vacuum/outgassing, radiation, abrasion/tribology,
manufacturability, heritage, selected, rationale, source.
"""
import csv
from pathlib import Path

ROWS = [
    # --- primary structure
    ("primary structure faces", "Al 7075-T7351 / Al 5056 honeycomb", 2810, 71.7, 390, 23.4, 155, "strength rises, no DBTT", "no outgassing", "immune", "n/a (enclosed)", "excellent", "very high (spacecraft panels)", "Y",
     "Chassis is minimum-gauge driven (TS-10): CFRP saves only ~15 kg (1.3 % of delivered mass) but adds microcracking/insert risk over 10-yr 40-390 K cycling; Al conducts heat for the WEB and gives EMI/radiation shielding; uniform CTE across box", "L005; TS-10"),
    ("primary structure faces", "CFRP M55J/cyanate faces", 1650, 110, 450, 0.5, 30, "microcracking risk under deep cycling", "low CVCM with cyanate", "immune", "n/a", "good (autoclave)", "high", "N", "Mass option (−15 kg) held as descope lever; rejected for thermal-cycling durability and insert/fitting complexity", "L007; TS-10"),
    ("primary structure faces", "Al-Li 2195-T8", 2710, 76, 500, 21.6, 88, "good", "none", "immune", "n/a", "fair (sheet availability)", "high (launch vehicles)", "N", "Only −1.3 kg vs 7075 at minimum gauge; supply/forming cost not justified", "L005; TS-10"),
    ("primary structure faces", "Al 2219-T87", 2840, 73.8, 345, 22.3, 121, "excellent (cryogenic tanks)", "none", "immune", "n/a", "excellent (weldable)", "LRV frame (S027)", "N", "Equivalent mass to 7075; weldability not needed for bonded sandwich", "L005; S027"),
    ("primary structure faces", "Ti-6Al-4V", 4430, 113.8, 880, 8.6, 6.7, "good (ELI grade)", "none", "immune", "n/a", "poor for thin sheet", "high", "N", "+21 kg at minimum gauge; poor heat spreading", "L005; TS-10"),
    ("hard points / fittings", "Ti-6Al-4V", 4430, 113.8, 880, 8.6, 6.7, "good", "none", "immune", "galling (coat)", "good (machined)", "very high", "Y", "Highest specific strength for winch/crane/anchor lugs; CTE mismatch with Al panels handled with slotted/flexure joints (≈265 MPa if fully constrained over 250 K, structures.chassis.thermal_mismatch_stress)", "L005"),
    ("secondary structure", "Al 6061-T6 / 7075 brackets", 2700, 69, 276, 23.6, 167, "good", "none", "immune", "n/a", "excellent", "very high", "Y", "Low cost, easy machining, CTE-matched to chassis", "L005"),
    # --- mobility
    ("wheel structure", "Ti-6Al-4V rim + spokes", 4430, 113.8, 880, 8.6, 6.7, "ductile at 40 K", "none", "immune", "good; TiN/nitride on grousers", "good", "high (rigid wheels)", "Y", "Rigid wheel per TS-02 (model confidence, dust tolerance); Ti for impact/fatigue over >1000 km and cryogenic toughness", "L005; TS-02"),
    ("wheel structure", "Al 7075-T7351 rim", 2810, 71.7, 390, 23.4, 155, "good", "none", "immune", "poor (abrasion, rock punctures on MSL)", "excellent", "MSL/M2020", "N", "MSL wheel damage history; would need thicker skin for 10-yr life, erasing mass advantage", "TS-02"),
    ("wheel structure", "NiTi superelastic spring tyre", 6450, 75, 500, 11, 18, "transformation T must be tuned", "none", "immune", "mesh admits dust", "difficult", "prototype (NASA GRC)", "N", "TRL 4; retained as upgrade path (lower sinkage/energy, cf. k_cal 0.62)", "TS-02"),
    ("wheel contact surface / grousers", "Ti-6Al-4V + plasma nitride / TiN", 4430, 113.8, 880, 8.6, 6.7, "good", "none", "immune", "hard surface vs abrasive agglutinates", "good", "medium", "Y", "Abrasion resistance against regolith; integral with rim", "L015"),
    ("suspension links", "Al 7075-T7351 tubes, Ti pivots", 2810, 71.7, 390, 23.4, 155, "good", "none", "immune", "pivots need seals", "excellent", "MER/MSL rocker-bogie", "Y", "Heritage; stiffness-driven tubes; Ti pivot housings for bearing CTE match", "L005"),
    # --- manipulators
    ("dexterous arm links", "Ti-6Al-4V tube", 4430, 113.8, 880, 8.6, 6.7, "good", "none", "immune", "tough vs contact/impact", "good", "MSL/M2020 arms", "Y", "Arm mass is actuator-dominated: Ti costs +2.4 kg vs CFRP per arm (TS-10) but avoids bonded CFRP-metal joints across 40-390 K and is impact/abrasion tolerant for a contact-intensive servicing arm", "TS-10"),
    ("dexterous arm links", "CFRP tube", 1600, 120, 400, 0.5, 30, "microcracking", "low", "immune", "impact-sensitive", "good", "Canadarm/ERA", "N", "Thermal growth advantage (0.19 vs 3.2 mm per 1.5 m) is removed by visual servoing", "TS-10"),
    ("crane boom and A-frame", "CFRP tube + Ti end fittings", 1600, 120, 400, 0.5, 30, "acceptable for compression member", "low", "immune", "protected by boom sleeve", "good", "LSMS concepts (S015)", "Y", "Buckling/stiffness-driven slender member; low CTE keeps hoist geometry stable", "S015; L007"),
    ("joint housings", "Ti-6Al-4V", 4430, 113.8, 880, 8.6, 6.7, "good", "none", "immune", "n/a", "good", "high", "Y", "CTE closer to steel bearings/gears than Al (8.6 vs 10-11 ppm/K) → preload stability across 40-390 K", "L005; L015"),
    ("gears (high-load drives)", "strain-wave gear: maraging/15-5PH flexspline, 440C circular spline", 7800, 200, 1500, 10.5, 20, "good", "lubricant-limited", "immune", "needs lubrication", "specialist", "LRV 80:1 harmonic drive; MSL", "Y", "Heritage strain-wave gearing; dry MoS2 + PFPE barrier in cold; warm-up only for heavy-duty starts", "S027; L015"),
    ("gears (cold arm/wrist joints)", "bulk metallic glass (Cu-Zr / Ti-based)", 6100, 95, 1800, 9, 10, "no DBTT; operated at −173 °C without heaters", "none", "immune", "wear-resistant, unlubricated", "casting/moulding (limited sizes)", "COLDArm demo (S040)", "Y", "Eliminates actuator survival heaters (~85 W, thermal.lumped.actuator_heater_power) → technology gap item", "S040"),
    ("bearings", "hybrid Si3N4 balls / 440C races", 3200, 310, 3000, 3, 30, "excellent", "none", "immune", "low wear; tolerant of marginal lubrication", "specialist", "high (space mechanisms)", "Y", "Dry-running tolerance in cold and dust; lower thermal expansion mismatch with steel races", "L015"),
    ("bearings", "all-440C steel", 7650, 200, 1900, 10.2, 24, "good", "none", "immune", "needs lubricant", "standard", "very high", "N", "Lower tolerance to lubricant starvation", "L015"),
    ("solid lubricant", "sputtered MoS2 (+ Ti doping)", 4800, None, None, None, None, "works to cryogenic T", "none", "immune", "μ≈0.01-0.05 in vacuum; poor in humid air (ground test control)", "PVD", "very high", "Y", "Cold-capable, no viscosity limit", "L015"),
    ("liquid lubricant", "Braycote 601EF PFPE grease", 1900, None, None, None, None, "usable to −80 °C; viscosity rises", "low vapour pressure", "good", "excellent wear life when warm", "standard", "MSL/M2020 (S041)", "Y", "For warm-started heavy drives (wheel drives, winch) with heaters", "S041"),
    ("shafts", "Ti-6Al-4V (arms) / 15-5PH (drive outputs)", 7800, 197, 1170, 10.8, 18, "good", "none", "immune", "hardened journals", "good", "high", "Y", "Strength and CTE compatibility with gears/bearings", "L005"),
    # --- recovery
    ("recovery line", "Vectran (LCP) braid + aramid/PTFE jacket", 1400, 65, 2900, -4.8, 0.4, "retains strength cold", "low", "UV-sensitive (jacketed)", "jacket sacrificial vs abrasion", "commercial", "Mars Pathfinder airbags (Vectran)", "Y", "~0.03 kg/m vs ~0.15 kg/m for 6 mm SS rope; low creep (unlike UHMWPE)", "L007"),
    ("recovery line", "316 SS wire rope 6 mm", 7900, 193, 1500, 16, 16, "excellent", "none", "immune", "abrasion tolerant", "commercial", "terrestrial", "N", "5× heavier; kinking", "L005"),
    ("recovery line", "UHMWPE (Dyneema)", 970, 100, 3000, -12, 0.4, "good", "low", "UV-sensitive", "creep under sustained load", "commercial", "terrestrial", "N", "Creep and low melting point (~145 °C) near sunlit hardware", "L007"),
    ("spades / helical anchors", "Ti-6Al-4V + TiN edge", 4430, 113.8, 880, 8.6, 6.7, "good", "none", "immune", "abrasive regolith penetration", "good", "terrestrial anchors (steel)", "Y", "Strength-to-mass; non-magnetic; edge hard-coat", "L005"),
    # --- thermal / power
    ("thermal radiator", "Al 6063 heat-pipe panel + OSR/Ag-FEP + ITO EDS film", 2700, 69, 214, 23.4, 200, "ammonia heat pipes freeze safe by design", "FEP low", "UV darkening of FEP minor on Moon", "dust: EDS + zenith orientation", "standard", "very high (radiators); EDS lunar demo 2025", "Y", "Zenith-facing at the pole sees grazing sun; EDS restores α after dust (S019, S062)", "L006; S019; S062"),
    ("insulation", "MLI: aluminised Kapton/Mylar + Dacron net, Beta-cloth outer", 1420, None, None, None, None, "fine", "low (bake-out)", "Kapton good", "Beta cloth resists abrasion/dust", "standard", "very high", "Y", "ε* 0.015-0.05; Beta outer layer for dust abrasion (Apollo suit lesson S022)", "L006; S022"),
    ("battery structure", "Al 6061 interstitial heat sinks + mica sleeves", 2700, 69, 276, 23.6, 167, "n/a (WEB > −20 °C)", "none", "immune", "n/a", "standard", "NASA PPR packs (S070)", "Y", "Passive thermal-runaway propagation resistance", "S070"),
    ("cables / harness", "Cu conductors, PTFE/polyimide (AS22759-type) insulation", 8960, 117, 70, 16.5, 400, "PTFE flexible to cryogenic T", "low", "PTFE degrades at high dose (not an issue: ~0.1 krad/10 yr GCR)", "jacket vs abrasion", "standard", "very high", "Y", "Cold flexibility for moving harness across joints; radiation dose negligible on the surface", "L007; S033"),
    ("power tether", "Cu 2×6.9 mm² PTFE + aramid braid + PTFE jacket", 8960, None, None, None, None, "flexible cold", "low", "low dose", "aramid braid against regolith", "standard", "terrestrial", "Y", "3 % drop at 3 kW over 25 m (power.electrical.size_cable)", "power model"),
    ("connector shells", "Ti-6Al-4V shell, PEEK insert, Au-plated BeCu contacts", 4430, 113.8, 880, 8.6, 6.7, "good", "PEEK low", "immune", "self-closing cover; DTC class (S042)", "specialist", "DTC prototypes >500 cycles", "Y", "Dust-tolerant mating; galvanic compatibility with Ti structures", "S042"),
    ("electronics enclosures", "Al 6061-T6, 3 mm walls", 2700, 69, 276, 23.6, 167, "n/a (inside WEB)", "none", "3 mm Al ≈ 0.8 g/cm² shielding", "n/a", "standard", "very high", "Y", "Conduction cooling to WEB plate; shielding against SPE protons (A-24)", "L014"),
    ("service panels / doors", "Al 6061 honeycomb + Beta-cloth edge seals", 2700, 69, 276, 23.6, 167, "good", "low", "immune", "labyrinth edges", "standard", "high", "Y", "Robot-openable panels with captive fasteners", "L007"),
    ("fasteners", "A286 CRES (structural) / Ti-6Al-4V + WS2 (light)", 7940, 201, 690, 16.5, 14, "good", "none", "immune", "dry-film to prevent cold welding/galling", "standard", "very high", "Y", "Captive, robot-compatible heads; dry film against vacuum cold welding", "L015"),
    ("tool heads", "Ti-6Al-4V bodies, tool-steel bits with DLC", 4430, 113.8, 880, 8.6, 6.7, "good", "none", "immune", "DLC low friction/wear", "good", "RRM tools (ISS)", "Y", "Wear resistance on sockets/probes", "L015"),
    ("dynamic seals", "labyrinth + PTFE-coated bellows (no elastomers)", 2200, 0.5, 20, 120, 0.25, "PTFE stays compliant; elastomers glassy below ~−60 °C", "low", "PTFE: fine at surface dose", "regolith exclusion via labyrinth", "standard", "MSL bellows/boots", "Y", "Apollo seal failures (S022); elastomer Tg limits", "S022; L015"),
    ("fenders", "CFRP shell + PTFE-coated glass-fabric skirts", 1600, 70, 300, 2, 5, "fine", "low", "fine", "skirt sacrificial", "good", "LRV fenders (S022 lesson)", "Y", "Ejecta control; replaceable skirts", "S022"),
    ("sensor mast", "CFRP tube, Ti hinge", 1600, 120, 400, 0.5, 30, "fine", "low", "fine", "n/a", "good", "VIPER mast class", "Y", "Pointing stability (low CTE) for NavCams", "S064"),
]
HDR = ["application", "candidate", "density_kg_m3", "E_GPa", "strength_MPa", "CTE_ppm_per_K", "k_W_per_mK",
       "cryogenic_behaviour", "vacuum_outgassing", "radiation", "abrasion_tribology", "manufacturability",
       "heritage", "selected", "rationale", "source"]

if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "materials_matrix.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(HDR)
        for r in ROWS:
            w.writerow(["" if v is None else v for v in r])
    print(len(ROWS), "rows ->", out)
