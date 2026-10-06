# TSR-1 Blender build notes

## Result and provenance

This visualization reconstructs the complete dedicated TSR-1 frozen vehicle from `claude/happy-feynman-043306`, engineering baseline commit `95f06abd408712dffba3958a1003227ca7db70d2`. Repository identity/default branch and PROJECT_STATE were checked through the GitHub connector. The engineering study reports Phase 7 complete, baseline 2026-10-03. No frozen engineering requirements, design freeze, mass/power budget, simulation or trade-study source was changed.

Model scale is 1 Blender unit=1 metre; X forward, Y left, Z up. The .blend contains separately organized subsystem collections, source metadata, material assignments, camera sets and inspectable internal allocation volumes. It is an engineering concept visualization, not manufacturing CAD or an independently qualified vehicle design.

Blender 5.2.2 LTS was opened and operated through Computer Use on the Mac. The build script was executed in Blender's Python console and saved the actual .blend. Background Blender was also used for repeatable dimension/collision checks and batch rendering. The first console attempt reset its editor context; the script was corrected to preserve the interactive context. An initial restricted-process graphics startup failed; successful Blender runs then used the permitted graphics environment. These are tooling issues, not model completion evidence; actual saved geometry, rendered images and read-back results are the evidence.

## Files and configurations

- `TSR1.blend`: editable primary model, five required configurations plus `RECOVERY_SLOPE_12DEG`.
- `TSR1_engineering.glb` and `.fbx`: TRAVERSE interchange assembly. Both were imported back into clean Blender sessions; 942 mesh objects and 3.60×2.40×2.20m bounds verified. The .blend is the authoritative articulated/multi-scene deliverable; interchange files depict the traverse configuration.
- `build_tsr1.py`: entry point, reads run_config and imports actual `src/tsr1/design/layout.py`.
- `tsr1_utils.py`, `tsr1_mobility.py`, `tsr1_equipment.py`, `tsr1_manipulation.py`: reproducible geometry, materials and pivots.
- `inspect_tsr1.py`, `verify_interchange.py`, `render_tsr1.py`: validation and render entry points. `finalize_tsr1.py` refreshes embedded provenance and the startup view without rebuilding geometry.
- `geometry_measurements.json`, `collision_review.json`, `interchange_validation.json`: raw measured evidence.
- Seven requested BLENDER documentation files accompany the project; source scripts and documentation are also embedded as Blender text blocks.

Choose a scene in Blender's top scene selector:

| Scene | Pose |
|---|---|
| TRAVERSE | Chassis underside 0.45 m, candle arms, deployed mast, rearward crane, carried anchors/spades |
| SERVICING | Chassis underside 0.10 m, both arms working with gripper/socket, deployed cable-stayed crane and illustrative 18 kg ORU |
| RECOVERY | Chassis underside 0.10 m, working fairlead 0.25 m, inserted spades, two front anchors/straps and rear line |
| EMERGENCY_POWER | Orange tether toward a remote asset interface datum; no invented target rover |
| LANDER_STOW | Mast folded 37°, candle arms/launch locks, crane locked; maximum height 1.75 m |
| RECOVERY_SLOPE_12DEG | Additional terrain pose derived from RECOVERY; physical uphill/downhill context |

Each primary scene contains ISO_FRONT_LEFT, ISO_REAR_RIGHT, FRONT, REAR, LEFT, RIGHT, TOP and FUNCTIONAL cameras. Internal packaging collection is hidden in exterior renders and can be inspected separately. The default saved view is TRAVERSE. There is no executable startup handler in the blend; embedded scripts run only when explicitly invoked.

## Rebuild and verify

From repository root, with a Blender executable:

```sh
blender --background --python visualization/blender/build_tsr1.py -- --render
blender --background visualization/blender/TSR1.blend --python visualization/blender/inspect_tsr1.py
blender --background --python visualization/blender/verify_interchange.py
blender --background visualization/blender/TSR1.blend --python visualization/blender/finalize_tsr1.py
```

On this Mac, the executable is `/Applications/Blender.app/Contents/MacOS/Blender`. To render an existing project without rebuilding:

```sh
blender --background visualization/blender/TSR1.blend --python visualization/blender/render_tsr1.py
```

The scripts require Blender's bundled Python and this repository checkout; no pip dependencies, external assets or generated-image textures are required. Geometry parameters are centralized or cited where they are derived. Rebuilding replaces only visualization outputs in this directory.

## Validation and limits

63 of 63 dimension checks pass within stated tolerances. Both interchange formats reopen at the intended metre scale. Reviewed primary static subsystem pairs have no detected surface intersections after corrections. 53 of 54 sampled sensor sightlines are clear; a downward rear LiDAR ray meets the deployed recovery line. The full steering/suspension swept envelope is not validated and sampled large steering angles do collide with the frozen body. This remains a source-design packaging issue, explicitly logged as C14.

Documented reconstruction assumptions include the outer-diameter grouser convention, folding A-frame, 37° mast stow, low service-spine loadout, elevated fixed side-array brackets, middle-fender clearance relief, transverse link section, anchor clips, segmented MOD-KA folded PV and spade deployment links. Fairlead 0.25 m applies to lowered recovery; it is 0.60 m in raised unloaded transport. The latter is not permission to winch in the rejected high-fairlead condition. Mass budgets and material strengths were not recalculated.

Rendering uses a neutral engineering studio and a separate lunar setup with black world/background, a 1° solar elevation and 0.53° solar angular diameter. No atmosphere, blue haze, dust plume, agency insignia or invented vehicle equipment is added. Texture nodes are material approximations, not optical/thermal measurements.


## Final completion pass — 2026-10-06

The newest on-disk/UI save contained an earlier geometry revision than the validated render checkpoint. Both earlier files and the live UI state were preserved under local `checkpoints/` before the final build. These recovery copies are excluded from version control and are not delivery files.

The final source reconstruction was executed again in Blender. All 63 dimensional checks passed. GLB and FBX were exported and re-imported, each containing 942 meshes with the expected 3.60 × 2.40 × 2.20 m traverse bounds. The static subsystem review was repeated, including arms against mobility hardware. An additional 20 independent rocker/bogie samples at −10°, −5°, 0°, +5° and +10° found no intersections with the chassis and side arrays. This is a sampled clearance check, not a terrain-contact or combined-motion solution.

The supplemental 12° scene initially exposed a duplicated-parent transform defect. Explicitly preserving parent inverses and local transforms corrected it. All 1,011 copied non-presentation objects are checked against the expected rigid rotation, with maximum matrix-element error below 2.4×10⁻⁷. The final slope render shows the assembled rover.

A 1 mm deck-finish offset removed coplanar shading artifacts. Side branding orientation and placement were corrected. Horizontal orthographic views now have a seamless neutral background. The fourteen PNG renders were regenerated from the corrected geometry. Final documentation and sources are embedded in the saved `.blend`; its default view is TRAVERSE with editing overlays hidden for readability. Enable overlays when inspecting pivots and cameras.

The unresolved design issue is C14: sampled large steering angles intersect the frozen closed body. The model preserves that body and reports the conflict. Other documented assumptions and the one sampled recovery-line LiDAR occlusion remain explicit. No engineering-design approval, full swept-motion clearance, mass verification or manufacturing qualification is implied.
