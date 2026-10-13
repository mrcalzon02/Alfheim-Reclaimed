package com.continuityworks.alfheimcompanion.client;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.material.FogType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Atmospheric shore fog; does not change terrain, underwater fog or status effects. */
@Mod.EventBusSubscriber(modid = AlfheimCompanion.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
public final class MistbarkFogEvents {
    private static final ResourceLocation SHORE = new ResourceLocation("alfheim", "mistbark_shore");
    private static float strength;
    private static long lastTime;

    private MistbarkFogEvents() {}

    @SubscribeEvent
    public static void renderFog(ViewportEvent.RenderFog event) {
        Minecraft client = Minecraft.getInstance();
        if (client.level == null) { strength = 0; lastTime = 0; return; }
        long now = System.nanoTime();
        float dt = lastTime == 0 ? 0 : Math.min(0.1F, (now - lastTime) / 1_000_000_000F);
        lastTime = now;
        boolean mist = client.level.getBiome(event.getCamera().getBlockPosition())
                .unwrapKey().map(key -> SHORE.equals(key.location())).orElse(false);
        float target = mist ? 1 : 0;
        strength += (target - strength) * Math.min(1, dt * 1.5F);
        if (strength < 0.001F || event.getType() != FogType.NONE) return;
        // Keep shorter vanilla fog (blindness, darkness, short render distance).
        float far = event.getFarPlaneDistance();
        float near = event.getNearPlaneDistance();
        event.setFarPlaneDistance(far + (Math.min(far, 56F) - far) * strength);
        event.setNearPlaneDistance(near + (Math.min(near, 4F) - near) * strength);
        event.setCanceled(true);
    }
}
