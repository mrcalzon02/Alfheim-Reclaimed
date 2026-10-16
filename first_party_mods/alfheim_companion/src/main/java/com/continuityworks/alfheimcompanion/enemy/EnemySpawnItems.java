package com.continuityworks.alfheimcompanion.enemy;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;

/** Named NBT selections retain the five existing item IDs and vanilla egg spawning. */
public final class EnemySpawnItems {
    public static final String[] LABELS={"Revenant","Boneguard","Outcast","Riftwalker","Riftmite"};
    public static final String[] STYLES={"Bound","Shrouded","Crowned"};
    public static ItemStack variant(int species,int profile,int style) {
        ItemStack stack=new ItemStack(ModThemedEnemies.EGGS.get(species).get());
        CompoundTag entity=stack.getOrCreateTagElement("EntityTag");
        entity.putString("AlfheimBiome",EnemyProfiles.get(profile).biome());
        entity.putInt("AlfheimStyle",Math.floorMod(style,3));
        return stack;
    }
    public static int profile(ItemStack stack) {
        CompoundTag entity=stack.getTagElement("EntityTag");
        return entity!=null && entity.contains("AlfheimBiome") ? EnemyProfiles.index(entity.getString("AlfheimBiome")) : 23;
    }
    public static int style(ItemStack stack) {
        CompoundTag entity=stack.getTagElement("EntityTag");
        return entity==null ? 0 : Math.floorMod(entity.getInt("AlfheimStyle"),3);
    }
    public static int modelKey(ItemStack stack) {
        CompoundTag entity=stack.getTagElement("EntityTag");
        return entity==null || !entity.contains("AlfheimBiome") ? 0 : profile(stack)*3+style(stack)+1;
    }
    public static Component name(ItemStack stack,String species) {
        return Component.literal(EnemyProfiles.get(profile(stack)).title()+" "+STYLES[style(stack)]+" "+species+" Spawn Egg");
    }
    public static void addCreativeItems(BuildCreativeModeTabContentsEvent event) {
        ModThemedEnemies.EGGS.forEach(egg->event.accept(egg.get()));
        for(int species=0;species<5;species++) for(int profile=0;profile<EnemyProfiles.ALL.length;profile++)
            for(int style=0;style<3;style++) event.accept(variant(species,profile,style));
    }
    private EnemySpawnItems() {}
}
