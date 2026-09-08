package com.continuityworks.alfheimcompanion.integration;

import com.continuityworks.alfheimcompanion.api.quest.QuestProvider;

import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;

public final class QuestAwarenessBridge {
    private static final AtomicReference<QuestProvider> PROVIDER = new AtomicReference<>();

    private QuestAwarenessBridge() {}

    public static void register(QuestProvider provider) {
        Objects.requireNonNull(provider, "provider");
        if (provider.apiVersion() != QuestProvider.API_VERSION)
            throw new IllegalArgumentException("Unsupported quest API version " + provider.apiVersion());
        if (!PROVIDER.compareAndSet(null, provider))
            throw new IllegalStateException("A quest provider is already registered");
    }

    public static Optional<QuestProvider> provider() {
        return Optional.ofNullable(PROVIDER.get());
    }
}
