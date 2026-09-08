package com.continuityworks.alfheimcompanion.registry;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.menu.CompanionInventoryMenu;
import net.minecraft.world.inventory.MenuType;
import net.minecraftforge.common.extensions.IForgeMenuType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModMenus {
    public static final DeferredRegister<MenuType<?>> REGISTRY =
            DeferredRegister.create(ForgeRegistries.MENU_TYPES, AlfheimCompanion.MOD_ID);
    public static final RegistryObject<MenuType<CompanionInventoryMenu>> COMPANION_INVENTORY =
            REGISTRY.register("companion_inventory", () -> IForgeMenuType.create(CompanionInventoryMenu::fromNetwork));

    private ModMenus() {}
}
