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

    /** Internal two-choice value decision; implementations cannot supply coordinates or actions. */
    default CompletableFuture<ClaimDistrictDecision> chooseClaimDistrict(ClaimDistrictSnapshot snapshot) {
        ClaimDistrictDecision.Choice choice = snapshot.candidateValue() >= snapshot.currentValue() + 10
                ? ClaimDistrictDecision.Choice.RELOCATE_DISTRICT
                : ClaimDistrictDecision.Choice.KEEP_DISTRICT;
        return CompletableFuture.completedFuture(new ClaimDistrictDecision(snapshot.requestId(), choice));
    }

    /** Slow self-direction choice. The result must name one Java-offered option and nothing else. */
    default CompletableFuture<AutonomousActivityDecision> chooseAutonomousActivity(
            AutonomousActivitySnapshot snapshot) {
        AutonomousActivityOption selected = snapshot.options().stream()
                .max(java.util.Comparator.comparingInt(AutonomousActivityOption::value)
                        .thenComparing(AutonomousActivityOption::id, java.util.Comparator.reverseOrder()))
                .orElseThrow(() -> new IllegalArgumentException("no autonomous activity options"));
        return CompletableFuture.completedFuture(new AutonomousActivityDecision(
                snapshot.requestId(), selected.id()));
    }

    /** Dialogue-only reflection. An empty result means remain silent. */
    default CompletableFuture<Optional<String>> reflect(AmbientSnapshot snapshot) {
        return CompletableFuture.completedFuture(Optional.empty());
    }

    @Override
    default void close() { deactivate(); }
}
