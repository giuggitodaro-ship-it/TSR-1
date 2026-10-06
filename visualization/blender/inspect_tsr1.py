"""Reproducible static surface-intersection review and steering samples."""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from math import radians
HERE=Path(__file__).resolve().parent
out={}; sightlines=[]
def geometry(o,dg):
    ev=o.evaluated_get(dg);m=ev.to_mesh()
    if not m:return None
    vs=[ev.matrix_world@v.co for v in m.vertices];fs=[tuple(p.vertices) for p in m.polygons]
    ev.to_mesh_clear()
    if not vs or not fs:return None
    return ([(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)], BVHTree.FromPolygons(vs,fs))
def broad(a,b):return all(min(a[i][1],b[i][1])-max(a[i][0],b[i][0])>0.0001 for i in range(3))
def pairs(A,B,G):
    hits=[]
    for a in A:
        for b in B:
            if a==b or a.name not in G or b.name not in G:continue
            aa,ab=G[a.name];ba,bb=G[b.name]
            if broad(aa,ba) and ab.overlap(bb):hits.append([a.name,b.name])
    return hits
for mode in ('TRAVERSE','SERVICING','RECOVERY','LANDER_STOW'):
    s=bpy.data.scenes[mode];bpy.context.window.scene=s;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    obs=[o for o in s.objects if o.type in ('MESH','CURVE') and o.get('subsystem') not in ('PRESENTATION','CONTEXT','INTERNAL_VOLUMES')]
    G={o.name:geometry(o,dg) for o in obs};G={k:v for k,v in G.items() if v}
    group=lambda c:[o for o in obs if o.get('subsystem')==c]
    case={}
    for a,b in [('DEX_ARM_L','DEX_ARM_R'),('DEX_ARM_L','SENSOR_MAST'),('DEX_ARM_R','SENSOR_MAST'),('DEX_ARM_L','CRANE'),('DEX_ARM_R','CRANE'),('DEX_ARM_L','DUST_MITIGATION'),('DEX_ARM_R','DUST_MITIGATION'),('DEX_ARM_L','TOOL_RACK'),('DEX_ARM_R','TOOL_RACK'),('CRANE','THERMAL'),('CRANE','SERVICE_SPINE'),('SENSOR_MAST','SERVICE_SPINE'),('POWER','DUST_MITIGATION'),('POWER','MOBILITY'),('RECOVERY','DUST_MITIGATION'),('RECOVERY','MOBILITY'),('RECOVERY','POWER')]:case[a+'__'+b]=pairs(group(a),group(b),G)
    links=[o for o in group('MOBILITY') if any(t in o.name for t in ('link_','pin_','guide_','screw_','carriage_','steering_fork'))]
    wheel=[o for o in group('MOBILITY') if any(t in o.name for t in ('wheel_rim','grouser','flexure_spoke'))]
    case['LINKS__WHEEL']=pairs(links,wheel,G)
    case['DEX_ARM_L__MOBILITY']=pairs(group('DEX_ARM_L'),group('MOBILITY'),G)
    case['DEX_ARM_R__MOBILITY']=pairs(group('DEX_ARM_R'),group('MOBILITY'),G)
    out[mode]=case
    if mode in ('TRAVERSE','SERVICING','RECOVERY'):
        sensor_specs=[('NAV_L','NavCam_L_optical_center',(1,0,0),.006),('NAV_R','NavCam_R_optical_center',(1,0,0),.006),('LIDAR_FRONT','front_LiDAR',(1,0,0),.080),('LIDAR_REAR','rear_LiDAR',(-1,0,0),.080),('HAZ_SIDE_L','HazCam_L_housing',(0,1,0),.045),('HAZ_SIDE_R','HazCam_R_housing',(0,-1,0),.045)]
        for tag,n,direc,offset in sensor_specs:
            ob=s.objects[mode+'_'+n];direction=Vector(direc);origin=ob.matrix_world.translation+direction*offset
            for tilt in (0,-.45,.45):
                ray=(direction+Vector((0,0,tilt))).normalized();hits=[]
                for name,(bb,tree) in G.items():
                    hit,normal,index,dist=tree.ray_cast(origin,ray,3.0)
                    if hit is not None and dist>.001:hits.append((dist,name))
                sightlines.append({'mode':mode,'sensor':tag,'vertical_slope':tilt,'first_obstruction':min(hits) if hits else None,'distance_checked_m':3})
# Steering sample complete wheel/fender assemblies against chassis and fixed arrays.
s=bpy.data.scenes['TRAVERSE'];bpy.context.window.scene=s
steers=[o for o in s.objects if 'steering_' in o.name and o.type=='EMPTY']
res=[]
for st in steers:
    original=st.rotation_euler.copy();desc=list(st.children_recursive)
    fixed=[o for o in s.objects if o.name.endswith('chassis_torque_box') or '_solar_array_' in o.name]
    for deg in (0,10,15,30,60,90):
        st.rotation_euler.z=radians(deg);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
        objects=[o for o in desc+fixed if o.type in ('MESH','CURVE')];G={o.name:geometry(o,dg) for o in objects};G={k:v for k,v in G.items() if v}
        hit=pairs(desc,fixed,G);res.append({'assembly':st.name,'degrees':deg,'intersections':hit})
    st.rotation_euler=original
bpy.context.view_layer.update();out['steering_samples']=res;out['sensor_sightlines']=sightlines
# Independent concept-pivot excursions, not a closed-loop suspension/contact solver.
motion=[]
for pivot in [o for o in s.objects if o.type=='EMPTY' and any(k in o.name for k in ('rocker_pivot_','bogie_pivot_'))]:
    original=pivot.rotation_euler.copy();desc=list(pivot.children_recursive)
    fixed=[o for o in s.objects if o.name.endswith('chassis_torque_box') or '_solar_array_' in o.name]
    for deg in (-10,-5,0,5,10):
        pivot.rotation_euler.y=radians(deg);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
        objects=[o for o in desc+fixed if o.type in ('MESH','CURVE')];G={o.name:geometry(o,dg) for o in objects};G={k:v for k,v in G.items() if v}
        motion.append({'pivot':pivot.name,'degrees':deg,'intersections':pairs(desc,fixed,G)})
    pivot.rotation_euler=original;bpy.context.view_layer.update()
out['rocker_bogie_samples']=motion
(HERE/'collision_review.json').write_text(json.dumps(out,indent=2))
for k,v in out.items():
    if k not in ('steering_samples','sensor_sightlines','rocker_bogie_samples'):print(k,{a:len(b) for a,b in v.items() if b})
print('Steering sampled results',[(r['assembly'],r['degrees'],len(r['intersections'])) for r in res])
print('Rocker/bogie sampled results',[(r['pivot'],r['degrees'],len(r['intersections'])) for r in motion])
