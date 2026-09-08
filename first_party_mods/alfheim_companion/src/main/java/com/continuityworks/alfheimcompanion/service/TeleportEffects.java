package com.continuityworks.alfheimcompanion.service;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;

public final class TeleportEffects {
    private TeleportEffects() {}

    public static void play(Entity entity) {
        if (!(entity.level() instanceof ServerLevel level)) return;
        level.playSound(null, entity.blockPosition(), SoundEvents.ENDERMAN_TELEPORT,
                SoundSource.NEUTRAL, 1.0F, 0.9F + level.random.nextFloat() * 0.2F);
        level.sendParticles(ParticleTypes.PORTAL, entity.getX(), entity.getY() + 0.9D, entity.getZ(),
                48, 0.45D, 0.9D, 0.45D, 0.08D);
    }
}
