package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.monstrosity.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;

public final class MonstrosityRenderer extends MobRenderer<MonstrosityEntity,MonstrosityModel> {
    public MonstrosityRenderer(EntityRendererProvider.Context context,MonstrosityKind kind){super(context,new MonstrosityModel(context.bakeLayer(MonstrosityModel.location(kind)),kind),kind.width*.45F);}
    @Override public ResourceLocation getTextureLocation(MonstrosityEntity mob){return new ResourceLocation("alfheim_companion","textures/entity/monstrosities/"+mob.kind.id+"_"+mob.variant()+".png");}
}
