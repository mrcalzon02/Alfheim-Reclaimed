package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.monstrosity.MonstrosityEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;

/** Only the actual core UV islands emit; the surrounding crystal still receives world light. */
final class MonstrosityGlowLayer extends RenderLayer<MonstrosityEntity,MonstrosityModel> {
    MonstrosityGlowLayer(RenderLayerParent<MonstrosityEntity,MonstrosityModel> parent){super(parent);}
    @Override public void render(PoseStack poses,MultiBufferSource buffers,int light,MonstrosityEntity mob,float walk,float amount,float partial,float age,float yaw,float pitch){
        if(!mob.kind.crystal()||mob.isInvisible())return;
        var texture=new ResourceLocation("alfheim_companion","textures/entity/monstrosities/"+mob.kind.id+"_"+mob.variant()+"_glow.png");
        getParentModel().renderToBuffer(poses,buffers.getBuffer(RenderType.eyes(texture)),15728640,OverlayTexture.NO_OVERLAY,1,1,1,1);
    }
}
