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

Positions are rectangle bounds on the 2.60 × 1.50 m deck (x forward, y left), taken from `src/tsr1/design/layout.py`
(the same geometry used by the mass model and the closure checks; plan view in figure fig03).

| Item | Position (x range, y range) | Appearance |
|---|---|---|
| Radiator | x −1.30 to −0.21, y −0.75 to +0.75 (full width, rear) | flat, mirror-like optical-solar-reflector tiles facing straight up, faint transparent electrode-film sheen; nothing mounted above it except the stowed crane boom tip |
| Service spine | x −0.18 to +0.73, y −0.68 to +0.68 | low aluminium frame with **six** latch slots in a **2 × 3 grid** (0.45 × 0.45 m each); typical load: two ORU cradles, one gold-MLI keep-alive module occupying two slots (0.9 × 0.45 × 0.45 m box, panels folded flat on top), one recovery-kit box, one empty slot |
| Crane turntable | x +0.85 to +1.30, y −0.20 to +0.20 (front centre) | short A-frame (0.9 high) on a slewing ring; slender black CFRP boom Ø 50 mm, **2.60** long; stowed lying **rearward** along the centre line over the spine (tip just past the rear edge of the radiator); thin luff cable to the A-frame top; hoist line with small hook block |
| Sensor mast | base x +0.76 to +0.96, y +0.22 to +0.42 | single black CFRP tube Ø 60 mm, 1.2 m tall above deck; head with two stereo cameras (dark lenses, 0.25 m baseline), small thermal-IR camera, two **blue-white** LED headlamps, small gimballed flat relay antenna |
| Dexterous arm R | base x +1.00 to +1.30, y −0.75 to −0.45 (front-right corner) | white/grey 7-joint arm, titanium link tubes Ø 60–100 mm, joint housings with black bellows boots; upper arm 0.75, forearm 0.70, wrist 0.15; end effector with tool-changer disc and small macro camera. **Stowed upright** ("candle" stow): upper arm vertical, forearm folded down beside it, top ≈ 0.85 above deck |
| Dexterous arm L | base x +1.00 to +1.30, y +0.45 to +0.75 (front-left corner) | identical mirror of arm R |
| (internal) Warm electronics box | inside the chassis, x −1.00 to 0.00 (under the radiator) | not visible; do not render hatches for it |
| Tool rack | chassis **front face**, y −0.55 to +0.55, between the front wheels | open holster panel with tools (gripper, socket driver, brush, scoop, probe, adapters) facing forward |
| Solar panels | both body sides, vertical | **two vertical** dark-blue solar panels 1.5 × 0.5 mounted on the body sides above the rocker pivots, facing ±y |
| Power tether | reel inside the chassis front; exit guide on the front face at y +0.55 | orange-jacketed cable; connector head stowed on arm L wrist when in use |

## 5. Rear equipment
- **Winch** below the rear deck, fairlead at **0.25** above ground on the centre-line (low!), light-grey jacketed line.
- **Two rear spades** (titanium plates 0.6 × 0.3) folded up against the rear face; deployed: hinged down and pushed
  into the regolith behind the vehicle.
- Rear LiDAR (small black box) at deck level.
- Two helical anchors (titanium rods with a single helix plate Ø 0.15) clipped to the right body side.

## 6. Configurations to render
1. **Traverse**: body raised (clearance 0.45), arms in upright stow at the front corners, crane boom stowed rearward, mast up, LEDs on, slow motion
   (0.5 m/s): faint wheel tracks only, **no billowing dust clouds** (in vacuum, ejecta follow ballistic arcs and fall
   immediately; fenders capture most).
2. **Servicing a communication tower**: body lowered, both arms extended toward an equipment box at 1–2.5 m height,
   power tether connected to the tower's port, crane holding a 15–20 kg grey module.
3. **Emergency power to a disabled small rover**: orange tether running 10–20 m to the rover; keep-alive module left
   beside the rover — a gold-MLI box 0.9 × 0.45 × 0.45 m on four short feet with a vertical mast carrying two
   back-to-back dark-blue solar panels (≈ 1.2 m wide × 1.25 m tall each, top edge ≈ 1.6 m above ground) and a short
   cable to the rover's power port.
4. **Anchored winch recovery on a 10–15° slope**: TSR-1 upslope and lowered, rear spades in the ground, two anchors
   installed in front of it with short straps to the front lugs, taut line running downslope to a 450 kg rover whose
   wheels are partly sunk.
5. **Stowed on a lander deck**: mast folded rearward, arms in upright stow at the front corners (highest point ≈ 1.75 above
   ground), boom stowed rearward over the spine; launch locks visible at the arm elbows and boom tip.

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
