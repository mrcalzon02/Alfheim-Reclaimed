package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.society.*;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.*;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;

public final class ElvenCitizenRenderer extends MobRenderer<ElvenCitizenEntity,PlayerModel<ElvenCitizenEntity>> {
    private final java.util.List<HumanoidModel<ElvenCitizenEntity>> wardrobes=new java.util.ArrayList<>();
    public ElvenCitizenRenderer(EntityRendererProvider.Context context){
        super(context,new PlayerModel<>(context.bakeLayer(ElvenSocietyModels.location(0)),true),.4F);
        for(int i=0;i<ElvenSociety.IDS.length;i++)wardrobes.add(new HumanoidModel<>(context.bakeLayer(ElvenSocietyModels.wardrobeLocation(i))));
        addLayer(new RenderLayer<ElvenCitizenEntity,PlayerModel<ElvenCitizenEntity>>(this){
            @Override public void render(PoseStack pose,MultiBufferSource buffers,int light,ElvenCitizenEntity elf,float swing,float amount,float tick,float age,float yaw,float pitch){
                if(elf.isInvisible())return;
                String id=ElvenSociety.IDS[elf.role()]+"_"+elf.appearance();
                var wardrobe=wardrobes.get(elf.role());getParentModel().copyPropertiesTo(wardrobe);
                wardrobe.renderToBuffer(pose,buffers.getBuffer(RenderType.entityCutoutNoCull(new ResourceLocation(
                    "alfheim_companion","textures/entity/society/wardrobe/"+id+".png"))),light,OverlayTexture.NO_OVERLAY,1,1,1,1);
            }
        });
    }
    @Override public ResourceLocation getTextureLocation(ElvenCitizenEntity elf){
        String[] path=ElvenSociety.baseSkin(elf.role(),elf.appearance()).split(":");
        return new ResourceLocation(path[0],"textures/"+path[1]+".png");
    }
    public static void itemProperties(){
        net.minecraft.client.renderer.item.ItemProperties.register(
            com.continuityworks.alfheimcompanion.registry.ModItems.ELVEN_CITIZEN_SPAWN_EGG.get(),
            new ResourceLocation("alfheim_companion","social_appearance"),(stack,world,entity,seed)->ElvenSociety.modelKey(stack));
    }
}
