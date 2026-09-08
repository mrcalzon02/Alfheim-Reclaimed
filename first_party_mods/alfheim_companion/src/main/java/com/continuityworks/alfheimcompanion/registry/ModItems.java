package com.continuityworks.alfheimcompanion.registry;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.item.CompanionSigilItem;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModItems {
    public static final DeferredRegister<Item> REGISTRY =
            DeferredRegister.create(ForgeRegistries.ITEMS, AlfheimCompanion.MOD_ID);

    public static final RegistryObject<Item> COMPANION_SIGIL = REGISTRY.register(
            "companion_sigil", () -> new CompanionSigilItem(new Item.Properties().stacksTo(1))
    );

    private ModItems() {}
}
