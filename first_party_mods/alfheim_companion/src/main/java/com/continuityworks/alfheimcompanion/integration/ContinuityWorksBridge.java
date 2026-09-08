package com.continuityworks.alfheimcompanion.integration;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.api.blueprint.BlueprintProvider;

import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;

public final class ContinuityWorksBridge {
    private static final AtomicReference<BlueprintProvider> PROVIDER = new AtomicReference<>();

    private ContinuityWorksBridge() {}

    public static void register(BlueprintProvider provider) {
        Objects.requireNonNull(provider, "provider");
        if (provider.apiVersion() != BlueprintProvider.API_VERSION) {
            throw new IllegalArgumentException("Unsupported Continuity Works blueprint API version "
                    + provider.apiVersion());
        }
        if (!PROVIDER.compareAndSet(null, provider)) {
            throw new IllegalStateException("A Continuity Works blueprint provider is already registered");
        }
        AlfheimCompanion.LOGGER.info("Continuity Works blueprint provider connected with capabilities {}",
                provider.capabilities());
    }

    public static Optional<BlueprintProvider> provider() {
        return Optional.ofNullable(PROVIDER.get());
    }
}
