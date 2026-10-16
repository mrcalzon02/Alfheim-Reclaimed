package com.continuityworks.alfheimcompanion.client;

import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;

/** A low marsh arthropod; four native segments retain the mite's curling motion. */
public final class MireRiftmiteModel {
    public static final ModelLayerLocation LAYER=new ModelLayerLocation(new ResourceLocation("alfheim_companion","mire_riftmite"),"main");
    public static LayerDefinition layer() {
        var root=new MeshDefinition();var parts=root.getRoot();
        var head=parts.addOrReplaceChild("segment0",CubeListBuilder.create().texOffs(0,0)
            .addBox(-2.5F,-1.5F,-1.5F,5,3,3),PartPose.offset(0,22,-5));
        for(int side:new int[]{-1,1})head.addOrReplaceChild("mandible"+side,CubeListBuilder.create().texOffs(40,0)
            .addBox(-.5F,0,-2,1,1,2),PartPose.offsetAndRotation(side*1.4F,.5F,-1,0,side*.25F,0));
        parts.addOrReplaceChild("segment1",CubeListBuilder.create().texOffs(0,8)
            .addBox(-3,-2,-2,6,4,4),PartPose.offset(0,21.5F,-1.5F));
        parts.addOrReplaceChild("segment2",CubeListBuilder.create().texOffs(24,8)
            .addBox(-2,-1.5F,-1.5F,4,3,3),PartPose.offset(0,22,2));
        parts.addOrReplaceChild("segment3",CubeListBuilder.create().texOffs(24,16)
            .addBox(-1,-1,-1,2,2,2),PartPose.offset(0,23,4.5F));
        for(int segment=1;segment<=2;segment++)for(int side:new int[]{-1,1}) {
            float width=segment==1?3:2;
            parts.getChild("segment"+segment).addOrReplaceChild("leg"+side,CubeListBuilder.create().texOffs(40,8)
                .addBox(side<0?-2:0,0,-.5F,2,.75F,1),PartPose.offsetAndRotation(side*width,1.5F,0,0,0,side*.25F));
        }
        return LayerDefinition.create(root,64,32);
    }
    private MireRiftmiteModel() {}
}
