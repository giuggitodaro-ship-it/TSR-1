"""Blender geometry helpers. World coordinates, metre units, preserved pivot parenting."""
import bpy, math
from mathutils import Vector, Matrix
MODE=''; ROOT=None; COLLECTIONS={}; MATERIALS={}
SOURCES={'STRUCTURE':'DESIGN_FREEZE_V1.md §14; engineering/subsystem_specs/structure.md','MOBILITY':'DESIGN_FREEZE_V1.md §3; engineering/subsystem_specs/mobility.md','DEX_ARM_L':'DESIGN_FREEZE_V1.md §5; engineering/subsystem_specs/manipulation.md','DEX_ARM_R':'DESIGN_FREEZE_V1.md §5; engineering/subsystem_specs/manipulation.md','CRANE':'DESIGN_FREEZE_V1.md §5; engineering/subsystem_specs/manipulation.md','SERVICE_SPINE':'src/tsr1/design/layout.py; engineering/subsystem_specs/service_spine.md','RECOVERY':'DESIGN_FREEZE_V1.md §7; engineering/subsystem_specs/recovery.md','SENSOR_MAST':'engineering/subsystem_specs/structure.md; sensors.md','SENSORS':'DESIGN_FREEZE_V1.md §10; engineering/subsystem_specs/sensors.md','POWER':'DESIGN_FREEZE_V1.md §8; engineering/subsystem_specs/power.md','THERMAL':'DESIGN_FREEZE_V1.md §9; src/tsr1/design/layout.py','TOOL_RACK':'engineering/subsystem_specs/tools.md; engineering/interfaces.md','DUST_MITIGATION':'DESIGN_FREEZE_V1.md §13; engineering/subsystem_specs/dust.md','BRANDING':'docs/VISUAL_RENDER_SPEC.md §8','INTERNAL_VOLUMES':'engineering/subsystem_specs/structure.md; power.md'}
def setup(scene,mode):
    global MODE, ROOT, COLLECTIONS
    MODE=mode; COLLECTIONS={}
    ROOT=bpy.data.collections.new('TSR1_ROOT_'+mode); scene.collection.children.link(ROOT)
    ROOT['source_commit']='95f06abd408712dffba3958a1003227ca7db70d2'
    for k in SOURCES: collection(k)
def name(n): return n if n.startswith(MODE+'_') else MODE+'_'+n
def collection(k):
    if k not in COLLECTIONS:
        c=bpy.data.collections.new(MODE+'/'+k); ROOT.children.link(c); COLLECTIONS[k]=c
        c['engineering_source']=SOURCES.get(k,'Visualization environment / presentation only')
    return COLLECTIONS[k]
def finish(o,n,mat,coll,parent=None):
    o.name=name(n); collection(coll).objects.link(o)
    o['engineering_source']=SOURCES.get(coll,'Presentation geometry, not part of TSR-1')
    o['configuration']=MODE; o['subsystem']=coll
    if mat:
        m=MATERIALS[mat] if isinstance(mat,str) else mat
        o.data.materials.append(m)
    if parent:
        o.parent=parent; o.matrix_parent_inverse=parent.matrix_world.inverted()
    return o
def mesh(name_,verts,faces,mat,coll,parent=None,loc=(0,0,0)):
    m=bpy.data.meshes.new(name(name_)+'_mesh');m.from_pydata(verts,[],faces);m.update()
    o=bpy.data.objects.new(name(name_),m);o.matrix_world=Matrix.Translation(Vector(loc))
    return finish(o,name_,mat,coll,parent)
def box(name,loc,dims,mat,coll,parent=None,bevel=.004):
    x,y,z=[v/2 for v in dims]
    v=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
    f=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
    o=mesh(name,v,[tuple(reversed(face)) for face in f],mat,coll,parent,loc)
    if bevel:
        b=o.modifiers.new('Small manufactured edge radius','BEVEL');b.width=min(bevel,min(dims)/4);b.segments=2
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o
def cyl(name,a,b,r,mat,coll,parent=None,vertices=32):
    a,b=Vector(a),Vector(b);d=b-a;L=d.length
    if L<1e-7: raise ValueError(name+' zero cylinder')
    v=[(r*math.cos(i*math.tau/vertices),r*math.sin(i*math.tau/vertices),z) for z in (-L/2,L/2) for i in range(vertices)]
    f=[tuple(reversed(range(vertices))),tuple(range(vertices,2*vertices))]+[(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
    o=mesh(name,v,f,mat,coll,None)
    o.matrix_world=Matrix.Translation((a+b)/2)@d.to_track_quat('Z','Y').to_matrix().to_4x4()
    if parent:o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted()
    for p in o.data.polygons[2:]:p.use_smooth=True
    return o
def empty(name,loc,coll,parent=None):
    o=bpy.data.objects.new(name, None);o.matrix_world=Matrix.Translation(Vector(loc));o.empty_display_size=.065;o.empty_display_type='PLAIN_AXES'
    return finish(o,name,None,coll,parent)
def sphere(name,loc,r,mat,coll,parent=None):
    v=[];f=[];n=24;k=12
    for j in range(k+1):
        th=math.pi*j/k
        for i in range(n):v.append((r*math.sin(th)*math.cos(i*math.tau/n),r*math.sin(th)*math.sin(i*math.tau/n),r*math.cos(th)))
    for j in range(k):
        for i in range(n):f.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    o=mesh(name,v,f,mat,coll,parent,loc)
    for p in o.data.polygons:p.use_smooth=True
    return o
def line(name,points,r,mat,coll,parent=None):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=r;c.bevel_resolution=2;c.use_fill_caps=True
    s=c.splines.new('POLY');s.points.add(len(points)-1)
    for p,xyz in zip(s.points,points):p.co=(*xyz,1)
    o=bpy.data.objects.new(name,c);o.matrix_world=Matrix.Identity(4)
    return finish(o,name,mat,coll,parent)
def torus(name,loc,major,minor,mat,coll,parent=None,axis='Z'):
    v=[];f=[];n=40;k=8
    for i in range(n):
        a=i*math.tau/n
        for j in range(k):
            b=j*math.tau/k;x=(major+minor*math.cos(b))*math.cos(a);y=(major+minor*math.cos(b))*math.sin(a);z=minor*math.sin(b)
            v.append((x,y,z) if axis=='Z' else (x,z,y) if axis=='Y' else (z,x,y))
    for i in range(n):
        for j in range(k):f.append((i*k+j,((i+1)%n)*k+j,((i+1)%n)*k+(j+1)%k,i*k+(j+1)%k))
    o=mesh(name,v,f,mat,coll,parent,loc)
    for p in o.data.polygons:p.use_smooth=True
    return o
def label(name,text,loc,size,mat,coll,parent=None,rotation=(0,0,0)):
    c=bpy.data.curves.new(name,'FONT');c.body=text;c.size=size;c.extrude=.0002;c.align_x='CENTER';c.align_y='CENTER'
    o=bpy.data.objects.new(name,c);o.matrix_world=Matrix.Translation(Vector(loc));o.rotation_euler=rotation
    return finish(o,name,mat,coll,parent)
def materials():
    defs={'Ti':((.28,.31,.34),.78,.39),'Al':((.64,.68,.71),.8,.28),'CFRP':((.008,.012,.016),.02,.72),'White':((.8,.81,.77),.06,.7),'Boot':((.095,.105,.11),.1,.7),'Vectran':((.69,.7,.6),.05,.75),'Glass':((.013,.04,.058),.6,.12),'Gold':((.54,.35,.10),.72,.36),'PV':((.015,.035,.10),.55,.27),'OSR':((.72,.83,.86),.62,.2),'Orange':((.95,.20,.025),.0,.48),'Dark':((.027,.043,.055),.15,.4),'LED':((.60,.76,.95),.0,.28),'Ground':((.60,.65,.69),.0,.9),'Regolith':((.19,.19,.18),.0,1)}
    for k,(color,metal,rough) in defs.items():
        m=bpy.data.materials.new('TSR1_'+k);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
        if k=='LED':p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=.5
        if k in ('Gold','White','CFRP','Regolith'):
            nodes=m.node_tree.nodes;noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value={'Gold':95,'White':180,'CFRP':230,'Regolith':35}[k];noise.inputs['Detail'].default_value=2
            bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.004 if k=='Regolith' else .0005;m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
        MATERIALS[k]=m
    return MATERIALS
