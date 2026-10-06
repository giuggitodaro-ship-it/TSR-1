"""Repository-derived deck, recovery, power and sensor equipment.
Unspecified housings/tool shapes are visual approximations, not manufacturing CAD.
Frozen dimensions and inferred packaging choices documented in BLENDER_* files.
"""
import math

def build(ctx):
    u=ctx['utils']; d=ctx['deck']; mode=ctx['mode']; body=ctx['body']; layout=ctx['layout']
    meta={}
    def box(n,p,s,m,c,parent=body,bevel=.004): return u.box(n,p,s,m,c,parent=parent,bevel=bevel)
    def cyl(n,a,b,r,m,c,parent=body,vertices=32): return u.cyl(n,a,b,r,m,c,parent=parent,vertices=vertices)
    def line(n,p,r,m,c,parent=body): return u.line(n,p,r,m,c,parent=parent)
    def tor(n,p,r,t,m,c,parent=body,axis='Z'): return u.torus(n,p,r,t,m,c,parent=parent,axis=axis)
    def label(n,txt,p,size,m,c,rotation=(0,0,0)): return u.label(n,txt,p,size,m,c,parent=body,rotation=rotation)
    # Exact layout radiator: heat-pipe substrate, thin OSR tiles and sparse EDS traces.
    rad=layout['radiator']; rx,ry=rad.centre; lx=rad.x1-rad.x0; ly=rad.y1-rad.y0
    meta['radiator']=box('radiator_1p643m2_heatpipe_substrate',(rx,ry,d+.008),(lx,ly,.016),'Al','THERMAL',bevel=.001)
    for i in range(6):
        for j in range(8):
            box('OSR_tile_%02d_%02d'%(i,j),(rad.x0+(i+.5)*lx/6,rad.y0+(j+.5)*ly/8,d+.018),(lx/6-.004,ly/8-.004,.004),'OSR','THERMAL',bevel=.0005)
    for j in range(15):
        y=rad.y0+.04+j*(ly-.08)/14
        line('EDS_transparent_electrode_%02d'%j,[(rad.x0+.015,y,d+.0202),(rad.x1-.015,y,d+.0202)],.0003,'Glass','THERMAL')
    # Six exact pitch interfaces. Rails fit inside footprint; no occupied module over radiator.
    sp=layout['service_spine']; sx,sy=sp.centre
    for y in (sp.y0+.012,sp.y1-.012):
        box('spine_long_rail',(sx,y,d+.016),(.90,.024,.032),'Al','SERVICE_SPINE')
    for x in (sp.x0+.012,sp.x0+.45,sp.x1-.012):
        box('spine_cross_rail',(x,0,d+.016),(.024,1.35,.032),'Al','SERVICE_SPINE')
    slots=[]
    for i in range(2):
        for j in range(3):
            x=sp.x0+.225+.45*i; y=sp.y0+.225+.45*j; slots.append((x,y))
            latch=box('slot_%s%s_thermal_interface'%(i,j),(x,y,d+.019),(.19,.19,.018),'Al','SERVICE_SPINE')
            latch['interface']='120 VDC / 1 kW / Ethernet; 40 kg max single slot'
            for a,b in ((-.085,-.085),(-.085,.085),(.085,-.085),(.085,.085)):
                box('slot_%s%s_Ti_latch'%(i,j),(x+a,y+b,d+.034),(.038,.026,.024),'Ti','SERVICE_SPINE')
            box('slot_%s%s_power_data_cover'%(i,j),(x,y+.115,d+.035),(.11,.035,.016),'Dark','SERVICE_SPINE')
    # Double-slot MOD-KA on right; envelope includes folded PV pack and lift ring.
    ka=box('MOD_KA_stowed_envelope',(sx,-.45,d+.20),(.90,.45,.34),'Gold','SERVICE_SPINE',bevel=.009)
    ka['engineering_envelope_m']=[.90,.45,.45]; ka['source']='service_spine.md KA-C double-slot module'
    for z in (d+.035,d+.435):
        for dy in (-.218,.218):box('MOD_KA_frame',(sx,-.45+dy,z),(.90,.014,.02),'Al','SERVICE_SPINE')
        for dx in (-.443,.443):box('MOD_KA_frame',(sx+dx,-.45,z),(.014,.422,.02),'Al','SERVICE_SPINE')
    for i in range(12):
        leaf=box('MOD_KA_folded_PV_leaf_%d'%i,(sx,-.45,d+.374+i*.005),(.625,.40,.004),'PV','SERVICE_SPINE',bevel=.0005)
        leaf['folding_assumption']='12 tile leaves, 6 per 1.5m2 face; detailed folding mechanism unresolved'
        leaf['cell_surface_area_m2']=.25
    tor('MOD_KA_lift_eye',(sx,-.45,d+.43),.015,.004,'Ti','SERVICE_SPINE',axis='X')
    for x in (sp.x0+.06,sp.x1-.06):
        box('MOD_KA_fiducial_base',(x,-.679,d+.26),(.06,.004,.06),'White','SERVICE_SPINE',bevel=0)
        box('MOD_KA_fiducial_mark',(x,-.682,d+.26),(.034,.003,.034),'Dark','SERVICE_SPINE',bevel=0)
    # Two genuinely empty ORU cradles; low rails preserve boom/mast sweep corridors.
    for j in (1,2):
        x=sp.x0+.225; y=sp.y0+.225+.45*j
        for dy in (-.17,.17): box('empty_ORU_cradle_%d_rail'%j,(x,y+dy,d+.056),(.38,.025,.055),'Al','SERVICE_SPINE')
        for dx in (-.17,.17): box('empty_ORU_cradle_%d_end'%j,(x+dx,y,d+.056),(.025,.32,.055),'Al','SERVICE_SPINE')
    x=sp.x0+.675; y=.45
    box('MOD_REC_open_tray_floor',(x,y,d+.038),(.40,.40,.014),'White','SERVICE_SPINE')
    for dy in (-.19,.19): box('MOD_REC_open_tray_rail',(x,y+dy,d+.058),(.40,.014,.04),'Al','SERVICE_SPINE')
    for dx in (-.19,.19): box('MOD_REC_open_tray_end',(x+dx,y,d+.058),(.014,.38,.04),'Al','SERVICE_SPINE')
    tor('lifting_fixture_slings_in_MOD_REC',(x,y-.06,d+.054),.077,.004,'Vectran','TOOL_RACK')
    tor('recovery_shackle_in_MOD_REC',(x+.08,y+.08,d+.052),.026,.006,'Ti','TOOL_RACK')
    # Side arrays mounted above travel rocker pivot; fixed to body, vertical +/-Y.
    for side in (-1,1):
        n='R' if side<0 else 'L'; y=side*.775; z=d+.50
        pan=box('solar_array_'+n,(0,y,z),(1.50,.018,.50),'CFRP','POWER',bevel=.002)
        pan['active_nominal_area_m2']=.75; meta['solar_'+n]=pan
        for i in range(15):
            for j in range(5):
                box('PV_%s_%02d_%02d'%(n,i,j),(-.70+i*.10,y+side*.010,z-.20+j*.10),(.094,.003,.094),'PV','POWER',bevel=.0005)
        for x in (-.69,.69):
            box('PV_body_bracket_'+n,(x,side*.726,d+.125),(.035,.022,.25),'Ti','POWER')
            cyl('PV_upper_bracket_'+n,(x,side*.726,d+.255),(x,side*.775,d+.255),.008,'Ti','POWER')
        label('branding_'+n,'TODARO CORP.  |  TSR-1',(0,side*.756,d-.065),.061,'Dark','BRANDING',rotation=(math.pi/2,0,math.pi if side>0 else 0))
    # Winch package hidden within rear chassis, complete drum and levelwind.
    winch=box('winch_internal_envelope',(-1.04,0,d-.23),(.45,.30,.30),'Al','INTERNAL_VOLUMES')
    winch.display_type='WIRE'; winch.hide_render=True
    drum=cyl('winch_Ti_drum_120mm',(-1.06,-.11,d-.27),(-1.06,.11,d-.27),.06,'Ti','RECOVERY')
    for y in (-.115,.115): cyl('winch_drum_flange',(-1.06,y-.008,d-.27),(-1.06,y+.008,d-.27),.078,'Ti','RECOVERY')
    for i in range(17): tor('winch_wound_Vectran_%d'%i,(-1.06,-.10+i*.0125,d-.27),.064,.003,'Vectran','RECOVERY',axis='Y')
    cyl('winch_levelwind_guide',(-1.20,-.13,d-.24),(-1.20,.13,d-.24),.009,'Ti','RECOVERY')
    box('winch_levelwind_traveller',(-1.20,0,d-.24),(.04,.038,.045),'Al','RECOVERY')
    fz=d-.30
    for z in (fz-.046,fz+.046): cyl('low_fairlead_horizontal',(-1.343,-.10,z),(-1.343,.10,z),.015,'Ti','RECOVERY')
    for y in (-.103,.103): cyl('low_fairlead_vertical',(-1.343,y,fz-.045),(-1.343,y,fz+.045),.015,'Ti','RECOVERY')
    fair=u.empty('fairlead_centre',(-1.343,0,fz),'RECOVERY',parent=body); fair['working_height_m']=.25; meta['fairlead']=fair
    # Hinges remain meaningful, geometry created in world then parented by utility.
    for side in (-1,1):
        y=side*.40; hinge=u.empty('spade_hinge_'+str(side),(-1.33,y,d-.30),'RECOVERY',parent=body)
        cyl('spade_hinge_pin',(-1.34,y-.285,d-.30),(-1.34,y+.285,d-.30),.018,'Ti','RECOVERY',parent=hinge)
        platez=-.15 if mode=='RECOVERY' else d-.15
        platex=-1.52 if mode=='RECOVERY' else -1.36
        plate=box('spade_plate_'+str(side),(platex,y,platez),(.006,.60,.30),'Ti','RECOVERY',parent=hinge,bevel=.001)
        for yy in (y-.20,y+.20):
            box('spade_stiffener',(platex-.012,yy,platez),(.018,.018,.27),'Ti','RECOVERY',parent=hinge)
            if mode=='RECOVERY': cyl('spade_deploy_link',(-1.34,yy,d-.30),(platex,yy,.0),.018,'Ti','RECOVERY',parent=hinge)
        hinge['pose_note']='Deployed insertion link geometry inferred; motion interpolation not certified'
        hinge['joint']='rear spade deployment about Y'; hinge['plate_dimensions_m']=[.60,.30,.006]
    # Tow lugs and anchor stow or install positions. Open single-turn Ti helix plate.
    def helix_plate(n,origin,axis):
        verts=[];faces=[]
        for k in range(65):
            t=k*2*math.pi/64
            for r in (.014,.075):
                a,b,c=.075*t/(2*math.pi),r*math.cos(t),r*math.sin(t)
                off=(a,b,c) if axis=='X' else (b,c,a)
                verts.append(tuple(origin[i]+off[i] for i in range(3)))
        for k in range(64):faces.append((2*k,2*k+1,2*k+3,2*k+2))
        ob=u.mesh(n,verts,faces,'Ti','RECOVERY',parent=body)
        so=ob.modifiers.new('Titanium helical plate 4mm','SOLIDIFY');so.thickness=.004
        return ob
    for side in (-1,1):
        tor('front_anchor_tow_eye_'+str(side),(1.33,side*.43,d-.30),.033,.011,'Ti','RECOVERY',axis='Y')
        if mode=='RECOVERY':
            ax,ay,az=1.94,side*.70,-.60
            cyl('installed_anchor_shaft_'+str(side),(ax,ay,az),(ax,ay,az+.70),.0125,'Ti','RECOVERY')
            pts=[(ax+.069*math.cos(t),ay+.069*math.sin(t),az+.05+.075*t/(2*math.pi)) for t in [k*2*math.pi/64 for k in range(65)]]
            helix_plate('installed_anchor_helix_'+str(side),(ax,ay,az+.05),'Z')
            tor('anchor_eye_'+str(side),(ax,ay,.11),.025,.007,'Ti','RECOVERY',axis='Y')
            line('front_hold_down_strap_'+str(side),[(1.33,side*.43,d-.30),(ax,ay,.11)],.012,'Vectran','RECOVERY')
        else:
            y=-.885; z=d+.46+(side+1)*.08
            cyl('carried_anchor_shaft_'+str(side),(-.35,y,z),(.35,y,z),.0125,'Ti','RECOVERY')
            pts=[(-.30+.075*t/(2*math.pi),y+.069*math.cos(t),z+.069*math.sin(t)) for t in [k*2*math.pi/64 for k in range(65)]]
            helix_plate('carried_anchor_helix_'+str(side),(-.30,y,z),'X')
            for x in (-.16,.26):
                tor('anchor_stow_clip',(x,y,z),.018,.005,'Boot','RECOVERY',axis='X')
                line('anchor_clip_side_stand',( (x,-.73,d+.17),(x,-.73,d+.79),(x,y,d+.79),(x,y,z) ),.007,'Ti','RECOVERY')
    if mode=='RECOVERY':
        cable=line('deployed_50m_capacity_Vectran_line',[(-1.35,0,.25),(-3,0,.11),(-5.5,0,.08)],.006,'Vectran','RECOVERY')
        cable['depiction']='Illustrative deployed segment, full reel capacity 50 m'; cable['exclude_from_vehicle_envelope']=True
    # Tether reel, front guide and pose-dependent orange emergency line.
    cyl('power_tether_reel_350mm',(.91,.22,d-.245),(.91,.44,d-.245),.175,'Orange','INTERNAL_VOLUMES')
    tor('power_tether_exit_guide',(1.335,.55,d-.12),.027,.009,'Ti','POWER',axis='X')
    if mode=='EMERGENCY_POWER':
        pts=[(1.34,.55,d-.12),(1.65,.52,.10),(2.2,.32,.03),(3.3,.28,.025),(5,.10,.025),(7.5,.05,.025),(10.8,.0,.025),(11,0,.18)]
        cable=line('emergency_power_tether_25m_capacity',pts,.007,'Orange','POWER'); cable['exclude_from_vehicle_envelope']=True
        connector=cyl('DTC_remote_connector',(11,0,.18),(11.11,0,.18),.035,'Ti','POWER'); connector['exclude_from_vehicle_envelope']=True
    else:
        line('power_tether_parked_loop',[(1.34,.55,d-.12),(1.39,.55,d-.17),(1.39,.49,d-.20),(1.35,.46,d-.14)],.006,'Orange','POWER')
        cyl('DTC_parked_connector',(1.36,.46,d-.14),(1.36,.46,d-.07),.024,'Ti','POWER')
    # Internal volumes are inspectable but hidden in exterior renders.
    for n,p,s in [('WEB',(-.50,0,d-.225),(1,.8,.35)),('battery',(-.53,0,d-.31),(.8,.5,.18)),('PCDU',(-.71,-.20,d-.15),(.35,.25,.12)),('PTM',(-.25,.20,d-.15),(.30,.25,.12))]:
        ob=box('internal_'+n,p,s,'Al','INTERNAL_VOLUMES'); ob.display_type='WIRE'; ob.hide_render=True
    # Ten rack tools plus MOD-REC slings/shackle above; all twelve engineering identities.
    box('front_face_open_holster_backplate',(1.308,0,d-.225),(.016,1.10,.40),'Al','TOOL_RACK')
    names=['parallel_gripper','socket_driver','electrical_probe','connector_mate','dust_brush','eds_wand','anchor_driver','oru_adapter_otcm','oru_adapter_androgynous','regolith_scoop']
    for i,n in enumerate(names):
        y=-.44+(i%5)*.22; z=d-.13-(i//5)*.19; x=1.346
        box(n+'_holster',(1.323,y,z),(.024,.14,.125),'Dark','TOOL_RACK')
        if mode=='SERVICING' and n in ('parallel_gripper','socket_driver'):
            label(n+'_deployed_id','DEPLOYED',(1.349,y,z),.018,'White','TOOL_RACK',rotation=(math.pi/2,0,math.pi/2))
            continue
        cyl(n+'_toolchanger',(1.326,y,z),(1.350,y,z),.029,'Ti','TOOL_RACK')
        if n=='parallel_gripper':
            box(n+'_body',(x,y,z),(.035,.065,.04),'Ti','TOOL_RACK')
            for s in (-1,1): box(n+'_jaw',(x+.012,y+s*.045,z+.022),(.020,.015,.075),'Dark','TOOL_RACK')
        elif n in ('socket_driver','anchor_driver','electrical_probe'):
            cyl(n+'_handle',(x,y,z-.04),(x,y,z+.025),.022,'Ti','TOOL_RACK')
            cyl(n+'_bit',(x,y,z+.025),(x,y,z+.069),.007 if n=='electrical_probe' else .012,'Gold' if n=='electrical_probe' else 'Dark','TOOL_RACK',vertices=6)
        elif n=='dust_brush':
            box(n+'_head',(x,y,z+.03),(.025,.11,.025),'Ti','TOOL_RACK')
            for j in range(10): cyl(n+'_bristle',(x,y-.05+j*.011,z+.035),(x,y-.05+j*.011,z+.067),.003,'White','TOOL_RACK',vertices=8)
        elif n=='eds_wand':
            box(n+'_electrode_head',(x,y,z+.025),(.016,.10,.065),'CFRP','TOOL_RACK')
            for j in range(4): box(n+'_electrode',(x+.009,y-.035+j*.023,z+.025),(.002,.004,.055),'Al','TOOL_RACK')
        elif n=='regolith_scoop':
            box(n+'_blade',(x,y,z+.025),(.012,.10,.055),'Ti','TOOL_RACK')
            for s in (-1,1): box(n+'_cheek',(x+.013,y+s*.046,z+.025),(.025,.008,.055),'Ti','TOOL_RACK')
        else:
            tor(n+'_coupling',(x+.014,y,z+.018),.037,.009,'Ti','TOOL_RACK',axis='X')
            if n=='oru_adapter_otcm': box(n+'_crossbar',(x+.017,y,z+.018),(.014,.08,.018),'Ti','TOOL_RACK')
        label(n+'_id',n.replace('oru_adapter_','').replace('_',' ').upper(),(1.379,y-.075,z-.074),.012,'White','TOOL_RACK',rotation=(math.pi/2,0,math.pi/2))
    # Six HazCams: two forward, two rear, one on each outer side with clear apertures.
    for tag,p,axis in [('FL',(1.34,.64,d-.04),(1,0,0)),('FR',(1.34,-.64,d-.04),(1,0,0)),('RL',(-1.34,.63,d-.04),(-1,0,0)),('RR',(-1.34,-.63,d-.04),(-1,0,0)),('L',(.66,.765,d-.04),(0,1,0)),('R',(.66,-.765,d-.04),(0,-1,0))]:
        box('HazCam_'+tag+'_housing',p,(.055,.055,.055),'Ti','SENSORS')
        a=tuple(p[k]+axis[k]*.025 for k in range(3)); b=tuple(p[k]+axis[k]*.04 for k in range(3))
        cyl('HazCam_'+tag+'_sapphire_EDS_window',a,b,.017,'Glass','SENSORS')
    for sign in (-1,1):
        x=sign*1.39; z=d-.005
        box(('front' if sign>0 else 'rear')+'_LiDAR',(x,0,z),(.15,.15,.15),'Dark','SENSORS')
        box('LiDAR_EDS_window',(x+sign*.077,0,z),(.003,.105,.085),'Glass','SENSORS')
    cyl('star_tracker_baffle',(.79,-.30,d+.02),(.79,-.30,d+.16),.032,'Dark','SENSORS')
    cyl('star_tracker_optic',(.79,-.30,d+.157),(.79,-.30,d+.160),.022,'Glass','SENSORS')
    box('sun_sensor',(.83,-.39,d+.025),(.055,.055,.025),'Ti','SENSORS')
    return meta
