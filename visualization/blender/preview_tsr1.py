import bpy
from pathlib import Path
H=Path(__file__).resolve().parent
(H/'renders').mkdir(exist_ok=True)
for mode,cam in [('TRAVERSE','ISO_FRONT_LEFT'),('TRAVERSE','ISO_REAR_RIGHT'),('SERVICING','FUNCTIONAL'),('LANDER_STOW','ISO_FRONT_LEFT')]:
 s=bpy.data.scenes[mode];bpy.context.window.scene=s;s.camera=bpy.data.objects[mode+'_'+cam];s.render.resolution_percentage=60;s.cycles.samples=12;s.render.filepath=str(H/'renders'/('preview_'+mode+'_'+cam+'.png'));bpy.ops.render.render(write_still=True)
