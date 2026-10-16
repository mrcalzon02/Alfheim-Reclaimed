package com.continuityworks.alfheimcompanion.client;

import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;

/** One authored elven skeleton: a narrow skull, angled ears and an open rib cage. */
public final class SilverbarkBoneguardModel {
    public static final ModelLayerLocation LAYER=new ModelLayerLocation(new ResourceLocation("alfheim_companion","silverbark_boneguard"),"main");
    public static LayerDefinition layer() {
        MeshDefinition mesh=HumanoidModel.createMesh(CubeDeformation.NONE,0);
        PartDefinition root=mesh.getRoot();
        var head=root.addOrReplaceChild("head",CubeListBuilder.create().texOffs(0,0)
            .addBox(-3,-9,-3,6,9,6),PartPose.ZERO);
        head.addOrReplaceChild("left_ear",CubeListBuilder.create().texOffs(32,0)
            .addBox(0,-3,-.5F,2,3,1),PartPose.offsetAndRotation(3,-5,0,0,0,-.35F));
        head.addOrReplaceChild("right_ear",CubeListBuilder.create().texOffs(32,0).mirror()
            .addBox(-2,-3,-.5F,2,3,1),PartPose.offsetAndRotation(-3,-5,0,0,0,.35F));
        root.addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
        var body=root.addOrReplaceChild("body",CubeListBuilder.create().texOffs(24,16)
            .addBox(-.75F,0,-.75F,1.5F,11,1.5F),PartPose.ZERO);
        for(int i=0;i<3;i++)body.addOrReplaceChild("rib"+i,CubeListBuilder.create().texOffs(0,32)
            .addBox(-3,1+i*3,-1.5F,6,1,3),PartPose.ZERO);
        body.addOrReplaceChild("pelvis",CubeListBuilder.create().texOffs(16,32)
            .addBox(-2.5F,10,-1.5F,5,2,3),PartPose.ZERO);
        root.addOrReplaceChild("right_arm",CubeListBuilder.create().texOffs(40,16)
            .addBox(-1,-2,-1,2,13,2),PartPose.offset(-5,2,0));
        root.addOrReplaceChild("left_arm",CubeListBuilder.create().texOffs(40,16).mirror()
            .addBox(-1,-2,-1,2,13,2),PartPose.offset(5,2,0));
        root.addOrReplaceChild("right_leg",CubeListBuilder.create().texOffs(0,16)
            .addBox(-1,0,-1,2,12,2),PartPose.offset(-1.8F,12,0));
        root.addOrReplaceChild("left_leg",CubeListBuilder.create().texOffs(0,16).mirror()
            .addBox(-1,0,-1,2,12,2),PartPose.offset(1.8F,12,0));
        return LayerDefinition.create(mesh,64,64);
    }
    private SilverbarkBoneguardModel() {}
}
