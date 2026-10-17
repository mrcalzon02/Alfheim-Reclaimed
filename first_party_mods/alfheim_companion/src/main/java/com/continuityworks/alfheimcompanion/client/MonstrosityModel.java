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
        for(String name:new String[]{"head","body","right_arm","left_arm","right_leg","left_leg","rear_right_leg","rear_left_leg","middle_right_leg","middle_left_leg","tail","wing_left","wing_right"})pivot(root,name,0,0,0,0,0,0);
        switch(kind){case TROLL->troll(root);case CYCLOPS->cyclops(root);case BRIAR->briar(root);case INFESTOR->infestor(root);case GARGOYLE->gargoyle(root);case HAG->hag(root);case WENDIGO->wendigo(root);case DUSKWEAVER->duskweaver(root);case BRIDE->bride(root);case MAW->barrowMaw(root);case NUCKELAVEE->nuckelavee(root);case REDCAP->redcap(root);case CRYSTAL_COLOSSUS->crystalColossus(root);case SHARD_REAVER->shardReaver(root);case PRISM_WARDEN->prismWarden(root);case MARROW_TICK->marrowTick(root);case RIB_BURROWER->ribBurrower(root);case SINEW_LEECH->sinewLeech(root);case PARASITE_MAW->parasiteMaw(root);}
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
    private static void antler(PartDefinition p,String n,float x,float y,float z,int side){
        rod(p,n+"_burr","bone",x,y,z,side*2,-5,1,2.2F);
        rod(p,n+"_beam","bone",x+side*2,y-5,z+1,side*5,-7,2,1.8F);
        rod(p,n+"_crown","bone",x+side*7,y-12,z+3,side*4,-4,-1,1.2F);
        for(int i=0;i<4;i++){
            float px=x+side*(2+i*1.6F),py=y-5-i*2;
            rod(p,n+"_tine"+i,"bone",px,py,z+1+i*.5F,side*(1+i%2),-4-i%3,-2-i*.5F,1.1F-i*.12F);
        }
        rod(p,n+"_brow_tine","bone",x+side,y-3,z,side,-3,-5,1.1F);
    }
    private static void exposedRibs(PartDefinition p,String prefix,String mat,float y,float z,float width,int count){
        for(int side:new int[]{-1,1})for(int i=0;i<count;i++){
            float yy=y+i*3.1F,w=width-(i>count/2?(i-count/2)*.55F:0);
            rod(p,prefix+side+"_back"+i,mat,0,yy,z,side*w,1,-2,1.25F);
            rod(p,prefix+side+"_curve"+i,mat,side*w,yy+1,z-2,side*1.4F,2,-4,1.1F);
            rod(p,prefix+side+"_tip"+i,mat,side*(w+1.4F),yy+3,z-6,-side*2.6F,1,-2,1);
        }
    }
    private static void wendigo(PartDefinition r){
        var body=pivot(r,"body",0,-6,3,.18F,0,0);
        rod(body,"exposed_spinal_column","bone",0,-27,5,0,34,-1,2.5F);
        for(int i=0;i<11;i++)box(body,"vertebra"+i,"bone",-1.8F,-27+i*3,4,3.6F,1.6F,3,PartPose.rotation(.12F,0,0));
        exposedRibs(body,"stag_rib","bone",-20,5,6,6);
        b(body,"hollow_sternum","void",-1.5F,-18,-3,3,17,1.4F);rod(body,"sternum_keel","bone",0,-18,-4,0,16,0,1.1F);
        b(body,"fey_ember","rune",-.7F,-13,-4.7F,1.4F,3,.7F);
        for(int side:new int[]{-1,1}){
            box(body,"raised_scapula"+side,"bone",-2,-12,-1,4,14,2,PartPose.offsetAndRotation(side*5,-16,5,.18F,side*.35F,side*.3F));
            rod(body,"collarbone"+side,"bone",0,-20,0,side*11,3,-1,1.9F);
            box(body,"shoulder_pelt"+side,"fur",side<0?-10:3,-22,3,7,8,8,PartPose.rotation(.3F,0,-side*.22F));
            for(int i=0;i<5;i++)box(body,"hanging_pelt"+side+i,"fur",side<0?-10+i:5+i,-15+i%2,5+i%3,1.4F,7+i%3,2,PartPose.rotation(.2F,0,side*.12F));
        }
        b(body,"open_pelvis","bone",-4,5,-2,8,4,7);b(body,"pelvic_void","void",-2.5F,5,-2.3F,5,3,1);
        for(int i=0;i<4;i++)box(body,"hip_pelt_tatter"+i,"fur",-5+i*2.6F,7,3,2.2F,8+i%2,1.5F,PartPose.rotation(.16F,0,(i-1.5F)*.1F));
        rod(body,"arched_neck_keel","bone",0,-28,5,0,3,-7,2.2F);
        rod(body,"descending_neck","bone",0,-25,-2,0,7,-7,1.8F);
        for(int i=0;i<4;i++)box(body,"hunched_neck_vertebra"+i,"bone",-2,-28+i*1.5F,3-i*2,4,1.7F,2.5F,PartPose.rotation(.3F,0,0));
        var head=pivot(r,"head",0,-19,-11,.34F,0,-.08F);
        b(head,"deer_cranium","bone",-3.7F,-9,-3,7.4F,9,8);b(head,"frontal_keel","ivory",-1,-10,-3,2,6,6);
        box(head,"long_deer_rostrum","bone",-2.3F,-4,-12,4.6F,4.5F,11,PartPose.rotation(.1F,0,0));
        for(int side:new int[]{-1,1}){
            b(head,"empty_orbit"+side,"void",side<0?-3.6F:1.2F,-6.7F,-4.1F,2.4F,3.5F,1.5F);
            b(head,"pinprick_eye"+side,"eye",side<0?-2.8F:2,-5.6F,-4.8F,.8F,1,.5F);
            box(head,"orbital_rim"+side,"bone",side<0?-4.2F:1.3F,-8,-4.5F,3,1.5F,2,PartPose.rotation(0,0,side*.22F));
            rod(head,"zygomatic_arch"+side,"bone",side*3,-3,-2,-side*.7F,3,-6,1.1F);
            antler(head,"branching_antler"+side,side*3,-9,2,side);
            box(head,"withered_ear"+side,"fur",-1.3F,-.7F,-1.5F,5,1.4F,3,PartPose.offsetAndRotation(side*4,-7,2,0,side*.3F,-side*.45F));
        }
        b(head,"nasal_opening","void",-1.5F,-3.8F,-12.4F,3,2.4F,.8F);
        b(head,"jaw_gap","void",-2.4F,.2F,-10,4.8F,2,8);b(head,"skeletal_lower_jaw","bone",-2.5F,2,-11.5F,5,1.1F,10.5F);
        for(int i=0;i<5;i++)for(int side:new int[]{-1,1})tooth(head,"deer_molar"+side+i,side*2,.1F,-10+i*1.7F,.8F,true);
        for(int side:new int[]{-1,1}){
            String n=side<0?"right":"left";var arm=pivot(r,n+"_arm",side*10,-21,1,.08F,0,-side*.1F);
            rod(arm,"humerus","bone",0,0,0,side,15,-1,2.1F);b(arm,"elbow_knob","bone",side-1.6F,13,-2.5F,3.2F,3,3);
            rod(arm,"radius","bone",side,15,-1,-side*.6F,13,-3,1.2F);rod(arm,"ulna","bone",side+1,15,0,-side*.6F,13,-3,1);
            for(int i=0;i<3;i++)box(arm,"fur_strand"+i,"fur",-2+i*1.5F,2,1,1.3F,9-i,2,PartPose.rotation(.2F,0,0));
            b(arm,"skeletal_palm","bone",-2,27,-5.5F,4,4,3);
            for(int i=0;i<4;i++){rod(arm,"finger_bone"+i,"bone",-1.8F+i*1.2F,30,-4,side*(i-1.5F)*.5F,5,-2,.7F);rod(arm,"hooked_claw"+i,"shadow_stone",-1.8F+i*1.2F+side*(i-1.5F)*.5F,35,-6,0,2,-2,.55F);}
            var leg=pivot(r,n+"_leg",side*4,7,2,-.12F,0,side*.06F);
            rod(leg,"femur","bone",0,0,0,0,7,-1,2.2F);b(leg,"knee","bone",-1.6F,6,-3,3.2F,2.5F,3);
            rod(leg,"rear_hock","bone",0,8,-1,0,5,3,1.7F);rod(leg,"metatarsal","bone",0,13,2,0,3,-3,1.3F);
            for(int i=0;i<2;i++)b(leg,"cloven_hoof"+i,"shadow_stone",-2+i*2.1F,14,-4,1.8F,3,5);
        }
        for(int i=0;i<3;i++){rod(body,"fetish_cord"+i,"leather",-3+i*3,-18,-4,0,5+i,0,.45F);b(body,"bone_fetish"+i,"bone",-3.6F+i*3,-13+i,-4.6F,1.2F,2.5F,1);}
    }
    private static void duskweaver(PartDefinition r){
        var body=pivot(r,"body",0,9,3,-.08F,0,0);
        b(body,"thorax","chitin",-5,-3,-8,10,8,12);b(body,"abdomen_core","chitin",-6,-4,3,12,9,14);
        box(body,"faceted_abdomen","chitin",-5,-6,5,10,5,10,PartPose.rotation(.13F,0,0));
        for(int i=0;i<4;i++)box(body,"abdomen_band"+i,"fur",-5.4F,-4.5F,4+i*3,10.8F,2,1.2F,PartPose.rotation(-.1F,0,0));
        for(int side:new int[]{-1,1})for(int i=0;i<5;i++)box(body,"thorax_fuzz"+side+i,"fur",side<0?-6:4,-3+i%2,-5+i*2,2,3.5F,2.5F,PartPose.rotation(0,0,side*.3F));
        var head=pivot(r,"head",0,8,-7,.15F,0,0);b(head,"moth_mask","ivory",-4,-4,-3,8,6,5);b(head,"central_mask_split","void",-.6F,-3.5F,-3.5F,1.2F,5,.8F);
        for(int side:new int[]{-1,1}){
            box(head,"compound_eye"+side,"void",side<0?-4.4F:1.5F,-3.4F,-3.7F,2.9F,3.8F,1.5F,PartPose.rotation(0,side*.15F,side*.15F));
            for(int i=0;i<3;i++)b(head,"eye_facet"+side+i,"eye",side<0?-3.8F:2.1F,-2.8F+i, -4.4F,.8F,.7F,.5F);
            rod(head,"antenna"+side,"chitin",side*2,-4,0,side*5,-8,1,.7F);
            for(int i=0;i<5;i++)rod(head,"antenna_feather"+side+i,"fur",side*(2.5F+i),-5-i*1.4F,.5F,side*2,-.6F,-1,.35F);
            var jaw=pivot(head,"mandible"+side,side*2.7F,1,-3,0,0,-side*.35F);rod(jaw,"pincer_base","bone",0,0,0,side*1.5F,3,-2,1.1F);rod(jaw,"pincer_hook","bone",side*1.5F,3,-2,-side*2,1,-2,.7F);
        }
        for(int side:new int[]{-1,1})for(int pair=0;pair<3;pair++){
            String name=pair==0?(side<0?"right_arm":"left_arm"):(pair==2?"rear_":"")+(side<0?"right_leg":"left_leg");
            var leg=pivot(r,name,side*4.5F,12,-6+pair*8,0,0,0);
            rod(leg,"coxa","chitin",0,0,0,side*6,-3,pair==0?-3:2,1.5F);rod(leg,"femur","chitin",side*6,-3,pair==0?-3:2,side*4,4,0,1.1F);
            rod(leg,"needle_tibia","chitin",side*10,1,pair==0?-3:2,side*1.5F,10,-2,.75F);rod(leg,"foot_hook","bone",side*11.5F,11,pair==0?-5:0,-side*1.2F,1,-1,.5F);
            for(int i=0;i<3;i++)rod(leg,"leg_bristle"+i,"fur",side*(3+i*2),-1,1,side,-2,0,.4F);
        }
        for(int side:new int[]{-1,1}){
            var wing=pivot(r,side<0?"wing_right":"wing_left",side*3,6,4,.2F,side*.3F,0);
            for(int i=0;i<9;i++){
                float x=2+i*2,top=-5-Mth.sin(i*.33F)*4,h=11+Mth.sin(i*.4F)*9-(i%3==0?2:0);
                b(wing,"moth_wing_lobe"+i,"membrane",side<0?-x-2:x,top,0,2.1F,h,.7F);
            }
            rod(wing,"leading_vein","chitin",0,0,0,side*18,-7,0,.7F);
            for(int i=0;i<3;i++)rod(wing,"wing_vein"+i,"chitin",0,0,.2F,side*(8+i*5),5+i*2,0,.45F);
            b(wing,"watching_wing_eye","ivory",side<0?-13:8,-3,-.3F,5,4,1);b(wing,"wing_eye_ring","void",side<0?-12:9,-2.5F,-.6F,3,3,.6F);b(wing,"wing_eye_glint","rune",side<0?-11:10,-2,-1,1,1,.5F);
            for(int i=0;i<3;i++)box(wing,"frayed_wing_tip"+i,"web",side<0?-14-i*2:12+i*2,7+i%2,0,.7F,4+i,1,PartPose.rotation(0,0,side*.2F));
        }
        for(int i=0;i<3;i++)rod(body,"silk_spinneret"+i,"web",-2+i*2,3,15,0,3,5,.55F);
    }
    private static void bride(PartDefinition r){
        var body=pivot(r,"body",0,-4,0,.045F,0,0);b(body,"funeral_bodice","cloth",-3.5F,0,-2.8F,7,12,5.6F);
        b(body,"hollow_breast","void",-2.2F,1,-3.2F,4.4F,6,1);exposedRibs(body,"corset_bone","bone",1,1.5F,2.1F,2);
        for(int i=0;i<10;i++){
            float a=(float)(i*Math.PI/5),x=Mth.sin(a)*4,z=Mth.cos(a)*3;
            box(body,"tattered_skirt_panel"+i,"cloth",-1.7F,0,-.5F,3.4F,15+i%3,.9F,PartPose.offsetAndRotation(x,11,z,-.13F,a,0));
            box(body,"worn_lace_hem"+i,"web",-1.8F,12+i%3,-.7F,3.6F,2,.9F,PartPose.offsetAndRotation(x,11,z,-.13F,a,0));
            rod(body,"hanging_skirt_thread"+i,"web",x,24+i%2,z,0,3+i%2,0,.35F);
        }
        belt(body,10,3.5F,3);b(body,"dead_bouquet_binding","leather",-1.8F,8,-4,3.6F,3,1);
        for(int i=0;i<5;i++){rod(body,"bouquet_stem"+i,"bark",-1.6F+i*.8F,8,-4,0,-5-i%2,0,.4F);b(body,"withered_blossom"+i,"fungus",-2+i*.8F,2-i%2,-4.4F,1.3F,1.2F,1);}
        rod(body,"long_neck","bone",0,-7,0,0,7,0,1.6F);
        var head=pivot(r,"head",0,-12,-.5F,.08F,0,-.07F);b(head,"broken_porcelain_mask","ivory",-2.7F,-7,-3,5.4F,7,1.5F);b(head,"empty_head","void",-2.5F,-6.5F,-1.5F,5,6,4);
        for(int side:new int[]{-1,1}){
            b(head,"sorrow_orbit"+side,"void",side<0?-2.2F:.5F,-5.3F,-3.5F,1.7F,2,.8F);b(head,"distant_eye"+side,"eye",side<0?-1.7F:1,-4.8F,-4,.55F,.7F,.4F);
            box(head,"thorn_circlet"+side,"bark",side<0?-3.6F:2.5F,-8,-1,1.1F,3.5F,4,PartPose.rotation(0,0,-side*.2F));horn(head,"veil_crown_thorn"+side,"bone",side*2,-8,0,side,3.7F);
            for(int i=0;i<4;i++)box(head,"veil_lace_strand"+side+i,"web",side<0?-3.8F+i*.35F:2.7F+i*.35F,-7+i*.3F,-.7F+i, .55F,17+i%3,1.1F,PartPose.rotation(.12F,0,-side*.045F));
        }
        b(head,"mask_mouth","void",-.9F,-1.6F,-3.7F,1.8F,.8F,.7F);rod(head,"mask_fracture","shadow_stone",.5F,-6,-3.8F,1,4,0,.25F);
        b(head,"veil_crown","web",-3.3F,-8,-2,6.6F,1.2F,6);
        for(int i=0;i<7;i++)box(head,"trailing_veil"+i,"web",-3.3F+i,-7,3,.6F,22+i%3*2,.7F,PartPose.rotation(.12F,0,0));
        for(int side:new int[]{-1,1}){
            String n=side<0?"right":"left";var a=pivot(r,n+"_arm",side*4,-3,0,.1F,0,-side*.12F);
            b(a,"lace_sleeve","web",-1.5F,0,-1.8F,3,9,3.6F);rod(a,"forearm_bone","bone",0,7,0,0,10,-1,1.1F);
            for(int i=0;i<3;i++)box(a,"sleeve_ribbon"+i,"cloth",-1.5F+i,7,1,.7F,9+i*2,.8F,PartPose.rotation(.1F,0,side*.1F));
            b(a,"palm","bone",-1.4F,16,-2,2.8F,3,2);
            for(int i=0;i<4;i++){rod(a,"finger"+i,"bone",-1.2F+i*.8F,18,-1,-side*.2F,4,-1,.45F);rod(a,"talon"+i,"shadow_stone",-1.2F+i*.8F-side*.2F,22,-2,0,1,-1,.3F);}
            var leg=pivot(r,n+"_leg",side*1.7F,16,0,0,0,0);rod(leg,"shin","bone",0,0,0,0,7,0,1);b(leg,"worn_slipper","leather",-1,6,-2,2,2,4);
        }
    }
    private static void barrowMaw(PartDefinition r){
        var body=pivot(r,"body",0,7,4,-.12F,0,0);b(body,"rotting_core","shadow_skin",-7,-3,-7,14,13,21);
        box(body,"fungal_hump","fungus",-6,-8,0,12,9,13,PartPose.rotation(.18F,0,0));
        exposedRibs(body,"grave_rib","bone",-2,4,5.7F,4);
        for(int side:new int[]{-1,1})for(int i=0;i<4;i++)box(body,"armored_scute"+side+i,"chitin",side<0?-9:4,-3,-5+i*5,5,7,5,PartPose.rotation(0,0,side*.26F));
        for(int i=0;i<7;i++){
            float x=(i%3-1)*4,y=-6-i%2*3,z=1+i/3*5;
            rod(body,"mushroom_stalk"+i,"bone",x,y,z,0,-3-i%2,0,1.1F);
            b(body,"mushroom_gills"+i,"wrap",x-2.5F,y-3.8F-i%2,z-2.3F,5,1,4.6F);
            box(body,"tiered_fungal_cap"+i,"fungus",x-3,y-5-i%2,z-2.8F,6,2,5.6F,PartPose.rotation(0,0,(i%3-1)*.13F));
        }
        var head=pivot(r,"head",0,6,-9,-.08F,0,0);b(head,"huge_maw_void","void",-5.5F,-6,-7,11,13,9);
        b(head,"fractured_upper_skull","bone",-5,-9,-5.5F,10,4,8);b(head,"nasal_bridge","bone",-1.2F,-7,-8,2.4F,3,4);
        for(int side:new int[]{-1,1}){
            b(head,"empty_skull_orbit"+side,"void",side<0?-4.7F:1.5F,-7.5F,-6.1F,3.2F,2,.9F);
            rod(head,"side_jaw_hinge"+side,"bone",side*5,-5,-3,side*1,11,-1,1.8F);
            box(head,"cheek_blade"+side,"bone",-1,-4,-1,2,8,3,PartPose.offsetAndRotation(side*5,-3,-5,0,side*.2F,-side*.16F));
            for(int i=0;i<3;i++)rod(head,"side_fang"+side+i,"bone",side*5,-2+i*3,-7,-side*2,.5F,-1,.7F);
        }
        b(head,"wide_lower_jaw","bone",-6,7,-8,12,2.5F,10);b(head,"wet_throat","sinew",-3.5F,-3,-3,7,10,2);
        b(head,"throat_spore","rune",-1.5F,0,-4.2F,3,4,1);
        for(int i=0;i<7;i++){tooth(head,"upper_needle"+i,-4.5F+i*1.5F,-5.5F,-8.2F,3+i%3,true);tooth(head,"lower_needle"+i,-4.5F+i*1.5F,7,-8.5F,2.3F+i%2,false);}
        for(int side:new int[]{-1,1})for(int rear=0;rear<2;rear++){
            var leg=pivot(r,(rear==1?"rear_":"")+(side<0?"right":"left")+"_leg",side*6,13,rear==1?15:-6,0,0,-side*.1F);
            box(leg,"swollen_limb","shadow_skin",-2.8F,0,-3,5.6F,7,6,PartPose.rotation(rear==1?-.2F:.15F,0,0));
            b(leg,"bone_splint","bone",-1,1,-3.4F,2,8,1.5F);b(leg,"knuckled_foot","chitin",-3,8,-5,6,3,8);
            for(int i=0;i<3;i++)rod(leg,"burial_claw"+i,"bone",-2+i*2,9,-4,0,1,-4,.8F);
        }
        var tail=pivot(r,"tail",0,10,18,0,0,0);rod(tail,"bony_tail","bone",0,0,0,0,-1,9,1.5F);b(tail,"spore_sac","fungus",-2,-3,6,4,4,5);
    }
    private static void nuckelavee(PartDefinition r){
        var body=pivot(r,"body",0,2,2,-.05F,0,0);b(body,"equine_ribcage","sinew",-5,5,-11,10,10,24);
        box(body,"rounded_croup","skin",-5.5F,4,8,11,10,10,PartPose.rotation(-.12F,0,0));
        for(int side:new int[]{-1,1})for(int i=0;i<6;i++)box(body,"equine_exposed_rib"+side+i,"bone",side<0?-5.8F:4.8F,6,-8+i*3.3F,1,8-i%2,1.2F,PartPose.rotation(0,0,side*.12F));
        rod(body,"fused_human_spine","bone",0,-15,1,0,22,1,1.8F);b(body,"rider_torso","sinew",-3.7F,-12,-2.4F,7.4F,15,5.5F);
        exposedRibs(body,"rider_rib","bone",-11,2,3.5F,4);
        for(int i=0;i<5;i++)box(body,"spine_fin"+i,"chitin",-.8F,1,2+i*3,1.6F,5,3,PartPose.rotation(.25F,0,0));
        var horse=pivot(body,"fused_horse_head",0,4,-13,.22F,0,0);b(horse,"equine_skull","skin",-2.8F,-7,-4,5.6F,9,7);
        box(horse,"long_muzzle","bone",-2.1F,-2,-10,4.2F,5,9,PartPose.rotation(.15F,0,0));
        for(int side:new int[]{-1,1}){b(horse,"horse_empty_eye"+side,"void",side<0?-3:1.5F,-5,-4.5F,1.5F,2,.9F);b(horse,"horse_eye_glint"+side,"eye",side<0?-2.5F:2,-4.5F,-5,.5F,.6F,.5F);box(horse,"ragged_ear"+side,"skin",-.7F,-4,-1,1.4F,5,2,PartPose.offsetAndRotation(side*2,-6,1,0,0,side*.2F));}
        b(horse,"nostril_void","void",-1.5F,-.5F,-10.4F,3,2,.8F);
        for(int i=0;i<6;i++)box(horse,"mane_lock"+i,"hair",-1,-8+i,2,2,5+i%3,3,PartPose.rotation(.25F+i*.03F,0,.1F));
        var head=pivot(r,"head",0,-14,-1,.1F,0,0);b(head,"fused_rider_skull","skin",-3,-8,-3,6,8,6);
        b(head,"raw_facial_mask","sinew",-2.7F,-6.5F,-3.7F,5.4F,6,1.8F);
        for(int side:new int[]{-1,1}){b(head,"rider_orbit"+side,"void",side<0?-2.4F:.7F,-5.7F,-4.4F,1.7F,2,.8F);b(head,"rider_eye"+side,"eye",side<0?-1.9F:1.2F,-5,-4.9F,.6F,.6F,.5F);box(head,"skull_side_plate"+side,"bone",side<0?-3.4F:2.3F,-6,-1.8F,1.1F,5,4,PartPose.rotation(0,0,-side*.12F));}
        b(head,"rider_vertical_maw","void",-1.4F,-3,-4.2F,2.8F,3.6F,1);
        b(head,"exposed_nasal_keel","bone",-.5F,-6,-4.7F,1,2.5F,1.1F);
        for(int i=0;i<3;i++)tooth(head,"rider_tooth"+i,-.9F+i*.9F,-2.8F,-4.9F,i==1?.65F:1.3F,true);
        for(int side:new int[]{-1,1})box(head,"sunken_jaw_plate"+side,"bone",side<0?-2.8F:1.6F,-3.4F,-3.5F,1.2F,4,2,PartPose.rotation(0,0,-side*.2F));
        for(int i=0;i<3;i++)b(body,"rider_neck_vertebra"+i,"bone",-1.2F,-15+i*1.5F,-.2F,2.4F,1,2);
        for(int i=0;i<4;i++)rod(head,"wet_mane"+i,"hair",-2+i*1.3F,-8,2,0,12+i%2,2,.7F);
        for(int side:new int[]{-1,1}){
            var arm=pivot(r,side<0?"right_arm":"left_arm",side*5.5F,-9,0,.1F,0,-side*.08F);
            b(arm,"elongated_upper_arm","sinew",-1.4F,0,-1.5F,2.8F,12,3);rod(arm,"forearm_bone","bone",0,11,0,0,12,-2,1.2F);b(arm,"rider_hand","skin",-1.6F,22,-3,3.2F,3,2.6F);
            for(int i=0;i<4;i++)rod(arm,"needle_finger"+i,"bone",-1.3F+i*.85F,24,-2,0,5,-2,.5F);
            for(int rear=0;rear<2;rear++){
                var leg=pivot(r,(rear==1?"rear_":"")+(side<0?"right":"left")+"_leg",side*4.3F,14,rear==1?14:-7,0,0,0);
                rod(leg,"equine_upper_leg","sinew",0,0,0,0,4,rear==1?-2:0,2.6F);rod(leg,"equine_cannon","bone",0,4,rear==1?-2:0,0,5,rear==1?1:-1,1.4F);
                b(leg,"heavy_hoof","shadow_stone",-1.8F,8,-3,3.6F,2,4.5F);
            }
        }
        var tail=pivot(r,"tail",0,9,19,.2F,0,0);rod(tail,"tail_bone","bone",0,0,0,0,4,4,1.2F);for(int i=0;i<5;i++)rod(tail,"tail_hair"+i,"hair",-1+i*.5F,3,3,0,9+i%3,2,.5F);
    }
    private static void redcap(PartDefinition r){
        var body=pivot(r,"body",0,12,1,.15F,0,0);b(body,"crooked_torso","cloth",-3.5F,-3,-2.5F,7,10,5.5F);b(body,"leather_vest","leather",-3.8F,-2,-3.2F,7.6F,7,1.4F);
        for(int side:new int[]{-1,1}){
            box(body,"folded_lapel"+side,"cloth",side<0?-3.4F:1.2F,-2.5F,-4,2.2F,5,1,PartPose.rotation(0,0,side*.24F));
            for(int i=0;i<3;i++)b(body,"brass_button"+side+i,"metal",side*1.5F-.3F,i*1.5F,-4.2F,.6F,.6F,.6F);
            for(int i=0;i<2;i++)box(body,"coat_tail"+side+i,"cloth",side<0?-4+i*1.5F:1.3F+i*1.5F,5,1.6F,1.8F,6+i,1.5F,PartPose.rotation(.15F,0,side*.13F));
        }
        belt(body,4,3.7F,3);b(body,"stolen_pouch","leather",2.6F,6,-3.7F,2.8F,3,2);b(body,"pouch_flap","cloth",2.4F,5.7F,-4.1F,3.2F,1.3F,2);
        b(body,"patched_pack","leather",-3,-2,2.5F,6,7,3);b(body,"pack_patch","wrap",-1.4F,-1,5.3F,2.8F,2.8F,.5F);
        var head=pivot(r,"head",0,9,-2.5F,.07F,0,-.08F);b(head,"wizened_goblin_skull","skin",-3.5F,-6,-3,7,6.5F,6);
        for(int side:new int[]{-1,1}){
            b(head,"mean_orbit"+side,"void",side<0?-3:-.1F,-4.6F,-3.6F,3,1.8F,.8F);b(head,"mean_eye"+side,"eye",side<0?-2.4F:1,-4.3F,-4.2F,1.2F,.8F,.6F);
            box(head,"angry_brow"+side,"skin",side<0?-3.5F:.3F,-5.3F,-4,3.2F,1.3F,1.7F,PartPose.rotation(0,0,side*.22F));
            box(head,"knife_ear"+side,"skin",-1,-.7F,-.7F,5,1.4F,1.4F,PartPose.offsetAndRotation(side*3,-3.2F,0,0,side*.2F,-side*.3F));
            b(head,"hollow_cheek"+side,"shadow_skin",side<0?-3.3F:1.8F,-2.7F,-3.7F,1.5F,2,1.6F);
        }
        b(head,"hooked_nose","skin",-.9F,-4,-5.4F,1.8F,3.4F,2.7F);b(head,"wide_sneer","void",-2.7F,-.9F,-3.8F,5.4F,1.6F,1);b(head,"jutting_chin","skin",-2,-.1F,-3.6F,4,1.8F,3);
        for(int i=0;i<5;i++)tooth(head,"needle_tooth"+i,-2+i,-.8F,-4.4F,i%2==0?1.2F:.6F,true);
        box(head,"broad_red_brim","cap",-5.5F,-7,-4.4F,11,1.6F,9,PartPose.rotation(.04F,0,0));
        box(head,"red_cap_crown","cap",-4.7F,-10,-3.5F,9.4F,3.7F,7,PartPose.rotation(0,0,-.12F));
        box(head,"slouching_cap_tip","cap",-2.7F,-12,-2.3F,6,3.5F,5,PartPose.rotation(0,0,-.38F));
        b(head,"cap_leather_band","leather",-4.9F,-7.6F,-3.7F,9.8F,1.1F,7.4F);b(head,"hat_buckle","metal",-1,-7.8F,-4.4F,2,1.4F,1);
        for(int i=0;i<3;i++)b(head,"cap_repair_stitch"+i,"wrap",2.5F+i*.5F,-9+i*.3F,-3.8F,.4F,1,.5F);
        for(int side:new int[]{-1,1}){
            String n=side<0?"right":"left";var arm=pivot(r,n+"_arm",side*4,12,0,.12F,0,-side*.18F);
            b(arm,"puffed_sleeve","cloth",-1.8F,0,-1.8F,3.6F,5.5F,3.6F);b(arm,"cuff","leather",-1.9F,4,-2.1F,3.8F,1.7F,4);
            b(arm,"forearm","skin",-1.1F,5,-1.4F,2.2F,3.5F,2.8F);b(arm,"fist","skin",-1.5F,8,-2.5F,3,2.8F,3);
            for(int i=0;i<3;i++)b(arm,"knuckle"+i,"shadow_skin",-1.2F+i*.9F,8.5F,-3.1F,.7F,1.3F,1);
            if(side<0){rod(arm,"cleaver_grip","leather",0,8,-1,0,5,0,1);box(arm,"hooked_cleaver","iron",-1,10,-5.5F,1.3F,7,5,PartPose.rotation(.1F,0,-.1F));b(arm,"cleaver_edge","ivory",-.9F,10,-5.9F,1.1F,6.7F,.6F);b(arm,"blade_rivet","metal",-.9F,11,-4.5F,1.4F,.8F,.8F);}
            for(int i=0;i<3;i++)box(arm,"shoulder_scruff"+i,"fur",-2+i*1.4F,-.7F,1,1.5F,4+i%2,2,PartPose.rotation(.15F,0,(i-1)*.2F));
            var leg=pivot(r,n+"_leg",side*2,19,0,0,0,side*.05F);b(leg,"stocking","cloth",-1.2F,0,-1.2F,2.4F,3,2.4F);b(leg,"iron_boot","iron",-1.8F,2,-3,3.6F,3,5);b(leg,"boot_buckle","metal",-1,2.5F,-3.4F,2,1,.7F);
        }
    }
    private static void shard(PartDefinition p,String n,float x,float y,float z,float w,float h,float d,float rx,float rz){
        var a=box(p,n,"crystal",-w/2,-h*.7F,-d/2,w,h*.72F,d,PartPose.offsetAndRotation(x,y,z,rx,0,rz));
        b(a,n+"_facet","crystal",-w*.34F,-h*.92F,-d*.34F,w*.68F,h*.26F,d*.68F);
        b(a,n+"_tip","core",-w*.14F,-h,-d*.14F,w*.28F,h*.12F,d*.28F);
        if(w>=3)b(a,n+"_black_fissure","taint",-.3F,-h*.64F,-d/2-.2F,.6F,h*.5F,.45F);
    }
    private static void coreCage(PartDefinition p,float y,float z,float radius){
        b(p,"core_socket","void",-radius,y-radius,z+1,radius*2,radius*2,2);
        box(p,"corrupted_core","core",-2,-2,-1.5F,4,4,3,PartPose.offsetAndRotation(0,y,z,0,0,.785F));
        for(int i=0;i<8;i++){
            float a=(float)(i*Math.PI/4),xx=Mth.cos(a)*radius,yy=y+Mth.sin(a)*radius;
            box(p,"core_cage_segment"+i,"obsidian",-1.6F,-.6F,-.8F,3.2F,1.2F,1.6F,PartPose.offsetAndRotation(xx,yy,z-.3F,0,0,a+1.57F));
        }
    }
    private static void crystalColossus(PartDefinition r){
        var body=pivot(r,"body",0,-5,1,.1F,0,0);b(body,"obsidian_backbone","obsidian",-5,-18,1,10,25,9);
        box(body,"upper_mantle","obsidian",-9,-21,-3,18,10,12,PartPose.rotation(.15F,0,0));coreCage(body,-8,-6,5);
        for(int side:new int[]{-1,1}){
            box(body,"split_chest_plate"+side,"crystal",side<0?-10:5,-17,-7,5,14,5,PartPose.rotation(0,0,side*.15F));
            for(int j=0;j<3;j++)shard(body,"shoulder_cluster"+side+j,side*(9+j*2),-15,1+j*2,4-j*.6F,9+j*3,4,.15F,side*(.2F+j*.14F));
            box(body,"hip_shield"+side,"crystal",side<0?-8:2,4,-4,6,9,8,PartPose.rotation(0,0,-side*.18F));
            for(int j=0;j<3;j++)rod(body,"corruption_tendril"+side+j,"taint",side*7,-12+j*3,-7,side*2,5,-1,.7F);
        }
        b(body,"waist_lattice","obsidian",-4,2,-2,8,6,7);b(body,"belt_fracture","core",-3,4,-3,6,.8F,1);
        var head=pivot(r,"head",0,-24,-2,.08F,0,-.04F);b(head,"faceted_head","obsidian",-3.7F,-7,-3.4F,7.4F,7,7);
        for(int side:new int[]{-1,1}){box(head,"face_crystal_plane"+side,"crystal",side<0?-4.4F:.6F,-7,-4,3.8F,7,3,PartPose.rotation(0,0,side*.12F));b(head,"eye_fissure"+side,"core",side<0?-3.3F:1.5F,-4.7F,-4.5F,1.8F,.8F,.8F);shard(head,"crown_splinter"+side,side*2.5F,-6,1,2,5,2,.1F,side*.2F);}
        b(head,"black_face_cleft","taint",-.5F,-7.2F,-4.7F,1,6,1);b(head,"inset_jaw","obsidian",-2.5F,-.7F,-4,5,2,4);
        for(int side:new int[]{-1,1}){
            String n=side<0?"right":"left";var arm=pivot(r,n+"_arm",side*12,-17,1,.06F,0,-side*.13F);
            b(arm,"armature","obsidian",-3,0,-3,6,24,6);shard(arm,"upper_arm_prism",0,10,0,8,14,8,-.06F,side*.05F);
            b(arm,"elbow_core","core",-1.5F,12,-3.6F,3,2,1);shard(arm,"heavy_forearm",0,26,-1,side<0?10:8,13,9,.1F,-side*.08F);
            b(arm,"obsidian_fist","obsidian",-4,25,-5,8,5,9);
            for(int j=0;j<4;j++)shard(arm,"crystal_knuckle"+j,-3+j*2,27,-5.5F,1.7F,4,2,.2F,0);
            if(side<0)for(int j=0;j<3;j++)shard(arm,"hammer_growth"+j,-4+j*4,22,2,3.5F,9+j%2*2,4,.35F,-.15F+j*.15F);
            var leg=pivot(r,n+"_leg",side*5.5F,8,1,-.05F,0,side*.045F);b(leg,"leg_frame","obsidian",-2.8F,0,-2.8F,5.6F,16,5.6F);
            shard(leg,"crystal_greave",0,13,-.5F,7,12,7,-.04F,0);b(leg,"massive_foot","obsidian",-4,13,-7,8,3,11);
            for(int j=0;j<3;j++)box(leg,"crystal_toe"+j,"crystal",-3.2F+j*2.3F,14,-8.5F,1.9F,2,4,PartPose.rotation(.2F,0,0));
        }
        for(int j=0;j<5;j++)shard(body,"spinal_crystal"+j,0,-17+j*5,8,3,7,3,.5F,0);
    }
    private static void shardReaver(PartDefinition r){
        var body=pivot(r,"body",0,-3,1,.17F,0,0);b(body,"spinal_armature","obsidian",-2.5F,-12,0,5,23,5);coreCage(body,-6,-3.5F,3.4F);
        for(int side:new int[]{-1,1}){
            for(int i=0;i<3;i++)box(body,"overlapping_rib_blade"+side+i,"crystal",-1.7F,-4,-1.5F,3.4F,7,3,PartPose.offsetAndRotation(side*(4-i*.6F),-8+i*5,-2,.12F,side*.2F,side*.45F));
            shard(body,"shoulder_scythe"+side,side*7,-9,1,3.5F,14,4,.1F,side*.45F);
        }
        b(body,"narrow_pelvis","obsidian",-3,8,-2,6,4,5);
        var head=pivot(r,"head",0,-17,-4,.18F,0,0);box(head,"blade_mask","crystal",-2.6F,-7,-2.5F,5.2F,8,5,PartPose.rotation(.15F,0,0));
        b(head,"featureless_dark_face","taint",-2,-5.5F,-3.4F,4,5,1.5F);b(head,"vertical_eye","core",-.5F,-5,-4.2F,1,3.5F,1);
        for(int i=0;i<3;i++)shard(head,"swept_crest"+i,-2+i*2,-5,1,1.7F,6+i%2*3,2,-.35F,(i-1)*.15F);
        for(int side:new int[]{-1,1}){
            String n=side<0?"right":"left";var arm=pivot(r,n+"_arm",side*7,-9,0,.2F,0,-side*.15F);rod(arm,"upper_arm","obsidian",0,0,0,side,11,0,2.5F);
            b(arm,"elbow_hinge","core",side-1.3F,10,-1.3F,2.6F,2.6F,2.6F);
            var blade=pivot(arm,"serrated_forearm",side,12,-1,-.25F,0,-side*.17F);
            for(int j=0;j<6;j++)b(blade,"tapered_blade"+j,"crystal",-3+j*.4F,j*2.5F,-1.5F,6-j*.8F,3,3);
            rod(blade,"black_blade_vein","taint",0,1,-1.7F,0,12,0,.65F);
            for(int j=0;j<3;j++)shard(blade,"serration"+j,side*2,3+j*4,0,1.3F,4,1.5F,.2F,side*.7F);
            var leg=pivot(r,n+"_leg",side*3.7F,9,1,-.3F,0,side*.08F);
            rod(leg,"upper_leg","obsidian",0,0,0,0,6,1,2.5F);shard(leg,"thigh_shard",0,6,0,4,7,4,0,0);
            rod(leg,"reverse_shin","obsidian",0,6,1,0,7,-3,1.9F);shard(leg,"shin_blade",0,12,-1,3,8,3,.2F,0);
            b(leg,"clawed_foot","obsidian",-2,12,-5,4,3,7);for(int j=0;j<2;j++)rod(leg,"shard_talon"+j,"crystal",-1.2F+j*2.4F,14,-3,0,0,-4,.9F);
        }
    }
    private static void prismWarden(PartDefinition r){
        var body=pivot(r,"body",0,0,0,0,0,0);b(body,"hollow_obelisk_back","obsidian",-4,-8,1,8,22,6);coreCage(body,0,-4,4.5F);
        for(int side:new int[]{-1,1}){
            shard(body,"obelisk_side"+side,side*5,8,0,3,20,6,0,side*.12F);
            for(int i=0;i<4;i++)rod(body,"binding_lattice"+side+i,"taint",side*3,-6+i*4,-4,side*2,2,0,.7F);
        }
        b(body,"lower_hex_core","core",-1.5F,9,-3.5F,3,3,2);b(body,"splayed_base","obsidian",-5,12,-3,10,4,7);
        var head=pivot(r,"head",0,-12,0,.08F,0,0);b(head,"warden_mask","obsidian",-3,-6,-3,6,7,6);b(head,"mask_eye","core",-2,-4.5F,-3.7F,4,1,1);
        shard(head,"faceted_brow",0,-5,-1,5.5F,4,4,0,0);var orbit=pivot(head,"orbit",0,-4,0,0,0,0);
        for(int i=0;i<7;i++){float a=(float)(i*Math.PI*2/7);shard(orbit,"floating_crown_shard"+i,Mth.sin(a)*6,-2,Mth.cos(a)*6,1.8F,6+i%2*2,2,0,Mth.sin(a)*.3F);}
        for(int side:new int[]{-1,1}){
            String n=side<0?"right":"left";var arm=pivot(r,n+"_arm",side*6,-4,0,.1F,0,-side*.25F);rod(arm,"armature","obsidian",0,0,0,0,13,0,2);
            shard(arm,"forearm_prism",0,14,-1,4,9,4,.1F,0);
            for(int j=0;j<2;j++)shard(arm,"tuning_fork"+j,-2+j*4,16,-1,1.4F,9,1.5F,0,(j==0?-.2F:.2F));
            for(int rear=0;rear<2;rear++){
                var leg=pivot(r,(rear==1?"rear_":"")+n+"_leg",side*4,15,rear==1?4:-2,0,0,-side*.22F);
                rod(leg,"root_strut","obsidian",0,0,0,side*2,7,rear==1?3:-3,2.2F);shard(leg,"root_prism",side,6,0,3.5F,8,4,.15F,0);
                b(leg,"prism_foot","crystal",side*2-2,7,rear==1?1:-5,4,2,5);
            }
        }
    }
    private static void arthropodLeg(PartDefinition r,String n,int side,float y,float z,float spread,String material){
        var a=pivot(r,n,side*2.5F,y,z,0,0,0);rod(a,"coxa",material,0,0,0,side*spread,-2,0,1);
        rod(a,"jointed_tibia",material,side*spread,-2,0,side*1.4F,24-y+1,-1,.65F);rod(a,"hooked_tarsus","bone",side*(spread+1.4F),23-y,-1,-side*.8F,1,-1,.4F);
    }
    private static void marrowTick(PartDefinition r){
        var body=pivot(r,"body",0,19,2,0,0,0);b(body,"swollen_abdomen","skin",-3.8F,-3,-1,7.6F,6,10);
        box(body,"dorsal_shield","chitin",-4,-4,-2,8,3,10,PartPose.rotation(.1F,0,0));
        for(int i=0;i<5;i++){b(body,"shell_ridge"+i,"bone",-3.5F,-4.3F,-1+i*2,7,.8F,.9F);b(body,"swollen_spiracle"+i,"sinew",3.3F,-1,-1+i*2,1.2F,1.3F,1.3F);}
        for(int side:new int[]{-1,1})for(int i=0;i<4;i++)horn(body,"carapace_barb"+side+i,"bone",side*3,-3,i*2,side,2.2F);
        var head=pivot(r,"head",0,18,-3,.1F,0,0);b(head,"armored_head","chitin",-2.7F,-2.2F,-2.3F,5.4F,4.4F,4.6F);b(head,"feeding_orifice","void",-1.8F,-.8F,-2.8F,3.6F,2,.8F);
        for(int side:new int[]{-1,1}){
            for(int i=0;i<3;i++)b(head,"eye_cluster"+side+i,"eye",side*(1.6F+i*.2F)-.35F,-1.5F+i*.8F,-2.8F,.7F,.6F,.65F);
            rod(head,"mandible_base"+side,"bone",side*2,.5F,-2,side,1,-2,.8F);rod(head,"mandible_hook"+side,"bone",side*3,1.5F,-4,-side*1.4F,0,-1.5F,.5F);
            for(int i=0;i<3;i++)rod(head,"sensory_bristle"+side+i,"hair",side*2,-1,-1+i,side*2,-1,-2,.25F);
            for(int i=0;i<4;i++)arthropodLeg(r,i==0?(side<0?"right_arm":"left_arm"):(i==2?"middle_":i==3?"rear_":"")+(side<0?"right_leg":"left_leg"),side,19,-3+i*3,3+i%2,"chitin");
        }
        rod(head,"feeding_needle","bone",0,.7F,-2.5F,0,0,-4,.55F);
    }
    private static void ribBurrower(PartDefinition r){
        var body=pivot(r,"body",0,17,1,0,0,0);
        for(int i=0;i<7;i++){
            var seg=pivot(body,"segment"+i,0,0,-8+i*3.3F,0,0,0);b(seg,"pale_body","skin",-3.1F,-2.5F,-1.7F,6.2F,5,3.4F);
            box(seg,"rib_carapace","bone",-3.8F,-3.4F,-1.5F,7.6F,2,3,PartPose.rotation(.1F,0,0));
            for(int side:new int[]{-1,1}){
                box(seg,"clasping_rib"+side,"bone",side<0?-4:2.8F,-2.4F,-1.3F,1.2F,5,2.6F,PartPose.rotation(0,0,side*.15F));
                var leg=pivot(seg,"scuttling_leg"+side,side*3,1,0,0,0,-side*.15F);rod(leg,"leg_upper","chitin",0,0,0,side*4,0,-1,.9F);rod(leg,"leg_lower","bone",side*4,0,-1,side*1.2F,6,-1,.65F);
            }
            if(i%2==0)horn(seg,"dorsal_spine","bone",0,-3,0,0,3.5F);
        }
        var head=pivot(r,"head",0,17,-11,.06F,0,0);b(head,"bone_drill_head","bone",-4,-4,-3,8,7,6);b(head,"black_mouth","void",-2.7F,-1.8F,-3.4F,5.4F,4,.9F);
        for(int side:new int[]{-1,1}){
            b(head,"vestigial_eye"+side,"eye",side<0?-3:-.1F,-3,-3.8F,1.4F,.8F,.65F);
            rod(head,"drilling_mandible"+side,"bone",side*3,1,-3,side*2,2,-3,1.5F);rod(head,"mandible_tip"+side,"bone",side*5,3,-6,-side*2,-1,-2,1);
            for(int i=0;i<3;i++)tooth(head,"rasping_fang"+side+i,side*(1+i*.6F),-.5F,-4,1.5F,true);
        }
        var tail=pivot(r,"tail",0,17,16,.15F,0,0);rod(tail,"tail_hook","chitin",0,0,0,0,-2,6,1.6F);rod(tail,"tail_needle","bone",0,-2,6,0,-3,2,.8F);
    }
    private static void sinewLeech(PartDefinition r){
        var body=pivot(r,"body",0,19,0,0,0,0);
        for(int i=0;i<8;i++){
            float w=7-Math.abs(i-3.5F)*.6F;var seg=pivot(body,"segment"+i,0,0,-9+i*3.4F,0,0,0);
            b(seg,"muscular_lobe","maggot",-w/2,-3,-1.8F,w,6,3.6F);b(seg,"annular_sinew","sinew",-w/2-.2F,-3.2F,-1.2F,w+.4F,6.4F,.8F);
            for(int side:new int[]{-1,1}){b(seg,"breathing_pore"+side,"void",side*(w/2)-.4F,-.5F,-.5F,.8F,1,1);if(i%2==0)rod(seg,"grasping_tendril"+side,"sinew",side*w/2,1,0,side*3,3,-2,.8F);}
        }
        var head=pivot(r,"head",0,18,-12,.1F,0,0);b(head,"leech_maw_cavity","void",-3.6F,-3.6F,-3,7.2F,7.2F,3);
        for(int i=0;i<8;i++){
            float a=(float)(i*Math.PI/4),x=Mth.cos(a)*3.6F,y=Mth.sin(a)*3.6F;
            box(head,"maw_lip"+i,"maggot",-1.6F,-.9F,-1.5F,3.2F,1.8F,3,PartPose.offsetAndRotation(x,y,-2,0,0,a+1.57F));
            rod(head,"radial_tooth"+i,"bone",x*.8F,y*.8F,-3,-x*.4F,-y*.4F,-1.8F,.6F);
        }
        b(head,"inner_throat","sinew",-1.5F,-1.5F,-2.5F,3,3,1);rod(head,"proboscis","sinew",0,0,-3,0,0,-4,.8F);
        var tail=pivot(r,"tail",0,19,17,0,0,0);for(int side:new int[]{-1,1})rod(tail,"tail_fluke"+side,"maggot",0,0,0,side*3,-2,6,1.3F);
    }
    private static void parasiteMaw(PartDefinition r){
        var body=pivot(r,"body",0,14,4,0,0,0);b(body,"bloated_abdomen","maggot",-8,-10,-4,16,17,24);
        box(body,"upper_bloat_sac","maggot",-6,-13,1,12,7,17,PartPose.rotation(.07F,0,0));b(body,"diseased_dorsal_sac","sinew",-4,-16,8,8,5,8);
        for(int i=0;i<6;i++){
            for(int side:new int[]{-1,1}){
                box(body,"fleshy_fold"+side+i,"maggot",side<0?-8.8F:5.3F,-8,-3+i*4,3.5F,13,2.8F,PartPose.rotation(0,0,side*.12F));
                b(body,"black_spiracle"+side+i,"void",side<0?-9.1F:8.3F,-1,-2+i*4,.8F,1.6F,1.7F);
                if(i%2==0)b(body,"inflamed_gland"+side+i,"fungus",side<0?-8.8F:6.3F,-10,-1+i*4,2.5F,3,3);
            }
            b(body,"segment_saddle"+i,"sinew",-5,-11.6F,-2+i*4,10,1.2F,.9F);
        }
        var head=pivot(r,"head",0,11,-9,.12F,0,0);b(head,"massive_black_maw","void",-5.7F,-7,-5,11.4F,12,4);
        for(int i=0;i<10;i++){
            float a=(float)(i*Math.PI/5),x=Mth.cos(a)*6,y=-1+Mth.sin(a)*6;
            box(head,"bloated_mouth_lobe"+i,"maggot",-2,-1.7F,-2,4,3.4F,4,PartPose.offsetAndRotation(x,y,-4,0,0,a+1.57F));
            rod(head,"maw_hook"+i,"bone",x*.8F,-1+(y+1)*.8F,-5,-x*.35F,-(y+1)*.35F,-2.3F,.8F);
            rod(head,"facial_bristle"+i,"hair",x*1.15F,-1+(y+1)*1.1F,-3,x*.3F,(y+1)*.3F,-1,.3F);
        }
        b(head,"throat_tissue","sinew",-3,-4,-3.8F,6,6,1.5F);b(head,"throat_inner_void","void",-1.3F,-2.4F,-4.5F,2.6F,2.8F,.8F);
        for(int side:new int[]{-1,1}){
            rod(head,"giant_feeding_hook"+side,"chitin",side*5,3,-5,side*2,2,-3,1.8F);rod(head,"feeding_hook_point"+side,"bone",side*7,5,-8,-side*3,-1,-1,1);
            for(int i=0;i<3;i++)b(head,"sensory_nodule"+side+i,"sinew",side<0?-7:5.4F,-6+i*2,-1,1.6F,1.4F,2);
            for(int pair=0;pair<3;pair++){
                var leg=pivot(r,pair==0?(side<0?"right_arm":"left_arm"):(pair==2?"rear_":"")+(side<0?"right_leg":"left_leg"),side*6.5F,19,-4+pair*9,0,0,-side*.2F);
                b(leg,"fleshy_proleg","maggot",-1.7F,0,-1.8F,3.4F,4,3.6F);b(leg,"gripping_pad","chitin",-2.1F,3,-2.7F,4.2F,2,5);for(int j=0;j<3;j++)rod(leg,"proleg_hook"+j,"bone",-1.4F+j*1.4F,4,-2,0,0,-1.8F,.45F);
            }
            var wing=pivot(r,side<0?"wing_right":"wing_left",side*6,3,10,.2F,side*.55F,0);
            for(int i=0;i<5;i++)box(wing,"vestigial_fly_wing"+i,"membrane",side<0?-2-i*2:i*2,-4+i*.8F,0,2.2F,10-i,.45F,PartPose.rotation(0,0,side*.16F));
            for(int i=0;i<3;i++)rod(wing,"wing_vein"+i,"chitin",0,0,0,side*(4+i*2),5-i,0,.4F);
        }
        var tail=pivot(r,"tail",0,16,24,.1F,0,0);for(int side:new int[]{-1,1})rod(tail,"respiratory_tube"+side,"sinew",side*2,0,0,side,-2,4,1.2F);
    }
    @Override public void setupAnim(MonstrosityEntity mob,float walk,float amount,float age,float yaw,float pitch){
        root.getAllParts().forEach(ModelPart::resetPose);var head=root.getChild("head");head.yRot+=yaw*Mth.DEG_TO_RAD;head.xRot+=pitch*Mth.DEG_TO_RAD*.6F;
        float attack=mob==null?0:mob.attackMotion(0),step=Mth.cos(walk*.65F)*amount;
        for(int side:new int[]{-1,1}){
            String n=side<0?"right":"left";root.getChild(n+"_leg").xRot+=step*side*.65F;root.getChild("rear_"+n+"_leg").xRot-=step*side*.65F;root.getChild("middle_"+n+"_leg").xRot-=step*side*.5F;
            var arm=root.getChild(n+"_arm");arm.xRot+=-step*side*.32F-attack*(kind==MonstrosityKind.TROLL||kind==MonstrosityKind.CYCLOPS?1.2F:1.3F);
            if(kind==MonstrosityKind.INFESTOR){arm.zRot=-side*(1.05F-attack*.8F+Mth.sin(age*.06F)*.08F);arm.xRot=-attack*1.45F;var middle=arm.getChild("whip_middle");middle.zRot=side*(.6F-attack*.7F);middle.getChild("whip_tip").zRot=side*(.8F-attack*.8F);}
            if(kind==MonstrosityKind.HAG)arm.xRot-=attack*.3F;
            root.getChild(side<0?"wing_right":"wing_left").yRot+=side*(.15F+attack*.25F+(mob!=null&&!mob.onGround()?.2F:0));
        }
        if(kind==MonstrosityKind.PRISM_WARDEN)head.getChild("orbit").yRot+=age*.018F;
        if(kind==MonstrosityKind.RIB_BURROWER||kind==MonstrosityKind.SINEW_LEECH){
            var body=root.getChild("body");int segments=kind==MonstrosityKind.RIB_BURROWER?7:8;
            for(int i=0;i<segments;i++){
                var seg=body.getChild("segment"+i);seg.yRot+=Mth.sin(walk*.7F-i*.6F)*amount*.12F;
                if(kind==MonstrosityKind.RIB_BURROWER)for(int side:new int[]{-1,1})seg.getChild("scuttling_leg"+side).zRot+=Mth.sin(walk*.8F-i*.9F)*amount*side*.25F;
            }
        }
        root.getChild("tail").yRot+=Mth.sin(age*.08F)*.15F;root.getChild("body").xRot+=Mth.sin(age*.045F)*.012F;
    }
}
