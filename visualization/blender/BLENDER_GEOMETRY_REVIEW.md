# TSR-1 Blender geometry and access review

Executed in Blender 5.2.2 LTS, repeated on the final geometry on 2026-10-06. Baseline `95f06abd408712dffba3958a1003227ca7db70d2`. Multiple build/inspect/correct iterations were completed. Reproduce using `inspect_tsr1.py`; machine results are in `collision_review.json`. The 63 dimensional checks are recorded separately.

The review uses evaluated mesh/curve geometry, world-space bounding-box candidate rejection, and triangle BVH surface-overlap tests. It checks the actual final static assemblies in TRAVERSE, SERVICING, RECOVERY and LANDER_STOW. EMERGENCY_POWER uses the same raised assembly with the tether deployed. It does not establish full solid interference certification, joint load paths, tolerance stacks, cable tension, dynamics or a collision-free transition path. Intentional joints/fasteners, overlapping material layers and wheel/ground contact are not treated as defects.

| Review pair / function | Final observed result | Disposition |
|---|---|---|
| Left arm / right arm | No detected surface intersections in reviewed endpoint poses | Separate mirrored 7-joint chains; deployed tools are removed from rack holsters |
| Arms / mast | No detected intersections | Fixed front strip positions retained |
| Arms / crane | No detected intersections | Crane occupies centreline; service arms approach in parallel |
| Arms / wheels and fenders | No detected intersections with mobility and dust assemblies; work tips face forward | Neutral static wheel pose only |
| Arms / tool rack | No detected intersections | Rack stays within front face and above ground in lowered pose |
| Crane / radiator | No detected intersections after moving tip support off the active radiator | Frozen horizontal boom has allowed projected shading; support attaches outside rear edge |
| Crane / service spine | No detected intersections for selected low-cradle loadout | MOD-KA occupies right two slots; central low cradle/empty lane reserves boom path |
| Mast / service spine | No detected intersections | Fixed1.20m tube,37° inclined folded pose; tall future payloads require review |
| PV / fenders | No detected intersections after middle-shell relief and support rerouting | C05/C17 inferred local mounting shapes documented |
| PV / mobility | No detected intersections in raised or lowered poses | Fixed panel lower edge deck+.25; inboard bracket legs and elevated attachment |
| Recovery hardware / wheels/fenders/PV | No detected intersections | External anchor clips rerouted; anchors removed from carrier for recovery pose |
| Rocker/bogie/guide links / wheel skins and spokes | No detected intersections after narrowed transverse link envelope and carriage correction | 70×40mm link section is an inference, not a new sized structure |
| Rocker/bogie pivot excursions | 20 samples at −10°, −5°, 0°, +5° and +10° have no detected intersections against chassis/side PV | Independent pivot excursions with neutral steering; excludes wheel/ground contact constraints, differential coupling and combined articulation |
| Spade deployment | Stowed upward against rear face; recovery blades Z−.30..0 | Ground insertion is intentional. Link endpoint geometry is inferred; swept motion and soil engagement are not validated |
| Power tether exit | Front guide at Y+.55; cable clears tool face and descends to ground | Orange cable is a depicted segment;25m is reel capacity, not rendered length |
| Service-spine access | Six mechanical/power/data interface positions; two low empty ORU cradles, double-slot KA, open REC, one empty slot | Exact deck footprints preserved; no complete robotic access-path optimization claimed |
| Sensor view obstruction | 53 of54 sampled sightlines unobstructed for3m | Rear LiDAR downward sample in RECOVERY hits deployed winch line at~.90m; centre ray is clear. This is an operational line occlusion, not all-FOV clearance |

## Steering and motion limitation

Six independent steering pivots and six drive axes exist. All six neutral steering assemblies have zero detected intersections against the chassis/PV in the sampled check. Rotating them through10°,15°,30°,60° and90° shows collision for several assemblies; two corner assemblies remain clear through30° in the tested positive direction. These samples do **not** define a permissible steering envelope and do not cover both steering directions, terrain articulation or all nearby hardware.

The frozen2.00m track, .90m wheels and closed1.50m-wide body leave only.25m from wheel centre to the body side, while a wheel rotated90° projects .45m inward. The repository lacks offsets/cutouts or a detailed kingpin solution reconciling this. C14 remains an open **engineering packaging issue**. No frozen body cutout, track change or wheel relocation has been made to disguise it.

Rocker, bogie, steering, drive, lowering carriage, seven arm joints, crane slew/luff, A-frame fold, mast fold/pan/tilt and spade pivots are distinct. These are meaningful editable pivots and replicated endpoint poses; no inverse-kinematics, suspension contact solver, driven cable-length constraint or safe autonomous motion controller is supplied.

The supplemental slope scene is checked separately as a rigid transform of all 1,011 copied non-presentation objects. Maximum matrix-element deviation from the expected 12° rotation is 2.39×10⁻⁷. This verifies that the assembled model stays intact when placed on the inclined terrain; it does not simulate terrain compliance or establish slope-recovery performance.

## Corrections verified

Initial PV/fender and PV/lowering intersections were removed. Main suspension links were moved into the actual lateral clearance with a documented narrower transverse section. An initial rear crane rest crossed an EDS trace and was moved outside the radiator edge. Anchor supports were rerouted to avoid wheel skins in the lowered configuration. The module's folded PV stack now represents3.00m² total cell faces and remains within the stated stowed module envelope. Camera housings, tools and all structural details remain concept approximations.

Visual review includes front-left, rear-right, working-arm and stowed views, then all final technical and functional renders. Standard exterior renders conceal the internal packaging collection. Regolith insertion is visible in the recovery configuration; the12° slope scene applies the same terrain rotation to all recovery hardware and its ground plane, leaving the primary RECOVERY datums unchanged.

Final presentation corrections: a 1 mm offset separates the aluminium deck finish from the coplanar top of the closed chassis to remove a rendering artifact; side lettering faces outward and sits above the main suspension links; horizontal orthographic views use a seamless neutral background. The slope-scene duplicate now explicitly preserves parent inverses and local transforms. These changes do not revise frozen engineering dimensions.
