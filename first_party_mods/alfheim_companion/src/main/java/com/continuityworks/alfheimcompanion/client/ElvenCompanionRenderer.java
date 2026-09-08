package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.resources.DefaultPlayerSkin;
import net.minecraft.resources.ResourceLocation;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.client.renderer.entity.ItemRenderer;

public final class ElvenCompanionRenderer
        extends MobRenderer<ElvenCompanionEntity, PlayerModel<ElvenCompanionEntity>> {
    private final ItemRenderer statusItemRenderer;

    public ElvenCompanionRenderer(EntityRendererProvider.Context context) {
        super(context, new PlayerModel<>(context.bakeLayer(ModelLayers.PLAYER), false), 0.45F);
        this.statusItemRenderer = context.getItemRenderer();
    }

    @Override
    public ResourceLocation getTextureLocation(ElvenCompanionEntity entity) {
        return DefaultPlayerSkin.getDefaultSkin(entity.getUUID());
    }

    @Override
    public void render(ElvenCompanionEntity entity, float entityYaw, float partialTick,
                       PoseStack pose, MultiBufferSource buffers, int packedLight) {
        super.render(entity, entityYaw, partialTick, pose, buffers, packedLight);
        // Physical needs take visual priority over the current order so the player can react.
        ItemStack status;
        if (entity.nutrition() <= 4) {
            status = new ItemStack(Items.APPLE);
        } else if (entity.stamina() <= 10) {
            status = new ItemStack(Items.RED_BED);
        } else {
            status = switch (entity.mode()) {
                case FOLLOWING -> new ItemStack(Items.COMPASS);
                case WAITING -> new ItemStack(Items.CLOCK);
                case GUARDING -> new ItemStack(Items.SHIELD);
                case DEFENDING -> new ItemStack(Items.IRON_SWORD);
                case RETREATING -> new ItemStack(Items.LEATHER_BOOTS);
                case WORKING -> new ItemStack(Items.CRAFTING_TABLE);
                case DISMISSED -> ItemStack.EMPTY;
            };
        }
        if (status.isEmpty() || entity.distanceToSqr(entityRenderDispatcher.camera.getPosition()) > 1024.0D) return;

        pose.pushPose();
        pose.translate(0.0D, entity.getBbHeight() + 0.75D, 0.0D);
        pose.mulPose(entityRenderDispatcher.cameraOrientation());
        pose.scale(0.42F, -0.42F, 0.42F);
        statusItemRenderer.renderStatic(status, ItemDisplayContext.GUI, packedLight, OverlayTexture.NO_OVERLAY,
                pose, buffers, entity.level(), entity.getId());
        pose.popPose();
    }
}
