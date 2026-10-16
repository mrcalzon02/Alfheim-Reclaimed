package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.enemy.EnemyProfiles;
import com.continuityworks.alfheimcompanion.enemy.EnemySpawnItems;
import com.continuityworks.alfheimcompanion.enemy.ModThemedEnemies;
import net.minecraft.client.renderer.item.ItemProperties;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.client.event.RegisterColorHandlersEvent;

/** The same saved biome/style selects the spawned entity, icon geometry and material tint. */
public final class EnemySpawnItemAppearance {
    public static void registerProperties() {
        ModThemedEnemies.EGGS.forEach(egg->ItemProperties.register(egg.get(),
            new ResourceLocation("alfheim_companion","appearance"),
            (stack,world,entity,seed)->EnemySpawnItems.modelKey(stack)));
    }
    public static void colors(RegisterColorHandlersEvent.Item event) {
        ModThemedEnemies.EGGS.forEach(egg->event.register((stack,layer)-> {
            var profile=EnemyProfiles.get(EnemySpawnItems.profile(stack));
            return layer==0 ? profile.body() : layer==1 ? profile.accent() : -1;
        },egg.get()));
    }
    private EnemySpawnItemAppearance() {}
}
