package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.monstrosity.*;
import java.util.*;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

/** Native articulated creature sculpture, with independent UV islands for every sculpted surface. */
public final class MonstrosityModel extends HierarchicalModel<MonstrosityEntity> {
    public static final int ATLAS_SIZE=512;
    public record Surface(int u,int v,int width,int height,String material,String name){}
    private static final class Atlas {
        int x=2,y=2,row;final List<Surface> surfaces=new ArrayList<>();
        Surface allocate(String name,String material,float w,float h,float d){
            int width=(int)Math.ceil(2*(w+d))+2,height=(int)Math.ceil(h+d)+2;
            if(x+width>=ATLAS_SIZE){x=2;y+=row+2;row=0;}
            if(y+height>=ATLAS_SIZE)throw new IllegalStateException("Creature atlas overflow");
            var s=new Surface(x,y,width,height,material,name);surfaces.add(s);x+=width+2;row=Math.max(row,height);return s;
        }
    }
    private static final ThreadLocal<Atlas> ATLAS=ThreadLocal.withInitial(Atlas::new);
    public static List<Surface> surfaces(){return List.copyOf(ATLAS.get().surfaces);}
    private final ModelPart root;private final MonstrosityKind kind;
    public MonstrosityModel(ModelPart root,MonstrosityKind kind){this.root=root;this.kind=kind;}
    public static ModelLayerLocation location(MonstrosityKind kind){return new ModelLayerLocation(new ResourceLocation("alfheim_companion","monstrosity/"+kind.id),"main");}
    @Override public ModelPart root(){return root;}
    private static PartDefinition box(PartDefinition p,String name,String material,float x,float y,float z,float w,float h,float d,PartPose pose){
        var uv=ATLAS.get().allocate(name,material,w,h,d);
        return p.addOrReplaceChild(name,CubeListBuilder.create().texOffs(uv.u,uv.v).addBox(x,y,z,w,h,d),pose);
    }
    private static PartDefinition b(PartDefinition p,String n,String m,float x,float y,float z,float w,float h,float d){return box(p,n,m,x,y,z,w,h,d,PartPose.ZERO);}
    private static PartDefinition pivot(PartDefinition p,String n,float x,float y,float z,float rx,float ry,float rz){return p.addOrReplaceChild(n,CubeListBuilder.create(),PartPose.offsetAndRotation(x,y,z,rx,ry,rz));}
    private static void rod(PartDefinition p,String n,String m,float x,float y,float z,float dx,float dy,float dz,float width){
        float len=Mth.sqrt(dx*dx+dy*dy+dz*dz),rx=(float)Math.atan2(dz,Math.sqrt(dx*dx+dy*dy)),rz=-(float)Math.atan2(dx,dy);
        box(p,n,m,-width/2,0,-width/2,width,len,width,PartPose.offsetAndRotation(x,y,z,rx,0,rz));
    }
    private static void horn(PartDefinition p,String n,String m,float x,float y,float z,float side,float length){
        var a=box(p,n,m,-1.3F,-length*.45F,-1.2F,2.6F,length*.5F,2.4F,PartPose.offsetAndRotation(x,y,z,.22F,0,side*.35F));
        var c=box(a,n+"_curve",m,-.85F,-length*.4F,-.7F,1.7F,length*.45F,1.5F,PartPose.offsetAndRotation(0,-length*.42F,0,.35F,0,side*.4F));
        box(c,n+"_point",m,-.35F,-length*.35F,-.35F,.7F,length*.4F,.7F,PartPose.offsetAndRotation(0,-length*.32F,0,.35F,0,side*.25F));
    }
    private static void tooth(PartDefinition p,String n,float x,float y,float z,float length,boolean down){
        box(p,n,"bone",-.45F,down?0:-length,-.6F,.9F,length,1.2F,PartPose.offsetAndRotation(x,y,z,down?-.1F:.15F,0,0));
    }
    public static LayerDefinition layer(MonstrosityKind kind){
        ATLAS.set(new Atlas());var mesh=new MeshDefinition();var root=mesh.getRoot();
        for(String name:new String[]{"head","body","right_arm","left_arm","right_leg","left_leg","rear_right_leg","rear_left_leg","tail","wing_left","wing_right"})pivot(root,name,0,0,0,0,0,0);
        switch(kind){case TROLL->troll(root);case CYCLOPS->cyclops(root);case BRIAR->briar(root);case INFESTOR->infestor(root);case GARGOYLE->gargoyle(root);case HAG->hag(root);}
        return LayerDefinition.create(mesh,ATLAS_SIZE,ATLAS_SIZE);
    }
    private static void troll(PartDefinition r){
        var body=pivot(r,"body",0,-4,1,.13F,0,0);
        box(body,"hunched_trapezius","skin",-8,-24,1,16,14,11,PartPose.rotation(.18F,0,0));
        box(body,"sloping_upper_back","skin",-7,-28,3,14,10,8,PartPose.rotation(.28F,0,0));
        box(body,"raised_spinal_knots","skin",-4,-30,5,8,9,6,PartPose.rotation(.34F,0,0));
        for(int s:new int[]{-1,1})box(body,"sloped_scapula"+s,"skin",s<0?-10:5,-21,2,5,12,9,PartPose.rotation(.15F,0,-s*.26F));
        b(body,"ribcage","skin",-9,-14,-7,18,19,13);b(body,"sagging_belly","skin",-7,-1,-8,14,12,12);
        for(int s:new int[]{-1,1}){
            box(body,"pectoral"+s,"skin",s<0?-9:0,-12,-9,9,8,5,PartPose.rotation(0,0,s*.09F));
            box(body,"oblique"+s,"skin",s<0?-8:4,-4,-7,4,10,7,PartPose.rotation(0,0,-s*.16F));
        }
        var head=pivot(r,"head",0,-18,-6,.1F,0,-.045F);
        b(head,"cranium","skin",-6,-12,-5,12,10,11);b(head,"occiput","skin",-5,-11,3,10,9,6);
        b(head,"sunken_mask","shadow_skin",-5.4F,-8,-6.8F,10.8F,5,3);b(head,"right_eye_socket","void",-4.5F,-7.2F,-7.1F,3,2.4F,.8F);
        b(head,"eye_right","eye",-3.9F,-6.7F,-7.7F,1.8F,1.4F,.7F);b(head,"eye_left","cloud_eye",2.1F,-6.7F,-7.7F,1.6F,1.2F,.7F);
        for(int s:new int[]{-1,1}){
            box(head,"angry_brow"+s,"skin",s<0?-5.5F:.5F,-9,-7.8F,5,2.6F,3,PartPose.rotation(0,0,s*.16F));
            box(head,"cheek_plane"+s,"skin",s<0?-6.3F:3.4F,-5,-7,3,4.5F,4,PartPose.rotation(0,0,s*.16F));
            var ear=pivot(head,"ear"+s,s*6,-8,0,.15F,0,s*.55F);
            b(ear,"outer_ear","skin",s<0?-5:0,-1,-1,5,3,2);b(ear,"inner_ear","scar",s<0?-4.5F:.5F,-.4F,-1.2F,3.5F,1.3F,.5F);
            horn(head,"curving_tusk"+s,"bone",s*4,-.5F,-8,s,5.4F);
        }
        b(head,"nose_bridge","skin",-1.8F,-8.8F,-9.5F,3.6F,5,4.5F);b(head,"drooping_nose","skin",-2.4F,-5.5F,-11,4.8F,3.2F,4);
        b(head,"nostril_r","void",-2,-4,-11.2F,1.2F,1,.5F);b(head,"nostril_l","void",.9F,-4,-11.2F,1.1F,1,.5F);
        b(head,"black_maw","void",-4.5F,-1.7F,-7.5F,9,3.2F,2);b(head,"heavy_lower_jaw","skin",-5.5F,.5F,-8,11,3.5F,7);
        for(int i=0;i<5;i++)tooth(head,"crooked_tooth"+i,-3.5F+i*1.7F,-1.8F,-8.8F,i%2==0?1.4F:1,true);
        box(head,"old_eye_scar","scar",1.7F,-9,-8.4F,.7F,6,.65F,PartPose.rotation(0,0,-.3F));
        b(head,"chin_wart","moss",2,3,-8.3F,1.3F,1.1F,1.2F);
        // One salvaged stone pauldron; the opposing shoulder is moss and scarred hide.
        box(body,"ruin_pauldron","stone",-14,-19,-6,9,6,14,PartPose.rotation(0,0,-.2F));
        b(body,"pauldron_carving","rune",-13,-16,-6.4F,6,2,.6F);
        for(int i=0;i<3;i++)horn(body,"pauldron_trophy"+i,"bone",-12+i*2,-20,1,-1,3+i%2);
        for(int i=0;i<7;i++)box(body,"shoulder_moss"+i,"moss",1+i%3*2,-28+i/3*2,5,3,2,4,PartPose.rotation(0,0,i*.13F));
        belt(body,7,9,7);
        for(int i=0;i<5;i++)box(body,"stitched_hide_panel"+i,i%2==0?"leather":"cloth",-8+i*3.3F,8,-8.3F,3.7F,7+(i%3)*1.5F,1.3F,PartPose.rotation(-.08F,0,(i-2)*.045F));
        for(int s:new int[]{-1,1}){
            String n=s<0?"right":"left";var a=pivot(r,n+"_arm",s*12,-16,0,.08F,0,-s*.12F);
            box(a,"deltoid","skin",-4,-2,-5,8,10,10,PartPose.rotation(.12F,0,0));
            box(a,"bicep","skin",-3.5F,6,-4.5F,7,11,9,PartPose.rotation(-.08F,0,s*.07F));
            b(a,"elbow","shadow_skin",-3.5F,13,-3,7,6,8);
            box(a,"heavy_forearm","skin",-4.2F,16,-5.8F,8.4F,10,10,PartPose.rotation(-.17F,0,0));
            b(a,"wrist_bindings","wrap",-4.6F,22,-6,9.2F,3,10.5F);b(a,"fist","skin",-4.7F,25,-7,9.4F,5,10);
            for(int i=0;i<4;i++){b(a,"knuckle"+i,"shadow_skin",-4.2F+i*2.1F,25,-8,1.7F,2.5F,2);b(a,"finger_nail"+i,"bone",-4+i*2.1F,28,-7.5F,1.2F,1.6F,1);}
            var leg=pivot(r,n+"_leg",s*5.5F,7,1,-.08F,0,s*.035F);
            b(leg,"thigh","skin",-3.8F,0,-4.5F,7.6F,8,9);b(leg,"kneecap","shadow_skin",-3.3F,6,-5.5F,6.6F,4,3);
            b(leg,"shin","skin",-3.3F,8,-3,6.6F,8,7);b(leg,"ankle_rags","wrap",-3.6F,12,-3.3F,7.2F,3,7.5F);
            b(leg,"splayed_foot","skin",-4,14,-8,8,3,12);
            for(int i=0;i<3;i++)b(leg,"toe_nail"+i,"bone",-3+i*2.2F,15,-8.8F,1.6F,1.2F,2);
        }
    }
    private static void belt(PartDefinition p,float y,float w,float d){
        b(p,"rope_belt","wrap",-w,y,-d,w*2,2,d*2);
        b(p,"belt_buckle","metal",-2,y-.4F,-d-.8F,4,3,1.3F);b(p,"buckle_inset","void",-1,y+.3F,-d-1,2,1.4F,.5F);
        for(int i=0;i<3;i++){rod(p,"charm_cord"+i,"leather",-w+2+i*2,y+2,-d,0,3+i,0,.5F);b(p,"bone_charm"+i,"bone",-w+1.6F+i*2,y+4+i,-d-.5F,1,2,1);}
    }
    private static void cyclops(PartDefinition r){
        var body=pivot(r,"body",0,-3,0,.06F,0,0);b(body,"broad_ribs","skin",-8,-14,-5,16,17,12);b(body,"abdomen","shadow_skin",-6,1,-4.5F,12,9,10);
        for(int s:new int[]{-1,1})box(body,"pectoral"+s,"skin",s<0?-7.5F:.3F,-12,-7,7.2F,7,3.6F,PartPose.rotation(0,0,s*.06F));
        var head=pivot(r,"head",0,-16,-1,.06F,0,0);b(head,"skull","skin",-5.5F,-10,-4.5F,11,10,10);
        b(head,"eye_socket","shadow_skin",-4.6F,-8.7F,-5.8F,9.2F,6.4F,2);b(head,"single_eye_white","ivory",-3.7F,-7.8F,-6.7F,7.4F,4.5F,1.2F);
        b(head,"single_iris","eye",-1.9F,-7.2F,-7.6F,3.8F,3.4F,.8F);b(head,"upper_lid","skin",-4,-8.6F,-7.5F,8,1.7F,1.8F);
        box(head,"brow_ridge","skin",-5,-10,-6.7F,10,2.4F,3.2F,PartPose.rotation(.12F,0,-.05F));
        b(head,"broken_nose","skin",-1.2F,-3.9F,-7.3F,2.4F,3.7F,3);b(head,"mouth","void",-3.8F,-.9F,-5.8F,7.6F,2.8F,1.3F);
        b(head,"lower_lip","shadow_skin",-4,1.4F,-6.2F,8,1.2F,2);b(head,"chin","skin",-4.4F,1.9F,-5.2F,8.8F,2,6);
        for(int i=0;i<4;i++)tooth(head,"broken_tooth"+i,-3+i*1.8F,-.7F,-6.6F,i==2?.7F:1.6F,true);
        for(int s:new int[]{-1,1}){box(head,"jaw_beard"+s,"hair",s<0?-5:3,-1,-3.8F,2.4F,7,5.5F,PartPose.rotation(0,0,-s*.16F));box(head,"ear"+s,"skin",s<0?-7:5,-5,0,2,4,2,PartPose.rotation(0,0,-s*.2F));}
        for(int i=0;i<4;i++)box(head,"beard_lock"+i,"hair",-3.8F+i*2,3,-5.8F,2,4+(i%2)*2,2.3F,PartPose.rotation(-.18F,0,(i-1.5F)*-.09F));
        b(head,"leather_headband","leather",-5.8F,-10,-4.8F,11.6F,2,10.6F);b(head,"headband_rune","metal",-.9F,-10,-5.5F,1.8F,1.6F,.9F);
        rod(body,"diagonal_harness","leather",-8,-14,-7,15,23,0,3);b(body,"harness_medallion","metal",-1,-5,-9,3,3,1.4F);
        box(body,"left_shoulder_plate","stone",6,-16,-6,7,5,12,PartPose.rotation(0,0,.24F));b(body,"shoulder_rune","rune",8,-13,-6.4F,3,2,.7F);
        belt(body,7,7,6);
        for(int s:new int[]{-1,1}){
            String n=s<0?"right":"left";var a=pivot(r,n+"_arm",s*10,-12,0,.07F,0,-s*.1F);
            b(a,"upper_arm","skin",-3.1F,-2,-4,6.2F,13,8);b(a,"elbow","shadow_skin",-3,9,-3,6,4,7);
            box(a,"forearm","skin",-3.4F,12,-4.5F,6.8F,11,8,PartPose.rotation(-.14F,0,0));b(a,"stitched_bracer","leather",-3.8F,16,-5,7.6F,5.5F,9);
            b(a,"hand","skin",-3.5F,22,-5.8F,7,5,8);for(int i=0;i<3;i++)b(a,"finger"+i,"shadow_skin",-2.8F+i*2,25,-6,1.6F,3,3);
            var leg=pivot(r,n+"_leg",s*4.2F,8,0,-.06F,0,s*.035F);b(leg,"thigh","skin",-3.2F,0,-3.7F,6.4F,7,7.4F);b(leg,"calf","skin",-2.7F,7,-2.7F,5.4F,9,6);
            b(leg,"boot_wrap","wrap",-3,10,-3.2F,6,5,7);b(leg,"foot","leather",-3.4F,13,-6,6.8F,3,10);
            if(s>0){b(leg,"salvaged_greave","stone",-2.6F,5,-4.3F,5.2F,8,1.8F);b(leg,"greave_glyph","rune",-.7F,7,-4.6F,1.4F,4,.5F);}
            for(int i=0;i<3;i++)box(body,"hide_skirt"+s+i,"cloth",s<0?-7+i*2.5F:.4F+i*2.5F,9,-6.6F,2.8F,6+(i%2)*2,1.2F,PartPose.rotation(-.12F,0,s*.04F));
            if(s<0){
                rod(a,"club_shaft","bark",0,23,-2,0,15,-3,2.5F);
                box(a,"stone_maul","stone",-5,28,-9,10,9,9,PartPose.rotation(-.18F,0,.15F));
                b(a,"maul_binding","wrap",-5.5F,31,-9.5F,11,2,10);b(a,"maul_rune","rune",-2,28,-10,4,3,.7F);
                for(int i=0;i<3;i++)horn(a,"maul_tooth"+i,"bone",-4+i*4,29,-6,i-1,3);
            }
        }
    }
    private static void briar(PartDefinition r){
        var body=pivot(r,"body",0,8,2,-.08F,0,0);b(body,"hollow_core","void",-6,-4,-6,12,11,21);
        box(body,"arched_spine","bark",-4,-8,-4,8,7,23,PartPose.rotation(-.12F,0,0));
        b(body,"heartwood","rune",-3,-2,-7.5F,6,5,2);
        for(int s:new int[]{-1,1}){
            box(body,"shoulder_knot"+s,"bark",s<0?-10:4,-6,-7,6,12,10,PartPose.rotation(-.2F,0,s*.16F));
            box(body,"haunch"+s,"bark",s<0?-8:3,-5,10,5,9,10,PartPose.rotation(.2F,0,-s*.2F));
            for(int i=0;i<4;i++)rod(body,"exposed_rib"+s+i,"bark",s*3,-5,-2+i*4,s*5,6,0,1.7F);
            for(int i=0;i<4;i++)box(body,"layered_bark"+s+i,"bark",s<0?-10:5,-5,-4+i*5,5,7,5,PartPose.rotation(-.25F,0,s*.32F));
            for(int i=0;i<3;i++)box(body,"lichen_shelf"+s+i,"moss",s<0?-10:6,-4+i*2,3+i*3,4,1.2F,5,PartPose.rotation(0,0,s*.2F));
        }
        for(int i=0;i<5;i++)horn(body,"swept_dorsal_thorn"+i,"bone",0,-8,-3+i*5,0,4+i%3);
        var head=pivot(r,"head",0,5,-9,.12F,0,0);box(head,"split_skull","bark",-5,-5,-6,10,8,9,PartPose.rotation(.12F,0,0));
        b(head,"maw_cavity","void",-4,-1,-11,8,5,6);b(head,"nasal_ridge","bark",-1.4F,-4.5F,-11,2.8F,3.5F,7);
        for(int s:new int[]{-1,1}){
            box(head,"cheek_blade"+s,"bark",s<0?-6.2F:3.3F,-3,-9,3,6,7,PartPose.rotation(0,s*.16F,s*.16F));
            b(head,"eye_socket"+s,"void",s<0?-5:-.1F,-3.6F,-7,5,2.7F,1.8F);b(head,"eye"+s,"eye",s<0?-4.5F:2.5F,-3,-8,2,1.3F,1);
            horn(head,"antler"+s,"bark",s*4,-6,0,s,9+(s>0?2:0));
            rod(head,"antler_fork"+s,"bone",s*6,-11,1,s*4,-4,2,1.3F);
            b(head,"jaw_hinge"+s,"bark",s<0?-5:3,3,-3,2,3,5);
        }
        b(head,"lower_jaw","bark",-4,4,-11,8,2,10);
        for(int i=0;i<6;i++){tooth(head,"upper_fang"+i,-3.3F+i*1.3F,-.4F,-11.4F,i%2==0?2.8F:1.8F,true);tooth(head,"lower_fang"+i,-3.3F+i*1.3F,4,-11.5F,1.5F,false);}
        for(int s:new int[]{-1,1})for(int rear=0;rear<2;rear++){
            var leg=pivot(r,(rear==1?"rear_":"")+(s<0?"right":"left")+"_leg",s*6,11,rear==1?14:-5,0,0,-s*.16F);
            box(leg,"knotted_upper","bark",-2.7F,0,-3,5.4F,6,6,PartPose.rotation(rear==1?-.45F:.25F,0,0));
            box(leg,"reverse_hock","bark",-1.7F,5,-2,3.4F,6,4,PartPose.rotation(rear==1?.35F:-.2F,0,0));
            b(leg,"root_paw","bark",-2.8F,10,-4,5.6F,2.5F,7);
            for(int i=0;i<3;i++)rod(leg,"root_claw"+i,"bone",-2+i*2,11,-3,0,1,-4,1.1F);
        }
        var tail=pivot(r,"tail",0,8,18,.1F,0,0);rod(tail,"tail_base","bark",0,0,0,2,-2,8,2.5F);rod(tail,"tail_tip","bark",2,-2,8,2,-4,6,1.5F);horn(tail,"tail_barb","bone",4,-6,14,1,3);
        for(int i=0;i<3;i++){rod(body,"pod_stem"+i,"bark",-4+i*4,-6,6+i*2,0,-3,1,.7F);b(body,"scarlet_seed_pod"+i,"fungus",-5+i*4,-10,6+i*2,2.5F,3,3);}
    }
    private static void infestor(PartDefinition r){
        var body=pivot(r,"body",0,1,0,.14F,0,.08F);b(body,"rotten_trunk","bark",-4,0,-3,8,15,7);b(body,"open_chest","void",-3,-1,-4,6,11,2);
        b(body,"infected_heart","fungus",-1.8F,3,-5,3.6F,4,2.7F);
        for(int s:new int[]{-1,1})for(int i=0;i<4;i++)rod(body,"cage_rib"+s+i,"bone",s*3,1+i*2.5F,-4,-s*1.5F,1,0,.9F);
        for(int i=0;i<4;i++)box(body,"twisting_bark"+i,"bark",-4+i*2,0,2,2.8F,16-i,3,PartPose.rotation(0,0,(i-1.5F)*.08F));
        var head=pivot(r,"head",0,-2,-2,.15F,0,-.2F);
        b(head,"rotten_seedpod","bark",-3.5F,-9,-2.5F,7,8,7);
        b(head,"split_pod_cavity","void",-3.8F,-8,-4.5F,7.6F,8,3);
        b(head,"spore_eye_core","fungus",-1.5F,-6.5F,-5.2F,3,3,1.5F);
        b(head,"offset_seed_eye","eye",-.7F,-6,-5.9F,1.4F,1.5F,.8F);
        for(int side:new int[]{-1,1}){
            box(head,"splintered_maw_lobe"+side,"bark",-1.2F,-1,-2,2.4F,9,3.5F,PartPose.offsetAndRotation(side*3.4F,-8,-4,.12F,side*.2F,-side*.3F));
            box(head,"upper_pod_lobe"+side,"bark",-1.2F,-5,-1.5F,2.4F,6,3,PartPose.offsetAndRotation(side*2.4F,-7,-2,.1F,0,-side*.45F));
            horn(head,"crown_branch"+side,"bark",side*2.5F,-9,1,side,side>0?7:10);
            rod(head,"crown_fork"+side,"bone",side*4,-14,2,side*3,-3,-2,1);
            for(int i=0;i<3;i++)rod(head,"inward_maw_thorn"+side+i,"bone",side*3.3F,-6+i*2.5F,-5,-side*1.7F,.7F,-1,.65F);
        }
        box(head,"lower_pod_lobe","bark",-3,-1,-6,6,2.5F,5,PartPose.rotation(-.25F,0,0));
        for(int i=0;i<3;i++)box(head,"head_fungal_shelf"+i,"fungus",2.5F,-8+i*2,-1,3.8F,1,4,PartPose.rotation(0,0,.18F));
        for(int s:new int[]{-1,1}){
            String n=s<0?"right":"left";var a=pivot(r,n+"_arm",s*5,-1,0,.12F,0,-s*1.05F);
            b(a,"tendril_base","bark",-1.6F,0,-1.6F,3.2F,8,3.2F);b(a,"vine_whip","bark",-1,6,-1,2,11,2);
            var middle=pivot(a,"whip_middle",0,16,0,.15F,0,s*.6F);b(middle,"whip_coil","bark",-.8F,0,-.8F,1.6F,14,1.6F);
            var tip=pivot(middle,"whip_tip",0,13,0,-.12F,0,s*.8F);b(tip,"living_lash","bark",-.55F,0,-.55F,1.1F,12,1.1F);
            for(int i=0;i<4;i++){horn(a,"lash_thorn"+i,"bone",1,3+i*3,0,1,2.3F);horn(middle,"reverse_barb"+i,"bone",-1,2+i*3,0,-1,2);}
            rod(tip,"curved_hook","bone",0,11,0,s*2,-3,-2,.8F);
            for(int rear=0;rear<2;rear++){
                var leg=pivot(r,(rear==1?"rear_":"")+n+"_leg",s*3.2F,15,rear==1?2:-2,rear==1?.35F:-.25F,0,-s*.25F);
                b(leg,"root_shin","bark",-1.6F,0,-1.6F,3.2F,7,3.2F);rod(leg,"spreading_root","bark",0,6,0,s*3,2,-3,1.8F);rod(leg,"root_talon","bone",s*3,8,-3,s*1,0,-3,.7F);
            }
        }
        for(int i=0;i<5;i++){box(body,"shelf_fungus"+i,"fungus",i%2==0?-5:2,2+i*2,1,4,1.2F,5,PartPose.rotation(0,0,i*.07F));}
    }
    private static void gargoyle(PartDefinition r){
        var body=pivot(r,"body",0,1,2,.18F,0,0);b(body,"carved_ribcage","stone",-5.5F,-3,-4.5F,11,11,9);b(body,"narrow_waist","stone",-3.5F,6,-3,7,6,6);
        for(int s:new int[]{-1,1}){box(body,"angular_pectoral"+s,"stone",s<0?-5.4F:.2F,-2,-6,5.2F,5,3,PartPose.rotation(0,0,s*.14F));horn(body,"shoulder_spire"+s,"stone",s*6,-3,1,s,5);}
        for(int i=0;i<3;i++)b(body,"rib_carving"+i,"shadow_stone",-3.5F,3+i*2,-4,7,.7F,1.2F);
        b(body,"heart_glyph","rune",-.9F,0,-6.4F,1.8F,3,.7F);
        var head=pivot(r,"head",0,-2,-2,.18F,0,0);b(head,"demonic_cranium","stone",-4,-8,-3,8,7,8);
        b(head,"sunken_face","shadow_stone",-3.6F,-5,-4,7.2F,4,2);
        for(int s:new int[]{-1,1}){box(head,"knife_brow"+s,"stone",s<0?-4:.5F,-6,-5.1F,3.5F,1.4F,2,PartPose.rotation(0,0,s*.22F));b(head,"eye"+s,"eye",s<0?-3.1F:1.8F,-4.6F,-5,1.5F,.9F,.6F);horn(head,"swept_horn"+s,"stone",s*3,-8,2,s,7);box(head,"ear_fin"+s,"stone",s<0?-7:4,-4,1,3,1.8F,5,PartPose.rotation(0,s*.3F,s*.3F));}
        b(head,"nasal_blade","stone",-.8F,-5,-6.2F,1.6F,3.5F,3);b(head,"snarling_mouth","void",-3,-1.5F,-5.7F,6,2,1.7F);
        box(head,"pointed_chin","stone",-2.5F,.5F,-5.3F,5,3,3.5F,PartPose.rotation(-.25F,0,0));
        for(int i=0;i<5;i++)tooth(head,"stone_fang"+i,-2.4F+i*1.2F,-1.5F,-6.6F,i%2==0?1.7F:1,true);
        for(int s:new int[]{-1,1}){
            String n=s<0?"right":"left";var arm=pivot(r,n+"_arm",s*6,1,0,.25F,0,-s*.18F);
            b(arm,"shoulder","stone",-2.8F,-1,-3,5.6F,6,6);box(arm,"forearm","stone",-2,5,-3,4,9,5,PartPose.rotation(-.25F,0,0));
            b(arm,"taloned_palm","stone",-2.4F,12,-5,4.8F,3.5F,5);
            for(int i=0;i<3;i++)rod(arm,"finger_talon"+i,"bone",-1.7F+i*1.7F,14,-4,0,3,-3,.9F);
            var leg=pivot(r,n+"_leg",s*3.8F,12,2,-.32F,0,s*.06F);b(leg,"haunch","stone",-2.6F,-1,-3,5.2F,6,7);box(leg,"digitigrade_shin","stone",-1.7F,4,-1,3.4F,8,4,PartPose.rotation(.4F,0,0));b(leg,"clawed_foot","stone",-2.5F,10,-5,5,2,8);
            for(int i=0;i<3;i++)rod(leg,"toe_talon"+i,"bone",-1.8F+i*1.8F,11,-4,0,0,-3,1);
            var wing=pivot(r,s<0?"wing_right":"wing_left",s*4,-1,4,0,s*.12F,0);
            rod(wing,"leading_edge","stone",0,0,0,s*24,-9,0,1.9F);
            for(int i=0;i<12;i++){
                float x=2+i*1.85F,top=-x*.375F;
                float bottom=x<9?9-1.1F*(x-2):x<17?3.8F-.6F*(x-9):-.9F-1.02F*(x-17);
                float scallop=(float)Math.sin((x%8)/8*Math.PI)*1.4F;float h=Math.max(.7F,bottom-top-scallop);
                b(wing,"scalloped_membrane"+i,"membrane",s<0?-x-1.9F:x,top,.35F,1.9F,h,.55F);
            }
            rod(wing,"inner_finger","stone",0,0,0,s*8,8,0,1.1F);rod(wing,"middle_finger","stone",0,0,0,s*16,1,0,1.1F);horn(wing,"wing_claw","bone",s*23,-8,0,s,3);
        }
        var tail=pivot(r,"tail",0,11,5,.2F,0,0);rod(tail,"tail_base","stone",0,0,0,0,3,8,2.3F);rod(tail,"tail_curve","stone",0,3,8,5,-1,6,1.8F);rod(tail,"tail_point","stone",5,2,14,3,-5,0,1.2F);
        for(int i=0;i<4;i++)horn(body,"spine_crest"+i,"stone",0,-5+i*3,4,0,3);
    }
    private static void hag(PartDefinition r){
        var body=pivot(r,"body",0,1,0,.12F,0,-.055F);b(body,"ragged_bodice","cloth",-3.5F,-1,-2.8F,7,12,6);
        box(body,"humped_back","cloth",-4,-4,0,8,9,6,PartPose.rotation(.2F,0,0));
        for(int i=0;i<8;i++){
            float angle=(float)(i*Math.PI/4);float x=Mth.sin(angle)*4,z=Mth.cos(angle)*3.4F;
            box(body,"layered_robe_gore"+i,i%3==0?"leather":"cloth",-2,0,-.7F,4,12+(i%3),1.4F,PartPose.offsetAndRotation(x,9,z,-.12F,angle,0));
            box(body,"embroidered_hem"+i,"trim",-2,9+(i%3),-.9F,4,1.4F,1.8F,PartPose.offsetAndRotation(x,9,z,-.12F,angle,0));
        }
        box(body,"tattered_shawl","cloth",-5,-3,3.5F,10,14,1,PartPose.rotation(.15F,0,0));
        for(int i=0;i<5;i++)box(body,"cloak_tatter"+i,"cloth",-5+i*2,10,4.8F,1.6F,5+i%3,1,PartPose.rotation(.12F,0,(i-2)*.06F));
        belt(body,8,4,3.6F);
        rod(body,"amulet_chain","metal",-2,0,-3.8F,2,4,0,.4F);rod(body,"amulet_chain_other","metal",2,0,-3.8F,-2,4,0,.4F);b(body,"hex_amulet","rune",-1,3.4F,-4.8F,2,3,1);
        for(int i=0;i<3;i++){b(body,"belt_bottle"+i,i==1?"rune":"fungus",2+i*1.2F,10+i%2,-4,1.1F,2.3F,1.3F);b(body,"bottle_stop"+i,"bark",2+i*1.2F,9.5F+i%2,-3.9F,1,1,1);}
        var head=pivot(r,"head",0,-3,-3,.08F,0,.08F);b(head,"gaunt_face","skin",-3.2F,-9,-3.3F,6.4F,9,6.6F);
        b(head,"sunken_mask","shadow_skin",-2.9F,-6.7F,-4.1F,5.8F,4,1.5F);
        for(int s:new int[]{-1,1}){
            b(head,"eye_socket"+s,"void",s<0?-2.8F:.7F,-6.3F,-4.6F,2.1F,1.8F,.7F);b(head,"eye"+s,"eye",s<0?-2.3F:1.2F,-5.9F,-5,1.2F,.85F,.7F);
            box(head,"crooked_brow"+s,"skin",s<0?-3.2F:.5F,-7.2F,-4.5F,2.7F,1.5F,1.5F,PartPose.rotation(0,0,s*.16F));
            box(head,"cheekbone"+s,"skin",s<0?-3.5F:1.7F,-4.4F,-4.3F,1.8F,3,2,PartPose.rotation(0,0,-s*.12F));
            for(int i=0;i<3;i++)box(head,"hair_lock"+s+i,"hair",s<0?-4.2F+i*.5F:2.3F+i*.5F,-8+i*.7F,-1.5F-i,1.1F,10+i%2*2,1.7F,PartPose.rotation(.08F,0,-s*.1F));
            box(head,"hood_flap"+s,"cloth",s<0?-4.7F:3.6F,-8,-3.8F,1.1F,8,8,PartPose.rotation(0,0,-s*.1F));
            horn(head,"antler_circlet"+s,"bone",s*3,-10,1,s,5);
        }
        b(head,"nose_bridge","skin",-.8F,-6.5F,-6,1.6F,4,2.5F);box(head,"hooked_nose","skin",-.9F,-3.5F,-7,1.8F,2.5F,2.1F,PartPose.rotation(-.25F,0,0));b(head,"nose_wart","moss",.5F,-3,-7.4F,.7F,.7F,.6F);
        b(head,"thin_mouth","void",-1.9F,-1.4F,-4.5F,3.8F,1.2F,1);b(head,"chin","skin",-1.8F,-.1F,-4.5F,3.6F,2.4F,3);
        for(int i=0;i<3;i++)tooth(head,"rotted_tooth"+i,-1.3F+i*1.2F,-1.4F,-5.2F,i==1?.8F:.4F,true);
        box(head,"peaked_hood","cloth",-4.5F,-10,-4.3F,9,2.5F,8.7F,PartPose.rotation(.1F,0,0));box(head,"slouched_hood_tip","cloth",-3.2F,-12,-2.5F,6.4F,3,6.5F,PartPose.rotation(.18F,0,-.22F));
        for(int i=0;i<3;i++)b(head,"hood_rune"+i,"trim",-3.8F+i*3.1F,-8.4F,-4.7F,.7F,2,.6F);
        for(int s:new int[]{-1,1}){
            String n=s<0?"right":"left";var arm=pivot(r,n+"_arm",s*4.8F,1,-.3F,.2F,0,-s*.13F);
            box(arm,"ragged_sleeve","cloth",-2,-1,-2.2F,4,10,4.4F,PartPose.rotation(-.18F,0,0));b(arm,"sleeve_trim","trim",-2.2F,7,-3.4F,4.4F,1.7F,5);
            b(arm,"sinewy_forearm","skin",-1.1F,8,-3.1F,2.2F,5,3);b(arm,"bony_hand","skin",-1.6F,12,-4,3.2F,4,3.5F);
            for(int i=0;i<3;i++){rod(arm,"long_finger"+i,"skin",-1.2F+i*1.2F,15,-3,0,3,-1,.7F);rod(arm,"finger_claw"+i,"bone",-1.2F+i*1.2F,18,-4,0,1,-1.6F,.4F);}
            for(int i=0;i<3;i++)box(arm,"shoulder_feather"+i,"hair",-2.6F+i*1.5F,-1,-1,1.2F,5+i%2,3,PartPose.rotation(.15F,0,(i-1)*.2F));
            var leg=pivot(r,n+"_leg",s*1.8F,13,0,0,0,0);b(leg,"leg","shadow_skin",-1.1F,0,-1.2F,2.2F,9,2.4F);b(leg,"pointed_boot","leather",-1.4F,8,-3.5F,2.8F,3,5);
            if(s>0){rod(arm,"gnarled_staff","bark",0,13,-1,0,-31,-1,1.5F);horn(arm,"staff_fork_left","bark",-1,-18,-2,-1,6);horn(arm,"staff_fork_right","bark",1,-18,-2,1,5);b(arm,"staff_skull","bone",-2,-22,-3,4,4,3);b(arm,"skull_eye_r","void",-1.5F,-21,-3.3F,1,1,.5F);b(arm,"skull_eye_l","void",.5F,-21,-3.3F,1,1,.5F);b(arm,"staff_charm","rune",-.7F,-17,-3,.9F,2,1);}
        }
    }
    @Override public void setupAnim(MonstrosityEntity mob,float walk,float amount,float age,float yaw,float pitch){
        root.getAllParts().forEach(ModelPart::resetPose);var head=root.getChild("head");head.yRot+=yaw*Mth.DEG_TO_RAD;head.xRot+=pitch*Mth.DEG_TO_RAD*.6F;
        float attack=mob==null?0:mob.attackMotion(0),step=Mth.cos(walk*.65F)*amount;
        for(int side:new int[]{-1,1}){
            String n=side<0?"right":"left";root.getChild(n+"_leg").xRot+=step*side*.65F;root.getChild("rear_"+n+"_leg").xRot-=step*side*.65F;
            var arm=root.getChild(n+"_arm");arm.xRot+=-step*side*.32F-attack*(kind==MonstrosityKind.TROLL||kind==MonstrosityKind.CYCLOPS?1.2F:1.3F);
            if(kind==MonstrosityKind.INFESTOR){arm.zRot=-side*(1.05F-attack*.8F+Mth.sin(age*.06F)*.08F);arm.xRot=-attack*1.45F;var middle=arm.getChild("whip_middle");middle.zRot=side*(.6F-attack*.7F);middle.getChild("whip_tip").zRot=side*(.8F-attack*.8F);}
            if(kind==MonstrosityKind.HAG)arm.xRot-=attack*.3F;
            root.getChild(side<0?"wing_right":"wing_left").yRot+=side*(.15F+attack*.25F+(mob!=null&&!mob.onGround()?.2F:0));
        }
        root.getChild("tail").yRot+=Mth.sin(age*.08F)*.15F;root.getChild("body").xRot+=Mth.sin(age*.045F)*.012F;
    }
}
