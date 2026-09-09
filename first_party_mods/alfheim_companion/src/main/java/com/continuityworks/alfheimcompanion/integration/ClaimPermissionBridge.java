package com.continuityworks.alfheimcompanion.integration;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.fml.ModList;
import net.minecraft.world.level.ChunkPos;

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

    @FunctionalInterface
    public interface ClaimProvider {
        ClaimAttempt claim(ServerPlayer owner, ServerLevel level, ChunkPos position);
    }

    @FunctionalInterface
    public interface ClaimStatusProvider {
        boolean isClaimed(ServerLevel level, ChunkPos position);
    }

    public interface ClaimMutationProvider {
        ClaimAttempt previewClaim(ServerPlayer owner, ServerLevel level, ChunkPos position);
        ClaimAttempt unclaim(ServerPlayer owner, ServerLevel level, ChunkPos position);
    }

    public record ClaimAttempt(boolean success, String message) {
        public ClaimAttempt {
            message = message == null ? "" : message.strip();
            if (message.length() > 160) message = message.substring(0, 160);
        }
    }

    private static final AtomicReference<Provider> PROVIDER = new AtomicReference<>();
    private static final AtomicReference<ClaimProvider> CLAIM_PROVIDER = new AtomicReference<>();
    private static final AtomicReference<ClaimStatusProvider> CLAIM_STATUS_PROVIDER = new AtomicReference<>();
    private static final AtomicReference<ClaimMutationProvider> CLAIM_MUTATION_PROVIDER = new AtomicReference<>();

    private ClaimPermissionBridge() {}

    public static void register(Provider provider) {
        Objects.requireNonNull(provider, "provider");
        if (!PROVIDER.compareAndSet(null, provider)) {
            throw new IllegalStateException("A claim permission provider is already registered");
        }
    }

    public static void registerClaimProvider(ClaimProvider provider) {
        Objects.requireNonNull(provider, "provider");
        if (!CLAIM_PROVIDER.compareAndSet(null, provider))
            throw new IllegalStateException("A chunk claim provider is already registered");
    }

    public static void registerClaimStatusProvider(ClaimStatusProvider provider) {
        Objects.requireNonNull(provider, "provider");
        if (!CLAIM_STATUS_PROVIDER.compareAndSet(null, provider))
            throw new IllegalStateException("A chunk claim status provider is already registered");
    }

    public static void registerClaimMutationProvider(ClaimMutationProvider provider) {
        Objects.requireNonNull(provider, "provider");
        if (!CLAIM_MUTATION_PROVIDER.compareAndSet(null, provider))
            throw new IllegalStateException("A chunk claim mutation provider is already registered");
    }

    public static boolean mayAct(ServerPlayer owner, ServerLevel level, BlockPos position, Action action) {
        Provider provider = PROVIDER.get();
        if (provider != null) return provider.mayAct(owner, level, position, action);
        // Never guess around claimed land. An FTB-aware adapter is mandatory when FTB Chunks is present.
        return !ModList.get().isLoaded("ftbchunks");
    }

    public static ClaimAttempt claim(ServerPlayer owner, ServerLevel level, ChunkPos position) {
        ClaimProvider provider = CLAIM_PROVIDER.get();
        if (provider == null) return new ClaimAttempt(false, "No compatible chunk-claim provider is connected.");
        return provider.claim(owner, level, position);
    }

    public static boolean isClaimed(ServerLevel level, ChunkPos position) {
        ClaimStatusProvider provider = CLAIM_STATUS_PROVIDER.get();
        return provider == null || provider.isClaimed(level, position);
    }

    public static ClaimAttempt previewClaim(ServerPlayer owner, ServerLevel level, ChunkPos position) {
        ClaimMutationProvider provider = CLAIM_MUTATION_PROVIDER.get();
        return provider == null ? new ClaimAttempt(false, "No compatible chunk-claim provider is connected.")
                : provider.previewClaim(owner, level, position);
    }

    public static ClaimAttempt unclaim(ServerPlayer owner, ServerLevel level, ChunkPos position) {
        ClaimMutationProvider provider = CLAIM_MUTATION_PROVIDER.get();
        return provider == null ? new ClaimAttempt(false, "No compatible chunk-claim provider is connected.")
                : provider.unclaim(owner, level, position);
    }
}
