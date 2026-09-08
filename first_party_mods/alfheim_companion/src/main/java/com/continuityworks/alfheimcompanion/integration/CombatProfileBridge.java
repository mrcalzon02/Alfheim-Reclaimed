package com.continuityworks.alfheimcompanion.integration;

import com.continuityworks.alfheimcompanion.api.combat.CombatProfileProvider;

import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;

public final class CombatProfileBridge {
    private static final AtomicReference<CombatProfileProvider> PROVIDER = new AtomicReference<>();
    private CombatProfileBridge() {}

    public static void register(CombatProfileProvider provider) {
        Objects.requireNonNull(provider);
        if (provider.apiVersion() != CombatProfileProvider.API_VERSION)
            throw new IllegalArgumentException("Unsupported combat profile API version " + provider.apiVersion());
        if (!PROVIDER.compareAndSet(null, provider))
            throw new IllegalStateException("A combat profile provider is already registered");
    }

    public static Optional<CombatProfileProvider> provider() { return Optional.ofNullable(PROVIDER.get()); }
}
