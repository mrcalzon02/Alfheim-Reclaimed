package com.continuityworks.alfheimcompanion.client;

import net.minecraft.client.Minecraft;
import com.continuityworks.alfheimcompanion.registry.ModItems;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;

public final class ClientWheelHooks {
    private ClientWheelHooks() {}

    public static void open() {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft.player != null && minecraft.screen == null) {
            if (!minecraft.player.getInventory().contains(new ItemStack(ModItems.COMPANION_SIGIL.get()))) {
                minecraft.player.displayClientMessage(Component.literal(
                        "You need the Sigil of the Hollow Court to use the companion wheel."), true);
                return;
            }
            minecraft.setScreen(new CompanionCommandWheelScreen());
        }
    }
}
