package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;

public final class ClientWheelEvents {
    private static final KeyMapping OPEN_WHEEL = new KeyMapping(
            "key.alfheim_companion.command_wheel", InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_V, "key.categories.alfheim_companion");

    private ClientWheelEvents() {}

    @Mod.EventBusSubscriber(modid = AlfheimCompanion.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
    public static final class ModBus {
        @SubscribeEvent
        public static void registerKeys(RegisterKeyMappingsEvent event) { event.register(OPEN_WHEEL); }
    }

    @Mod.EventBusSubscriber(modid = AlfheimCompanion.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
    public static final class ForgeBus {
        @SubscribeEvent
        public static void clientTick(TickEvent.ClientTickEvent event) {
            if (event.phase != TickEvent.Phase.END) return;
            while (OPEN_WHEEL.consumeClick()) ClientWheelHooks.open();
        }
    }
}
