"""Rebuild the repository-frozen TSR-1 in Blender 5.x, metres.
Run from Blender Python console:
 exec(compile(open('/absolute/path/build_tsr1.py').read(), '/absolute/path/build_tsr1.py', 'exec'))
Or: blender --background --python build_tsr1.py -- --render
Only visualization outputs are written. Engineering source files are read-only.
"""
from pathlib import Path
import sys, json, math, importlib, datetime, random
import bpy
from mathutils import Vector, Matrix
HERE=Path(__file__).resolve().parent
REPO=HERE.parent.parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(REPO/'src'))
for m in ('tsr1_utils','tsr1_mobility','tsr1_equipment','tsr1_manipulation'):
    if m in sys.modules: importlib.reload(sys.modules[m])
import tsr1_utils as u
import tsr1_mobility, tsr1_equipment, tsr1_manipulation
from tsr1.design.layout import deck_layout
assert (HERE/'BLENDER_MODEL_REQUIREMENTS.md').exists(), 'Requirements must predate detailed model'
assert (HERE/'BLENDER_MATERIAL_TRACEABILITY.md').exists()
P=json.loads((REPO/'simulations/configs/run_config.json').read_text())['baseline_options']
RAD_AREA=1.6429435507420518 # thermal radiator_area result, recorded in requirements; rounded freeze1.64
LAYOUT=deck_layout(P['wheelbase'],1.5,RAD_AREA,P['dex_links'][0])
MODES=['TRAVERSE','SERVICING','RECOVERY','EMERGENCY_POWER','LANDER_STOW']
METADATA={}

def progress(s):
    print(s,flush=True)
    with (HERE/'build_progress.log').open('a') as f:f.write(s+'\n')

def camera(scene,n,loc,target,scale):
    data=bpy.data.cameras.new(n);data.type='ORTHO';data.ortho_scale=scale;data.lens=50;data.clip_end=500
    o=bpy.data.objects.new(scene.name+'_'+n,data);u.collection('PRESENTATION').objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o['exclude_from_vehicle_envelope']=True
    return o

def lighting(scene):
    world=bpy.data.worlds.new(scene.name+'_world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.37,.42,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45;scene.world=world
    for name,loc,energy,size in [('Key',(3,4,7),1250,5),('Fill',(-4,1,4),950,4),('Rim',(1,-5,5),1400,4)]:
        ld=bpy.data.lights.new(scene.name+'_'+name,'AREA');ld.energy=energy;ld.shape='DISK';ld.size=size;o=bpy.data.objects.new(scene.name+'_'+name,ld);u.collection('PRESENTATION').objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
    ld=bpy.data.lights.new(scene.name+'_LUNAR_SUN_1deg','SUN');ld.energy=3;ld.angle=math.radians(.53)
    sun=bpy.data.objects.new(scene.name+'_LUNAR_SUN_1deg',ld);u.collection('PRESENTATION').objects.link(sun);sun.rotation_euler=Vector((-.94,-.34,-math.sin(math.radians(1)))).to_track_quat('-Z','Y').to_euler();sun.hide_render=True
    floor=u.box('presentation_ground',(0,0,-.03),(100,100,.05),'Ground','PRESENTATION',bevel=0);floor['exclude_from_vehicle_envelope']=True
    if scene.name=='TRAVERSE':
        rng=random.Random(21)
        for k in range(48):
            x,y=rng.uniform(-7,7),rng.uniform(-7,7)
            if abs(x)<2.1 and abs(y)<1.55:continue
            r=rng.uniform(.045,.12)
            ob=u.sphere('lunar_rock_'+str(k),(x,y,r*.4),r,'Regolith','LUNAR_TERRAIN')
            ob.scale=(1.3,.8,.55)
        u.collection('LUNAR_TERRAIN').hide_render=True
    return floor

def scene_settings(s):
    s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.unit_settings.length_unit='METERS'
    s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.cycles.max_bounces=5
    s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=False
    s.view_settings.view_transform='AgX';s.view_settings.exposure=-.25;s.render.use_file_extension=True
    s['coordinate_system']='X forward / Y left / Z up; 1 Blender unit=1m'
    s['source_branch']='claude/happy-feynman-043306';s['source_commit']='95f06abd408712dffba3958a1003227ca7db70d2'
    s['model_scope']='Concept-level geometric reconstruction, not qualified manufacturing or collision-certified CAD'

def build_all():
    (HERE/'build_progress.log').write_text('TSR-1 rebuild started\n')
    # Clean generated Blender scene only; disk sources are never edited.
    if bpy.app.background:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    else:
        for ob in list(bpy.data.objects): bpy.data.objects.remove(ob, do_unlink=True)
        for co in list(bpy.data.collections): bpy.data.collections.remove(co)
        for sc in list(bpy.data.scenes):
            if sc != bpy.context.scene: bpy.data.scenes.remove(sc)
        for ma in list(bpy.data.materials): bpy.data.materials.remove(ma)
    base=bpy.context.scene
    u.materials()
    for idx,mode in enumerate(MODES):
        progress('Building '+mode)
        s=base if idx==0 else bpy.data.scenes.new(mode);s.name=mode;bpy.context.window.scene=s
        scene_settings(s);u.setup(s,mode)
        body=u.empty('body_lowering_carriage_ROOT',(0,0,0),'STRUCTURE');body['mode']=mode
        deck=.55 if mode in ('SERVICING','RECOVERY') else .9
        ctx={'utils':u,'mode':mode,'deck':deck,'body':body,'params':P,'layout':LAYOUT}
        a=tsr1_mobility.build(ctx);b=tsr1_equipment.build(ctx);c=tsr1_manipulation.build(ctx)
        METADATA[mode]={'mobility':a,'equipment':b,'manipulation':c,'deck':deck}
        bpy.context.view_layer.update()
        floor=lighting(s)
        # Exact standard camera set, available in every scene for further inspection.
        views={'ISO_FRONT_LEFT':((6,7,5),(0,0,1),5.0),'ISO_REAR_RIGHT':((-6,-7,4.7),(0,0,.95),5.0),
               'FRONT':((8,0,1.1),(0,0,1.1),4.3),'REAR':((-8,0,1.1),(0,0,1.1),4.3),
               'LEFT':((0,8,1.1),(0,0,1.1),4.5),'RIGHT':((0,-8,1.1),(0,0,1.1),4.5),'TOP':((0,0,9),(0,0,0),4.6)}
        if mode=='SERVICING':views['FUNCTIONAL']=((7,7,5.3),(.5,0,1.2),5.6)
        elif mode=='RECOVERY':views['FUNCTIONAL']=((-8,-9,6),(-1.4,0,.5),8.5)
        elif mode=='EMERGENCY_POWER':views['FUNCTIONAL']=((10,12,9),(4.5,0,.7),14.5)
        else:views['FUNCTIONAL']=((5.5,6.5,4.3),(0,0,.9),5.0)
        cams={n:camera(s,n,*v) for n,v in views.items()};s.camera=cams['ISO_FRONT_LEFT']
        if mode=='SERVICING':
            hook=c['crane']['hook'].matrix_world.translation
            load=u.box('demonstration_ORU_18kg',(hook.x,hook.y,hook.z-.28),(.34,.32,.36),'White','CONTEXT',bevel=.008)
            load['depiction']='Example 18kg ORU envelope, not a newly specified TSR1 component';load['exclude_from_vehicle_envelope']=True
            u.line('demonstration_load_sling',[hook,(hook.x,hook.y-.12,hook.z-.1),(hook.x,hook.y+.12,hook.z-.1),hook],.005,'Vectran','CONTEXT')
        if mode=='EMERGENCY_POWER':
            target=u.box('demonstration_asset_power_port',(11.16,0,.22),(.10,.18,.24),'Dark','CONTEXT');target['exclude_from_vehicle_envelope']=True
            target['depiction']='Asset interface datum only; no invented target vehicle hardware'
        # Internals toggle as whole collection, geometries retained for engineering inspection.
        u.collection('INTERNAL_VOLUMES').hide_render=True
        bpy.context.view_layer.update()
        progress(mode+' objects '+str(len(s.objects)))
    make_slope_scene()
    bpy.context.window.scene=bpy.data.scenes['TRAVERSE']
    for screen in bpy.data.screens:
        for ar in screen.areas:
            if ar.type=='VIEW_3D':
                ar.spaces.active.region_3d.view_distance=5.5;ar.spaces.active.region_3d.view_location=(0,0,1)
                ar.spaces.active.region_3d.view_rotation=bpy.data.scenes['TRAVERSE'].camera.rotation_euler.to_quaternion()
                ar.spaces.active.shading.type='MATERIAL'
    validate()
    # Scripts/docs packed as Blender text blocks for provenance and inspectability.
    for p in sorted(HERE.glob('*.py'))+sorted(HERE.glob('BLENDER_*.md')):
        t=bpy.data.texts.get(p.name) or bpy.data.texts.new(p.name);t.clear();t.write(p.read_text())
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'TSR1.blend'),compress=True)
    progress('SAVED TSR1.blend')

def make_slope_scene():
    src=bpy.data.scenes['RECOVERY'];bpy.context.window.scene=src;bpy.context.view_layer.update()
    dst=bpy.data.scenes.new('RECOVERY_SLOPE_12DEG');scene_settings(dst);dst.world=src.world.copy();cl=bpy.data.collections.new('RECOVERY_SLOPE_CONTEXT');dst.collection.children.link(cl)
    mapping={}
    for ob in src.objects:
        n=ob.copy();n.name='SLOPE_'+ob.name;cl.objects.link(n);mapping[ob]=n
    for ob,n in mapping.items():
        # Object.copy() parenting can reset the inverse; restore both explicitly.
        if ob.parent:n.parent=mapping[ob.parent]
        n.matrix_parent_inverse=ob.matrix_parent_inverse.copy()
        n.matrix_basis=ob.matrix_basis.copy()
    root=bpy.data.objects.new('RECOVERY_TERRAIN_FRAME_12DEG',None);cl.objects.link(root)
    for ob,n in mapping.items():
        if not ob.parent and ob.get('subsystem')!='PRESENTATION':
            n.parent=root;n.matrix_parent_inverse=Matrix.Identity(4);n.matrix_basis=ob.matrix_world.copy()
    root.rotation_euler.y=math.radians(-12)
    ground=mapping[src.objects['RECOVERY_presentation_ground']];ground.rotation_euler.y=math.radians(-12)
    dst.camera=mapping[src.objects['RECOVERY_FUNCTIONAL']]
    dst['terrain_slope_degrees']=12;dst['dimension_note']='Primary flat RECOVERY scene retains engineering frame; this pose rotates hardware and terrain together.'
    bpy.context.window.scene=dst;bpy.context.view_layer.update()
    deviations=[]
    for ob,n in mapping.items():
        if ob.get('subsystem')!='PRESENTATION':
            expected=root.matrix_world@ob.matrix_world
            deviations.append(max(abs(n.matrix_world[i][j]-expected[i][j]) for i in range(4) for j in range(4)))
    largest=max(deviations)
    assert largest<1e-5, f'Slope assembly transform error: {largest}'
    dst['verified_rigid_transform_max_error']=largest
    progress('SLOPE rigid transform checked: '+str(len(deviations))+' objects, max error '+str(largest))


def points(o):
    if o.type not in ('MESH','CURVE','FONT'):return []
    return [o.matrix_world@Vector(p) for p in o.bound_box]

def bbox(objects):
    pts=[v for o in objects for v in points(o)]
    if not pts:return None
    lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
    return {'min':lo,'max':hi,'size':[hi[i]-lo[i] for i in range(3)]}

def validate():
    result={'source_commit':'95f06abd408712dffba3958a1003227ca7db70d2','blender_version':bpy.app.version_string,'modes':{},'checks':[]}
    rows=[]
    def check(label,ref,measured,tol=.005,note=''):
        err=measured-ref;ok=abs(err)<=tol
        result['checks'].append({'property':label,'repository':ref,'measured':measured,'error':err,'tolerance':tol,'pass':ok,'note':note})
        rows.append(f'| {label} | {ref:.6f} | {measured:.6f} | {err:+.6f} | {"PASS" if ok else "FAIL"} | {note} |')
    for mode in MODES:
        s=bpy.data.scenes[mode];bpy.context.window.scene=s;bpy.context.view_layer.update()
        objs=[o for o in s.objects if o.get('subsystem') not in ('PRESENTATION','CONTEXT','INTERNAL_VOLUMES','LUNAR_TERRAIN') and not o.get('exclude_from_vehicle_envelope')]
        bb=bbox(objs);result['modes'][mode]={'hardware_bounds_m':bb,'objects':len(objs),'mesh_objects':sum(o.type=='MESH' for o in objs)}
        if mode in ('TRAVERSE','LANDER_STOW'):
            check(mode+' overall length [m]',3.6,bb['size'][0],.015)
            check(mode+' overall width [m]',2.4,bb['size'][1],.005)
            check(mode+' top above ground [m]',2.2 if mode=='TRAVERSE' else 1.75,bb['max'][2],.005)
        ch=next(o for o in s.objects if o.name==mode+'_chassis_torque_box')
        cb=bbox([ch]);check(mode+' chassis ground clearance [m]',.10 if mode in ('SERVICING','RECOVERY') else .45,cb['min'][2])
        for i,n in enumerate(('length','width','height')):
            if mode=='TRAVERSE':check('chassis '+n+' [m]',(2.6,1.5,.45)[i],cb['size'][i])
        loc=lambda n:s.objects.get(mode+'_'+n).matrix_world.translation
        if mode=='TRAVERSE':
            check('wheelbase [m]',2.6,abs(loc('wheel_axle_FL').x-loc('wheel_axle_RL').x))
            check('track [m]',2.0,abs(loc('wheel_axle_FL').y-loc('wheel_axle_FR').y))
            wheelparts=[o for o in s.objects if any(k in o.name for k in ('wheel_rim_FL','rim_edge_FL','grouser_FL'))]
            wb=bbox(wheelparts);check('wheel tip diameter [m]',.90,2*max(math.hypot((o.matrix_world@v.co).x-1.3,(o.matrix_world@v.co).z-.45) for o in wheelparts for v in o.data.vertices),.002,'C06: radial tip diameter; .43 tread + .02 grouser')
            check('wheel width [m]',.40,wb['size'][1],.001)
            check('mast tube [m]',1.20,(loc('mast_pan_axis')-loc('mast_fold_hinge')).length)
            check('stereo optical baseline [m]',.25,(loc('NavCam_L_optical_center')-loc('NavCam_R_optical_center')).length)
            rb=bbox([next(o for o in s.objects if 'radiator_1p643m2' in o.name)]);check('radiator gross area [m2]',RAD_AREA,rb['size'][0]*rb['size'][1],.0001)
            spineparts=[o for o in s.objects if 'spine_long_rail' in o.name or 'spine_cross_rail' in o.name];sb=bbox(spineparts)
            check('spine X footprint [m]',.90,sb['size'][0]);check('spine Y footprint [m]',1.35,sb['size'][1])
            for side in ('L','R'):
                pb=bbox([s.objects[mode+'_solar_array_'+side]]);check('solar '+side+' length [m]',1.50,pb['size'][0]);check('solar '+side+' height [m]',.50,pb['size'][2])
        for side in ('L','R'):
            A=loc('arm_'+side+'_J1_shoulder_yaw');B=loc('arm_'+side+'_J4_elbow_pitch');C=loc('arm_'+side+'_J6_wrist_pitch');D=loc('arm_'+side+'_tool_datum')
            for label_,ref,val in [('upper',.75,(B-A).length),('forearm',.70,(C-B).length),('wrist',.15,(D-C).length)]:check(mode+' arm'+side+' '+label_+' [m]',ref,val,.0001)
        check(mode+' crane boom [m]',2.60,(loc('crane_tip_datum')-loc('crane_luff_axis')).length,.0001)
        if mode=='RECOVERY':check('recovery working fairlead height [m]',.25,loc('fairlead_centre').z,.0001)
    (HERE/'geometry_measurements.json').write_text(json.dumps(result,indent=2))
    txt='# Blender geometry validation\n\nMeasured inside Blender on world-space geometry / joint datums. Unit: metres unless shown. Ground datum Z=0. Repository baseline commit `95f06abd408712dffba3958a1003227ca7db70d2`. Bounds include hardware and exclude presentation, hidden internal allocation boxes, and deployed remote cables. Functioning arms/crane naturally enlarge the operating envelope.\n\n| Property | Repository value | Blender measured value | Error | PASS/FAIL | Note |\n|---|---:|---:|---:|---|---|\n'+'\n'.join(rows)+'\n\nPASS is dimensional conformity under documented interpretations, not engineering certification. C04 fairlead height applies only in lowered recovery. C06 wheel diameter includes grousers. Internal material density/mass budgets are not recalculated by this visualization. Full motion collision certification is not claimed.\n'
    (HERE/'BLENDER_GEOMETRY_VALIDATION.md').write_text(txt)
    progress('DIMENSION CHECKS '+str(sum(x['pass'] for x in result['checks']))+'/'+str(len(result['checks'])))
    bpy.context.window.scene=bpy.data.scenes['TRAVERSE']

def export_models():
    s=bpy.data.scenes['TRAVERSE'];bpy.context.window.scene=s
    bpy.ops.object.select_all(action='DESELECT')
    for o in s.objects:
        if o.get('subsystem') not in ('PRESENTATION','CONTEXT','INTERNAL_VOLUMES','LUNAR_TERRAIN') and o.type in ('MESH','CURVE','FONT','EMPTY'):o.select_set(True)
    # glTF supports meshes; create evaluated temporary mesh copies for curves/text.
    temps=[]
    for o in list(bpy.context.selected_objects):
        if o.type in ('CURVE','FONT'):
            ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=bpy.data.meshes.new_from_object(ev);n=bpy.data.objects.new(o.name+'_export',me);s.collection.objects.link(n);n.matrix_world=o.matrix_world;temps.append(n);o.select_set(False);n.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(HERE/'TSR1_engineering.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True)
    try:
        bpy.ops.export_scene.fbx(filepath=str(HERE/'TSR1_engineering.fbx'),use_selection=True,object_types={'MESH','EMPTY'},apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
        progress('EXPORTED FBX')
    except Exception as e:progress('Optional FBX unavailable: '+str(e))
    for o in temps:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.object.select_all(action='DESELECT')
    progress('EXPORTED GLB')

def render_views(names=None):
    rd=HERE/'renders';rd.mkdir(exist_ok=True)
    jobs=[('TRAVERSE',v,f'{i:02d}_{v.lower()}') for i,v in enumerate(('ISO_FRONT_LEFT','ISO_REAR_RIGHT','FRONT','REAR','LEFT','RIGHT','TOP'),1)]
    jobs += [(m,'FUNCTIONAL',f'{i:02d}_{m.lower()}') for i,m in enumerate(MODES,8)]
    for mode,v,f in jobs:
        if names and f not in names:continue
        s=bpy.data.scenes[mode];bpy.context.window.scene=s;s.camera=bpy.data.objects[mode+'_'+v];s.render.filepath=str(rd/(f+'.png'))
        # Horizontal orthographic views use a seamless neutral background.
        ortho=v in ('FRONT','REAR','LEFT','RIGHT')
        ground=s.objects[mode+'_presentation_ground'];bg=s.world.node_tree.nodes['Background']
        old=(ground.hide_render,tuple(bg.inputs[0].default_value),bg.inputs[1].default_value)
        if ortho:
            ground.hide_render=True;bg.inputs[0].default_value=(.65,.68,.71,1);bg.inputs[1].default_value=.8
        progress('RENDER '+f);bpy.ops.render.render(write_still=True,scene=mode)
        if ortho:
            ground.hide_render,bg.inputs[0].default_value,bg.inputs[1].default_value=old
    if not names or '14_recovery_slope_12deg' in names:
        s=bpy.data.scenes['RECOVERY_SLOPE_12DEG'];bpy.context.window.scene=s;s.render.filepath=str(rd/'14_recovery_slope_12deg.png');progress('RENDER recovery slope 12deg');bpy.ops.render.render(write_still=True)
    # A physically distinct lunar lighting setup; technical views above retain neutral clarity.
    if not names or '13_lunar_south_pole' in names:
        s=bpy.data.scenes['TRAVERSE'];bpy.context.window.scene=s
        for o in s.objects:
            if o.type=='LIGHT':o.hide_render=o.data.type!='SUN'
        ground=s.objects['TRAVERSE_presentation_ground'];ground.data.materials[0]=u.MATERIALS['Regolith']
        bpy.data.collections['TRAVERSE/LUNAR_TERRAIN'].hide_render=False
        bg=s.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(0,0,0,1);bg.inputs[1].default_value=0
        s.camera=bpy.data.objects['TRAVERSE_FUNCTIONAL'];s.render.filepath=str(rd/'13_lunar_south_pole.png');progress('RENDER lunar 1deg Sun');bpy.ops.render.render(write_still=True)
        for o in s.objects:
            if o.type=='LIGHT':o.hide_render=o.data.type=='SUN'
        bpy.data.collections['TRAVERSE/LUNAR_TERRAIN'].hide_render=True
        ground.data.materials[0]=u.MATERIALS['Ground'];bg.inputs[0].default_value=(.32,.37,.42,1);bg.inputs[1].default_value=.45
    bpy.context.window.scene=bpy.data.scenes['TRAVERSE'];bpy.context.scene.camera=bpy.data.objects['TRAVERSE_ISO_FRONT_LEFT']
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'TSR1.blend'),compress=True)
    progress('RENDERS COMPLETE')

if __name__=='__main__':
    build_all()
    export_models()
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'TSR1.blend'),compress=True)
    if '--render' in sys.argv:render_views()
    from finalize_tsr1 import finalize
    finalize()
