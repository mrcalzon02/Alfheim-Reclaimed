package com.continuityworks.alfheimcompanion.integration;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.fml.ModList;

import java.util.Objects;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Fail-closed integration point for FTB Chunks/Claims. The FTB-specific adapter registers a
 * provider during common setup without making Alfheim Companion depend on FTB implementation classes.
 */
public final class ClaimPermissionBridge {
    public enum Action { BREAK, PLACE, INTERACT, CONTAINER_EXTRACT, CONTAINER_INSERT }

    @FunctionalInterface
    public interface Provider {
        boolean mayAct(ServerPlayer owner, ServerLevel level, BlockPos position, Action action);
    }

    private static final AtomicReference<Provider> PROVIDER = new AtomicReference<>();

    private ClaimPermissionBridge() {}

    public static void register(Provider provider) {
        Objects.requireNonNull(provider, "provider");
        if (!PROVIDER.compareAndSet(null, provider)) {
            throw new IllegalStateException("A claim permission provider is already registered");
        }
    }

    public static boolean mayAct(ServerPlayer owner, ServerLevel level, BlockPos position, Action action) {
        Provider provider = PROVIDER.get();
        if (provider != null) return provider.mayAct(owner, level, position, action);
        // Never guess around claimed land. An FTB-aware adapter is mandatory when FTB Chunks is present.
        return !ModList.get().isLoaded("ftbchunks");
    }
}
