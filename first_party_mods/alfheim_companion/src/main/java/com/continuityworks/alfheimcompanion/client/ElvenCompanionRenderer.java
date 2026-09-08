package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.resources.DefaultPlayerSkin;
import net.minecraft.resources.ResourceLocation;

public final class ElvenCompanionRenderer
        extends MobRenderer<ElvenCompanionEntity, PlayerModel<ElvenCompanionEntity>> {

    public ElvenCompanionRenderer(EntityRendererProvider.Context context) {
        super(context, new PlayerModel<>(context.bakeLayer(ModelLayers.PLAYER), false), 0.45F);
    }

    @Override
    public ResourceLocation getTextureLocation(ElvenCompanionEntity entity) {
        return DefaultPlayerSkin.getDefaultSkin(entity.getUUID());
    }
}
