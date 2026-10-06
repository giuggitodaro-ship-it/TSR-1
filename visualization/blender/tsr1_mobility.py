"""Frozen chassis and six-wheel rocker-bogie. Unspecified linkage details are concept geometry."""
import math
from mathutils import Vector

def build(ctx):
    u=ctx['utils'];p=ctx['params'];z=ctx['deck'];body=ctx['body'];mode=ctx['mode']
    chassis=u.box('chassis_torque_box',(0,0,z-.225),(2.6,1.5,.45),'White','STRUCTURE',body,bevel=.007)
    chassis['engineering_material']='Al7075 faces / Al5056 honeycomb; white thermal finish';chassis['nominal_dimensions_m']=[2.6,1.5,.45]
    # Offset the finish by 1 mm to avoid coplanar faces with the closed torque box.
    u.box('deck_structural_face',(0,0,z-.001),(2.59,1.49,.004),'Al','STRUCTURE',body,bevel=.001)
    skid=u.box('belly_skid',(0,0,z-.446),(2.30,.61,.008),'Al','STRUCTURE',body,bevel=.001)
    for x in (-.85,0,.85):
        u.box('belly_titanium_cleat_'+str(x),(x,0,z-.446),(0.08,.6,.008),'Ti','STRUCTURE',body,bevel=.001)
    for x in (-1.18,1.18):
        for y in (-.63,.63):
            u.box('titanium_hardpoint',(x,y,z-.225),(.18,.12,.41),'Ti','STRUCTURE',body,bevel=.005)
            if mode=='LANDER_STOW':
                u.cyl('launch_lock_pin',(x,y,z-.45),(x,y,z-.39),.026,'Ti','STRUCTURE',body)
    # Honeycomb panels retain exact external envelope; shallow seams reveal service panel edges.
    for s in (-1,1):
        for x in (-.86,-.25,.38,.96):
            u.box('body_panel_seam',(x,s*.7502,z-.26),(.004,.0004,.32),'Dark','STRUCTURE',body,bevel=0)
    u.cyl('differential_transverse_bar',(.2,-.71,z-.012),(.2,.71,z-.012),.024,'Ti','MOBILITY',body)
    u.box('differential_lock_housing',(.2,0,z-.02),(.16,.12,.05),'Dark','MOBILITY',body)
    def beam(n,a,b,parent):
        aa,bb=Vector(a),Vector(b);delta=bb-aa
        ob=u.box(n,(aa+bb)/2,(delta.length,.04,.07),'Al','MOBILITY',parent,bevel=.003)
        ob.rotation_euler[1]=-math.atan2(delta.z,delta.x)
        ob['section_assumption']='70mm vertical x40mm transverse; narrowed inboard gap concept tube'
        return ob
    wheels=[];steers=[];rockers=[];bogies=[]
    wc=p['wheel_r'];rw=wc-p['grouser_h'];w=p['wheel_b']
    for s,side in ((1,'L'),(-1,'R')):
        yp=s*.775
        rock=u.empty('rocker_pivot_'+side,(.2,yp,.70),'MOBILITY');rock['joint_axis']='Y';rockers.append(rock)
        bog=u.empty('bogie_pivot_'+side,(-.65,yp,.64),'MOBILITY',rock);bog['joint_axis']='Y';bogies.append(bog)
        # Two fixed-frame screw/guide assemblies with body carriage moving through .35m stroke.
        guide=u.empty('body_lowering_guide_'+side,(.2,s*.775,.48),'MOBILITY')
        u.cyl('lowering_screw_'+side,(.2,s*.775,.27),(.2,s*.775,.77),.014,'Ti','MOBILITY',guide)
        for xx in (.15,.25):u.cyl('lowering_guide_rail_'+side,(xx,s*.775,.27),(xx,s*.775,.78),.009,'Al','MOBILITY',guide)
        carriage=u.box('body_lowering_carriage_'+side,(.2,s*.775,z-.18),(.16,.04,.09),'Ti','MOBILITY',body)
        carriage['actuator_stroke_m']=.35
        for j in range(11):u.torus('lowering_bellows_'+side,(.2,s*.775,.30+j*.04),.020,.004,'Boot','DUST_MITIGATION',guide)
        u.cyl('rocker_pivot_pin_'+side,(.2,s*.751,.7),(.2,s*.797,.7),.052,'Ti','MOBILITY',rock)
        beam('rocker_forward_link_'+side,(.2,yp,.7),(1.30,yp,.72),rock)
        beam('rocker_aft_link_'+side,(.2,yp,.7),(-.65,yp,.64),rock)
        beam('bogie_mid_link_'+side,(-.65,yp,.64),(0,yp,.72),bog)
        beam('bogie_rear_link_'+side,(-.65,yp,.64),(-1.30,yp,.72),bog)
        u.cyl('bogie_pivot_pin_'+side,(-.65,s*.751,.64),(-.65,s*.797,.64),.045,'Ti','MOBILITY',bog)
        for x,pos in ((1.3,'F'),(0,'M'),(-1.3,'R')):
            stem=u.empty('steering_'+pos+side,(x,s*1.0,.72),'MOBILITY',rock if x>0 else bog);stem['axis']='Z';stem['design_steering_range_deg']=90;stem['verified_static_pose_deg']=0;steers.append(stem)
            u.cyl('steering_motor_'+pos+side,(x,s*.94,.66),(x,s*.94,.80),.07,'Ti','MOBILITY',stem)
            u.cyl('knuckle_crossmember_'+pos+side,(x,yp,.72),(x,s*.94,.72),.032,'Al','MOBILITY',stem)
            u.box('steering_fork_'+pos+side,(x,s*.875,.555),(.055,.045,.22),'Ti','MOBILITY',stem)
            axle=u.empty('wheel_axle_'+pos+side,(x,s*1.0,wc),'MOBILITY',stem);axle['axis']='Y';wheels.append(axle)
            u.cyl('drive_housing_'+pos+side,(x,s*.85,wc),(x,s*1.03,wc),.11,'Ti','MOBILITY',axle)
            for k in range(4):u.torus('drive_labyrinth_'+pos+side,(x,s*(1.055+k*.012),wc),.107,.006,'Boot','DUST_MITIGATION',axle,axis='Y')
            # Open titanium drum: 1.2mm circumferential skin, no pneumatic sidewalls.
            verts=[];faces=[];N=96
            for y in (-w/2,w/2):
                for radius in (rw,rw-.0012):
                    for i in range(N):
                        a=math.tau*i/N;verts.append((x+radius*math.cos(a),s*1+y,wc+radius*math.sin(a)))
            for i in range(N):
                j=(i+1)%N
                faces.extend([(i,j,2*N+j,2*N+i),(N+i,3*N+i,3*N+j,N+j),(i,N+i,N+j,j),(2*N+i,2*N+j,3*N+j,3*N+i)])
            rim=u.mesh('wheel_rim_'+pos+side,verts,faces,'Ti','MOBILITY',axle)
            for poly in rim.data.polygons:poly.use_smooth=True
            for yy in (s*1-w/2+.009,s*1+w/2-.009):
                u.torus('rim_edge_'+pos+side,(x,yy,wc),rw-.005,.005,'Ti','MOBILITY',axle,axis='Y')
                for i in range(10):
                    a=math.tau*i/10;aa=a+.16
                    pts=[(x+.1*math.cos(a),yy,wc+.1*math.sin(a)),(x+.24*math.cos(aa),yy,wc+.24*math.sin(aa)),(x+(rw-.008)*math.cos(a),yy,wc+(rw-.008)*math.sin(a))]
                    u.line('flexure_spoke_'+pos+side,pts,.009,'Ti','MOBILITY',axle)
            for i in range(18):
                a=math.tau*i/18+math.radians(10)
                # 18 straight transverse bars; radius includes the 20mm grouser.
                g=u.box('grouser_'+pos+side+'_'+str(i),(x+(rw+.01)*math.cos(a),s*1,wc+(rw+.01)*math.sin(a)),(.02,w,.012),'Ti','MOBILITY',axle,bevel=.001)
                g.rotation_euler[1]=-a
                g['grouser_height_m']=.02
            # Fenders: upper120° shell radius.52, .45 width inset25mm to respect2.40 envelope.
            yc=s*.975;fr=.52;fv=[];ff=[];Nf=36
            for yy in (yc-.225,yc+.225):
                for j in range(Nf+1):
                    a=math.pi/6+j*(2*math.pi/3)/Nf
                    zf=wc+fr*math.sin(a)
                    # Middle shell inner-edge relief for fixed vertical PV; full width retained at ends.
                    yf=s*.80 if pos=='M' and abs(yy)<.8 and zf>.775 else yy
                    fv.append((x+fr*math.cos(a),yf,zf))
            for j in range(Nf):ff.append((j,j+1,Nf+2+j,Nf+1+j))
            f=u.mesh('fender_'+pos+side,fv,ff,'CFRP','DUST_MITIGATION',stem)
            solid=f.modifiers.new('CFRP shell','SOLIDIFY');solid.thickness=.002;solid.offset=-1
            # Flat end tabs continue the arc tangent clearance and set3.60 longitudinal envelope.
            for d in (-1,1):
                u.box('fender_end_lip_'+pos+side,(x+d*.475,yc,.70),(.05,.45,.012),'CFRP','DUST_MITIGATION',stem,bevel=.002)
            u.box('replaceable_fabric_skirt_'+pos+side,(x-.496,yc,.63),(.007,.445,.14),'White','DUST_MITIGATION',stem,bevel=.002)
            if pos=='M':
                u.line('fender_support_offset_'+pos+side,[(x+.53,s*.775,.735),(x+.53,s*.84,.735),(x+.53,s*.84,.95),(x,yc,.968)],.008,'Al','DUST_MITIGATION',stem)
            else:
                u.cyl('fender_support_inboard_'+pos+side,(x,s*.773,.77),(x,s*.773,.955),.012,'Al','DUST_MITIGATION',stem)
                u.cyl('fender_support_top_'+pos+side,(x,s*.773,.955),(x,yc,.968),.009,'Al','DUST_MITIGATION',stem)
    return {'chassis':chassis,'skid':skid,'wheels':wheels,'steers':steers,'rockers':rockers,'bogies':bogies}
