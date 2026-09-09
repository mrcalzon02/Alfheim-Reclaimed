package com.continuityworks.alfheimcompanion.brain.local;

import com.continuityworks.alfheimcompanion.AlfheimCompanion;
import com.continuityworks.alfheimcompanion.brain.AmbientSnapshot;
import com.continuityworks.alfheimcompanion.brain.BrainDecision;
import com.continuityworks.alfheimcompanion.brain.BrainSnapshot;
import com.continuityworks.alfheimcompanion.brain.TinyBrainEngine;
import com.continuityworks.alfheimcompanion.brain.ClaimDistrictDecision;
import com.continuityworks.alfheimcompanion.brain.ClaimDistrictSnapshot;
import com.continuityworks.alfheimcompanion.brain.AutonomousActivityDecision;
import com.continuityworks.alfheimcompanion.brain.AutonomousActivitySnapshot;

import java.util.Optional;
import java.util.concurrent.CompletableFuture;

/** Keeps gameplay deterministic and available while the optional worker is absent or warming up. */
public final class ResilientTinyBrainEngine implements TinyBrainEngine {
    private final TinyBrainEngine primary;
    private final TinyBrainEngine fallback;

    public ResilientTinyBrainEngine(TinyBrainEngine primary, TinyBrainEngine fallback) {
        this.primary = primary;
        this.fallback = fallback;
    }

    @Override public String engineId() { return primary.engineId() + "+fallback:" + fallback.engineId(); }

    @Override
    public void activate() {
        primary.activate();
        fallback.activate();
    }

    @Override
    public void deactivate() {
        primary.deactivate();
        fallback.deactivate();
    }

    @Override
    public CompletableFuture<BrainDecision> plan(BrainSnapshot snapshot) {
        try {
            return primary.plan(snapshot).handle((decision, error) -> {
                if (error == null && decision != null) return CompletableFuture.completedFuture(decision);
                AlfheimCompanion.LOGGER.warn("Local inference unavailable; using deterministic companion response: {}",
                        error == null ? "empty decision" : rootMessage(error));
                return fallback.plan(snapshot);
            }).thenCompose(value -> value);
        } catch (RuntimeException error) {
            AlfheimCompanion.LOGGER.warn("Local inference could not start; using deterministic companion response: {}",
                    rootMessage(error));
            return fallback.plan(snapshot);
        }
    }

    @Override
    public CompletableFuture<Optional<String>> reflect(AmbientSnapshot snapshot) {
        try {
            return primary.reflect(snapshot).handle((line, error) -> {
                if (error == null && line != null && line.isPresent())
                    return CompletableFuture.completedFuture(line);
                return fallback.reflect(snapshot);
            }).thenCompose(value -> value);
        } catch (RuntimeException error) {
            return fallback.reflect(snapshot);
        }
    }

    @Override
    public CompletableFuture<ClaimDistrictDecision> chooseClaimDistrict(ClaimDistrictSnapshot snapshot) {
        try {
            return primary.chooseClaimDistrict(snapshot).handle((decision, error) -> {
                if (error == null && decision != null) return CompletableFuture.completedFuture(decision);
                AlfheimCompanion.LOGGER.warn("Claim district inference unavailable; using value fallback: {}",
                        error == null ? "empty decision" : rootMessage(error));
                return fallback.chooseClaimDistrict(snapshot);
            }).thenCompose(value -> value);
        } catch (RuntimeException error) {
            return fallback.chooseClaimDistrict(snapshot);
        }
    }

    @Override
    public CompletableFuture<AutonomousActivityDecision> chooseAutonomousActivity(
            AutonomousActivitySnapshot snapshot) {
        try {
            return primary.chooseAutonomousActivity(snapshot).handle((decision, error) -> {
                if (error == null && decision != null) return CompletableFuture.completedFuture(decision);
                AlfheimCompanion.LOGGER.warn("Autonomous activity inference unavailable; using value fallback: {}",
                        error == null ? "empty decision" : rootMessage(error));
                return fallback.chooseAutonomousActivity(snapshot);
            }).thenCompose(value -> value);
        } catch (RuntimeException error) {
            return fallback.chooseAutonomousActivity(snapshot);
        }
    }

    @Override
    public void close() {
        try { primary.close(); }
        finally { fallback.close(); }
    }

    private static String rootMessage(Throwable error) {
        Throwable current = error;
        while (current.getCause() != null) current = current.getCause();
        return current.getClass().getSimpleName() + ": " + String.valueOf(current.getMessage());
    }
}
