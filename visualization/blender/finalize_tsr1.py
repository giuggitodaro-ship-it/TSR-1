"""Refresh embedded provenance and save an uncluttered, editable startup view.

Run in the existing TSR1.blend, after geometry validation and rendering.
This does not rebuild geometry or alter engineering dimensions.
"""
from pathlib import Path
import bpy

HERE = Path(__file__).resolve().parent


def finalize():
    required = {'TRAVERSE', 'SERVICING', 'RECOVERY', 'EMERGENCY_POWER',
                'LANDER_STOW', 'RECOVERY_SLOPE_12DEG'}
    assert required <= set(bpy.data.scenes.keys())
    scene = bpy.data.scenes['TRAVERSE']
    bpy.context.window.scene = scene
    scene.camera = scene.objects['TRAVERSE_ISO_FRONT_LEFT']
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.collections['TRAVERSE/LUNAR_TERRAIN'].hide_viewport = True
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'CONSOLE' and area == bpy.context.area:
                area.type = 'VIEW_3D'
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                space.overlay.show_overlays = False
                space.shading.type = 'MATERIAL'
                space.region_3d.view_rotation = scene.camera.rotation_euler.to_quaternion()
                space.region_3d.view_location = (0, 0, 1)
                space.region_3d.view_distance = 7
                space.region_3d.view_perspective = 'ORTHO'
            elif area.type == 'OUTLINER':
                area.spaces.active.display_mode = 'VIEW_LAYER'
    files = sorted(HERE.glob('*.py')) + sorted(HERE.glob('BLENDER_*.md')) + [HERE/'README.md']
    for path in files:
        text = bpy.data.texts.get(path.name) or bpy.data.texts.new(path.name)
        text.clear()
        text.write(path.read_text())
        text.use_module = False
    scene['delivery_revision'] = '2026-10-06; frozen engineering 95f06abd'
    scene['validation_summary'] = '63 dimensional checks; 36 steering and 20 rocker/bogie samples; see packed documentation'
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'TSR1.blend'), compress=True)
    print('FINALIZED: six scenes, embedded source/documents, clean TRAVERSE viewport')


if __name__ == '__main__':
    finalize()
