package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.society.ElvenSociety;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;

/** Exact installed wood-elf slim/layered rig; finery is an independent animated model layer. */
public final class ElvenSocietyModels {
    public static ModelLayerLocation location(int role){return new ModelLayerLocation(new ResourceLocation("alfheim_companion","society/"+ElvenSociety.IDS[role]),"main");}
    public static ModelLayerLocation wardrobeLocation(int role){return new ModelLayerLocation(new ResourceLocation("alfheim_companion","society/"+ElvenSociety.IDS[role]),"wardrobe");}
    public static LayerDefinition layer(int role){return LayerDefinition.create(PlayerModel.createMesh(CubeDeformation.NONE,true),64,64);}
    private static PartDefinition box(PartDefinition p,String n,int u,int v,float x,float y,float z,float w,float h,float d,PartPose pose){
        return p.addOrReplaceChild(n,CubeListBuilder.create().texOffs(u,v).addBox(x,y,z,w,h,d),pose);
    }
    public static LayerDefinition wardrobe(int role){
        var mesh=new MeshDefinition();var root=mesh.getRoot();
        for(String p:new String[]{"head","hat","body","right_arm","left_arm","right_leg","left_leg"})root.addOrReplaceChild(p,CubeListBuilder.create(),PartPose.ZERO);
        var head=root.getChild("head");var body=root.getChild("body");
        // In model space negative Y is up: each tip rises above its attachment.
        for(int side:new int[]{-1,1}){
            var ear=box(head,"ear"+side,112,64,side<0?-1.3F:0,-2.4F,-.35F,1.3F,2.4F,.7F,
                PartPose.offsetAndRotation(side*3.85F,-3.2F,0,0,0,side*.45F));
            box(ear,"point",112,72,side<0?-.95F:.3F,-3.4F,-.25F,.65F,1.1F,.5F,PartPose.ZERO);
        }
        if(role==0||role==2||role==4||role==6){
            box(head,"hat_brim",64,24,-4.7F,-8.25F,-4.7F,9.4F,.6F,9.4F,PartPose.ZERO);
            box(head,"hat_crown",64,40,-3.8F,-10.7F,-3.8F,7.6F,2.6F,7.6F,PartPose.ZERO);
            if(role>=4)box(head,"hat_fold",104,24,2.8F,-12,-1,1,3,2,PartPose.rotation(0,0,.2F));
        }
        if(role>=8){
            for(int side:new int[]{-1,1}){
                box(head,"crown_side"+side,64,0,side<0?-4.25F:3.65F,-8.3F,-4.25F,.6F,.9F,8.5F,PartPose.ZERO);
                box(head,"crown_cross"+side,64,0,-3.65F,-8.3F,side<0?-4.25F:3.65F,7.3F,.9F,.6F,PartPose.ZERO);
            }
            int points=role>=10?5:3;
            for(int i=0;i<points;i++)box(head,"crown_point"+i,104,0,-3+i*(6F/(points-1)),-9.6F,-4.2F,.7F,1.4F,.7F,PartPose.ZERO);
            box(head,"crown_jewel",116,0,-.55F,-8.55F,-4.45F,1.1F,.8F,.3F,PartPose.ZERO);
        }
        if(ElvenSociety.gown(role)){
            box(body,"skirt_hem",0,96,-6.4F,17,-3.5F,12.8F,4,7,PartPose.ZERO);
            for(int i=0;i<5;i++)box(body,"skirt_pleat"+i,32,64,-5.8F+i*2.6F,13,-3.65F,.8F,7,.65F,PartPose.ZERO);
            box(body,"skirt_core",0,0,-4.3F,10,-2.4F,8.6F,10,4.8F,PartPose.ZERO);
            box(body,"skirt_front",0,24,-5.1F,10,-3,10.2F,11,.6F,PartPose.rotation(.075F,0,0));
            box(body,"skirt_back",0,24,-5.1F,10,2.4F,10.2F,11,.6F,PartPose.rotation(-.075F,0,0));
            box(body,"skirt_left",32,24,3.8F,10,-2.5F,1.4F,11,5,PartPose.rotation(0,0,-.055F));
            box(body,"skirt_right",32,24,-5.2F,10,-2.5F,1.4F,11,5,PartPose.rotation(0,0,.055F));
        }else if(role>=4){
            box(body,"coat_left",0,24,-4.3F,8,-2.4F,3.6F,8,4.8F,PartPose.rotation(0,0,.035F));
            box(body,"coat_right",0,24,.7F,8,-2.4F,3.6F,8,4.8F,PartPose.rotation(0,0,-.035F));
        }else if(role==1||role==3)box(body,"apron",0,24,-3,3,-2.65F,6,12,.4F,PartPose.ZERO);
        if(role>=6){
            box(body,"cape_top",0,64,-5,1,2.7F,10,8,.5F,PartPose.ZERO);
            box(body,"cape_lower",0,80,-5.4F,8.8F,3.5F,10.8F,9,.6F,PartPose.rotation(-.06F,0,0));
            box(body,"clasp",116,0,-.65F,1,-2.4F,1.3F,1.3F,.4F,PartPose.ZERO);
        }
        if(role>=4){
            for(int side:new int[]{-1,1}){
                var arm=root.getChild(side<0?"right_arm":"left_arm");
                box(arm,"puffed_sleeve",32,0,-2,-1,-2.4F,4,4.4F,4.8F,PartPose.ZERO);
                box(arm,"ruffled_cuff",32,40,-1.9F,7.3F,-2.35F,3.8F,1.3F,4.7F,PartPose.ZERO);
            }
            box(body,"ruffled_collar",32,40,-3.8F,-.25F,-2.45F,7.6F,1,1,PartPose.ZERO);
            for(int i=0;i<6;i++)box(body,"collar_fold"+i,32,40,-3.6F+i*1.25F,.4F,-2.65F,.7F,.9F,.65F,PartPose.ZERO);
            for(int side:new int[]{-1,1})box(body,"embroidered_lapel"+side,32,24,side<0?-3.25F:1.65F,1,-2.65F,1.6F,5,.5F,PartPose.rotation(0,0,side*.14F));
        }
        return LayerDefinition.create(mesh,128,128);
    }
    private ElvenSocietyModels(){}
}
