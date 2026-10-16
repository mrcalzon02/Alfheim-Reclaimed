package com.continuityworks.alfheimcompanion.enemy;

import java.util.function.Supplier;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.*;
import net.minecraft.world.item.*;
import net.minecraftforge.common.ForgeSpawnEggItem;

/** A display name derived from entity NBT avoids naming the spawned mob after an egg. */
public final class ThemedSpawnEggItem extends ForgeSpawnEggItem {
    private final String species;
    public ThemedSpawnEggItem(Supplier<? extends EntityType<? extends Mob>> type,int base,int accent,String species) {
        super(type,base,accent,new Item.Properties());this.species=species;
    }
    @Override public Component getName(ItemStack stack) {
        return EnemySpawnItems.modelKey(stack)==0 ? super.getName(stack) : EnemySpawnItems.name(stack,species);
    }
}
