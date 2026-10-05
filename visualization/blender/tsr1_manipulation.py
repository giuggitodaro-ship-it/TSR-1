"""Source-traced TSR-1 manipulation and mast geometry; metres, +X forward.
See BLENDER_MODEL_REQUIREMENTS and CONFLICT_LOG for pose/packaging assumptions.
"""
import math
from mathutils import Vector


def build(ctx):
    u, deck, body, mode, layout = (ctx[k] for k in ('utils','deck','body','mode','layout'))
    P = mode + '_'
    def E(n,p,c,parent): return u.empty(P+n,p,c,parent=parent)
    def C(n,a,b,r,m,c,parent): return u.cyl(P+n,a,b,r,m,c,parent=parent)
    def B(n,p,d,m,c,parent): return u.box(P+n,p,d,m,c,parent=parent)
    def T(n,p,r,t,m,c,parent,axis='Z'): return u.torus(P+n,p,r,t,m,c,parent=parent,axis=axis)
    def V(p): return Vector(p)
    arms = {}
    working = mode == 'SERVICING'
    for side, sign in [('L',1),('R',-1)]:
        col = 'DEX_ARM_'+side
        x,y = layout['dex_arm_'+side+'_base'].centre
        shoulder = V((x,y,deck+.04))
        if working:
            upper_dir = V((math.cos(math.radians(48)),0,math.sin(math.radians(48))))
            fore_dir = V((math.cos(math.radians(10)),-sign*.10,math.sin(math.radians(10)))).normalized()
            wrist_dir = V((1,0,0))
        else:
            upper_dir = V((0,0,1))
            fore_dir = V((.13,0,-math.sqrt(.70**2-.13**2)))/.70
            wrist_dir = V((1,0,0))
        elbow = shoulder + .75*upper_dir
        wrist = elbow + .70*fore_dir
        tip = wrist + .15*wrist_dir
        origins = [shoulder,shoulder,shoulder,elbow,elbow,wrist,wrist]
        labels = ['shoulder_yaw','shoulder_pitch','upper_roll','elbow_pitch','forearm_roll','wrist_pitch','wrist_roll']
        joints=[]
        par=body
        for i,(pos,lbl) in enumerate(zip(origins,labels),1):
            joint=E('arm_'+side+'_J'+str(i)+'_'+lbl,pos,col,par)
            joint['joint_index']=i
            joint['logical_axis']='Y' if i in (2,4,6) else ('Z' if i==1 else 'LINK')
            joint['source']='DESIGN_FREEZE_V1 §5; run_config dex_links'
            joints.append(joint); par=joint
        B('arm_'+side+'_base_flange',(x,y,deck+.012),(.19,.19,.024),'Ti',col,body)
        for dx in [-.07,.07]:
            for dy in [-.07,.07]:
                C('arm_'+side+'_captive_base_fastener',(x+dx,y+dy,deck+.018),(x+dx,y+dy,deck+.034),.008,'Dark',col,body)
        for i,pos in [(0,shoulder),(3,elbow),(5,wrist)]:
            r=.060 if i<5 else .046
            C('arm_'+side+'_joint_housing_'+str(i),pos+V((0,-.057,0)),pos+V((0,.057,0)),r,'Ti',col,joints[i])
            for offset in [-.059,-.046,.046,.059]:
                T('arm_'+side+'_joint_bellows_'+str(i),pos+V((0,offset,0)),r*.86,.007,'Boot',col,joints[i],axis='Y')
        # Distinct roll/yaw actuator shells complete the seven-joint visual chain.
        C('arm_'+side+'_J1_yaw_shell',shoulder+V((0,0,-.025)),shoulder+V((0,0,.025)),.056,'Ti',col,joints[0])
        for j,origin,axis,radius in [(2,shoulder,upper_dir,.043),(4,elbow,fore_dir,.039)]:
            C('arm_'+side+'_J'+str(j+1)+'_roll_shell',origin+.10*axis,origin+.18*axis,radius,'Ti',col,joints[j])
            for dist in [.11,.135,.16]:
                C('arm_'+side+'_roll_labyrinth',origin+dist*axis,origin+(dist+.009)*axis,radius+.003,'Boot',col,joints[j])
        upper=C('arm_'+side+'_upper_Ti_075',shoulder,elbow,.035,'Ti',col,joints[2])
        fore=C('arm_'+side+'_forearm_Ti_070',elbow,wrist,.030,'Ti',col,joints[4])
        C('arm_'+side+'_wrist_015',wrist,tip,.025,'Ti',col,joints[6])
        upper['nominal_length_m']=.75; fore['nominal_length_m']=.70
        # F/T and changer fit inside the final 0.15 m wrist section.
        C('arm_'+side+'_FT_sensor',wrist+.02*wrist_dir,wrist+.075*wrist_dir,.048,'Dark',col,joints[6])
        C('arm_'+side+'_tool_changer',wrist+.075*wrist_dir,wrist+.14*wrist_dir,.050,'Ti',col,joints[6])
        cam=wrist+.075*wrist_dir+V((0,sign*.067,0))
        B('arm_'+side+'_macro_camera',cam,(.07,.045,.045),'Dark',col,joints[6])
        C('arm_'+side+'_macro_lens',cam+V((.03,0,0)),cam+V((.041,0,0)),.014,'Glass',col,joints[6])
        # Flexible harness follows link chain and retains independent parents.
        for idx,(a,b,par) in enumerate([(shoulder,elbow,joints[2]),(elbow,wrist,joints[4])]):
            off=V((0,sign*.045,0))
            u.line(P+'arm_'+side+'_protected_harness_'+str(idx),[a+off,(a+b)/2+off,b+off],.006,'Boot',col,parent=par)
        tipmarker=E('arm_'+side+'_tool_datum',tip,col,joints[6])
        if working:
            if side=='L':
                B('arm_L_parallel_gripper_body',tip+V((.035,0,0)),(.07,.085,.06),'Ti',col,tipmarker)
                for s in [-1,1]:
                    B('arm_L_gripper_finger',tip+V((.10,s*.04,0)),(.11,.015,.045),'Ti',col,tipmarker)
            else:
                C('arm_R_socket_driver',tip,tip+V((.13,0,0)),.028,'Ti',col,tipmarker)
                C('arm_R_socket_bit',tip+V((.13,0,0)),tip+V((.19,0,0)),.015,'Dark',col,tipmarker)
        if mode=='LANDER_STOW':
            B('arm_'+side+'_elbow_launch_lock',elbow+V((-.065,0,-.04)),(.04,.14,.10),'Orange',col,body)
        arms[side]={'shoulder':joints[0],'elbow':joints[3],'wrist':joints[5],'tip':tipmarker,'joints':joints}

    col='CRANE'
    cx,cy=layout['crane_turntable'].centre
    pivot=V((cx,cy,deck+.15))
    slew=E('crane_slew_axis',(cx,cy,deck+.035),col,body)
    C('crane_turntable_lower',(cx,cy,deck+.01),(cx,cy,deck+.065),.18,'Ti',col,body)
    C('crane_turntable_upper',(cx,cy,deck+.065),(cx,cy,deck+.09),.155,'Dark',col,slew)
    C('crane_slew_pedestal',(cx,cy,deck+.09),pivot,.055,'Ti',col,slew)
    for sy in [-1,1]:
        B('crane_boom_pivot_cheek',(cx,sy*.06,deck+.125),(.12,.025,.10),'Ti',col,slew)
    luff=E('crane_luff_axis',pivot,col,slew)
    deployed=mode=='SERVICING'
    direction=V((math.cos(math.radians(55)),0,math.sin(math.radians(55)))) if deployed else V((-1,0,0))
    tip=pivot+2.60*direction
    boom=C('crane_CFRP_boom_2600',pivot,tip,.025,'CFRP',col,luff)
    boom['length_m']=2.6; boom['diameter_m']=.05
    C('crane_boom_root_fitting',pivot,pivot+.11*direction,.032,'Ti',col,luff)
    C('crane_boom_tip_fitting',tip-.075*direction,tip,.031,'Ti',col,luff)
    tipmark=E('crane_tip_datum',tip,col,luff)
    framehinge=E('crane_Aframe_fold_hinge',pivot,col,slew)
    framehinge['assumption']='Inferred folding A-frame required by frozen stowed height; operational top follows CraneSpec.'
    # Same rigid A-frame geometry, rotated about transverse hinge in stow.
    frame_top=pivot+V((-.30,0,.90)) if deployed else pivot+V((-math.sqrt(.3**2+.9**2-.10**2),0,.10))
    for sy in [-1,1]:
        C('crane_Aframe_leg',pivot+V((0,sy*.14,0)),frame_top,.020,'CFRP',col,framehinge)
        C('crane_Aframe_hinge',pivot+V((0,sy*.14-.025,0)),pivot+V((0,sy*.14+.025,0)),.032,'Ti',col,slew)
    atop=E('crane_Aframe_top',frame_top,col,framehinge)
    u.line(P+'crane_luff_Vectran_stay',[frame_top,tip],.004,'Vectran',col,parent=framehinge)
    for iy in [-.095,.095]:
        C('crane_luff_hoist_winch_drum',(cx-.08,iy-.035,deck+.08),(cx-.08,iy+.035,deck+.08),.045,'Dark',col,slew)
    C('crane_tip_sheave',tip+V((0,-.032,0)),tip+V((0,.032,0)),.038,'Ti',col,luff)
    if deployed:
        hookpos=V((tip.x,tip.y,deck+.94))
        u.line(P+'crane_hoist_Vectran',[pivot+V((0,.075,0)),tip+V((0,.025,0)),hookpos],.004,'Vectran',col,parent=luff)
    else:
        hookpos=tip+V((.085,0,-.055))
        u.line(P+'crane_hoist_stowed',[pivot+V((0,.045,0)),tip+V((0,.025,0)),hookpos],.004,'Vectran',col,parent=luff)
    hook=E('crane_hook_datum',hookpos,col,luff)
    B('crane_hook_block',hookpos,(.06,.038,.065),'Ti',col,hook)
    u.line(P+'crane_hook',[hookpos+V((0,0,-.03)),hookpos+V((0,0,-.08)),hookpos+V((.03,0,-.095)),hookpos+V((.05,0,-.065))],.008,'Ti',col,parent=hook)
    if not deployed:
        # Rear lock extends from rear chassis edge to the overhanging boom tip.
        u.line(P+'crane_tip_stow_support',[(-1.32,0,deck-.06),(-1.32,0,deck+.11),(tip.x+.08,0,deck+.11)],.012,'Ti',col,parent=body)
        B('crane_tip_launch_latch',(tip.x+.08,0,deck+.135),(.06,.10,.025),'Orange',col,body)

    col='SENSOR_MAST'
    mx,my=layout['sensor_mast_base'].centre
    mb=V((mx,my,deck+.05))
    mhinge=E('mast_fold_hinge',mb,col,body)
    B('mast_base_foot',(mx,my,deck+.015),(.15,.16,.03),'Ti',col,body)
    C('mast_hinge_pin',(mx,my-.07,deck+.05),(mx,my+.07,deck+.05),.03,'Ti',col,body)
    md=V((-math.cos(math.radians(37)),0,math.sin(math.radians(37)))) if mode=='LANDER_STOW' else V((0,0,1))
    mt=mb+1.2*md
    tube=C('mast_CFRP_tube_1200',mb,mt,.03,'CFRP',col,mhinge)
    tube['length_m']=1.2; tube['diameter_m']=.06
    mpan=E('mast_pan_axis',mt,col,mhinge)
    mtilt=E('mast_head_tilt_axis',mt,col,mpan)
    C('mast_pan_tilt_housing',mt+V((0,-.05,-.035)),mt+V((0,.05,-.035)),.04,'Ti',col,mtilt)
    B('mast_sensor_head',mt,(.10,.34,.10),'White',col,mtilt)
    stereo={}
    for side,sy in [('L',1),('R',-1)]:
        cp=mt+V((.064,sy*.125,0))
        C('NavCam_'+side+'_barrel',cp+V((-.02,0,0)),cp,.025,'Dark',col,mtilt)
        C('NavCam_'+side+'_optical_window',cp,cp+V((.004,0,0)),.021,'Glass',col,mtilt)
        stereo[side]=E('NavCam_'+side+'_optical_center',cp,col,mtilt)
        lp=mt+V((.057,sy*.073,-.027))
        C('mast_LED_'+side,lp,lp+V((.008,0,0)),.015,'LED',col,mtilt)
    C('mast_thermal_IR_lens',mt+V((.05,0,.012)),mt+V((.065,0,.012)),.015,'Glass',col,mtilt)
    B('mast_relay_flat_antenna',mt+V((-.08,0,0)),(.018,.16,.075),'White',col,mtilt)
    C('mast_relay_antenna_gimbal',mt+V((-.04,0,0)),mt+V((-.08,0,0)),.016,'Ti',col,mtilt)
    masttop=E('mast_head_top_datum',mt+V((0,0,.05)),col,mtilt)
    if mode=='LANDER_STOW':
        B('mast_fold_launch_latch',mt+V((0,0,-.065)),(.12,.10,.035),'Orange',col,body)
    return {'arms':arms,'crane':{'pivot':luff,'tip':tipmark,'boom':boom,'aframe_top':atop,'hook':hook},'mast':{'base':mhinge,'tip':mpan,'head_top':masttop,'tube':tube,'stereo_L':stereo['L'],'stereo_R':stereo['R']}}
