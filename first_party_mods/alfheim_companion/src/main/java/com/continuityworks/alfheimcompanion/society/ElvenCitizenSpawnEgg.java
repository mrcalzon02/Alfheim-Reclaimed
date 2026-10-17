package com.continuityworks.alfheimcompanion.society;

import com.continuityworks.alfheimcompanion.registry.ModEntities;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.*;
import net.minecraftforge.common.ForgeSpawnEggItem;

public final class ElvenCitizenSpawnEgg extends ForgeSpawnEggItem {
    public ElvenCitizenSpawnEgg(){super(ModEntities.ELVEN_CITIZEN,0x91ac83,0xe0c998,new Item.Properties());}
    @Override public Component getName(ItemStack stack){return Component.literal("Elven "+ElvenSociety.NAMES[ElvenSociety.role(stack)]+" Spawn Egg ("+ElvenSociety.LOOKS[ElvenSociety.look(stack)]+")");}
}
