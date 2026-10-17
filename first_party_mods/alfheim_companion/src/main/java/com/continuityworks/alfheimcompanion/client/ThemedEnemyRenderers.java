package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.enemy.ModThemedEnemies;
import net.minecraft.client.renderer.entity.*;
import net.minecraftforge.client.event.EntityRenderersEvent;

/** Keep vanilla animation, equipment, eye glow, held blocks and weapons. */
public final class ThemedEnemyRenderers {
    private static net.minecraft.resources.ResourceLocation skin(net.minecraft.world.entity.Mob mob,String species) {
        return new net.minecraft.resources.ResourceLocation("alfheim_companion","textures/entity/themed/"+species+"_"+
            com.continuityworks.alfheimcompanion.enemy.EnemyAppearance.profile(mob)+"_"+
            com.continuityworks.alfheimcompanion.enemy.EnemyAppearance.style(mob)+".png");
    }
    public static void register(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModThemedEnemies.ZOMBIE.get(),ctx->new ZombieRenderer(ctx) {
            private final net.minecraft.client.model.ZombieModel<net.minecraft.world.entity.monster.Zombie> normal=this.model;
            private final net.minecraft.client.model.ZombieModel<net.minecraft.world.entity.monster.Zombie> regional=
                new net.minecraft.client.model.ZombieModel<>(ctx.bakeLayer(RegionalMonstrosityModels.location("zombie")));
            @Override public void render(net.minecraft.world.entity.monster.Zombie mob,float yaw,float tick,
                    com.mojang.blaze3d.vertex.PoseStack pose,net.minecraft.client.renderer.MultiBufferSource buffers,int light) {
                this.model=RegionalMonstrosityModels.matches("zombie",
                    com.continuityworks.alfheimcompanion.enemy.EnemyAppearance.profile(mob))?regional:normal;
                try {super.render(mob,yaw,tick,pose,buffers,light);} finally {this.model=normal;}
            }
            @Override public net.minecraft.resources.ResourceLocation getTextureLocation(net.minecraft.world.entity.monster.Zombie mob){return skin(mob,"zombie");}
        });
        event.registerEntityRenderer(ModThemedEnemies.SKELETON.get(),ctx->new SkeletonRenderer(ctx) {
            private final net.minecraft.client.model.SkeletonModel<net.minecraft.world.entity.monster.AbstractSkeleton> normal=this.model;
            private final net.minecraft.client.model.SkeletonModel<net.minecraft.world.entity.monster.AbstractSkeleton> silverbark=
                new net.minecraft.client.model.SkeletonModel<>(ctx.bakeLayer(SilverbarkBoneguardModel.LAYER));
            @Override public void render(net.minecraft.world.entity.monster.AbstractSkeleton mob,float yaw,float tick,
                    com.mojang.blaze3d.vertex.PoseStack pose,net.minecraft.client.renderer.MultiBufferSource buffers,int light) {
                boolean custom=com.continuityworks.alfheimcompanion.enemy.EnemyAppearance.profile(mob)==13 &&
                    com.continuityworks.alfheimcompanion.enemy.EnemyAppearance.style(mob)==0;
                this.model=custom?silverbark:normal;
                try {super.render(mob,yaw,tick,pose,buffers,light);} finally {this.model=normal;}
            }
            @Override public net.minecraft.resources.ResourceLocation getTextureLocation(net.minecraft.world.entity.monster.AbstractSkeleton mob){return skin(mob,"skeleton");}
        });
        event.registerEntityRenderer(ModThemedEnemies.PILLAGER.get(),ctx->new PillagerRenderer(ctx) {
            private final net.minecraft.client.model.IllagerModel<net.minecraft.world.entity.monster.Pillager> normal=this.model;
            private final net.minecraft.client.model.IllagerModel<net.minecraft.world.entity.monster.Pillager> regional=
                new net.minecraft.client.model.IllagerModel<>(ctx.bakeLayer(RegionalMonstrosityModels.location("pillager")));
            @Override public void render(net.minecraft.world.entity.monster.Pillager mob,float yaw,float tick,
                    com.mojang.blaze3d.vertex.PoseStack pose,net.minecraft.client.renderer.MultiBufferSource buffers,int light) {
                this.model=RegionalMonstrosityModels.matches("pillager",
                    com.continuityworks.alfheimcompanion.enemy.EnemyAppearance.profile(mob))?regional:normal;
                try {super.render(mob,yaw,tick,pose,buffers,light);} finally {this.model=normal;}
            }
            @Override public net.minecraft.resources.ResourceLocation getTextureLocation(net.minecraft.world.entity.monster.Pillager mob){return skin(mob,"pillager");}
        });
        event.registerEntityRenderer(ModThemedEnemies.ENDERMAN.get(),ctx->new EndermanRenderer(ctx) {
            private final net.minecraft.client.model.EndermanModel<net.minecraft.world.entity.monster.EnderMan> normal=this.model;
            private final net.minecraft.client.model.EndermanModel<net.minecraft.world.entity.monster.EnderMan> regional=
                new net.minecraft.client.model.EndermanModel<>(ctx.bakeLayer(RegionalMonstrosityModels.location("enderman")));
            private boolean usingRegional;
            {
                this.layers.removeIf(layer->layer instanceof net.minecraft.client.renderer.entity.layers.EnderEyesLayer<?>);
                this.addLayer(new net.minecraft.client.renderer.entity.layers.EnderEyesLayer<net.minecraft.world.entity.monster.EnderMan>(this) {
                    @Override public net.minecraft.client.renderer.RenderType renderType() {
                        return usingRegional?net.minecraft.client.renderer.RenderType.eyes(new net.minecraft.resources.ResourceLocation(
                            "alfheim_companion","textures/entity/themed/verge_eyes.png")):super.renderType();
                    }
                });
            }
            @Override public void render(net.minecraft.world.entity.monster.EnderMan mob,float yaw,float tick,
                    com.mojang.blaze3d.vertex.PoseStack pose,net.minecraft.client.renderer.MultiBufferSource buffers,int light) {
                usingRegional=RegionalMonstrosityModels.matches("enderman",
                    com.continuityworks.alfheimcompanion.enemy.EnemyAppearance.profile(mob));
                this.model=usingRegional?regional:normal;
                try {super.render(mob,yaw,tick,pose,buffers,light);} finally {this.model=normal;usingRegional=false;}
            }
            @Override public net.minecraft.resources.ResourceLocation getTextureLocation(net.minecraft.world.entity.monster.EnderMan mob){return skin(mob,"enderman");}
        });
        event.registerEntityRenderer(ModThemedEnemies.ENDERMITE.get(),ctx->new EndermiteRenderer(ctx) {
            private final net.minecraft.client.model.EndermiteModel<net.minecraft.world.entity.monster.Endermite> normal=this.model;
            private final net.minecraft.client.model.EndermiteModel<net.minecraft.world.entity.monster.Endermite> mire=
                new net.minecraft.client.model.EndermiteModel<>(ctx.bakeLayer(MireRiftmiteModel.LAYER));
            @Override public void render(net.minecraft.world.entity.monster.Endermite mob,float yaw,float tick,
                    com.mojang.blaze3d.vertex.PoseStack pose,net.minecraft.client.renderer.MultiBufferSource buffers,int light) {
                boolean custom=com.continuityworks.alfheimcompanion.enemy.EnemyAppearance.profile(mob)==3 &&
                    com.continuityworks.alfheimcompanion.enemy.EnemyAppearance.style(mob)==0;
                this.model=custom?mire:normal;
                try {super.render(mob,yaw,tick,pose,buffers,light);} finally {this.model=normal;}
            }
            @Override public net.minecraft.resources.ResourceLocation getTextureLocation(net.minecraft.world.entity.monster.Endermite mob){return skin(mob,"endermite");}
        });
    }
    private ThemedEnemyRenderers() {}
}
