# TSR-1 Visual Render Specification

> TSR-1 is an independent conceptual engineering study by Todaro Corp. References to NASA, ESA and other
> organizations are used solely as technical and architectural context.

Instructions for an external image-generation or 3-D rendering system to visualise the **frozen engineering
configuration** (`DESIGN_FREEZE_V1.md`). Every visible element below exists in the design and has a stated
function; do not add elements that are not listed. Dimensions in metres. Coordinate frame: x forward, y left, z up,
origin on the ground under the vehicle centre.

## 1. Overall form
- Low, wide, six-wheeled utility robot — **not** a crew vehicle (no seats, no steering wheel, no cockpit, no
  windows, no pressurised cabin).
- Overall length **3.60**, width **2.40**, deck top at **0.90**, sensor-mast head at **2.20** (deployed).
- Proportions: wheels large relative to body (wheel Ø 0.90 is half the deck height + clearance).

## 2. Chassis
- Rectangular closed box **2.60 L × 1.50 W × 0.45 H**, underside at **0.45** above ground (driving) or **0.10**
  (lowered for servicing/winching).
- Finish: white thermal-paint / silver MLI on side panels (MLI blankets visible as quilted, slightly crinkled
  silver-gold Kapton with white Beta-cloth outer layer on the electronics enclosure areas); deck top flat.
- Belly: flat aluminium skid plate with small titanium cleats (visible only from low angles).
- Ti-6Al-4V hard points (dull grey metal) at front and rear centre (tow lugs).

## 3. Mobility
- **Six rigid wheels**, Ø **0.90**, width **0.40**, titanium (dull satin grey), **18 straight grousers 20 mm high**
  across the tread; internal flexure spokes visible through the open sides.
- Axles at x = **+1.30, 0, −1.30**; track **2.00** (wheel centre-lines at y = ±1.00).
- **Rocker-bogie** linkage on each side: a long rocker (aluminium tube, Ø ~70 mm) from the front wheel to a pivot
  on the body side near x ≈ +0.2, and a bogie carrying the middle and rear wheels; a transverse differential bar on
  top of the body. Each wheel has a vertical steering actuator housing (cylinder Ø ~0.14) above the hub.
- **Fenders**: black CFRP arcs over the upper third of each wheel with a short light-grey fabric skirt at the rear
  edge.

## 4. Deck equipment (top view, front at top)
| Item | Position (x, y) | Appearance |
|---|---|---|
| Sensor mast | (+1.10, +0.50) | single black CFRP tube Ø 60 mm, 1.2 m tall above deck; head with two stereo cameras (dark lenses, 0.25 m baseline), small thermal-IR camera, two **blue-white** LED headlamps, small gimballed flat relay antenna |
| Dexterous arm R | base (+1.15, −0.45) | white/grey 7-joint arm, titanium link tubes Ø 60–100 mm, joint housings with black bellows boots; upper arm 0.75, forearm 0.70, wrist 0.15; end effector with tool-changer disc and small macro camera |
| Dexterous arm L | base (+1.15, +0.45) | identical mirror of arm R |
| Crane boom | turntable (+0.30, 0) | slender black CFRP tube Ø 50 mm, **2.60** long; short A-frame (0.9 high) behind the turntable; thin luff cable from boom tip to A-frame top; hoist line with small hook block. Stowed: boom lies forward along the deck centre-line |
| Service spine | x −1.0 to +0.6, y ±0.25 | low aluminium rail with **six** box-shaped module slots (≈ 0.45 × 0.45 m footprint); typical load: two ORU cradles, one gold-MLI "keep-alive" module with a small vertical solar panel, one recovery-kit box, empty slots |
| Tool rack | (−0.40, −0.60) | open rack with holstered tools (gripper, socket driver, brush, scoop, probe) |
| Radiator | rear deck x −1.30 to −0.30 | flat, mirror-like (optical solar reflector tiles) panel ≈ 1.0 × 1.6, facing straight up, with a faint transparent electrode film sheen |
| Solar panels | both sides, vertical | **two vertical** dark-blue solar panels 1.5 × 0.5 mounted on the body sides above the rocker pivots, facing ±y |
| Power tether reel | (+0.80, +0.55) | drum Ø 0.35 with orange-jacketed cable; connector head stowed on arm L wrist when in use |

## 5. Rear equipment
- **Winch** below the rear deck, fairlead at **0.25** above ground on the centre-line (low!), light-grey jacketed line.
- **Two rear spades** (titanium plates 0.6 × 0.3) folded up against the rear face; deployed: hinged down and pushed
  into the regolith behind the vehicle.
- Rear LiDAR (small black box) at deck level.
- Two helical anchors (titanium rods with a single helix plate Ø 0.15) clipped to the right body side.

## 6. Configurations to render
1. **Traverse**: body raised (clearance 0.45), arms folded on deck, crane stowed, mast up, LEDs on, slow motion
   (0.5 m/s): faint wheel tracks only, **no billowing dust clouds** (in vacuum, ejecta follow ballistic arcs and fall
   immediately; fenders capture most).
2. **Servicing a communication tower**: body lowered, both arms extended toward an equipment box at 1–2.5 m height,
   power tether connected to the tower's port, crane holding a 15–20 kg grey module.
3. **Emergency power to a disabled small rover**: orange tether running 10–20 m to the rover; keep-alive module left
   beside the rover.
4. **Anchored winch recovery on a 10–15° slope**: TSR-1 upslope and lowered, rear spades in the ground, two anchors
   installed in front of it with short straps to the front lugs, taut line running downslope to a 450 kg rover whose
   wheels are partly sunk.
5. **Stowed on a lander deck**: mast folded, arms and boom folded flat; total height 1.2.

## 7. Environment and lighting (lunar south pole)
- Sun **within 0–2° of the horizon** (never overhead); extremely long, razor-sharp shadows; high contrast; shadowed
  areas almost black except for faint fill from sunlit terrain.
- Black sky with no atmosphere glow; stars only if the camera exposure is set for shadow (not in sunlit shots).
- Earth, if shown, low on the horizon and small (≈ 2° across).
- Terrain: grey regolith, gentle undulations, small craters and scattered rocks 0.1–0.5 m; distant rim of Shackleton
  crater; permanently shadowed crater floors as pure black regions.
- Infrastructure context (optional, de-emphasised): tall vertical solar-array mast in the distance, a lattice
  communication tower, a cargo lander.

## 8. Branding and labelling
- **"TODARO CORP."** and **"TSR-1"** in clean sans-serif dark-grey lettering on the chassis side panel below the solar
  panel, ≈ 0.10 m letter height; small TSR-1 marking on the mast head.
- **No NASA, ESA, JAXA, CSA or other agency logos, flags or mission patches** anywhere. No text implying partnership.
- Optional caption on images: "TSR-1 — independent conceptual study by Todaro Corp."

## 9. Do not render
- Crew seats, handles shaped for passengers, windshields, headlights styled like cars.
- Large heavy industrial arm, hydraulic cylinders, tracks, legs, thrusters, glowing exhausts.
- Earth-like dust plumes, atmosphere haze, blue sky, sunlit-from-above lighting.
- Exaggerated wheel size or "monster-truck" suspension travel.
