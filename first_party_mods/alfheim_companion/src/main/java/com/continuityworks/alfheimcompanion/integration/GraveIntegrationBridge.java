package com.continuityworks.alfheimcompanion.integration;

import com.continuityworks.alfheimcompanion.entity.ElvenCompanionEntity;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;

import java.util.List;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicReference;

/** Optional explicit grave-mod endpoint. No installed grave mod currently supplies an adapter. */
public final class GraveIntegrationBridge {
    @FunctionalInterface
    public interface Provider {
        boolean capture(ServerPlayer lessee, ElvenCompanionEntity companion, List<ItemStack> contents);
    }

    private static final AtomicReference<Provider> PROVIDER = new AtomicReference<>();
    private GraveIntegrationBridge() {}

    public static void register(Provider provider) {
        if (!PROVIDER.compareAndSet(null, Objects.requireNonNull(provider)))
            throw new IllegalStateException("A grave integration provider is already registered");
    }

    public static boolean capture(ServerPlayer lessee, ElvenCompanionEntity companion, List<ItemStack> contents) {
        Provider provider = PROVIDER.get();
        return provider != null && provider.capture(lessee, companion, List.copyOf(contents));
    }
}
