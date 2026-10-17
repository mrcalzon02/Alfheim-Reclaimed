package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.gem.*;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.blockentity.*;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.world.item.ItemDisplayContext;

public final class GemDisplayRenderer implements BlockEntityRenderer<GemDisplayBlockEntity> {
    public GemDisplayRenderer(BlockEntityRendererProvider.Context context){}
    @Override public void render(GemDisplayBlockEntity display,float partial,PoseStack pose,MultiBufferSource buffers,int light,int overlay){
        if(display.sample().isEmpty())return;var mc=Minecraft.getInstance();
        pose.pushPose();pose.translate(.5,1.19,.5);pose.mulPose(Axis.YP.rotationDegrees(((display.getLevel().getGameTime()+partial)*.65F)%360));pose.scale(.52F,.52F,.52F);
        mc.getItemRenderer().renderStatic(display.sample(),ItemDisplayContext.FIXED,light,OverlayTexture.NO_OVERLAY,pose,buffers,display.getLevel(),0);pose.popPose();
        if(mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(display.getBlockPos().getCenter())>64)return;
        var label=display.label();float scale=Math.min(.005F,.68F/Math.max(1,mc.font.width(label)));
        pose.pushPose();pose.translate(.5,.62,.5);pose.mulPose(Axis.YP.rotationDegrees(-display.getBlockState().getValue(GemDisplayBlock.FACING).toYRot()));pose.translate(0,0,.441);pose.scale(scale,-scale,scale);
        mc.font.drawInBatch(label,-mc.font.width(label)/2F,0,0xFF292522,false,pose.last().pose(),buffers,Font.DisplayMode.NORMAL,0,light);pose.popPose();
    }
}
