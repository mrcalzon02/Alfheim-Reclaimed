package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.enemy.ModThemedEnemies;
import net.minecraft.client.renderer.entity.*;
import net.minecraftforge.client.event.EntityRenderersEvent;

/** Keep vanilla animation, equipment, eye glow, held blocks and weapons. */
public final class ThemedEnemyRenderers {
    public static void register(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModThemedEnemies.ZOMBIE.get(),ctx->new ZombieRenderer(ctx) {{
            addLayer(new ThemedMaterialLayer<>(this,ctx,"zombie"));
        }});
        event.registerEntityRenderer(ModThemedEnemies.SKELETON.get(),ctx->new SkeletonRenderer(ctx) {{
            addLayer(new ThemedMaterialLayer<>(this,ctx,"skeleton"));
        }});
        event.registerEntityRenderer(ModThemedEnemies.PILLAGER.get(),ctx->new PillagerRenderer(ctx) {{
            addLayer(new ThemedMaterialLayer<>(this,ctx,"pillager"));
        }});
        event.registerEntityRenderer(ModThemedEnemies.ENDERMAN.get(),ctx->new EndermanRenderer(ctx) {{
            addLayer(new ThemedMaterialLayer<>(this,ctx,"enderman"));
        }});
        event.registerEntityRenderer(ModThemedEnemies.ENDERMITE.get(),ctx->new EndermiteRenderer(ctx) {{
            addLayer(new ThemedMaterialLayer<>(this,ctx,"endermite"));
        }});
    }
    private ThemedEnemyRenderers() {}
}
