package com.continuityworks.alfheimcompanion.brain;

import java.util.concurrent.CompletableFuture;
import java.util.Optional;

/**
 * Pluggable planning boundary. Implementations must consume only immutable snapshots and must
 * never retain or access Minecraft world objects from a worker thread.
 */
public interface TinyBrainEngine extends AutoCloseable {
    String engineId();

    /** Allocate model resources. Called only while the companion is summoned and needs reasoning. */
    default void activate() {}

    /** Release model weights and working buffers when the companion is dismissed. */
    default void deactivate() {}

    CompletableFuture<BrainDecision> plan(BrainSnapshot snapshot);

    /** Dialogue-only reflection. An empty result means remain silent. */
    default CompletableFuture<Optional<String>> reflect(AmbientSnapshot snapshot) {
        return CompletableFuture.completedFuture(Optional.empty());
    }

    @Override
    default void close() { deactivate(); }
}
