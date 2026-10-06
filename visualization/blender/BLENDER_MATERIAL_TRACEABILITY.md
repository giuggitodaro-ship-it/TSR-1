# TSR-1 Blender material traceability

Prepared before final shader assignment. Engineering selections come from `engineering/materials_matrix.csv` (only selected=Y rows) and the stated subsystem sheets. Blender names below are actual shared material datablocks used by the executed build. Shader numbers are visual approximations and are not measured BRDF, thermal absorptance/emittance, or material qualification data. Internal gears/lubricants are not exposed merely to add detail.

| Component | Engineering material | Source file | Blender material name | Shader approximation | Notes |
|---|---|---|---|---|---|
| Chassis torque box | Al7075-T7351 faces/Al5056 honeycomb | DESIGN_FREEZE_V1.md §14; materials_matrix.csv primary structure | TSR1_Al | Light grey metallic1, roughness .30–.45 | Honeycomb concealed; no CFRP shell |
| Chassis thermal finish | White thermal coating | docs/VISUAL_RENDER_SPEC.md §2 | TSR1_White | Warm off-white, metallic0, roughness .65–.8 | Coating over structural alloy |
| Secondary rails/brackets/rack | Al6061/7075 | materials_matrix.csv secondary structure; tools.md | TSR1_Al | Light satin metallic | No decorative armour |
| Hardpoints, tow lugs, hinges, arm joints | Ti-6Al-4V | materials_matrix.csv hard points/joint housings | TSR1_Ti | Neutral/dark grey metallic1, roughness .35–.50 | Dull machined metal |
| Dexterous principal links | Ti-6Al-4V tubes | DESIGN_FREEZE_V1.md §14; run_config.json dex_link_material; matrix dexterous arm links | TSR1_Ti | Satin grey metallic, no carbon weave | Overrides stale CFRP mass text |
| Wheels/rims/spokes | Ti-6Al-4V | materials_matrix.csv wheel structure; mobility.md | TSR1_Ti | Satin grey metallic | No rubber/pneumatic tyre |
| Grouser contact tips | Titanium with plasma nitride/TiN | materials_matrix.csv wheel contact surface | TSR1_Ti | Slightly darker satin metallic | Avoid exaggerated gold surface |
| Rocker/bogie links | Al7075-T7351 | materials_matrix.csv suspension links | TSR1_Al | Light metallic grey | Ti pivots use TSR1_Ti |
| Lowering screw/pivots | Ti/BMG mechanism; Ti fittings | mobility.md; FINAL_SPECIFICATIONS.md | TSR1_Ti / TSR1_Dark | Grey metallic / dark protected housing | Detailed threads optional |
| Crane boom/A-frame | CFRP tubes +Ti end fittings | materials_matrix.csv crane boom and A-frame | TSR1_CFRP | Charcoal, restrained texture, roughness .5–.65 | No glossy automotive finish |
| Sensor mast | CFRP tube/Ti hinge | materials_matrix.csv sensor mast | TSR1_CFRP / TSR1_Ti | As above | Use single mast tube |
| Fenders | CFRP shell | materials_matrix.csv fenders | TSR1_CFRP | Dark matte composite | Six upper arcs |
| Fender skirt | PTFE-coated glass fabric | materials_matrix.csv fenders | TSR1_White | Light grey nonmetal roughness .8 | Replaceable flexible skirt |
| Joint bellows | PTFE-coated fabric, Ti labyrinth | materials_matrix.csv dynamic seals; dust.md | TSR1_Boot | Dark grey nonmetal roughness .65–.8 | Dark color visual spec; NOT rubber elastomer |
| Radiator body | Al6063 heat-pipe panel | materials_matrix.csv thermal radiator | TSR1_Al | Satin aluminium | Hidden pipe internals optional |
| Radiator optical surface | OSR/Ag-FEP with ITO EDS | materials_matrix.csv thermal radiator | TSR1_OSR / TSR1_Glass | Pale silver tiles, low roughness .15–.3; faint transparent film | EDS not glowing; shader not thermal model |
| WEB/chassis insulation | Aluminised Kapton/Mylar, Dacron net, Beta outer | materials_matrix.csv insulation | TSR1_Al / TSR1_White | Metallic silver subtle wrinkle; off-white rough fabric | Don't replace all alloy faces with foil |
| MOD-KA enclosure blanket | MLI on Al7075 frame | service_spine.md; visual spec | TSR1_Gold | Muted gold/silver metallic, restrained wrinkle | Gold is visual convention, no claim of bare gold |
| MOD-KA latch/hinge/lift eye | Ti6Al4V | service_spine.md | TSR1_Ti | Satin grey metal | Fiducials matte printed marking |
| Rover / MOD-KA PV | IMM/triple-junction GaAs on CFRP | power.md; service_spine.md | TSR1_PV / TSR1_CFRP | Dark navy cells, roughness .18–.28, fine interconnects | Vertical panels; no emissive glow |
| Recovery rope/slings/crane lines | Vectran with aramid/PTFE jacket | materials_matrix.csv recovery line; manipulation.md; tools.md | TSR1_Vectran | Light-grey technical fibre roughness .7 | Grey differentiates from orange power cable |
| Winch drum | Ti; steel gears | recovery.md | TSR1_Ti / TSR1_Dark | Satin metal | Covered mechanism keeps gears hidden |
| Spades/anchors | Ti6Al4V +TiN edge | materials_matrix.csv spades / helical anchors | TSR1_Ti / TSR1_Ti | Grey metallic | No steel construction-site outriggers |
| Belly skid | Al7075 +Ti cleats | structure.md | TSR1_Al / TSR1_Ti | Satin metals | No rubber skid |
| Power tether | Cu conductors, PTFE/aramid jacket | materials_matrix.csv power tether; visual spec | TSR1_Orange | Matte orange nonmetal roughness .6 | Outer jacket only; no exposed copper |
| Connector shell/insert/pins | Ti/PEEK/Au-plated BeCu | materials_matrix.csv connector shells | TSR1_Ti / TSR1_Dark / TSR1_Gold | Satin grey, dark polymer, small gold contacts | Self-closing cover |
| Sensor housing/window | Ti housing, sapphire+EDS | sensors.md | TSR1_Ti / TSR1_Glass | Dark transmissive glass, minimal reflection tint | No futuristic glowing sensor |
| LED illuminators | LED optical assembly | sensors.md; visual spec | LED_White | Small localized blue-white emission | Lamps only, not camera emission |
| Relay antenna | RF radiator/radome geometry, composition unspecified | communications.md; visual spec | Antenna_Neutral | Pale matte neutral finish | Appearance assumption; no unsupported material certification |
| Tool bodies/bits | Ti, tool steel with DLC | materials_matrix.csv tool heads; tools.md | TSR1_Ti / Tool_Steel_Dark | Satin body/dark metal wear surface | Per-tool engineering identity retained |
| Gripper fingers/probe insulator | PEEK/Vespel | tools.md | TSR1_Dark | Dark brown-grey nonmetal | Not rubber |
| Brush bristles | PTFE-coated aramid | tools.md | TSR1_White | Fine matte fibres | Representative coarse bristles sufficient |
| EDS wand | CFRP with ITO/PI film | tools.md | TSR1_CFRP / TSR1_Glass | Dark frame/faint film | No luminous energy beam |
| Branding / fiducials | Printed markings, substrate unspecified | visual spec §8; interfaces.md | TSR1_Dark / Fiducial_White | Matte dark grey/white | User brand only |
| Internal packaging | Al6061, battery Al/mica, copper harness | power.md; matrix electronics/battery/cables | TSR1_Al / TSR1_Dark | Hidden envelope materials | Standard exterior remains closed |

No shader may be used as evidence of mechanical, thermal, dust, radiation, or electrical performance. Geometry traceability and source materials determine material assignment, not aesthetics.

Actual numerical shader settings are centralized in `tsr1_utils.materials()`. Ti uses metallic.78/roughness.39, Al.80/.28, CFRP.02/.72, White.06/.70, PV.55/.27, OSR.62/.20. Nitrided tips share the Ti shader: coating microstructure is not resolved. EDS is represented by sparse fine electrode traces; no film thickness or optical/thermal performance is inferred.
