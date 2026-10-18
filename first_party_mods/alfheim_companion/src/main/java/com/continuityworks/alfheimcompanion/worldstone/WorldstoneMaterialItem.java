package com.continuityworks.alfheimcompanion.worldstone;

import net.minecraft.network.chat.Component;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import java.util.List;

public final class WorldstoneMaterialItem extends Item {
    private final boolean attuned;
    public WorldstoneMaterialItem(boolean attuned){super(new Item.Properties());this.attuned=attuned;}
    @Override public boolean isFoil(ItemStack stack){return attuned;}
    @Override public void appendHoverText(ItemStack stack,Level level,List<Component> lines,TooltipFlag flag) {
        if(attuned) {
            lines.add(Component.literal("Worldstone Fragments bound with Alfsteel and Rimebound Lattice in a Mana Infuser."));
            lines.add(Component.literal("Use in an Enchanting Apparatus to refine Divine Ore, Godly Ore, Legendary Stone or Mythic Stone."));
        } else {
            lines.add(Component.literal("Mine Worldstone Fragment Ore or harvest mature Worldstone Crystal Clusters."));
            lines.add(Component.literal("Bind fragments with Alfsteel and Rimebound Lattice in a Mana Infuser."));
        }
    }
}
