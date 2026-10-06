"""Read GLB and FBX back into independent empty Blender scenes; report bounds."""
import bpy,json
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;out={}
for ext in ('glb','fbx'):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 p=H/('TSR1_engineering.'+ext)
 if ext=='glb':bpy.ops.import_scene.gltf(filepath=str(p))
 else:bpy.ops.import_scene.fbx(filepath=str(p))
 bpy.context.view_layer.update()
 pts=[o.matrix_world@Vector(v) for o in bpy.context.scene.objects if o.type=='MESH' for v in o.bound_box]
 lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 dims=[hi[i]-lo[i] for i in range(3)]
 out[ext]={'import_success':True,'mesh_objects':sum(o.type=='MESH' for o in bpy.context.scene.objects),'bounds_min_m':lo,'bounds_max_m':hi,'dimensions_m':dims,'dimension_check_pass':all(abs(a-b)<.015 for a,b in zip(dims,(3.6,2.4,2.2)))}
(H/'interchange_validation.json').write_text(json.dumps(out,indent=2));print(out)
